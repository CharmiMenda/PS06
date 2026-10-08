"""
PS-06 UI — Clean 5-Step Request Order
-------------------------------------
1. Linux VM (saich@Varun) -> Run Commands
2. KPI Going High or Low -> Trigger an Alarm (with 'Trigger Fault' Demo Button)
3. Correlate Alarms & Main Root Cause
4. Agentic AI RAG & Resolve Issue (with 'Resolve Issues with Agentic AI' Demo Button)
5. Mail Alarms / Logs / Summary in DB
"""

import importlib
import json
import os
import sqlite3
import pandas as pd
import streamlit as st

import step1_linux_vm
import step2_kpi_and_trigger
import step3_correlate_root_cause
import step4_rag
import step5_summary_db_notify

importlib.reload(step1_linux_vm)
importlib.reload(step2_kpi_and_trigger)
importlib.reload(step3_correlate_root_cause)
importlib.reload(step4_rag)
importlib.reload(step5_summary_db_notify)

from step1_linux_vm import run_on_linux_vm, get_live_cloud_cluster_from_vm, set_vm_cluster_state
from step2_kpi_and_trigger import observe_kpis_and_trigger_alarms
from step4_rag import run_agentic_rag_resolver
from step5_summary_db_notify import run_step5_triage_and_save, send_real_or_mock_email

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "triage_reports.db")
NOTIFY_PATH = os.path.join(BASE_DIR, "data", "notifications_sent.json")

st.set_page_config(
    page_title="PS-06 | Network Health-Check & Alarm Triage Agent",
    page_icon="🖥️",
    layout="wide",
)

live_vm_state = get_live_cloud_cluster_from_vm()
is_resolved = live_vm_state.get("cluster_health") == "RESOLVED"

if not os.path.exists(DB_PATH):
    run_step5_triage_and_save(execute_fix_on_vm=is_resolved)

with open(os.path.join(BASE_DIR, "data", "kpis", "kpi_anomalies.json"), "r", encoding="utf-8") as f:
    kpi_data = json.load(f)

with open(os.path.join(BASE_DIR, "data", "alarms", "correlated_incidents.json"), "r", encoding="utf-8") as f:
    corr_data = json.load(f)

df_kpis = pd.read_csv(os.path.join(BASE_DIR, "data", "kpis", "masked_kpis.csv"))
incidents = corr_data["incidents"]
live_vm = kpi_data.get("live_vm_telemetry", {})

st.title("🖥️ PS-06: Network Health-Check & Alarm Triage Agent")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("1. Linux VM (saich@Varun)", "🟢 RESOLVED" if is_resolved else "🔴 FAULT ACTIVE")
m2.metric("2. Live VM Faults", "0 Active (4 Resolved)" if is_resolved else "4 Active Faults")
m3.metric("3. Correlated Incidents", f"{len(incidents)} Incidents")
m4.metric("4. Agentic AI RAG", "RESOLVED" if is_resolved else "Ready to Resolve")
m5.metric("5. Drafted Mail & DB", f"{len(incidents)} Drafted in Mail & DB")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1️⃣ Linux VM (saich@Varun) → Run Commands",
    "2️⃣ KPI High/Low → Trigger an Alarm",
    "3️⃣ Correlate Alarms & Main Root Cause",
    "4️⃣ Agentic AI RAG & Resolve Issue",
    "5️⃣ Mail Alarms / Logs / Summary in DB",
])

# ==============================================================================
# TAB 1: LINUX VM (saich@Varun) -> RUN COMMANDS
# ==============================================================================
with tab1:
    c_left, c_right = st.columns([1, 1.4])
    with c_left:
        st.subheader("🖥️ 1A. Live Linux VM (`saich@Varun`) Status")
        st.json({
            "linux_vm_host": live_vm.get("vm_host", "saich@Varun"),
            "vm_operational_state": "RESOLVED (All 4 Faults Fixed via CLI)" if is_resolved else "FAULT (4 Telecom Faults Active)",
            "linux_kernel": live_vm.get("kernel", "Linux WSL2"),
            "cpu_cores": live_vm.get("cpu_cores", 12),
            "live_ram_usage": f"{live_vm.get('mem_used_mb', 535)} MB / {live_vm.get('mem_total_mb', 7598)} MB ({live_vm.get('mem_used_pct', 7.0)}%)",
            "bfd_vprn201_session": "Up (3) [RESOLVED]" if is_resolved else "Down (1) - nbrSignal [VRTR #2061]",
            "mg_vm6_mscp_state": "up (active) [RESOLVED]" if is_resolved else "standby [MOBILE_GATEWAY #2016]",
            "mg_vm3_cpu_pct": "7.0% (Normal) [RESOLVED]" if is_resolved else "15.0% (High CPU Spike) [SNMP #2102]",
            "s5_gtp_peer_state": "pathUp [RESOLVED]" if is_resolved else "pathIdle (6 Bearer Fails) [MOBILE_GATEWAY #2001]",
        })

    with c_right:
        st.subheader("▶️ 1B. Run Commands on `saich@Varun`")
        default_cmds_str = (
            "cmg status\n"
            "show vm\n"
            "show router Base bfd session\n"
            "show mobile-gateway pdn ref-point-peer"
        )
        cmds_input = st.text_area("Commands:", value=default_cmds_str, height=120)

        if st.button("▶️ Run Commands on `saich@Varun`", type="primary", width="stretch"):
            cmd_list = [c.strip() for c in cmds_input.splitlines() if c.strip()]
            vm_out = run_on_linux_vm(cmd_list)
            for r in vm_out["results"]:
                st.code(r["output"], language="text")
        else:
            st.code(live_vm.get("raw_vm_output", ""), language="text")

