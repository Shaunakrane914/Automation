import os
import re
import sys
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.config import settings
from app.database import get_db_connection, log_agent_event
from app.services.academic_engine import calculate_attendance_metrics
from app.services.desktop_automation import execute_desktop_command, launch_application

logger = logging.getLogger("chatbot_engine")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
STUDENT_OS_DIR = BACKEND_DIR.parent
WORKSPACE_ROOT = STUDENT_OS_DIR.parent
PROJECT_ROOT = WORKSPACE_ROOT
DATA_DIR = BACKEND_DIR / "data"
PROMPTS_DIR = DATA_DIR / "antigravity_prompts"
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

ANTIGRAVITY_EXE = r"C:\Users\Shaunak Rane\AppData\Local\Programs\Antigravity\Antigravity.exe"
ACADEMIC_ROOT = Path(settings.ACADEMIC_ROOT_DIR)

# ----------------- Tool Registry (Section 27 & 28) -----------------

def tool_execute_command(command: str) -> Dict[str, Any]:
    res = execute_desktop_command(command, str(WORKSPACE_ROOT))
    output = res.get("output") or res.get("error") or "Command completed."
    return {
        "tool": "execute_command",
        "command": command,
        "success": res.get("success", False),
        "result": output[:800]
    }

def tool_launch_app(app_name: str, target: str = "") -> Dict[str, Any]:
    res = launch_application(app_name, target)
    return {
        "tool": "open_application",
        "app": app_name,
        "target": target,
        "success": res.get("status") == "success",
        "message": res.get("message", "")
    }

