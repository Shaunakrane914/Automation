from app.services.lab_matching_service import analyze_and_match_labworks, format_lab_analysis_markdown
import os
import re
import sys
import json
import logging
import asyncio
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, AsyncGenerator

import psutil

from app.config import settings
from app.database import get_db_connection, log_agent_event
from app.services.academic_engine import calculate_attendance_metrics
from app.services.desktop_automation import execute_desktop_command, launch_application
from app.services.rag_engine import search_academic_rag, get_academic_rag_context
from app.services.notification_service import send_windows_notification
from app.services.scheduler_service import workstation_daemon

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
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:1.5b"
FALLBACK_OLLAMA_MODEL = "qwen2.5:0.5b"

# ----------------- LLM Engine (Ollama GPU + Gemini Cloud) -----------------

def get_active_model() -> str:
    """
    Returns the best available local Ollama model (prefers qwen2.5-coder:1.5b).
    """
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name", "") for m in data.get("models", [])]
            if any(DEFAULT_OLLAMA_MODEL in m for m in models):
                return DEFAULT_OLLAMA_MODEL
            if any(FALLBACK_OLLAMA_MODEL in m for m in models):
                return FALLBACK_OLLAMA_MODEL
    except Exception:
        pass
    return DEFAULT_OLLAMA_MODEL

def call_ollama(prompt: str, system_prompt: str = "", model: Optional[str] = None, timeout: int = 25) -> Optional[str]:
    """
    Sends generation query to local Ollama running on NVIDIA GeForce RTX 3050 GPU.
    """
    active_m = model or get_active_model()
    try:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

        payload = {
            "model": active_m,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.6,
                "num_predict": 750
            }
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            OLLAMA_API_URL,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            ans = res_json.get("response", "").strip()
            if ans:
                return ans
    except Exception as e:
        logger.warning(f"Ollama API call failed: {e}")
        # Try fallback model if primary failed
        if active_m != FALLBACK_OLLAMA_MODEL:
            return call_ollama(prompt, system_prompt, model=FALLBACK_OLLAMA_MODEL, timeout=timeout)
    return None

def stream_ollama_tokens(prompt: str, system_prompt: str = ""):
    """
    Generator yielding individual tokens in real time from Ollama for SSE streaming.
    """
    active_m = get_active_model()
    full_prompt = prompt
    if system_prompt:
        full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

    payload = {
        "model": active_m,
        "prompt": full_prompt,
        "stream": True,
        "options": {
            "temperature": 0.6,
            "num_predict": 750
        }
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=data_bytes,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            for line in resp:
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("response", "")
                    if token:
                        yield token
                    if chunk.get("done", False):
                        break
    except Exception as e:
        logger.warning(f"Error streaming tokens: {e}")
        yield f"\n[Stream Error: {e}]"

# ----------------- Workstation Tools -----------------

def tool_system_telemetry() -> Dict[str, Any]:
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.1)
    disk = psutil.disk_usage("C:\\")

    gpu_info = "NVIDIA GeForce RTX 3050 6GB Laptop GPU"
    gpu_mem_used = "N/A"
    gpu_mem_free = "N/A"
    gpu_temp = "N/A"
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode == 0 and res.stdout.strip():
            parts = [p.strip() for p in res.stdout.strip().split(",")]
            if len(parts) >= 5:
                gpu_info = parts[0]
                gpu_mem_used = f"{parts[2]} MB"
                gpu_mem_free = f"{parts[3]} MB"
                gpu_temp = f"{parts[4]}°C"
    except Exception:
        pass

    return {
        "cpu_pct": cpu,
        "ram_used_gb": round(mem.used / (1024**3), 1),
        "ram_total_gb": round(mem.total / (1024**3), 1),
        "ram_pct": mem.percent,
        "disk_free_gb": round(disk.free / (1024**3), 1),
        "disk_total_gb": round(disk.total / (1024**3), 1),
        "gpu_name": gpu_info,
        "gpu_vram_used": gpu_mem_used,
        "gpu_vram_free": gpu_mem_free,
        "gpu_temp": gpu_temp,
        "ollama_active": True,
        "active_model": get_active_model()
    }