# ==============================================================================
# TAB 2: KPI GOING HIGH OR LOW -> TRIGGER AN ALARM
# ==============================================================================
with tab2:
    if st.button("💥 Trigger Fault on `saich@Varun` (Demo Fault Injection)", type="primary"):
        set_vm_cluster_state("FAULT")
        observe_kpis_and_trigger_alarms()
        run_step5_triage_and_save(execute_fix_on_vm=False)
        st.rerun()

    all_flucs = kpi_data["fluctuations"]
    live_vm_flucs = [f for f in all_flucs if "LIVE" in str(f.get("source", ""))]
    xml_flucs = [f for f in all_flucs if "LIVE" not in str(f.get("source", ""))]

    st.subheader(
        f"{'🟢' if is_resolved else '🔴'} 2A. Live Parameters Fluctuating on Your Linux VM (`saich@Varun`) → Triggered Alarms "
        f"({'4 Resolved by Agentic AI CLI' if is_resolved else '4 Active Live Faults'})"
    )
    st.dataframe(pd.DataFrame(live_vm_flucs), width="stretch", hide_index=True)

    st.subheader(f"⚡ 2B. XML KPI Parameters Going HIGH or LOW → Triggered Alarms ({len(xml_flucs)} Triggers)")
    st.dataframe(pd.DataFrame(xml_flucs), width="stretch", hide_index=True, height=250)

    st.subheader("📊 2C. KPI Fluctuation Graph")
    kc1, kc2 = st.columns([1, 2.2])
    with kc1:
        node_choice = st.selectbox("Select Node:", kpi_data["nodes_checked"])
        metric_cols = [c for c in df_kpis.columns if c not in ("node", "timestamp")]
        metric_choice = st.selectbox("Select KPI Parameter:", metric_cols)
        b_info = kpi_data["baselines"][node_choice][metric_choice]
        st.metric("Normal Baseline", b_info["baseline_median"])
        st.metric("Peak High Value", b_info["max"])
        st.metric("Lowest Value", b_info["min"])
    with kc2:
        node_sub = df_kpis[df_kpis["node"] == node_choice][["timestamp", metric_choice]].set_index("timestamp")
        st.line_chart(node_sub)

# ==============================================================================
# TAB 3: CORRELATE ALARMS & MAIN ROOT CAUSE
# ==============================================================================
with tab3:
    inc_map = {f"{i['incident_id']} — {i['title']} ({i['total_alarms']} alarms)": i for i in incidents}
    selected_inc_label = st.selectbox("Select Incident:", list(inc_map.keys()))
    inc = inc_map[selected_inc_label]

    st.success(
        f"🎯 **#1 Main Root Cause**: `{inc['probable_root_alarm_code']}` (`{inc['probable_root_alarm_type']}`) "
        f"on **`{inc['probable_root_node']}`** | **Layer**: `{inc['probable_root_layer']}` | "
        f"**Confidence**: `{int(inc['confidence_score']*100)}%`"
    )
    st.info(inc["reasoning_summary"])

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.subheader("🏆 Root Cause Ranking (Out of 100)")
        rank_df = pd.DataFrame(inc["root_ranking"])[
            ["node", "alarm_code", "alarm_type", "layer", "severity", "score"]
        ]
        st.dataframe(rank_df, width="stretch", hide_index=True)

    with col_r2:
        st.subheader(f"📋 Correlated Symptom Alarms ({inc['total_alarms']} Alarms)")
        sym_df = pd.DataFrame(inc["symptom_alarms"])[
            ["alarm_id", "timestamp", "node", "severity", "alarm_code", "alarm_type", "resource"]
        ]
        st.dataframe(sym_df, width="stretch", hide_index=True, height=260)