def tool_academic_status(filter_type: str = "all") -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, code, attendance_percentage FROM subjects ORDER BY name ASC")
    subjects = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
    SELECT a.title, a.deadline, s.name as subject_name 
    FROM assignments a JOIN subjects s ON a.subject_id = s.id 
    WHERE a.status = 'pending'
    """)
    assignments = [dict(r) for r in cursor.fetchall()]
    conn.close()

    total_pct = sum(s["attendance_percentage"] for s in subjects) / max(1, len(subjects))
    at_risk = [s["name"] for s in subjects if s["attendance_percentage"] < 75.0]

    return {
        "tool": "academic_status",
        "subjects_count": len(subjects),
        "overall_attendance": round(total_pct, 1),
        "at_risk_subjects": at_risk,
        "pending_assignments_count": len(assignments),
        "pending_assignments": assignments,
        "subjects": subjects
    }

def tool_file_system(action: str, target_path: str = "", content: str = "") -> Dict[str, Any]:
    p = Path(target_path) if target_path else ACADEMIC_ROOT
    if not p.is_absolute():
        p = PROJECT_ROOT / p

    if action == "list":
        if not p.exists():
            return {"tool": "file_system", "error": f"Path not found: {p}"}
        items = [{"name": item.name, "is_dir": item.is_dir()} for item in sorted(p.iterdir())[:30]]
        return {"tool": "file_system", "action": "list", "path": str(p), "items": items}

    elif action == "read":
        if not p.exists() or not p.is_file():
            return {"tool": "file_system", "error": f"File not found: {p}"}
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read(2000)
            return {"tool": "file_system", "action": "read", "path": str(p), "content": data}
        except Exception as e:
            return {"tool": "file_system", "error": str(e)}

    elif action == "create":
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            return {"tool": "file_system", "action": "create", "path": str(p), "success": True}
        except Exception as e:
            return {"tool": "file_system", "error": str(e)}

    return {"tool": "file_system", "error": f"Unknown action: {action}"}

def tool_career_radar() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, category, deadline, benefits_credits, url FROM career_radar WHERE status = 'open'")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"tool": "career_radar", "count": len(rows), "opportunities": rows}

def tool_delegate_to_antigravity(user_request: str, target_area: str = "") -> Dict[str, Any]:
    """
    Formulates a specialized, high-context prompt in Shaunak Prompting Style (Section 30),
    persists it, copies to clipboard, and launches Antigravity IDE to execute the delegated task (Section 28 & 29).
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_file = PROMPTS_DIR / f"antigravity_task_{timestamp}.md"

    # Read user profile if exists
    profile_path = PROJECT_ROOT / "Student_OS" / "USER_PROFILE.md"
    user_profile_snippet = ""
    if profile_path.exists():
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                user_profile_snippet = f.read()
        except Exception:
            pass

    # Gather live system context
    academic_stat = tool_academic_status()
    git_branch = "main"
    git_last_commit = "b5db493"
    try:
        r_branch = subprocess.run(["git", "branch", "--show-current"], cwd=PROJECT_ROOT, capture_output=True, text=True)
        if r_branch.returncode == 0 and r_branch.stdout.strip():
            git_branch = r_branch.stdout.strip()
        r_log = subprocess.run(["git", "log", "-1", "--oneline"], cwd=PROJECT_ROOT, capture_output=True, text=True)
        if r_log.returncode == 0 and r_log.stdout.strip():
            git_last_commit = r_log.stdout.strip()
    except Exception:
        pass

    # Formulate high-leverage prompt per Section 30 & 31
    prompt_content = f"""# Autonomous Antigravity Execution Directive
*Generated automatically by Student OS Autonomous Copilot*

## 1. User Objective & Delegation Request
> {user_request}

## 2. Execution Authority & User Style
- **System:** Student OS Autonomous Copilot Workstation
- **User Working Profile:** Universal AI University • B.Tech CS (AI & ML)
- **Primary Project Root:** `{PROJECT_ROOT}`
- **Academic Source of Truth:** `{ACADEMIC_ROOT}`
- **Git Branch:** `{git_branch}` (Latest Commit: `{git_last_commit}`)
- **Execution Mandate:** Execute completely with zero unnecessary human steps. Test, verify, and commit cleanly to GitHub (`https://github.com/Shaunakrane914/Automation`).

## 3. Academic & Workspace Context
- **Overall Attendance:** {academic_stat.get('overall_attendance')}% across {academic_stat.get('subjects_count')} subjects.
- **Pending Assignments:** {academic_stat.get('pending_assignments_count')} pending items.
- **Target Scope:** {target_area or "Universal Automation / Student OS Workspace / 3rd Year Academic Directories"}

## 4. Operational Guidelines (Shaunak Working Style)
1. Thoroughly inspect the existing code structure in `{PROJECT_ROOT}` before modifying files.
2. Maintain clean architecture: no loose scripts in root, proper typing, and modern dark workstation aesthetics.
3. Automatically run verification (e.g. backend tests, build scripts, endpoint checks).
4. Stage and commit changes with a concise git message and push to `origin {git_branch}`.

---
*Directive Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Directive File: `{prompt_file.name}`*
"""

    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt_content)

    # Copy directive prompt to Windows clipboard using clip.exe
    clipboard_copied = False
    try:
        clip_proc = subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=True)
        clip_proc.communicate(input=prompt_content.encode("utf-8"))
        clipboard_copied = True
    except Exception as clip_err:
        logger.warning(f"Could not copy prompt to clipboard: {clip_err}")

    # Launch Antigravity IDE targeting the prompt and project workspace
    launched = False
    launch_msg = ""
    try:
        if Path(ANTIGRAVITY_EXE).exists():
            subprocess.Popen([ANTIGRAVITY_EXE, str(PROJECT_ROOT), str(prompt_file)])
            launched = True
            launch_msg = f"Antigravity IDE launched targeting {PROJECT_ROOT}"
        else:
            launch_application("antigravity", str(prompt_file))
            launched = True
            launch_msg = "Antigravity process invoked via system application launcher"
    except Exception as e:
        logger.warning(f"Error launching Antigravity: {e}")
        launch_msg = f"Prompt generated, launcher note: {e}"

    log_agent_event("INFO", f"Delegated task to Antigravity: {user_request[:60]}...")

    return {
        "tool": "delegate_to_antigravity",
        "launched": launched,
        "prompt_file": str(prompt_file),
        "prompt_name": prompt_file.name,
        "prompt_preview": prompt_content,
        "clipboard_copied": clipboard_copied,
        "message": launch_msg
    }