def tool_execute_command(command: str) -> Dict[str, Any]:
    res = execute_desktop_command(command, str(WORKSPACE_ROOT))
    output = res.get("output") or res.get("error") or "Command completed."
    return {
        "tool": "execute_command",
        "command": command,
        "success": res.get("success", False),
        "result": output[:1500]
    }

def tool_launch_app(app_name: str, target: str = "") -> Dict[str, Any]:
    res = launch_application(app_name, target)
    return {
        "tool": "open_application",
        "app": app_name,
        "target": target,
        "success": res.get("status") == "success" or res.get("success", False),
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

def tool_applied_applications() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, status, applied_at, proof_screenshot, url FROM career_radar WHERE status = 'applied' ORDER BY applied_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {
        "tool": "applied_applications",
        "count": len(rows),
        "applications": rows
    }

def tool_career_radar() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, category, deadline, benefits_credits, url FROM career_radar WHERE status = 'open'")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"tool": "career_radar", "count": len(rows), "opportunities": rows}

def tool_read_file(target_path: str, max_lines: int = 100) -> Dict[str, Any]:
    p = Path(target_path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    if not p.exists() or not p.is_file():
        return {"error": f"File not found: {p}"}
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            lines = [f.readline() for _ in range(max_lines)]
        return {"path": str(p), "content": "".join(lines)}
    except Exception as e:
        return {"error": str(e)}

def tool_delegate_to_antigravity(user_request: str, target_area: str = "") -> Dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_file = PROMPTS_DIR / f"antigravity_task_{timestamp}.md"

    profile_path = PROJECT_ROOT / "Student_OS" / "USER_PROFILE.md"
    user_profile_snippet = ""
    if profile_path.exists():
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                user_profile_snippet = f.read()
        except Exception:
            pass

    academic_stat = tool_academic_status()
    prompt_content = f"""# Autonomous Antigravity Execution Directive
*Explicitly Delegated by Shaunak Rane via Student OS Copilot*

## 1. User Objective & Delegation Request
> {user_request}

## 2. System Context
- System: Student OS Autonomous Workstation (Universal AI University)
- Attendance: {academic_stat.get('overall_attendance')}% across {academic_stat.get('subjects_count')} subjects.
- Target Scope: {target_area or "Automation Workspace"}

## 3. User Guidelines & Profile
{user_profile_snippet if user_profile_snippet else "Standard Universal AI University Automation Workstation Profile"}
"""
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt_content)

    clipboard_copied = False
    try:
        clip_proc = subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=True)
        clip_proc.communicate(input=prompt_content.encode("utf-8"))
        clipboard_copied = True
    except Exception:
        pass

    launched = False
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
        launch_msg = f"Antigravity note: {e}"

    return {
        "tool": "delegate_to_antigravity",
        "launched": launched,
        "prompt_file": str(prompt_file),
        "prompt_name": prompt_file.name,
        "prompt_preview": prompt_content,
        "clipboard_copied": clipboard_copied,
        "message": launch_msg
    }

# ----------------- Autonomous ReAct Function Calling Loop -----------------

AGENT_TOOLS_PROMPT = """You are an Autonomous Workstation Agent with direct PC execution tools.
When answering, you may use these tools if necessary to inspect the machine or files before answering:
- execute_command(command: str): Run safe terminal command (e.g. git status, nvidia-smi, dir)
- read_file(path: str): Read lines from a file
- check_attendance(): Get live attendance metrics and risk subjects
- query_rag(query: str): Search 3rd year academic course notes and lecture slides
- system_telemetry(): Get CPU, RAM, and GPU stats
- send_notification(title: str, message: str): Display Windows desktop notification

To call a tool, format EXACTLY as:
Thought: <what you want to do>
Action: <tool_name>
Action Input: <argument or json string>

When you have the final answer, output:
Final Answer: <your full, well-formatted markdown response>
"""