# ==============================================================================
# TAB 4: AGENTIC AI OVER RAG — RESOLVE ISSUE & AUTO-DRAFT MAIL
# ==============================================================================
with tab4:
    if st.button("🤖 Resolve Issues with Agentic AI (Execute CLI Fixes from RAG on `saich@Varun` & Draft Mail)", type="primary"):
        set_vm_cluster_state("RESOLVED")
        observe_kpis_and_trigger_alarms()
        run_step5_triage_and_save(execute_fix_on_vm=True)
        st.rerun()

    agent_res = run_agentic_rag_resolver(inc, execute_fix_on_vm=is_resolved)
    rag_res = agent_res["rag"]

    if is_resolved:
        st.success("✅ **All 4 Telecom Issues Resolved by Agentic AI via CLI Commands on `saich@Varun` & Drafted in Mail (Step 4C & Step 5)!**")
    else:
        st.warning("⚠️ **4 Telecom Faults Active on `saich@Varun`!** Click **'🤖 Resolve Issues with Agentic AI'** above to execute the RAG CLI fixes and draft the resolved mail.")

    st.subheader(f"📌 4A. RAG Reference for `{inc['probable_root_alarm_code']}` on `{inc['probable_root_node']}`")
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown(f"**Runbook Citation:** `{rag_res['citation']}`")
        st.markdown(f"**CLI Remediation Command:** `{rag_res['cli_remediation_cmd']}`")
        if rag_res.get("past_incident"):
            pi = rag_res["past_incident"]
            st.markdown(f"**Past Incident (`{pi['case_id']}`):** {pi['problem']}")
            st.markdown(f"**RAG Resolution Reference:** {pi['resolution']}")
    with rc2:
        st.info(rag_res["section_content"])

    st.subheader("🤖 4B. Agentic AI CLI Remediation & Verification Output on `saich@Varun`")
    st.code(f"{agent_res['resolution_output']}\n\n{agent_res['pre_check_output']}", language="text")

    st.subheader("✉️ 4C. Auto-Drafted Mail of Issues Resolved by Agentic AI")
    st.text_input("Drafted Subject:", value=agent_res["draft_mail_subject"], disabled=True)
    st.code(agent_res["draft_mail_body"], language="text")

# ==============================================================================
# TAB 5: MAIL ALARMS / LOGS / SUMMARY IN DB
# ==============================================================================
with tab5:
    conn = sqlite3.connect(DB_PATH)
    df_db = pd.read_sql_query(
        "SELECT ticket_id, incident_id, severity, root_node, root_alarm_code, root_alarm_type, confidence_pct, grouped_alarms_count, runbook_citation, engineer_status FROM triage_summaries",
        conn,
    )
    conn.close()

    st.subheader("🗄️ 5A. Triage & Agentic AI Resolution Records in SQLite DB (`data/triage_reports.db`)")
    st.dataframe(df_db, width="stretch", hide_index=True)

    col_m1, col_m2 = st.columns([1.2, 1])
    with col_m1:
        st.subheader(f"📧 5B. Drafted Mail for `{inc['incident_id']}` (Issues Resolved by Agentic AI)")
        mail_content_type = st.radio(
            "Select Mail Content (`Requirement.txt`):",
            [
                "1. Issues Resolved by Agentic AI & Summary in DB",
                "2. Alarms (Correlated Fault Alarms)",
                "3. Logs (Live Linux VM `saich@Varun` CLI Logs)",
            ],
            horizontal=True,
        )

        to_email = st.text_input("Recipient Email:", value="saich@telecom-noc.local")

        alarms_text = "\n".join(
            f"- [{a['timestamp']}] {a['node']} | {a['severity']} | {a['alarm_code']} ({a['alarm_type']}) on {a['resource']}"
            for a in inc["symptom_alarms"][:15]
        )
        logs_text = f"{agent_res['resolution_output']}\n\n{agent_res['pre_check_output']}"
        summary_db_text = agent_res["draft_mail_body"]

        if mail_content_type.startswith("1."):
            final_body = summary_db_text
            subj = agent_res["draft_mail_subject"]
        elif mail_content_type.startswith("2."):
            final_body = f"CORRELATED ALARMS FOR {inc['incident_id']}:\n{alarms_text}"
            subj = f"[{inc['severity']}] PS-06 Alarms — {inc['incident_id']}"
        else:
            final_body = f"LIVE LINUX VM (saich@Varun) CLI LOGS:\n{logs_text}"
            subj = f"[{inc['severity']}] PS-06 Linux VM Logs — {inc['incident_id']}"

        st.text_input("Mail Subject:", value=subj, disabled=True)
        edited_body = st.text_area("Drafted Mail Body (Ready to Send):", value=final_body, height=340)

        if st.button("📩 Send / Save Drafted Mail", type="primary", width="stretch"):
            sent = send_real_or_mock_email(to_email, subj, edited_body)
            st.success(f"Drafted Mail `{sent['notification_id']}` saved/sent to `{to_email}`!")

    with col_m2:
        st.subheader("📬 5C. Sent / Drafted Mail Outbox (`data/notifications_sent.json`)")
        if os.path.exists(NOTIFY_PATH):
            with open(NOTIFY_PATH, "r", encoding="utf-8") as f:
                notifs = json.load(f)
            st.dataframe(
                pd.DataFrame(notifs)[["notification_id", "sent_at", "to", "subject"]],
                width="stretch",
                hide_index=True,
                height=180,
            )
            if notifs:
                st.caption(f"Latest Drafted Mail Body in Outbox (`{notifs[0]['notification_id']}`):")
                st.code(notifs[0]["body"], language="text")
