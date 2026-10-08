"""
STEP 4: RAG Knowledge Retrieval (Search Masked Runbooks & Cite Exact Sections)
------------------------------------------------------------------------------
Reads:
  - data/runbooks/RB_CPF_Masked.md
  - data/runbooks/RB_UPF01_Masked.md
  - data/runbooks/RB_UPF02_Masked.md
Provides:
  - retrieve_runbook_guidance(alarm_code, alarm_type, node)
  - Returns exact section citations and CLI commands, or "not found" if unknown.
"""

import glob
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUNBOOKS_DIR = os.path.join(BASE_DIR, "data", "runbooks")

# Mapping of PS-06 Alarm Codes to Runbook files, sections, and past incidents
ALARM_KNOWLEDGE_MAP = {
    "VRTR #2061": {
        "alarm_type": "BFD_SESSION_DOWN_NBR_SIGNAL",
        "runbook_file": "RB_UPF01_Masked.md",
        "section_keyword": "To check BFD status",
        "past_incident": {
            "case_id": "PAST-INC-101",
            "problem": "VRTR #2061 BFD session went down due to neighbor signal (nbrSignal) on UPF VPRN interface, triggering MSCP standby and NAT group state changes.",
            "resolution": "Verified BFD session state and BGP peer summary on VPRN 100/200 and restored transport link stability.",
        },
    },
    "VRTR #2062": {
        "alarm_type": "BFD_SESSION_UP_TRANSITION",
        "runbook_file": "RB_UPF01_Masked.md",
        "section_keyword": "To check BFD status",
        "past_incident": {
            "case_id": "PAST-INC-101",
            "problem": "BFD session flapped (VRTR #2061 / #2062) on VPRN router.",
            "resolution": "Checked BFD flap counters and interface ARP/status.",
        },
    },
    "MOBILE_GATEWAY #2016": {
        "alarm_type": "MSCP_CARD_OPER_STATE_STANDBY",
        "runbook_file": "RB_CPF_Masked.md",
        "section_keyword": "Check VM/card and MDA status",
        "past_incident": {
            "case_id": "PAST-INC-102",
            "problem": "MOBILE_GATEWAY #2016 / #2015 triggered when MSCP Group/Card transitioned to standby/cold state.",
            "resolution": "Checked VM/card status ('show vm', 'show mda', 'show mobile-gateway system') and virtual fabric health.",
        },
    },
    "MOBILE_GATEWAY #2015": {
        "alarm_type": "MSCP_GROUP_OPER_STATE_HOT",
        "runbook_file": "RB_CPF_Masked.md",
        "section_keyword": "Check VM/card and MDA status",
        "past_incident": {
            "case_id": "PAST-INC-102",
            "problem": "MSCP redundancy group state transition on CMG node.",
            "resolution": "Verified active/standby VM pair and virtual fabric links.",
        },
    },
    "MOBILE_GATEWAY #2001": {
        "alarm_type": "GTP_PATH_STATE_IDLE_TRANSITION",
        "runbook_file": "RB_CPF_Masked.md",
        "section_keyword": "Check peer status for all the interfaces",
        "past_incident": {
            "case_id": "PAST-INC-103",
            "problem": "Surge of WARNING MOBILE_GATEWAY #2001 events as GTP peers on s5/s2b/gn transitioned to pathIdle.",
            "resolution": "Inspected ref-point peers ('show mobile-gateway pdn ref-point-peer s5/s11/gn') and failure-codes.",
        },
    },
    "MOBILE_GATEWAY #2032": {
        "alarm_type": "DIAMETER_GY_PEER_STATE_CHANGE",
        "runbook_file": "RB_CPF_Masked.md",
        "section_keyword": "Check peer status for all the interfaces",
        "past_incident": {
            "case_id": "PAST-INC-104",
            "problem": "Diameter Gy/Gx/S6b peer state changed on CPF control plane.",
            "resolution": "Checked 'show mobile-gateway pdn ref-point-peer gx/gy' and VPRN 10/11 interface status.",
        },
    },
    "SYSTEM #2009": {
        "alarm_type": "PORT_OR_REDUNDANCY_STATE_CHANGE",
        "runbook_file": "RB_CPF_Masked.md",
        "section_keyword": "To check interface status",
        "past_incident": {
            "case_id": "PAST-INC-105",
            "problem": "SYSTEM #2009 reported physical port or redundancy group administrative/operational state change.",
            "resolution": "Checked Base, management, and VPRN 10/11/12/100 interface status and cleared alarms.",
        },
    },
    "SYSTEM #2029": {
        "alarm_type": "CPM_SINGLETON_NO_STANDBY",
        "runbook_file": "RB_CPF_Masked.md",
        "section_keyword": "Check redundancy status",
        "past_incident": {
            "case_id": "PAST-INC-106",
            "problem": "CRITICAL SYSTEM #2029: Active CPM card A operating in singleton mode with no standby CPM.",
            "resolution": "Verified 'show redundancy synchronization' and standby OAM-B VM status.",
        },
    },
    "SNMP #2102": {
        "alarm_type": "RMON_CPU_THRESHOLD_ALARM",
        "runbook_file": "RB_CPF_Masked.md",
        "section_keyword": "Check cpu utilization and memory utilization",
        "past_incident": {
            "case_id": "PAST-INC-107",
            "problem": "SNMP #2102 RMON CPU threshold exceeded on ISM-MG card.",
            "resolution": "Checked 'show mobile-gateway ism-mg cpu' and per-VM CPU scheduling.",
        },
    },
    "NAT #2020": {
        "alarm_type": "NAT_MDA_ACTIVE_TRANSITION",
        "runbook_file": "RB_UPF01_Masked.md",
        "section_keyword": "Check VM/card and MDA status",
        "past_incident": {
            "case_id": "PAST-INC-108",
            "problem": "NAT MDA active/standby transition across NAT groups 1..9 on UPF.",
            "resolution": "Verified 'show mda' and 'show vm' status on UPF.",
        },
    },
    "SVCMGR #2210": {
        "alarm_type": "ACCESS_PORT_STATE_CHANGE_PROCESSED",
        "runbook_file": "RB_UPF01_Masked.md",
        "section_keyword": "To check interface status",
        "past_incident": {
            "case_id": "PAST-INC-109",
            "problem": "SVCMGR #2210 access port state change affected NAT SAPs on UPF.",
            "resolution": "Checked UPF router interfaces and BFD sessions.",
        },
    },
}