# ----------------- Natural Language Intent Engine -----------------

def process_chat_query(query: str) -> Dict[str, Any]:
    """
    Main entry point for processing natural language commands.
    Directs to local tool registry or delegates to Antigravity if the task requires deep code synthesis.
    """
    q = query.strip()
    ql = q.lower()

    if not q:
        return {
            "response": "Hello! I am your **Student OS Autonomous Copilot**. How can I assist your workstation today?",
            "tool_used": "none"
        }

    # 1. Identity, Capabilities & "Where is my chatbot" Queries
    if any(k in ql for k in [
        "where is my", "who are you", "what can you do", "help", "capabilities",
        "ultimate powerfull chatbot", "ultimate powerful chatbot", "controller", "how do you work"
    ]):
        reply = (
            "⚡ **Student OS Ultimate Autonomous Copilot & Workstation Controller**\n\n"
            "I am your central autonomous orchestrator for your PC, academics, and career development. "
            "I have real-time access to your local workstation, terminal execution, DigiCampus auditor, and Google Antigravity bridge.\n\n"
            "### 🛠️ What I Can Control Right Now:\n"
            "1. 💻 **PC & Terminal Execution:** Run any command (`run git status`, `run python ...`, `run dir`, `run npm test`).\n"
            "2. 🚀 **Application & Folder Launcher:** Instantly open VS Code, Windows Terminal, or File Explorer to any of your 12 academic folders (`open deep learning`, `open time series`, `open awt`, `open 3rd year`).\n"
            "3. 📊 **Academic Auditor:** Real-time attendance check, risk analysis (<75%), DigiCampus assignment status, and dynamic local file count.\n"
            "4. 🔄 **Classroom Sync:** Rerun full DigiCampus audit across all 15 subjects and auto-push to GitHub (`https://github.com/Shaunakrane914/Automation`).\n"
            "5. 🏆 **Career Radar:** Monitor active hackathons, GSoC programs, fellowships, and free cloud credits.\n"
            "6. 📌 **Task Priorities:** Manage daily action items and lab scaffolding.\n\n"
            "### ⚡ Autonomous Antigravity Self-Empowerment Protocol:\n"
            "> **If you ask me to do something and I cannot perform it with local tools** (e.g., training machine learning models, writing full software systems, deep debugging, complex architectural refactoring):\n"
            "> 1. I automatically formulate a specialized, high-context directive in your personal style (`USER_PROFILE.md`).\n"
            "> 2. Save it to `data/antigravity_prompts/`.\n"
            "> 3. Copy the directive to your clipboard.\n"
            "> 4. Launch **Google Antigravity** (`Antigravity.exe`) targeting the workspace so Antigravity gives me the full power to perform your task!\n\n"
            "Try a command: `Check my attendance`, `Run git status`, `Open Deep Learning folder`, or `Ask Antigravity to build a new feature`."
        )
        return {"response": reply, "tool_used": "identity_overview"}

    # 1.5 Autonomous Auto-Apply Pipeline Trigger
    if any(k in ql for k in ["auto apply", "auto-apply", "apply to all", "apply to opportunities", "apply to jobs", "rerun auto apply"]):
        try:
            from app.services.auto_apply_engine import run_auto_apply_pipeline, get_latest_resume
            resume = get_latest_resume()
            summary = run_auto_apply_pipeline()
            reply = (
                f"⚡ **Autonomous Auto-Apply Pipeline Execution Completed!**\n\n"
                f"- **Latest Resume Used:** `{resume['name']}` ({resume['size_bytes']:,} bytes)\n"
                f"- **Opportunities Evaluated:** {summary['total']}\n"
                f"- **Successfully Applied:** ✅ **{summary['applied']}**\n"
                f"- **Skipped / Pending:** ⏭️ **{summary['skipped']}**\n"
                f"- **Failed:** ❌ **{summary['failed']}**\n\n"
                "### Application Evidence & Status:\n"
            )
            for res in summary["results"]:
                reply += f"- **{res['name']}**: `{res['status'].upper()}` — {res['notes']}\n"
            reply += "\n*Visual proof screenshots logged to `Auto Apply/logs/screenshots/` and recorded to history CSV.*"
            return {"response": reply, "tool_used": "auto_apply_pipeline", "data": summary}
        except Exception as e:
            return {"response": f"⚠️ Auto-apply pipeline error: {e}", "tool_used": "auto_apply_pipeline"}

    # 2. Antigravity Delegation / Complex Code Creation Triggers
    antigravity_triggers = [
        "antigravity", "power to", "give it power", "ask antigravity", "delegate",
        "write prompt for antigravity", "open antigravity and", "cannot", "escalate"
    ]
    code_generation_triggers = [
        "build a new", "refactor my", "develop a", "train model", "implement full",
        "write a python script", "write code for", "solve lab", "create a readme for",
        "neural network", "train a pytorch", "create project", "generate documentation"
    ]

    is_antigravity_explicit = any(t in ql for t in antigravity_triggers)
    is_code_generation = any(t in ql for t in code_generation_triggers) and not any(k in ql for k in ["show", "list", "check attendance", "how many"])

    if is_antigravity_explicit or is_code_generation:
        res = tool_delegate_to_antigravity(user_request=q)
        clip_msg = "✅ Copied to clipboard" if res.get("clipboard_copied") else "⚠️ Clipboard skipped"
        reply = (
            f"⚡ **Task Delegated to Google Antigravity (Power Injection Protocol)**\n\n"
            f"I have formulated a specialized directive in your configured prompting style (`USER_PROFILE.md`) "
            f"and launched Antigravity IDE with full workspace context so it has the power to execute the task:\n\n"
            f"- 📁 **Directive File:** `{res['prompt_file']}`\n"
            f"- 🚀 **Launcher Status:** {res['message']}\n"
            f"- 📋 **Clipboard:** {clip_msg}\n\n"
            f"```markdown\n{res['prompt_preview'][:500]}...\n```\n\n"
            f"Antigravity is now active in your workspace to perform the task."
        )
        return {
            "response": reply,
            "tool_used": "delegate_to_antigravity",
            "details": res
        }

    # 3. Desktop Shell Commands
    if ql.startswith("run ") or ql.startswith("exec ") or ql.startswith("cmd ") or any(ql.startswith(x) for x in ["git ", "python ", "npm ", "pytest", "pip ", "dir", "tasklist", "curl"]):
        cmd = q
        for prefix in ["run ", "exec ", "cmd "]:
            if ql.startswith(prefix):
                cmd = q[len(prefix):].strip()
                break
        res = tool_execute_command(cmd)
        reply = (
            f"💻 **Executed Terminal Command:** `{cmd}`\n\n"
            f"```text\n{res['result']}\n```"
        )
        return {"response": reply, "tool_used": "execute_command", "details": res}

    # 3. Application & Folder Launching
    if any(k in ql for k in ["open ", "launch "]):
        app_target = "explorer"
        param = ""

        if "code" in ql or "vs code" in ql:
            app_target = "code"
            param = str(PROJECT_ROOT)
        elif "terminal" in ql or "powershell" in ql:
            app_target = "terminal"
            param = str(PROJECT_ROOT)
        elif "antigravity" in ql:
            app_target = "antigravity"
            param = str(PROJECT_ROOT)
        elif "3rd year" in ql or "academic" in ql:
            app_target = "explorer"
            param = str(ACADEMIC_ROOT)
        elif any(subj in ql for subj in ["time series", "awt", "bda", "deep learning", "nlp", "sepm", "ajp", "mentoring"]):
            for s in ["time series", "awt", "bda", "deep learning", "nlp lab", "nlp", "sepm", "ajp", "mentoring"]:
                if s in ql:
                    folder_name = "NLP Lab" if s == "nlp lab" else s.title()
                    app_target = "explorer"
                    param = str(ACADEMIC_ROOT / folder_name)
                    break

        res = tool_launch_app(app_target, param)
        reply = f"🚀 **Launched {app_target.upper()}**\n\nTarget path: `{param or 'Default'}`\nResult: {res['message']}"
        return {"response": reply, "tool_used": "open_application", "details": res}

    # 4. Sync & Rerun
    if any(k in ql for k in ["sync", "update", "rerun", "crawl", "digicampus audit"]):
        # Trigger sync
        from app.services.digicampus_scraper import sync_digicampus
        asyncio.create_task(sync_digicampus())
        reply = (
            f"🔄 **DigiCampus Audit & Update Triggered**\n\n"
            f"The crawler is now connecting to your active Chrome browser session on port 9222. "
            f"It will audit all 15 subjects, cross-reference `{ACADEMIC_ROOT}`, update the SQLite database, "
            f"and automatically push results to GitHub."
        )
        return {"response": reply, "tool_used": "sync_digicampus"}

    # 5. Academic Status & Attendance
    if any(k in ql for k in ["attendance", "present", "risk", "safe"]):
        res = tool_academic_status()
        lines = [
            f"📊 **Academic Attendance Overview:** Overall {res['overall_attendance']}%\n",
            f"Tracked Subjects: {res['subjects_count']} | Threshold: 75.0% Required\n"
        ]
        if res['at_risk_subjects']:
            lines.append(f"⚠️ **Attention Required:** {', '.join(res['at_risk_subjects'])}\n")
        else:
            lines.append("✅ **All enrolled courses are currently safe above the attendance threshold.**\n")

        for s in res['subjects'][:6]:
            badge = "🟢" if s['attendance_percentage'] >= 75.0 else "🔴"
            lines.append(f"- {badge} **{s['name']}**: `{s['attendance_percentage']}%`")

        if len(res['subjects']) > 6:
            lines.append(f"... and {len(res['subjects']) - 6} more courses.")

        return {"response": "\n".join(lines), "tool_used": "academic_status", "details": res}

    # 6. Assignments
    if any(k in ql for k in ["assignment", "homework", "task due", "pending"]):
        res = tool_academic_status()
        if res['pending_assignments_count'] == 0:
            reply = (
                "✅ **Classroom Status: All Caught Up!**\n\n"
                "There are **0 ongoing assignments** pending on DigiCampus across all 15 enrolled courses. "
                "All past submissions have been graded or evaluated."
            )
        else:
            lines = [f"⏳ **Pending Assignments ({res['pending_assignments_count']}):**"]
            for a in res['pending_assignments']:
                lines.append(f"- **{a['title']}** ({a['subject_name']}) — Due: `{a['deadline']}`")
            reply = "\n".join(lines)
        return {"response": reply, "tool_used": "academic_status", "details": res}

    # 7. Career & Competitions
    if any(k in ql for k in ["internship", "job", "hackathon", "competition", "fellowship", "opportunity"]):
        res = tool_career_radar()
        lines = [f"🏆 **Active Career Radar ({res['count']} Opportunities):**\n"]
        for opp in res['opportunities']:
            lines.append(f"- **{opp['name']}** [{opp['category'].upper()}]: {opp['benefits_credits']} (Deadline: `{opp['deadline']}`)")
        return {"response": "\n".join(lines), "tool_used": "career_radar", "details": res}

    # 8. Action Items / Daily Todos
    if any(k in ql for k in ["todo", "action item", "priorities", "what to do"]):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT title, category, due_date FROM daily_todos WHERE completed = 0 ORDER BY due_date ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        lines = ["📌 **Today's Action Items & Priorities:**\n"]
        for i, t in enumerate(rows, 1):
            lines.append(f"{i}. **[{t['category']}]** {t['title']} (Due: `{t['due_date']}`)")
        return {"response": "\n".join(lines), "tool_used": "daily_todos"}

    # 9. File System Queries
    if any(k in ql for k in ["list files", "show files", "what files in", "directory"]):
        target = ACADEMIC_ROOT
        for s in ["time series", "awt", "bda", "deep learning", "nlp lab", "nlp", "sepm", "ajp", "mentoring"]:
            if s in ql:
                folder_name = "NLP Lab" if s == "nlp lab" else s.title()
                target = ACADEMIC_ROOT / folder_name
                break
        res = tool_file_system("list", str(target))
        if "items" in res:
            items_str = ", ".join([it['name'] for it in res['items'][:15]])
            reply = f"📁 **Files in `{target.name}` ({len(res['items'])} items):**\n\n{items_str}"
        else:
            reply = f"Note: {res.get('error')}"
        return {"response": reply, "tool_used": "file_system", "details": res}

    # 10. Default Escalation / Fallback to Antigravity if unsupported
    # If the user asks something creative, custom, or complex that local simple commands cannot fulfill:
    res = tool_delegate_to_antigravity(user_request=q)
    reply = (
        f"⚡ **Task Escalated to Antigravity:**\n\n"
        f"This command requires deeper generative execution beyond local dashboard switches. "
        f"I have automatically formulated a high-leverage Antigravity directive and launched Antigravity IDE:\n\n"
        f"📁 **Directive File:** `{res['prompt_file']}`\n"
        f"🚀 **Action:** Antigravity IDE launched with full workspace context.\n\n"
        f"You can view the directive or continue the task in the opened Antigravity window."
    )
    return {"response": reply, "tool_used": "delegate_to_antigravity", "details": res}

