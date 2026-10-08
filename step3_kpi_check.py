"""
STEP 3: KPI Baseline & Anomaly Detection (Linux VM / Router Parameter Fluctuations)
-----------------------------------------------------------------------------------
Reads:
  - data/kpis/masked_kpis.csv (25 3GPP XML PM intervals across MASKED-CPF-01, MASKED-UPF-01, MASKED-UPF-02)
Outputs:
  - data/kpis/kpi_anomalies.json (Detected KPI spikes/drops vs Normal Baseline)
"""

import json
import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KPI_CSV_PATH = os.path.join(BASE_DIR, "data", "kpis", "masked_kpis.csv")
OUTPUT_ANOMALIES_PATH = os.path.join(BASE_DIR, "data", "kpis", "kpi_anomalies.json")

KPI_METRICS = [
    "avg_isa_cpu_pct",
    "max_cpm_cpu_pct",
    "avg_memory_utilization_pct",
    "cntrl_fabric_max_jitter_us",
    "data_fabric_max_jitter_us",
    "s5_modify_bearer_sr_pct",
    "s5_update_bearer_fails",
    "s2b_session_sr_pct",
    "total_traffic_mb",
]


def run_step3_kpi_check():
    df = pd.read_csv(KPI_CSV_PATH)
    anomalies = []
    baselines = {}

    for node, node_df in df.groupby("node"):
        baselines[node] = {}
        for metric in KPI_METRICS:
            if metric not in node_df.columns:
                continue
            vals = node_df[metric].astype(float).values
            median_val = float(np.median(vals))
            mad = float(np.median(np.abs(vals - median_val)))
            std_val = float(np.std(vals))
            scale = max(mad * 1.4826, std_val, 0.01)

            baselines[node][metric] = {
                "baseline_median": round(median_val, 2),
                "baseline_std": round(std_val, 2),
                "min": round(float(np.min(vals)), 2),
                "max": round(float(np.max(vals)), 2),
            }

            for _, row in node_df.iterrows():
                obs = float(row[metric])
                z_score = (obs - median_val) / scale

                is_anomaly = False
                direction = "SPIKE"
                if metric in ("s5_modify_bearer_sr_pct", "s2b_session_sr_pct"):
                    if z_score <= -2.0 and obs < median_val:
                        is_anomaly = True
                        direction = "DROP"
                elif metric == "s5_update_bearer_fails":
                    if obs > median_val and z_score >= 2.0:
                        is_anomaly = True
                        direction = "FAILURE_SPIKE"
                else:
                    if z_score >= 2.0 and obs > median_val:
                        is_anomaly = True
                        direction = "SPIKE"

                if is_anomaly:
                    anomalies.append({
                        "node": node,
                        "timestamp": row["timestamp"],
                        "metric": metric,
                        "observed_value": round(obs, 2),
                        "baseline_normal": round(median_val, 2),
                        "z_score": round(abs(z_score), 2),
                        "direction": direction,
                        "severity": "CRITICAL" if abs(z_score) >= 3.0 else "MAJOR",
                    })

    anomalies.sort(key=lambda x: (-x["z_score"], x["timestamp"]))

    output_data = {
        "total_kpi_rows": len(df),
        "nodes_checked": sorted(list(df["node"].unique())),
        "total_anomalies": len(anomalies),
        "baselines": baselines,
        "anomalies": anomalies,
    }

    with open(OUTPUT_ANOMALIES_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    return output_data


if __name__ == "__main__":
    res = run_step3_kpi_check()
    print("=" * 65)
    print("STEP 3 COMPLETE: KPI BASELINE & ANOMALY DETECTION")
    print("=" * 65)
    print(f"Nodes Checked       : {', '.join(res['nodes_checked'])}")
    print(f"Total KPI Rows      : {res['total_kpi_rows']} (25 XML intervals x 3 nodes)")
    print(f"Anomalies Detected  : {res['total_anomalies']} -> data/kpis/kpi_anomalies.json")
    for a in res["anomalies"][:5]:
        print(
            f"  - [{a['severity']}] {a['node']} @ {a['timestamp']} | "
            f"{a['metric']} = {a['observed_value']} (Normal Baseline: {a['baseline_normal']}, Z={a['z_score']})"
        )
    print("=" * 65)
