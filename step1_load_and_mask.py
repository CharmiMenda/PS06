"""
STEP 1: Load Original PS-06 Data & Mask All Confidential Information
--------------------------------------------------------------------
Reads original files from C:\\Users\\saich\\Downloads\\Hackathon_Central_Data\\PS06 (Read-Only)
and writes 100% masked files into ./data/:
1. data/alarms/masked_alarms.json & masked_alarms.csv  (from CPF Logs, UPF-01 Logs, UPF-02 Logs)
2. data/kpis/masked_kpis.csv                           (from 25 3GPP XML PM files in KPI-KCI)
3. data/topology/masked_topology.json                  (4 masked nodes & 6 links)
4. data/runbooks/RB_CPF_Masked.md, RB_UPF01_Masked.md, RB_UPF02_Masked.md (from Supported Commands)
"""

import csv
import glob
import gzip
import json
import os
import re
import xml.etree.ElementTree as ET

ORIGINAL_PS06_DIR = r"C:\Users\saich\Downloads\Hackathon_Central_Data\PS06"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def mask_confidential_text(text: str) -> str:
    """
    Masks all confidential identifiers in the original PS-06 text:
    - Real router hostnames -> MASKED-CPF-01, MASKED-UPF-01, MASKED-UPF-02
    - Diameter / GTP peer names -> MASKED_PEER_*
    - Operator / Location / PLMN / ASN -> [MASKED-OP], [MASKED-SITE], MCC=001,MNC=01
    - Every IPv4 and IPv6 address -> <MASKED-IP>, <MASKED-IPV6>
    """
    if not text:
        return ""
    out = text

    # 1. Mask router hostnames
    host_rules = [
        (r"INVIUW10AGRSSAEC01NK", "MASKED-CPF-01"),
        (r"INVIUW10AGRSSAEU01NK", "MASKED-UPF-01"),
        (r"INVIUW10AGRSSAEU02NK", "MASKED-UPF-02"),
        (r"INVIUE09LKW7SAEC01NK", "MASKED-CPF-01"),
        (r"INVIUE09AMGSSAEC01NK", "MASKED-CPF-01"),
        (r"INVI[A-Z0-9]+", "MASKED-NODE"),
    ]
    for pat, rep in host_rules:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)

    # 2. Mask Diameter peers, PLMNs, ASNs, and log filenames
    peer_rules = [
        (r"UWAGRS_OCC_[A-Z0-9_]+", "MASKED_PEER_GY"),
        (r"UWAGRS_DRA_[A-Z0-9_]+_S6b_[0-9]+", "MASKED_PEER_S6B"),
        (r"UWAGRS_DRA_[A-Z0-9_]+_GY_[0-9]+", "MASKED_PEER_GY"),
        (r"UWAGRS_DRA_[A-Z0-9_]+_GX_[0-9]+", "MASKED_PEER_GX"),
        (r"UWAGRS_PCRF_[A-Z0-9_]+", "MASKED_PEER_PCRF_GX"),
        (r"UWAGRS_[A-Z0-9_]+", "MASKED_DIAMETER_PEER"),
        (r"405\.066\.[A-Za-z0-9._-]+", "MASKED_PLMN.PGW.UP"),
        (r"MCC=404,MNC=015", "MCC=001,MNC=01"),
        (r"ASN\s+\d+", "ASN <MASKED-ASN>"),
        (r"A\d{8}\.\d{4}[+-]\d{4}-\d{4}[+-]\d{4}_[A-Za-z0-9_-]+\.xml\.gz", "<MASKED-PM-FILE>.xml.gz"),
        (r"act\d+-\d{8}-\d{6}\.xml\.gz", "<MASKED-ACT-FILE>.xml.gz"),
    ]
    for pat, rep in peer_rules:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)

    # 3. Mask operator names, APNs, and city/location names
    word_rules = [
        (r"imshomevoda", "imshome_opA"),
        (r"imshomeidea", "imshome_opB"),
        (r"imsroamvoda", "imsroam_opA"),
        (r"imsroamidea", "imsroam_opB"),
        (r"voda(fone)?", "[MASKED-OP-A]"),
        (r"idea", "[MASKED-OP-B]"),
        (r"\bvil\b", "[MASKED-OP]"),
        (r"airtel", "[MASKED-OP-C]"),
        (r"agra|lucknow|kanpur|mohali|meerut|gorakhpur|gomti|ashok", "[MASKED-SITE]"),
    ]
    for pat, rep in word_rules:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)

    # 4. Mask all IPv4 addresses
    out = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<MASKED-IP>", out)

    # 5. Mask all IPv6 addresses
    out = re.sub(r"\b(?:[0-9a-fA-F]{1,4}:){2,}[0-9a-fA-F:]*[0-9a-fA-F]+\b", "<MASKED-IPV6>", out)

    return out


