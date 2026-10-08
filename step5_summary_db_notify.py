"""
STEP 5: Triage Summary, Draft Ticket, Save to Database (SQLite), and Mail/Notify
--------------------------------------------------------------------------------
Matches Requirement.txt ("Mail me the alarms or Logs or summary sent in DB") & PS-06 PDF:
1. Combines Step 1 (Linux VM), Step 2 (KPIs), Step 3 (Root Cause), and Step 4 (RAG).
2. Builds a clear Triage & Agentic AI Resolution Summary & Draft Mail for each Incident.
3. Saves all Incidents, Summaries, and Tickets into a SQLite Database (`data/triage_reports.db`).
4. Sends/Logs the Drafted Mail (`data/notifications_sent.json` + optional SMTP Email).
"""

import json
import os
import smtplib
import sqlite3
from datetime import datetime
from email.message import EmailMessage

from step4_rag import run_agentic_rag_resolver

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INCIDENTS_PATH = os.path.join(BASE_DIR, "data", "alarms", "correlated_incidents.json")
DB_PATH = os.path.join(BASE_DIR, "data", "triage_reports.db")
NOTIFY_JSON_PATH = os.path.join(BASE_DIR, "data", "notifications_sent.json")


def init_sqlite_db():
    """Creates the SQLite database table for storing triage summaries and draft tickets."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS triage_summaries (
            ticket_id TEXT PRIMARY KEY,
            incident_id TEXT,
            created_at TEXT,
            severity TEXT,
            root_node TEXT,
            root_alarm_code TEXT,
            root_alarm_type TEXT,
            confidence_pct INTEGER,
            grouped_alarms_count INTEGER,
            runbook_citation TEXT,
            recommended_commands TEXT,
            vm_verification_output TEXT,
            summary_text TEXT,
            engineer_status TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def run_step5_triage_and_save(execute_fix_on_vm: bool = True):
    init_sqlite_db()
    with open(INCIDENTS_PATH, "r", encoding="utf-8") as f:
        corr_data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    reports = []
    notifications = []
    now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    for idx, inc in enumerate(corr_data["incidents"], start=1):
        ticket_id = f"TCK-2026-{idx:03d}"
        agent_res = run_agentic_rag_resolver(inc, execute_fix_on_vm=execute_fix_on_vm)
        rag = agent_res["rag"]
        vm_out_str = f"{agent_res['resolution_output']}\n\n{agent_res['pre_check_output']}"
        summary_text = agent_res["draft_mail_body"]

        # Save into SQLite DB
        cur.execute(
            """
            INSERT OR REPLACE INTO triage_summaries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                inc["incident_id"],
                now_str,
                inc["severity"],
                inc["probable_root_node"],
                inc["probable_root_alarm_code"],
                inc["probable_root_alarm_type"],
                int(inc["confidence_score"] * 100),
                inc["total_alarms"],
                rag["citation"],
                json.dumps([rag["cli_remediation_cmd"]] + rag["recommended_commands"]),
                vm_out_str,
                summary_text,
                agent_res["resolution_status"],
            ),
        )

        report_obj = {
            "ticket_id": ticket_id,
            "incident_id": inc["incident_id"],
            "created_at": now_str,
            "severity": inc["severity"],
            "root_node": inc["probable_root_node"],
            "root_alarm_code": inc["probable_root_alarm_code"],
            "root_alarm_type": inc["probable_root_alarm_type"],
            "confidence_pct": int(inc["confidence_score"] * 100),
            "grouped_alarms_count": inc["total_alarms"],
            "runbook_citation": rag["citation"],
            "recommended_commands": rag["recommended_commands"],
            "vm_verification_output": vm_out_str,
            "summary_text": summary_text,
            "engineer_status": agent_res["resolution_status"],
            "agent_steps": agent_res["agent_steps"],
            "draft_mail_subject": agent_res["draft_mail_subject"],
            "draft_mail_body": agent_res["draft_mail_body"],
        }
        reports.append(report_obj)

        notifications.append({
            "notification_id": f"MAIL-{idx:03d}",
            "sent_at": now_str,
            "channel": "AGENTIC_AI_DRAFTED_MAIL_AND_DB",
            "to": "saich@telecom-noc.local",
            "subject": agent_res["draft_mail_subject"],
            "body": agent_res["draft_mail_body"],
            "db_status": "SAVED_IN_SQLITE_DB (data/triage_reports.db)",
        })

    conn.commit()
    conn.close()

    with open(NOTIFY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(notifications, f, indent=2)

    return {
        "db_path": DB_PATH,
        "notify_path": NOTIFY_JSON_PATH,
        "reports": reports,
        "notifications": notifications,
    }


def send_real_or_mock_email(to_email: str, subject: str, body: str, smtp_user: str = "", smtp_pass: str = "") -> dict:
    """
    Sends a real email via Gmail SMTP if smtp_user and smtp_pass are provided,
    and always logs the email in data/notifications_sent.json so it works offline too.
    """
    now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = {
        "notification_id": f"MAIL-CUSTOM-{now_str[-6:]}",
        "sent_at": now_str,
        "to": to_email,
        "subject": subject,
        "body": body,
        "delivery_mode": "LOGGED_TO_OUTBOX_AND_DB",
    }

    if smtp_user and smtp_pass:
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = to_email
            msg.set_content(body)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            entry["delivery_mode"] = "SENT_VIA_GMAIL_SMTP"
        except Exception as e:
            entry["delivery_mode"] = f"SMTP_FALLBACK_TO_OUTBOX ({e})"

    existing = []
    if os.path.exists(NOTIFY_JSON_PATH):
        with open(NOTIFY_JSON_PATH, "r", encoding="utf-8") as f:
            existing = json.load(f)
    existing.insert(0, entry)
    with open(NOTIFY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    return entry


if __name__ == "__main__":
    res = run_step5_triage_and_save(execute_fix_on_vm=True)
    print("=" * 80)
    print("STEP 5 COMPLETE: TRIAGE SUMMARY, DRAFT TICKETS, SQLITE DB & MAIL NOTIFICATIONS")
    print("=" * 80)
    print(f"SQLite Database Saved : {res['db_path']} ({len(res['reports'])} tickets stored)")
    print(f"Mail Outbox Saved     : {res['notify_path']} ({len(res['notifications'])} notifications sent)")
    print("-" * 80)
    for r in res["reports"]:
        print(r["summary_text"])
        print("-" * 80)
