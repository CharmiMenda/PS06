# PS-06: Network Health-Check & Alarm Triage Agent

An end-to-end **Telecom Cloud Cluster $\rightarrow$ Linux VM $\rightarrow$ KPI Fluctuation $\rightarrow$ Root Cause Correlation $\rightarrow$ Runbook RAG & Notification** system built on **100% Masked Official PS-06 Telecom Data** and connected live to an **Ubuntu-24.04 (`saich@Varun`) Linux VM**.

---

## 5-Step Architecture (Aligned with `PS06/Requirement.txt`)

| Step | File | What It Does |
| :--- | :--- | :--- |
| **Step 1** | [`step1_linux_vm.py`](step1_linux_vm.py) | Connects to **Level 1 (Telecom Cloud Cluster `CMG-SVR-1` & `CMG-SVR-2`)** and **Level 2 (`Ubuntu-24.04` / `saich@Varun` Linux VM)** to execute read-only health-check commands (`cmg cluster-info`, `cmg status`, `cmg health-status`, `show vm`, `show router Base bfd session`) with a strict **Read-Only Safety Guardrail**. |
| **Step 2** | [`step2_kpi_and_trigger.py`](step2_kpi_and_trigger.py) | Observes **live parameters** from `saich@Varun` (`mg_vm3_cpu_pct`, `pci_temp_c`, `bfd_session_down`) + **25 3GPP XML KPI intervals** (`data/kpis/masked_kpis.csv`), compares against normal baselines, and **triggers alarms** when a parameter fluctuates. |
| **Step 3** | [`step3_correlate_root_cause.py`](step3_correlate_root_cause.py) | Filters out `100` routine file-backup logs (`LOGGER #2008/#2009`), correlates `400` real fault alarms into **3 Incidents (`INC-2026-001`..`003`)** (**99.4% alert noise reduction**), and scores the **#1 Main Root Cause** out of 100 marks (`Layer + Timing + Severity + Topology`). |
| **Step 4** | [`step4_rag.py`](step4_rag.py) | Performs **Zero-Hallucination RAG** over the 3 Masked Runbooks (`RB_CPF_Masked.md`, `RB_UPF01_Masked.md`, `RB_UPF02_Masked.md`) and past incidents, returning exact section citations or `"not found"` if an unknown alarm is queried. |
| **Step 5** | [`step5_summary_db_notify.py`](step5_summary_db_notify.py) | Runs read-only verification checks on `saich@Varun`, generates **Draft Tickets (`TCK-2026-001`..`003`)**, saves reports in **SQLite (`data/triage_reports.db`)**, and dispatches **Email Notifications (`data/notifications_sent.json`)**. |

---

## Quick Start

```bash
# 1. Run the automated PS-06 Requirement & Evaluation Verification Suite
python verify_ps06_requirements.py

# 2. Launch the 5-Tab Interactive Streamlit UI
python -m streamlit run app.py --server.port 8501
```