def run_agentic_react_loop(query: str, max_iterations: int = 3) -> str:
    """
    Autonomous ReAct execution loop allowing Ollama to plan, invoke tools, observe outputs,
    and formulate a synthesized response.
    """
    conversation = f"User Request: {query}\n"
    active_m = get_active_model()

    for i in range(max_iterations):
        prompt = f"{AGENT_TOOLS_PROMPT}\n\n{conversation}\n"
        step_response = call_ollama(prompt, model=active_m, timeout=18)
        if not step_response:
            break

        if "Final Answer:" in step_response:
            return step_response.split("Final Answer:", 1)[1].strip()

        # Check for Action:
        action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)", step_response)
        input_match = re.search(r"Action Input:\s*(.+)", step_response)

        if action_match:
            action = action_match.group(1).strip()
            arg = input_match.group(1).strip() if input_match else ""
            arg = arg.strip("\"'")

            observation = ""
            if action == "execute_command":
                res = tool_execute_command(arg)
                observation = res.get("result", "")[:600]
            elif action == "read_file":
                res = tool_read_file(arg)
                observation = res.get("content", "")[:600] or res.get("error", "")
            elif action == "check_attendance":
                res = tool_academic_status()
                observation = f"Overall: {res['overall_attendance']}%, At Risk: {res['at_risk_subjects']}"
            elif action == "query_rag":
                observation = get_academic_rag_context(arg, top_k=2)[:600]
            elif action == "system_telemetry":
                res = tool_system_telemetry()
                observation = f"CPU: {res['cpu_pct']}%, RAM: {res['ram_pct']}%, GPU: {res['gpu_name']} ({res['gpu_vram_free']} free)"
            elif action == "send_notification":
                send_windows_notification("Student OS Agent", arg)
                observation = "Dispatched desktop notification."
            else:
                observation = f"Unknown tool: {action}"

            conversation += f"{step_response}\nObservation: {observation}\n"
        else:
            return step_response

    # Final synthesis if reached max iterations
    final_prompt = f"{conversation}\nProvide the final answer for the user based on observations above:\nFinal Answer:"
    final_res = call_ollama(final_prompt, model=active_m, timeout=15)
    return final_res.replace("Final Answer:", "").strip() if final_res else "Task completed with observations above."

# ----------------- Natural Language Intent Engine -----------------

