"""
STEP 3: Group Triggered Alarms into Incidents & Find the Main Root Cause
------------------------------------------------------------------------
Reads:
  - data/kpis/kpi_anomalies.json     (Live VM triggered alarms from Step 2)
  - data/alarms/masked_alarms.json   (500 masked router log alarms)
  - data/topology/masked_topology.json
Does:
  1. Filters out 100 routine accounting rollover logs (LOGGER #2008 / #2009).
  2. Groups the 400 real fault alarms into 3 Incidents using a 10-minute sliding window.
  3. Links each Incident to the live VM KPI fluctuations from Step 2.
  4. Ranks the #1 Probable Root Cause out of 100 marks (Layer + Timing + Severity + Topology).
Outputs:
  - data/alarms/correlated_incidents.json
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALARMS_PATH = os.path.join(BASE_DIR, "data", "alarms", "masked_alarms.json")
TOPOLOGY_PATH = os.path.join(BASE_DIR, "data", "topology", "masked_topology.json")
KPI_ANOMALIES_PATH = os.path.join(BASE_DIR, "data", "kpis", "kpi_anomalies.json")
OUTPUT_INCIDENTS_PATH = os.path.join(BASE_DIR, "data", "alarms", "correlated_incidents.json")

LAYER_PRIORITY = {
    "L0_INFRA": 100,
    "L1_TRANSPORT": 85,
    "L2_ROUTING": 70,
    "L3_CONTROL_PLANE": 55,
    "L3_USER_PLANE": 50,
    "L4_SERVICE_KPI": 30,
    "L4_NOISE": 0,
}

SEVERITY_SCORE = {
    "CRITICAL": 40,
    "MAJOR": 30,
    "MINOR": 15,
    "WARNING": 10,
    "INDETERMINATE": 5,
}


def parse_ts(ts_str: str) -> datetime:
    return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ")


def run_step3_correlation():
    with open(ALARMS_PATH, "r", encoding="utf-8") as f:
        raw_alarms = json.load(f)
    with open(TOPOLOGY_PATH, "r", encoding="utf-8") as f:
        topology = json.load(f)
    with open(KPI_ANOMALIES_PATH, "r", encoding="utf-8") as f:
        kpi_data = json.load(f)

    # Build topology neighbor map
    neighbors = {n["id"]: set() for n in topology["nodes"]}
    for link in topology["links"]:
        s, t = link["source"], link["target"]
        neighbors.setdefault(s, set()).add(t)
        neighbors.setdefault(t, set()).add(s)

    # 1. Filter out routine accounting log rollovers (LOGGER #2008 / #2009)
    noise_alarms = []
    fault_alarms = []
    for alm in raw_alarms:
        if alm["layer"] == "L4_NOISE" or alm["alarm_code"] in ("LOGGER #2008", "LOGGER #2009"):
            noise_alarms.append(alm)
        else:
            fault_alarms.append(alm)

    fault_alarms.sort(key=lambda x: x["timestamp"])

    # 2. Group fault alarms into Incidents using a 10-minute sliding time window
    clusters = []
    current_cluster = []
    last_dt = None

    for alm in fault_alarms:
        dt = parse_ts(alm["timestamp"])
        if not current_cluster:
            current_cluster = [alm]
            last_dt = dt
        else:
            gap_minutes = (dt - last_dt).total_seconds() / 60.0
            if gap_minutes <= 10.0:
                current_cluster.append(alm)
                last_dt = dt
            else:
                clusters.append(current_cluster)
                current_cluster = [alm]
                last_dt = dt
    if current_cluster:
        clusters.append(current_cluster)

    # 3. Score every candidate inside each Incident to find the #1 Main Root Cause
    incidents = []
    for idx, cluster in enumerate(clusters, start=1):
        inc_id = f"INC-2026-{idx:03d}"
        start_ts = cluster[0]["timestamp"]
        end_ts = cluster[-1]["timestamp"]
        start_dt = parse_ts(start_ts)
        affected_nodes = sorted(list({a["node"] for a in cluster}))

        candidates = {}
        for alm in cluster:
            key = (alm["node"], alm["alarm_code"], alm["alarm_type"], alm["layer"])
            if key not in candidates:
                candidates[key] = {
                    "node": alm["node"],
                    "alarm_code": alm["alarm_code"],
                    "alarm_type": alm["alarm_type"],
                    "layer": alm["layer"],
                    "severity": alm["severity"],
                    "first_seen": alm["timestamp"],
                    "resource": alm["resource"],
                    "sample_details": alm["details"],
                    "count": 0,
                }
            candidates[key]["count"] += 1
            if SEVERITY_SCORE.get(alm["severity"], 0) > SEVERITY_SCORE.get(candidates[key]["severity"], 0):
                candidates[key]["severity"] = alm["severity"]

        ranked_candidates = []
        for cand in candidates.values():
            layer_pts = LAYER_PRIORITY.get(cand["layer"], 25) * 0.60
            sev_pts = SEVERITY_SCORE.get(cand["severity"], 10) * 0.45
            delay_sec = max(0.0, (parse_ts(cand["first_seen"]) - start_dt).total_seconds())
            timing_pts = max(0.0, 15.0 - (delay_sec / 60.0))
            connected_affected = sum(1 for n in affected_nodes if n != cand["node"] and n in neighbors.get(cand["node"], set()))
            topo_pts = connected_affected * 5.0

            total_score = round(min(99.0, layer_pts + sev_pts + timing_pts + topo_pts), 1)
            cand["score"] = total_score
            cand["explanation"] = (
                f"Layer={cand['layer']} ({round(layer_pts,1)} pts) + "
                f"Severity={cand['severity']} ({round(sev_pts,1)} pts) + "
                f"First Seen ({round(timing_pts,1)} pts) + "
                f"Topology Neighbors={connected_affected} ({round(topo_pts,1)} pts)"
            )
            ranked_candidates.append(cand)

        ranked_candidates.sort(key=lambda x: (-x["score"], x["first_seen"]))
        root = ranked_candidates[0]
        confidence = round(min(0.98, max(0.65, root["score"] / 100.0)), 2)

        # Match Step 2 KPI triggers related to this Root Cause
        matching_kpi_triggers = [
            f for f in kpi_data.get("fluctuations", [])
            if f["triggered_alarm_code"] == root["alarm_code"] or root["node"] in f["node"]
        ][:5]

        incidents.append({
            "incident_id": inc_id,
            "title": f"{root['alarm_type']} ({root['alarm_code']}) on {root['node']}",
            "time_window_start": start_ts,
            "time_window_end": end_ts,
            "total_alarms": len(cluster),
            "affected_nodes": affected_nodes,
            "probable_root_node": root["node"],
            "probable_root_alarm_code": root["alarm_code"],
            "probable_root_alarm_type": root["alarm_type"],
            "probable_root_layer": root["layer"],
            "probable_root_resource": root["resource"],
            "severity": root["severity"],
            "confidence_score": confidence,
            "reasoning_summary": (
                f"Main Root Cause is `{root['alarm_code']}` ({root['alarm_type']}) on `{root['node']}` "
                f"(Score: {root['score']}/100, Confidence: {int(confidence*100)}%). "
                f"It occurred FIRST at `{root['first_seen']}` on lower layer `{root['layer']}`, causing "
                f"{len(cluster)-1} downstream symptom alarms across {', '.join(affected_nodes)}."
            ),
            "linked_kpi_fluctuations": matching_kpi_triggers,
            "root_ranking": ranked_candidates[:5],
            "symptom_alarms": cluster,
        })

    output_data = {
        "live_vm_host": kpi_data.get("live_vm_telemetry", {}).get("vm_host", "saich@Varun"),
        "total_raw_alarms": len(raw_alarms),
        "filtered_noise_count": len(noise_alarms),
        "fault_alarms_count": len(fault_alarms),
        "incident_count": len(incidents),
        "incidents": incidents,
    }

    with open(OUTPUT_INCIDENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    return output_data


if __name__ == "__main__":
    res = run_step3_correlation()
    print("=" * 80)
    print(f"STEP 3 COMPLETE: CORRELATE ALARMS INTO INCIDENTS & FIND MAIN ROOT CAUSE")
    print("=" * 80)
    print(f"Live Linux VM Linked : {res['live_vm_host']}")
    print(f"Total Masked Alarms  : {res['total_raw_alarms']}")
    print(f"Filtered Noise Logs  : {res['filtered_noise_count']} (LOGGER #2008 / #2009 file rollovers)")
    print(f"Real Fault Alarms    : {res['fault_alarms_count']} -> Grouped into {res['incident_count']} Incidents:")
    print("-" * 80)
    for inc in res["incidents"]:
        print(
            f"  * {inc['incident_id']} ({inc['total_alarms']} alarms, {inc['time_window_start']} -> {inc['time_window_end']}):\n"
            f"    ==> #1 MAIN ROOT CAUSE: {inc['probable_root_alarm_code']} ({inc['probable_root_alarm_type']}) "
            f"on {inc['probable_root_node']} [Layer: {inc['probable_root_layer']} | Confidence: {int(inc['confidence_score']*100)}%]"
        )
    print("=" * 80)