def generate_daily_briefing() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects")
    subjects = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT * FROM assignments WHERE status = 'pending'")
    assignments = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT * FROM career_radar WHERE status = 'open' LIMIT 5")
    career_opps = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT * FROM daily_todos WHERE completed = 0 LIMIT 5")
    todos = [dict(r) for r in cursor.fetchall()]
    conn.close()

    total_pct = sum(s["attendance_percentage"] for s in subjects) / max(1, len(subjects))
    at_risk = [s["name"] for s in subjects if s["attendance_percentage"] < 75.0]

    return {
        "date": datetime.now().strftime("%A, %d %B %Y"),
        "academics": {
            "pending_assignments": len(assignments),
            "subjects_tracked": len(subjects)
        },
        "attendance": {
            "overall_pct": round(total_pct, 1),
            "subjects_at_risk": at_risk
        },
        "career": {
            "top_opportunities": [c["name"] for c in career_opps]
        },
        "top_5_priorities": [t["title"] for t in todos]
    }

def global_search(query_str: str) -> Dict[str, Any]:
    term = f"%{query_str.lower().strip()}%"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, attendance_percentage FROM subjects WHERE LOWER(name) LIKE ?", (term,))
    matched_subjects = [dict(r) for r in cursor.fetchall()]
    cursor.execute("""
    SELECT a.id, a.title, a.deadline, s.name as subject_name 
    FROM assignments a JOIN subjects s ON a.subject_id = s.id 
    WHERE LOWER(a.title) LIKE ? OR LOWER(s.name) LIKE ?
    """, (term, term))
    matched_assignments = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT id, name, category, benefits_credits, url FROM career_radar WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?", (term, term))
    matched_career = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT id, title, category FROM daily_todos WHERE LOWER(title) LIKE ?", (term,))
    matched_todos = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {
        "query": query_str,
        "subjects": matched_subjects,
        "assignments": matched_assignments,
        "opportunities": matched_career,
        "todos": matched_todos
    }
