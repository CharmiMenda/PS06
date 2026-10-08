# PS-06: Network Health-Check & Alarm Triage Agent

An end-to-end **Telecom Cloud Cluster $\rightarrow$ Linux VM $\rightarrow$ KPI Fluctuation $\rightarrow$ Root Cause Correlation $\rightarrow$ Runbook RAG & Notification** system built on **100% Masked Data** for secure, reproducible telecom operations analysis.

---

## 5-Step Architecture (Aligned with `PS06/Requirement.txt`)

| Step | File | What It Does |
| :--- | :--- | :--- |
| **Step 1** | [`step1_linux_vm.py`](step1_linux_vm.py) | Connects to **Level 1 (Telecom Cloud Cluster)** and **Level 2 (Linux VM)** to execute initial health checks and environment validation. |
| **Step 2** | [`step2_kpi_and_trigger.py`](step2_kpi_and_trigger.py) | Observes **live parameters** from the monitored VM (`mg_vm3_cpu_pct`, `pci_temp_c`, `bfd_session_down`) plus **25 3GPP XML KPI intervals** to detect abnormal deviations and trigger triage logic. |
| **Step 3** | [`step3_correlate_root_cause.py`](step3_correlate_root_cause.py) | Filters out routine file-backup logs, correlates real fault alarms into **3 Incident Clusters**, and ranks likely root causes with confidence scoring. |
| **Step 4** | [`step4_rag.py`](step4_rag.py) | Performs **Zero-Hallucination RAG** over the 3 Masked Runbooks (`RB_CPF_Masked.md`, `RB_UPF01_Masked.md`, `RB_UPF02_Masked.md`) and past incidents to produce evidence-based recommendations. |
| **Step 5** | [`step5_summary_db_notify.py`](step5_summary_db_notify.py) | Runs read-only verification checks on the monitored Linux VM, generates **Draft Tickets (`TCK-2026-001`..`003`)**, saves reports in the output workspace, and prepares notification-ready summaries. |

---

## Quick Start

```bash
# 1. Run the automated PS-06 Requirement & Evaluation Verification Suite
python verify_ps06_requirements.py

# 2. Launch the 5-Tab Interactive Streamlit UI
python -m streamlit run app.py --server.port 8501
```