def load_runbook_sections():
    """Parses all Markdown files in data/runbooks/ into sections."""
    sections = []
    for path in sorted(glob.glob(os.path.join(RUNBOOKS_DIR, "*.md"))):
        fname = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        blocks = re.split(r"(?m)^##\s+", text)
        for blk in blocks[1:]:
            lines = blk.strip().splitlines()
            if not lines:
                continue
            sec_title = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
            cmds = [re.sub(r"^-\s*`(.+)`$", r"\1", l.strip()) for l in lines[1:] if l.strip().startswith("- `")]
            sections.append({
                "file": fname,
                "section_title": sec_title,
                "citation": f"[{fname} - {sec_title}]",
                "commands": cmds,
                "content": f"## {sec_title}\n{body}",
            })
    return sections


def retrieve_runbook_guidance(alarm_code: str, alarm_type: str = "", node: str = ""):
    """
    Retrieves the matching Runbook section, CLI commands, and citation.
    Returns status='not found' if the alarm code/type is not in the knowledge base.
    """
    sections = load_runbook_sections()
    code_clean = (alarm_code or "").strip().upper()
    type_clean = (alarm_type or "").strip().upper()

    kb_entry = ALARM_KNOWLEDGE_MAP.get(code_clean)
    if not kb_entry:
        for k, v in ALARM_KNOWLEDGE_MAP.items():
            if type_clean and v["alarm_type"] == type_clean:
                kb_entry = v
                code_clean = k
                break

    if not kb_entry:
        return {
            "status": "not found",
            "message": f"not found: Alarm '{alarm_code}' ('{alarm_type}') does not exist in the Masked PS-06 Runbooks. Refusing to hallucinate commands.",
            "citation": "not found",
            "recommended_commands": [],
            "section_content": "",
            "past_incident": None,
        }

    # Choose node-specific runbook if applicable
    target_file = kb_entry["runbook_file"]
    if "UPF-02" in (node or "").upper():
        target_file = "RB_UPF02_Masked.md"
    elif "UPF-01" in (node or "").upper() and target_file == "RB_UPF01_Masked.md":
        target_file = "RB_UPF01_Masked.md"

    keyword = kb_entry["section_keyword"].lower()
    matched_sec = None
    for s in sections:
        if s["file"] == target_file and keyword in s["section_title"].lower():
            matched_sec = s
            break
    if not matched_sec:
        for s in sections:
            if keyword in s["section_title"].lower():
                matched_sec = s
                break

    if not matched_sec:
        return {
            "status": "not found",
            "message": "not found",
            "citation": "not found",
            "recommended_commands": [],
            "section_content": "",
            "past_incident": None,
        }

    return {
        "status": "found",
        "alarm_code": code_clean,
        "alarm_type": kb_entry["alarm_type"],
        "node": node,
        "citation": matched_sec["citation"],
        "recommended_commands": matched_sec["commands"][:8],
        "section_content": matched_sec["content"],
        "past_incident": kb_entry["past_incident"],
    }


if __name__ == "__main__":
    print("=" * 65)
    print("STEP 4 COMPLETE: RAG RUNBOOK RETRIEVAL & CITATION CHECK")
    print("=" * 65)
    r1 = retrieve_runbook_guidance("VRTR #2061", "BFD_SESSION_DOWN_NBR_SIGNAL", "MASKED-UPF-01")
    print(f"Test 1 (Valid Alarm VRTR #2061) -> Status: {r1['status']}")
    print(f"  Citation : {r1['citation']}")
    print(f"  Commands : {r1['recommended_commands'][:3]}")

    r2 = retrieve_runbook_guidance("MOBILE_GATEWAY #2016", "MSCP_CARD_OPER_STATE_STANDBY", "MASKED-CPF-01")
    print(f"Test 2 (Valid Alarm MOBILE_GATEWAY #2016) -> Status: {r2['status']}")
    print(f"  Citation : {r2['citation']}")
    print(f"  Commands : {r2['recommended_commands'][:3]}")

    r3 = retrieve_runbook_guidance("ALM-UNKNOWN-999", "FAKE_ALARM", "MASKED-CPF-01")
    print(f"Test 3 (Unknown Alarm ALM-UNKNOWN-999) -> Status: {r3['status']}")
    print("=" * 65)
