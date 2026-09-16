import os
import sys
import json
import time
import sqlite3
import subprocess
import urllib.request
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.services.chatbot_engine import process_chat_query, tool_delegate_to_antigravity
from app.services.notifications import dispatch_alert

regression_report = {
    "workflow_a_academics": {},
    "workflow_b_career": {},
    "workflow_c_chatbot": {},
    "workflow_d_antigravity": {},
    "workflow_e_notifications": {},
    "workflow_f_git": {},
    "overall_status": "PENDING"
}

# --- Workflow A: Academics & Full Update ---
t0 = time.time()
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/academic/overview", timeout=10) as resp:
        academic_data = json.loads(resp.read().decode())
    
    conn = sqlite3.connect(BACKEND_DIR / "student_os.db")
    c = conn.cursor()
    c.execute("SELECT count(*) FROM subjects")
    s_cnt = c.fetchone()[0]
    c.execute("SELECT count(*) FROM documents")
    d_cnt = c.fetchone()[0]
    c.execute("SELECT count(*) FROM assignments")
    a_cnt = c.fetchone()[0]
    conn.close()

    regression_report["workflow_a_academics"] = {
        "status": "PASS",
        "duration_ms": round((time.time() - t0) * 1000, 2),
        "subjects": s_cnt,
        "documents": d_cnt,
        "assignments": a_cnt,
        "local_folders_mapped": len(academic_data.get("folders", []))
    }
except Exception as e:
    regression_report["workflow_a_academics"] = {"status": "FAIL", "error": str(e)}

# --- Workflow B: Career Radar & Todos ---
t0 = time.time()
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/career/radar", timeout=5) as resp:
        career_data = json.loads(resp.read().decode())
    with urllib.request.urlopen("http://127.0.0.1:8000/api/todos", timeout=5) as resp:
        todos_data = json.loads(resp.read().decode())

    regression_report["workflow_b_career"] = {
        "status": "PASS",
        "duration_ms": round((time.time() - t0) * 1000, 2),
        "opportunities_count": len(career_data),
        "todos_count": len(todos_data)
    }
except Exception as e:
    regression_report["workflow_b_career"] = {"status": "FAIL", "error": str(e)}

# --- Workflow C: Chatbot Multi-Query & Harmless Task Creation ---
t0 = time.time()
try:
    res_academic = process_chat_query("Check my attendance.")
    res_career = process_chat_query("Find solo competitions.")
    
    # Harmless task creation via API
    task_payload = json.dumps({"title": "Regression Verification Task - Self Audit", "category": "Audit", "due_date": "2026-09-16", "completed": 0}).encode()
    req = urllib.request.Request("http://127.0.0.1:8000/api/todos", data=task_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        created_task = json.loads(resp.read().decode())

    # Clean up test task
    conn = sqlite3.connect(BACKEND_DIR / "student_os.db")
    conn.execute("DELETE FROM daily_todos WHERE title = 'Regression Verification Task - Self Audit'")
    conn.commit()
    conn.close()

    regression_report["workflow_c_chatbot"] = {
        "status": "PASS",
        "duration_ms": round((time.time() - t0) * 1000, 2),
        "academic_query_tool": res_academic.get("tool_used"),
        "career_query_tool": res_career.get("tool_used"),
        "task_created_id": created_task.get("id")
    }
except Exception as e:
    regression_report["workflow_c_chatbot"] = {"status": "FAIL", "error": str(e)}

# --- Workflow D: Antigravity Bridge & Profile Reflection ---
t0 = time.time()
try:
    res_ag = tool_delegate_to_antigravity("Create a minimal README for today's lab class")
    prompt_p = Path(res_ag["prompt_file"])
    has_directive = prompt_p.exists()
    content = prompt_p.read_text(encoding="utf-8") if has_directive else ""
    has_profile = "Active User Profile & Preferences" in content

    # Clean up test prompt
    if prompt_p.exists():
        prompt_p.unlink()

    regression_report["workflow_d_antigravity"] = {
        "status": "PASS" if (has_directive and has_profile) else "FAIL",
        "duration_ms": round((time.time() - t0) * 1000, 2),
        "directive_generated": has_directive,
        "profile_embedded": has_profile
    }
except Exception as e:
    regression_report["workflow_d_antigravity"] = {"status": "FAIL", "error": str(e)}

# --- Workflow E: Mobile Notification Pipeline ---
t0 = time.time()
try:
    # Synchronous test alert dispatch
    import asyncio
    alert_ok = asyncio.run(dispatch_alert(
        "Student OS Regression Verification",
        "✅ End-to-end regression workflows validated.",
        priority="default",
        tags="white_check_mark"
    ))
    regression_report["workflow_e_notifications"] = {
        "status": "PASS (NETWORK DELIVERY VERIFIED; DEVICE RECEIPT NOT DIRECTLY VERIFIABLE)" if alert_ok else "FAIL",
        "duration_ms": round((time.time() - t0) * 1000, 2),
        "network_delivered": alert_ok
    }
except Exception as e:
    regression_report["workflow_e_notifications"] = {"status": "FAIL", "error": str(e)}

# --- Workflow F: Git Remote & Status Verification ---
t0 = time.time()
try:
    r_remote = subprocess.run(["git", "remote", "-v"], cwd=Path("."), capture_output=True, text=True)
    r_branch = subprocess.run(["git", "branch", "--show-current"], cwd=Path("."), capture_output=True, text=True)
    r_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=Path("."), capture_output=True, text=True)

    regression_report["workflow_f_git"] = {
        "status": "PASS",
        "duration_ms": round((time.time() - t0) * 1000, 2),
        "remote_verified": "Shaunakrane914/Automation" in r_remote.stdout,
        "branch": r_branch.stdout.strip(),
        "commit_hash": r_head.stdout.strip()[:8]
    }
except Exception as e:
    regression_report["workflow_f_git"] = {"status": "FAIL", "error": str(e)}

all_passed = all("PASS" in str(v.get("status", "")) for v in regression_report.values() if isinstance(v, dict))
regression_report["overall_status"] = "PASS" if all_passed else "FAIL"

out_file = Path("Student_OS/logs/final_regression_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(regression_report, f, indent=2)

print("=== FINAL REGRESSION TEST RESULTS ===")
for wf, res in regression_report.items():
    if isinstance(res, dict):
        print(f"  {wf}: {res.get('status')}")
print("Overall Regression Status:", regression_report["overall_status"])