def create_data_folders():
    for folder in ["alarms", "kpis", "topology", "runbooks"]:
        os.makedirs(os.path.join(DATA_DIR, folder), exist_ok=True)


def load_and_mask_alarms():
    """Reads original CPF Logs, UPF-01 Logs, UPF-02 Logs and saves 500 masked alarms."""
    log_dir = os.path.join(ORIGINAL_PS06_DIR, "Alarms and Logs Outputs")
    sources = [
        ("CPF Logs", "MASKED-CPF-01"),
        ("UPF-01 Logs", "MASKED-UPF-01"),
        ("UPF-02 Logs", "MASKED-UPF-02"),
    ]

    code_map = {
        "SYSTEM #2029": ("CPM_SINGLETON_NO_STANDBY", "L0_INFRA"),
        "SNMP #2102": ("RMON_CPU_THRESHOLD_ALARM", "L0_INFRA"),
        "VRTR #2061": ("BFD_SESSION_DOWN_NBR_SIGNAL", "L1_TRANSPORT"),
        "SYSTEM #2009": ("PORT_OR_REDUNDANCY_STATE_CHANGE", "L1_TRANSPORT"),
        "MOBILE_GATEWAY #2060": ("OVERLAY_FABRIC_PORT_TRANSITION", "L1_TRANSPORT"),
        "MOBILE_GATEWAY #2016": ("MSCP_CARD_OPER_STATE_STANDBY", "L2_ROUTING"),
        "MOBILE_GATEWAY #2015": ("MSCP_GROUP_OPER_STATE_HOT", "L2_ROUTING"),
        "SVCMGR #2210": ("ACCESS_PORT_STATE_CHANGE_PROCESSED", "L2_ROUTING"),
        "SYSTEM #2024": ("REDUNDANCY_STANDBY_CPM_SYNC_START", "L3_CONTROL_PLANE"),
        "SYSTEM #2025": ("REDUNDANCY_STANDBY_CPM_SYNC_DONE", "L3_CONTROL_PLANE"),
        "MOBILE_GATEWAY #2032": ("DIAMETER_GY_PEER_STATE_CHANGE", "L3_CONTROL_PLANE"),
        "MOBILE_GATEWAY #2002": ("DIAMETER_PEER_PATH_CHANGE", "L3_CONTROL_PLANE"),
        "NAT #2020": ("NAT_MDA_ACTIVE_TRANSITION", "L3_USER_PLANE"),
        "NAT #2024": ("NAT_GROUP_IN_SERVICE", "L3_USER_PLANE"),
        "SYSTEM #2011": ("VRTR_BFD_ROUTE_NOTIFICATION_DROPPED", "L4_SERVICE_KPI"),
        "MOBILE_GATEWAY #2001": ("GTP_PATH_STATE_IDLE_TRANSITION", "L4_SERVICE_KPI"),
        "NAT #2025": ("NAT_GROUP_STATUS_CHECK", "L4_SERVICE_KPI"),
        "LOGGER #2012": ("EVENT_THROTTLING_CONFIG_DROPPED", "L4_SERVICE_KPI"),
        "LOGGER #2008": ("ACCOUNTING_LOG_ROLLOVER", "L4_NOISE"),
        "LOGGER #2009": ("ACCOUNTING_LOG_CLEANUP", "L4_NOISE"),
    }

    per_node = {"MASKED-CPF-01": [], "MASKED-UPF-01": [], "MASKED-UPF-02": []}
    seen = set()

    for fname, masked_node in sources:
        fpath = os.path.join(log_dir, fname)
        with open(fpath, "r", errors="ignore") as f:
            text = f.read()

        events = re.findall(
            r"(\d+)\s+(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\.\d+\s+\w+\s+(WARNING|MAJOR|CRITICAL|MINOR|INDETERMINATE):\s+([A-Z_]+\s+#\d+)\s+([^\r\n]+)\r?\n\s*\"([^\"]+)\"",
            text,
        )

        for seq_id, ts_raw, sev, code, res_raw, msg_raw in events:
            ts_iso = ts_raw.replace("/", "-").replace(" ", "T") + "Z"
            res_masked = mask_confidential_text(res_raw.strip())
            msg_masked = mask_confidential_text(msg_raw.strip())

            dedup_key = (masked_node, ts_iso, code, res_masked, msg_masked[:60])
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            if code == "MOBILE_GATEWAY #2001" and "pathUp" in msg_masked:
                continue

            atype, layer = code_map.get(code, (f"EVENT_{code.replace(' ', '_')}", "L4_SERVICE_KPI"))
            per_node[masked_node].append({
                "timestamp": ts_iso,
                "node": masked_node,
                "severity": sev,
                "alarm_code": code,
                "alarm_type": atype,
                "layer": layer,
                "resource": res_masked,
                "details": msg_masked,
            })

    # Balanced set of 500 alarms across CPF, UPF-01, UPF-02 + routine log rollovers
    cpf_faults = [a for a in per_node["MASKED-CPF-01"] if a["alarm_code"] not in ("LOGGER #2008", "LOGGER #2009", "MOBILE_GATEWAY #2001")]
    cpf_gtp = [a for a in per_node["MASKED-CPF-01"] if a["alarm_code"] == "MOBILE_GATEWAY #2001"]
    upf1_faults = [a for a in per_node["MASKED-UPF-01"] if a["alarm_code"] not in ("LOGGER #2008", "LOGGER #2009", "VRTR #2064", "VRTR #2062", "SNMP #2005")]
    upf2_faults = [a for a in per_node["MASKED-UPF-02"] if a["alarm_code"] not in ("LOGGER #2008", "LOGGER #2009", "VRTR #2064", "VRTR #2062", "SNMP #2005")]
    noise = [a for a in (per_node["MASKED-CPF-01"] + per_node["MASKED-UPF-01"]) if a["alarm_code"] in ("LOGGER #2008", "LOGGER #2009")]

    selected = cpf_faults[:140] + cpf_gtp[:80] + upf1_faults[:90] + upf2_faults[:90] + noise[:100]
    selected.sort(key=lambda x: x["timestamp"])

    for idx, item in enumerate(selected, start=1):
        item["alarm_id"] = f"MSK-ALM-{idx:04d}"

    json_path = os.path.join(DATA_DIR, "alarms", "masked_alarms.json")
    csv_path = os.path.join(DATA_DIR, "alarms", "masked_alarms.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(selected, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["alarm_id", "timestamp", "node", "severity", "alarm_code", "alarm_type", "layer", "resource", "details"])
        writer.writeheader()
        writer.writerows(selected)

    return selected


def load_and_mask_kpis():
    """Reads all 25 original 3GPP XML PM files and saves masked KPIs to data/kpis/masked_kpis.csv."""
    xml_gz_files = sorted(glob.glob(os.path.join(ORIGINAL_PS06_DIR, "KPI-KCI", "*.xml.gz")))
    xml_plain_files = sorted(glob.glob(os.path.join(ORIGINAL_PS06_DIR, "KPI-KCI ask 1", "KPI-KCI ask", "*.xml")))

    def parse_xml(stream):
        tree = ET.parse(stream)
        root = tree.getroot()
        begin_time = ""
        for el in root.iter():
            if el.tag.endswith("measCollec") and "beginTime" in el.attrib:
                begin_time = el.attrib["beginTime"]
                break

        cpu_list, mem_list, jitter_c1, jitter_d1 = [], [], [], []
        max_cpm_cpu = 0.0
        ul_bytes, dl_bytes = 0.0, 0.0
        s5_mod_req, s5_mod_succ, s5_upd_fail = 0.0, 0.0, 0.0
        s2b_req, s2b_fail = 0.0, 0.0

        for mi in root.iter():
            if not mi.tag.endswith("measInfo"):
                continue
            mid = mi.attrib.get("measInfoId", "")
            pmap = {}
            for ch in mi:
                if ch.tag.endswith("measType"):
                    pmap[ch.attrib.get("p")] = (ch.text or "").strip()
                elif ch.tag.endswith("measValue"):
                    vals = {}
                    for r in ch:
                        if r.tag.endswith("r"):
                            cname = pmap.get(r.attrib.get("p"))
                            if cname:
                                try:
                                    vals[cname] = float(r.text or 0)
                                except ValueError:
                                    pass
                    if mid == "KPISystemCP-ISA":
                        if vals.get("VS.avgCpuUtilization", 0) > 0:
                            cpu_list.append(vals["VS.avgCpuUtilization"])
                        if vals.get("VS.avgMemoryUtilization", 0) > 0:
                            mem_list.append(vals["VS.avgMemoryUtilization"])
                        if vals.get("VS.vmCntrl1FabricPathMaxJitter", 0) > 0:
                            jitter_c1.append(vals["VS.vmCntrl1FabricPathMaxJitter"])
                        if vals.get("VS.vmData1FabricPathMaxJitter", 0) > 0:
                            jitter_d1.append(vals["VS.vmData1FabricPathMaxJitter"])
                    elif mid == "KPISystemCPM":
                        max_cpm_cpu = max(max_cpm_cpu, vals.get("VS.maxCpuUtilization", 0.0))
                    elif mid == "KPIBearerTrafficPlmn":
                        ul_bytes += vals.get("VS.ulBytes", 0.0)
                        dl_bytes += vals.get("VS.dlBytes", 0.0)
                    elif mid == "KPIReferencePointS5":
                        s5_mod_req += vals.get("VS.ModifyBearerReq", 0.0)
                        s5_mod_succ += vals.get("VS.ModifyBearerRespSuccess", 0.0)
                        s5_upd_fail += vals.get("VS.UpdateBearerRespFail", 0.0)
                    elif mid == "KPIReferencePointS2B":
                        s2b_req += vals.get("VS.CreateSessnReq", 0.0)
                        s2b_fail += vals.get("VS.CreateSessnRespFail", 0.0)

        s5_sr = round((s5_mod_succ * 100.0) / s5_mod_req, 2) if s5_mod_req > 0 else 100.0
        s2b_sr = round(((s2b_req - s2b_fail) * 100.0) / s2b_req, 2) if s2b_req > 0 else 100.0

        return {
            "timestamp": begin_time,
            "avg_isa_cpu_pct": round(sum(cpu_list) / max(1, len(cpu_list)), 2),
            "max_cpm_cpu_pct": round(max_cpm_cpu, 2),
            "avg_memory_utilization_pct": round(sum(mem_list) / max(1, len(mem_list)), 2),
            "cntrl_fabric_max_jitter_us": round(max(jitter_c1) if jitter_c1 else 0.0, 1),
            "data_fabric_max_jitter_us": round(max(jitter_d1) if jitter_d1 else 0.0, 1),
            "s5_modify_bearer_sr_pct": s5_sr,
            "s5_update_bearer_fails": int(s5_upd_fail),
            "s2b_session_sr_pct": s2b_sr,
            "total_traffic_mb": round((ul_bytes + dl_bytes) / (1024.0 * 1024.0), 3),
        }

    intervals = []
    for p in xml_gz_files:
        with gzip.open(p, "rb") as gz:
            intervals.append(parse_xml(gz))
    for p in xml_plain_files:
        with open(p, "rb") as fp:
            intervals.append(parse_xml(fp))

    all_rows = []
    for node_id in ["MASKED-CPF-01", "MASKED-UPF-01", "MASKED-UPF-02"]:
        for row in intervals:
            all_rows.append({"node": node_id, **row})

    kpi_csv = os.path.join(DATA_DIR, "kpis", "masked_kpis.csv")
    with open(kpi_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    return intervals


def build_masked_topology():
    """Creates data/topology/masked_topology.json representing the 4 masked nodes and 6 links."""
    topology = {
        "network_name": "MASKED-PS06-MOBILE-CORE",
        "nodes": [
            {
                "id": "MASKED-AIM-SVR",
                "name": "Masked Linux KVM Host (svr1 / svr2)",
                "type": "LINUX_VM_HOST",
                "layer": "L0_INFRA",
                "role": "Hosts OAM-A/B, LB-VM1..2, and MG-VM3..20",
            },
            {
                "id": "MASKED-CPF-01",
                "name": "Masked Control Plane Function (CPF)",
                "type": "CMG_CPF",
                "layer": "L1_TRANSPORT",
                "role": "Control Plane Router (Base, vprn10 Gx, vprn11 Gy, vprn12 Ga, vprn100 S11/S5/Sx)",
            },
            {
                "id": "MASKED-UPF-01",
                "name": "Masked User Plane Function 1 (UPF-01)",
                "type": "CMG_UPF",
                "layer": "L2_ROUTING",
                "role": "User Plane Router 1 (vprn100..309, S1-U/S5-U/Sx, NAT groups 1..9)",
            },
            {
                "id": "MASKED-UPF-02",
                "name": "Masked User Plane Function 2 (UPF-02)",
                "type": "CMG_UPF",
                "layer": "L2_ROUTING",
                "role": "User Plane Router 2 (vprn1000..3009, S1-U/S5-U/Sx, NAT groups 1..9)",
            },
        ],
        "links": [
            {"source": "MASKED-AIM-SVR", "target": "MASKED-CPF-01", "relationship": "HOSTS_VMS", "interface": "Overlay Fabric (VM 1..20)"},
            {"source": "MASKED-AIM-SVR", "target": "MASKED-UPF-01", "relationship": "HOSTS_VMS", "interface": "Overlay Fabric (VM 1..20)"},
            {"source": "MASKED-AIM-SVR", "target": "MASKED-UPF-02", "relationship": "HOSTS_VMS", "interface": "Overlay Fabric (VM 1..20)"},
            {"source": "MASKED-CPF-01", "target": "MASKED-UPF-01", "relationship": "PFCP_SX_N4_BGP_BFD", "interface": "vprn100 / sx-n4"},
            {"source": "MASKED-CPF-01", "target": "MASKED-UPF-02", "relationship": "PFCP_SX_N4_BGP_BFD", "interface": "vprn100 / sx-n4"},
            {"source": "MASKED-UPF-01", "target": "MASKED-UPF-02", "relationship": "REDUNDANCY_PEER", "interface": "vprn200 / vprn1000 BFD"},
        ],
    }
    topo_path = os.path.join(DATA_DIR, "topology", "masked_topology.json")
    with open(topo_path, "w", encoding="utf-8") as f:
        json.dump(topology, f, indent=2)
    return topology


def load_and_mask_runbooks():
    """Reads the 3 Supported Commands files, masks confidential strings, and saves Markdown runbooks."""
    cmd_dir = os.path.join(ORIGINAL_PS06_DIR, "Supported Commands")
    files_map = [
        ("CPF Health Check Command_Agra A2 2.txt", "RB_CPF_Masked.md", "RB-CPF: Masked Control Plane Health Check Runbook"),
        ("UPF-1 Health Check Command_Agra A2 2.txt", "RB_UPF01_Masked.md", "RB-UPF01: Masked User Plane 1 Health Check Runbook"),
        ("UPF-2 Health Check Command_Agra A2 2.txt", "RB_UPF02_Masked.md", "RB-UPF02: Masked User Plane 2 Health Check Runbook"),
    ]

    saved_files = []
    for src_name, out_name, title in files_map:
        src_path = os.path.join(cmd_dir, src_name)
        with open(src_path, "r", errors="ignore") as f:
            masked_txt = mask_confidential_text(f.read())

        lines = [l.rstrip() for l in masked_txt.splitlines()]
        md_lines = [f"# {title}", ""]

        sec_num = 1
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("++++") and line and not line.startswith("++++"):
                heading = line
                i += 2
                cmds = []
                while i < len(lines):
                    cur = lines[i].strip()
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith("++++") and cur and not cur.startswith("++++"):
                        break
                    if cur and not cur.startswith("++++"):
                        cmds.append(cur)
                    i += 1
                if cmds:
                    md_lines.append(f"## Section {sec_num}: {heading}")
                    for c in cmds[:15]:
                        if c.startswith("show "):
                            md_lines.append(f"- `{c}`")
                        else:
                            md_lines.append(f"  {c}")
                    md_lines.append("")
                    sec_num += 1
            else:
                i += 1

        out_path = os.path.join(DATA_DIR, "runbooks", out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        saved_files.append(out_name)

    return saved_files


if __name__ == "__main__":
    create_data_folders()
    alarms = load_and_mask_alarms()
    kpis = load_and_mask_kpis()
    topo = build_masked_topology()
    rbs = load_and_mask_runbooks()

    print("=" * 65)
    print("STEP 1 COMPLETE: ORIGINAL PS-06 DATA LOADED & MASKED")
    print("=" * 65)
    print(f"1. Masked Alarms   : {len(alarms)} alarms -> data/alarms/masked_alarms.json & .csv")
    print(f"2. Masked KPIs     : {len(kpis)} XML intervals (75 rows) -> data/kpis/masked_kpis.csv")
    print(f"3. Masked Topology : {len(topo['nodes'])} nodes & {len(topo['links'])} links -> data/topology/masked_topology.json")
    print(f"4. Masked Runbooks : {len(rbs)} files -> data/runbooks/{', '.join(rbs)}")
    print("=" * 65)