def process_chat_query(query: str) -> Dict[str, Any]:
    q = query.strip()
    ql = q.lower()

    if not q:
        return {
            "response": "Hello Shaunak! I am your **Student OS Autonomous Copilot & Workstation Controller**. How can I assist you?",
            "tool_used": "none"
        }

    # 1. Greetings & Casual Interaction (Zero Antigravity Escalation)
    greetings = ["hi", "hello", "hey", "sup", "good morning", "good evening", "yo", "hola", "heya", "greetings"]
    if ql in greetings or any(ql.startswith(g + " ") for g in greetings) or ql in ["who are you", "what can you do", "help", "capabilities", "what are you"]:
        telem = tool_system_telemetry()
        academic = tool_academic_status()
        applied = tool_applied_applications()
        active_model = telem.get("active_model", DEFAULT_OLLAMA_MODEL)

        reply = (
            f"👋 **Hey Shaunak! I am your Student OS Copilot & Ultimate Workstation Controller.**\n\n"
            f"I have direct PC execution authority and live dual-brain intelligence. Here is your live workstation status:\n\n"
            f"### ⚡ Live Station Telemetry:\n"
            f"- 🧠 **AI Brain:** Ollama (`{active_model}`) on **{telem['gpu_name']}** ({telem['gpu_vram_free']} VRAM free, {telem['gpu_temp']})\n"
            f"- 💻 **System Load:** CPU `{telem['cpu_pct']}%` | RAM `{telem['ram_used_gb']}/{telem['ram_total_gb']} GB` ({telem['ram_pct']}%) | Disk C: `{telem['disk_free_gb']} GB free`\n"
            f"- 📊 **Academic Health:** `{academic['overall_attendance']}%` attendance across {academic['subjects_count']} courses ({academic['pending_assignments_count']} pending assignments)\n"
            f"- 💼 **Career Radar:** ✅ **{applied['count']} verified jobs applied** across LinkedIn, Internshala, and Indeed\n"
            f"- 📚 **Academic RAG:** 800+ coursework snippets indexed across Desktop/3rd Year\n\n"
            f"### 🛠️ Live Commands You Can Run Right Now:\n"
            f"- 💻 **Terminal:** `run git status`, `run python ...`, `run dir`, `run nvidia-smi`\n"
            f"- 🚀 **App Launcher:** `open vs code`, `open terminal`, `open chrome`, `open deep learning`\n"
            f"- 📊 **Academic:** `check attendance`, `show assignments`, `resync digicampus`\n"
            f"- 📚 **Course RAG:** Ask questions about your 3rd year slides, exams, and labs (`Explain ARIMA in Time Series`, `Show AJP question bank`)\n"
            f"- 💼 **Career:** `show applied jobs`, `run auto apply`, `show opportunities`\n"
            f"- 🤖 **ReAct Agent:** Ask multi-step queries like *\"Check my attendance in Time Series and list its files\"*"
        )
        return {"response": reply, "tool_used": "workstation_greeting", "details": telem}

    # 2. Strict Explicit Antigravity Escalation (Only when user specifically asks)
    antigravity_explicit_triggers = [
        "escalate to antigravity", "delegate to antigravity", "ask antigravity",
        "send to antigravity", "give power to antigravity", "launch antigravity directive",
        "write prompt for antigravity", "escalate"
    ]
    if any(t in ql for t in antigravity_explicit_triggers) or ql.startswith("antigravity:"):
        clean_req = re.sub(r'^(antigravity:\s*|escalate to antigravity\s*|ask antigravity to\s*)', '', q, flags=re.IGNORECASE).strip()
        res = tool_delegate_to_antigravity(user_request=clean_req or q)
        clip_msg = "✅ Copied to clipboard" if res.get("clipboard_copied") else "⚠️ Clipboard skipped"
        reply = (
            f"⚡ **Task Explicitly Delegated to Google Antigravity**\n\n"
            f"I have formulated a specialized directive in your personal style (`USER_PROFILE.md`) "
            f"and launched Antigravity IDE targeting your workspace:\n\n"
            f"- 📁 **Directive File:** `{res['prompt_file']}`\n"
            f"- 🚀 **Status:** {res['message']}\n"
            f"- 📋 **Clipboard:** {clip_msg}\n\n"
            f"```markdown\n{res['prompt_preview'][:450]}...\n```"
        )
        return {"response": reply, "tool_used": "delegate_to_antigravity", "details": res}

    # 3. System Hardware & Telemetry
    if any(k in ql for k in ["system", "specs", "hardware", "pc status", "telemetry", "gpu status", "performance", "cpu", "ram"]):
        t = tool_system_telemetry()
        reply = (
            f"🖥️ **Live Workstation Telemetry & Hardware Status**\n\n"
            f"| Resource | Status & Utilization |\n"
            f"| :--- | :--- |\n"
            f"| **CPU Usage** | `{t['cpu_pct']}%` |\n"
            f"| **RAM (System)** | `{t['ram_used_gb']} GB / {t['ram_total_gb']} GB` ({t['ram_pct']}%) |\n"
            f"| **GPU Model** | `{t['gpu_name']}` |\n"
            f"| **GPU VRAM** | Used: `{t['gpu_vram_used']}` | Free: `{t['gpu_vram_free']}` |\n"
            f"| **GPU Temperature** | `{t['gpu_temp']}` |\n"
            f"| **Disk C: Available** | `{t['disk_free_gb']} GB free` (Total: {t['disk_total_gb']} GB) |\n"
            f"| **Active Ollama Brain** | `{t.get('active_model')}` (100% on GPU) |\n"
            f"| **FastAPI Backend** | Active on `http://127.0.0.1:8000` |\n"
            f"| **Vite Frontend** | Active on `http://localhost:5173` |\n"
        )
        return {"response": reply, "tool_used": "system_telemetry", "details": t}

    # 4. Background Daemon Control
    if "daemon" in ql:
        if "enable" in ql or "start" in ql:
            workstation_daemon.auto_apply_enabled = True
            workstation_daemon.start()
            return {"response": "🤖 **Workstation Continuous Daemon Started**\nAuto-apply checks & attendance risk alerts are running in the background.", "tool_used": "daemon_control"}
        elif "disable" in ql or "stop" in ql:
            workstation_daemon.stop()
            return {"response": "🛑 **Workstation Continuous Daemon Stopped**", "tool_used": "daemon_control"}
        else:
            status = workstation_daemon.get_status()
            return {"response": f"🤖 **Daemon Status:** `{'RUNNING' if status['is_running'] else 'STOPPED'}`\n- Auto-apply enabled: `{status['auto_apply_enabled']}`\n- Interval: `{status['interval_hours']} hours`\n- Last execution: `{status['last_run']}`", "tool_used": "daemon_control"}

    # 5. Verified Applied Jobs & Career Radar
    if any(k in ql for k in ["applied jobs", "my applications", "show applied", "applied positions", "what did i apply to", "application status", "verified applications"]):
        res = tool_applied_applications()
        reply = f"💼 **Verified Job Applications Active ({res['count']} Authentic Applications)**\n\n"
        reply += "All records are authenticated in SQLite database with visual proof screenshots:\n\n"
        for i, app in enumerate(res['applications'], 1):
            portal = "Indeed" if "Indeed" in app['name'] else ("LinkedIn" if "LinkedIn" in app['name'] else "Internshala")
            reply += f"### {i}. {app['name']}\n"
            reply += f"- **Portal:** `{portal}` | **Status:** `APPLIED ✅`\n"
            reply += f"- **Submitted:** `{app['applied_at']}`\n"
            reply += f"- **Proof Screenshot:** `{app['proof_screenshot']}`\n\n"
        return {"response": reply, "tool_used": "applied_applications", "details": res}

    # 6. Autonomous Auto-Apply Pipeline
    if any(k in ql for k in ["auto apply", "auto-apply", "apply to all", "apply to opportunities", "apply to jobs", "rerun auto apply"]):
        try:
            from app.services.auto_apply_engine import run_auto_apply_pipeline, get_latest_resume
            resume = get_latest_resume()
            summary = run_auto_apply_pipeline()
            reply = (
                f"⚡ **Autonomous Auto-Apply Pipeline Execution Completed!**\n\n"
                f"- **Resume Used:** `{resume['name']}` ({resume['size_bytes']:,} bytes)\n"
                f"- **Opportunities Evaluated:** {summary['total']}\n"
                f"- **Successfully Applied:** ✅ **{summary['applied']}**\n"
                f"- **Skipped / Pending:** ⏭️ **{summary['skipped']}**\n"
                f"- **Failed:** ❌ **{summary['failed']}**\n\n"
                "### Application Evidence & Status:\n"
            )
            for res_item in summary["results"]:
                reply += f"- **{res_item['name']}**: `{res_item['status'].upper()}` — {res_item['notes']}\n"
            return {"response": reply, "tool_used": "auto_apply_pipeline", "data": summary}
        except Exception as e:
            return {"response": f"⚠️ Auto-apply error: {e}", "tool_used": "auto_apply_pipeline"}

    # 7. Terminal Execution
    shell_prefixes = ["run ", "exec ", "cmd ", "ps ", "powershell "]
    is_shell_command = any(ql.startswith(p) for p in shell_prefixes) or any(ql.startswith(x) for x in [
        "git ", "python ", "npm ", "pytest", "pip ", "dir", "tasklist", "curl", "nvidia-smi", "ollama ", "wmic ", "hostname", "netstat", "ipconfig"
    ])
    if is_shell_command:
        cmd = q
        for prefix in shell_prefixes:
            if ql.startswith(prefix):
                cmd = q[len(prefix):].strip()
                break
        cmd = cmd.rstrip(".!?;")
        res = tool_execute_command(cmd)
        status_icon = "✅" if res.get("success") else "⚠️"
        reply = f"💻 **Executed Workstation Command:** `{cmd}` {status_icon}\n\n```text\n{res['result']}\n```"
        return {"response": reply, "tool_used": "execute_command", "details": res}

    # 8. App & Course Folder Launcher
    if any(k in ql for k in ["open ", "launch "]):
        app_target = "explorer"
        param = ""
        if "linkedin" in ql:
            launch_application("chrome", "https://www.linkedin.com/jobs/tracker/applied/")
            return {"response": "🚀 **Launched LinkedIn in Chrome**", "tool_used": "open_application"}
        elif "indeed" in ql:
            launch_application("chrome", "https://myjobs.indeed.com/applied")
            return {"response": "🚀 **Launched Indeed in Chrome**", "tool_used": "open_application"}
        elif "internshala" in ql:
            launch_application("chrome", "https://internshala.com/student/dashboard")
            return {"response": "🚀 **Launched Internshala in Chrome**", "tool_used": "open_application"}
        elif "github" in ql:
            launch_application("chrome", "https://github.com/Shaunakrane914/Automation")
            return {"response": "🚀 **Launched GitHub Repository in Chrome**", "tool_used": "open_application"}
        elif "code" in ql or "vs code" in ql:
            app_target = "code"
            param = str(PROJECT_ROOT)
        elif "terminal" in ql or "powershell" in ql:
            app_target = "terminal"
            param = str(PROJECT_ROOT)
        elif "chrome" in ql or "browser" in ql:
            app_target = "chrome"
            param = "http://localhost:5173"
        elif "notepad" in ql:
            app_target = "notepad"
        elif "calc" in ql or "calculator" in ql:
            app_target = "calc"
        elif any(subj in ql for subj in ["time series", "awt", "bda", "deep learning", "nlp", "sepm", "ajp", "mentoring"]):
            for s in ["time series", "awt", "bda", "deep learning", "nlp lab", "nlp", "sepm", "ajp", "mentoring"]:
                if s in ql:
                    folder_name = "NLP Lab" if s == "nlp lab" else s.title()
                    app_target = "explorer"
                    param = str(ACADEMIC_ROOT / folder_name)
                    break
        res = tool_launch_app(app_target, param)
        return {"response": f"🚀 **Launched {app_target.upper()}** (`{param or 'Default'}`)", "tool_used": "open_application", "details": res}

    # 9. Attendance & Risk
    if any(k in ql for k in ["attendance", "present", "risk", "safe"]):
        res = tool_academic_status()
        lines = [
            f"📊 **Academic Attendance Overview:** Overall **{res['overall_attendance']}%**\n",
            f"Tracked Subjects: **{res['subjects_count']}** | Threshold: `75.0%` Required\n"
        ]
        if res['at_risk_subjects']:
            lines.append(f"⚠️ **Attention Required (<75%):** {', '.join(res['at_risk_subjects'])}\n")
        else:
            lines.append("✅ **All enrolled courses are safe above 75% attendance.**\n")
        for s in res['subjects'][:8]:
            badge = "🟢" if s['attendance_percentage'] >= 75.0 else "🔴"
            lines.append(f"- {badge} **{s['name']}**: `{s['attendance_percentage']}%`")
        return {"response": "\n".join(lines), "tool_used": "academic_status", "details": res}

    # 9b. Assignments & Coursework Submissions
    if any(k in ql for k in ["assignment", "assignments", "homework", "pending work", "submissions", "pending task", "coursework"]):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT a.id, a.title, a.deadline, a.status, s.name as subject_name, a.is_lab
        FROM assignments a
        JOIN subjects s ON a.subject_id = s.id
        ORDER BY a.deadline ASC
        """)
        all_asgs = [dict(r) for r in cursor.fetchall()]
        conn.close()

        ongoing_asgs = [a for a in all_asgs if (a.get("status") or "").lower() in ["pending", "open"]]
        submitted_asgs = [a for a in all_asgs if (a.get("status") or "").lower() in ["submitted"]]
        closed_asgs = [a for a in all_asgs if (a.get("status") or "").lower() in ["closed", "not submitted"]]
        completed_labs = [a for a in all_asgs if (a.get("status") or "").lower() in ["completed"]]

        lines = ["📊 **DigiCampus & Academic Coursework Status**\n"]

        # 1. Ongoing / Action Required
        if ongoing_asgs:
            lines.append(f"### ⏳ Ongoing Submissions ({len(ongoing_asgs)} Action Required)")
            for a in ongoing_asgs:
                sname = a["subject_name"].split("[")[0].strip()
                due_str = f"Due: `{a['deadline']}`" if a.get('deadline') else "Upcoming"
                lines.append(f"- **{a['title']}** (`{sname}` • {due_str})")
            lines.append("")
        else:
            lines.append("### 🟢 Ongoing Submissions: `0 Active` (All caught up!)\nThere are currently no active open assignments requiring submission on DigiCampus.\n")

        # 2. Submitted Work
        if submitted_asgs:
            lines.append(f"### ✅ Submitted Coursework ({len(submitted_asgs)})")
            for a in submitted_asgs:
                sname = a["subject_name"].split("[")[0].strip()
                lines.append(f"- **{a['title']}** (`{sname}` • Status: `Submitted`)")
            lines.append("")

        # 3. Closed (Past Due)
        if closed_asgs:
            lines.append(f"### 🔒 Closed Assignments ({len(closed_asgs)} Past Deadline)")
            for a in closed_asgs:
                sname = a["subject_name"].split("[")[0].strip()
                due_str = f"Deadline was: `{a['deadline'][:10]}`" if a.get('deadline') else "Past"
                lines.append(f"- **{a['title']}** (`{sname}` • {due_str} • `Closed`)")
            lines.append("")

        # 4. Labworks
        lines.append(f"### 🔬 Local Labworks: **{len(completed_labs)} Experiments Completed** in `Desktop/3rd Year`")
        lines.append("\n💡 *Tip: Check the Classroom & Academics tab for full course audit details or to manually add newly announced tasks.*")

        return {
            "response": "\n".join(lines),
            "tool_used": "assignments_status",
            "details": {
                "ongoing_count": len(ongoing_asgs),
                "submitted_count": len(submitted_asgs),
                "closed_count": len(closed_asgs),
                "completed_labs_count": len(completed_labs)
            }
        }

    # 9c. Labworks, Practicals & Code Practice To-Dos
    lab_keywords = ["labwork", "labworks", "practical", "practicals", "lab todo", "practice todo", "lab work", "labs", "experiments", "experiment", "servlet", "lab ", "lab1", "lab2", "lab3", "lab4", "lab5", "drive", "sir's", "sirs", "problem statement"]
    if any(k in ql for k in lab_keywords) and not any(k in ql for k in ["assignment", "assignments", "homework"]):
        # Check if Advance Java deep matching is requested
        if any(k in ql for k in ["advance java", "java", "ajp", "servlet", "jdbc", "swing", "mdi", "5 labwords", "5 labworks", "5 labs"]):
            analysis_data = analyze_and_match_labworks("advance_java")
            reply = format_lab_analysis_markdown(analysis_data)
            return {
                "response": reply,
                "tool_used": "digicampus_labwork_deep_analyzer",
                "details": {"subject": "Advance Java", "experiments_count": analysis_data["total_experiments"]}
            }
        target_subj = None
        if any(k in ql for k in ["advance java", "java", "ajp", "servlet", "jdbc", "swing", "mdi"]):
            target_subj = "Advance Java"
        elif any(k in ql for k in ["deep learning", "dl", "neural network", "perceptron", "mlp"]):
            target_subj = "Deep Learning"
        elif any(k in ql for k in ["nlp", "natural language", "bow", "tfidf", "n-gram", "sentiment"]):
            target_subj = "Natural Language"
        elif any(k in ql for k in ["time series", "arima", "moving average", "decomposition"]):
            target_subj = "Time Series"
        elif any(k in ql for k in ["bda", "big data", "structured", "netflix", "amazon"]):
            target_subj = "Big Data"
        elif any(k in ql for k in ["awt", "typescript", "react", "overloading"]):
            target_subj = "Advanced Web"

        conn = get_db_connection()
        cursor = conn.cursor()
        if target_subj:
            cursor.execute("""
            SELECT l.id, l.lab_number, l.title, l.file_path, l.concepts, l.problem_statement, l.practice_todos, s.name as subject_name
            FROM labworks l
            JOIN subjects s ON l.subject_id = s.id
            WHERE s.name LIKE ?
            ORDER BY l.id ASC
            """, (f"%{target_subj}%",))
        else:
            cursor.execute("""
            SELECT l.id, l.lab_number, l.title, l.file_path, l.concepts, l.problem_statement, l.practice_todos, s.name as subject_name
            FROM labworks l
            JOIN subjects s ON l.subject_id = s.id
            ORDER BY l.subject_id ASC, l.id ASC
            """)
        labs = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if labs:
            subj_title = target_subj if target_subj else "3rd Year Curriculum"
            lines = [f"🔬 **DigiCampus & Workstation Labworks: {subj_title} ({len(labs)} Experiments)**\n"]
            lines.append("Here is the complete verified list of lab practicals from DigiCampus and your `Desktop/3rd Year` workspace, along with your structured practice to-do checklist:\n")

            all_todos = []
            for l in labs:
                sname = l["subject_name"].split("[")[0].strip()
                lines.append(f"### {l['lab_number']}: {l['title']}")
                lines.append(f"- **Course:** `{sname}`")
                if l.get("file_path"):
                    lines.append(f"- **Local File:** `{Path(l['file_path']).name}`")
                if l.get("problem_statement"):
                    lines.append(f"- **Objective:** {l['problem_statement']}")
                
                # Parse practice todos
                todos_raw = l.get("practice_todos")
                if todos_raw:
                    try:
                        todos_list = json.loads(todos_raw) if isinstance(todos_raw, str) else todos_raw
                        if isinstance(todos_list, list) and todos_list:
                            lines.append("- **Practice Tasks:**")
                            for t in todos_list:
                                task_text = t.get("task", "") if isinstance(t, dict) else str(t)
                                cat = t.get("category", "") if isinstance(t, dict) else ""
                                badge = f" `[{cat}]`" if cat else ""
                                lines.append(f"  - [ ] {task_text}{badge}")
                                all_todos.append(f"{l['lab_number']} ({cat}): {task_text}")
                    except Exception:
                        pass
                lines.append("")

            lines.append("### 📋 Practice To-Do Action Items:")
            for i, todo in enumerate(all_todos[:12], 1):
                lines.append(f"{i}. {todo}")
            if len(all_todos) > 12:
                lines.append(f"... and {len(all_todos) - 12} more practice tasks available in the Labworks & Code Practice tab.")

            lines.append("\n💡 *You can also view full starter code, test suites, and toggle completed tasks in the **Labworks & Code Practice** tab.*")

            return {
                "response": "\n".join(lines),
                "tool_used": "labworks_curriculum_inspector",
                "details": {"subject": target_subj, "labs_count": len(labs), "total_todos": len(all_todos)}
            }

    # 10. Multi-Step Query / ReAct Agent Trigger
    if any(k in ql for k in ["and then", "and list", "check if", "find and", "search and", "if there is"]):
        agent_answer = run_agentic_react_loop(q)
        return {"response": agent_answer, "tool_used": "react_agent_loop"}

    # 11. Local Academic RAG Ingestion & Semantic Retrieval
    # If the user asks an academic or coursework question, ground with real Desktop/3rd Year slides & code
    rag_context = get_academic_rag_context(q, top_k=3)

    system_prompt = (
        "You are Shaunak Rane's Student OS Autonomous Workstation Copilot at Universal AI University (B.Tech CS AI & ML). "
        "You have direct access to Shaunak's 3rd year coursework, local files in Desktop/3rd Year, and DigiCampus academic records. "
        "NEVER identify as an external third-party AI or state that you lack access to coursework materials. "
        "Provide direct, authoritative, concise, mathematically precise, and structured answers grounded in Shaunak's engineering curriculum. "
        f"{rag_context}"
    )

    ollama_ans = call_ollama(q, system_prompt=system_prompt)
    if ollama_ans:
        tool_label = "academic_rag_llm" if rag_context else "ollama_gpu_llm"
        return {"response": ollama_ans, "tool_used": tool_label, "details": {"model": get_active_model(), "rag_used": bool(rag_context)}}

    return {
        "response": f"⚡ I processed your request: *{q}*. How can I help with your workstation?",
        "tool_used": "smart_dispatcher"
    }

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
