import os
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.services.ai_engine import generate_gemini_response

BRAIN_DIR = Path(r"C:\Users\Shaunak Rane\.gemini\antigravity-ide\brain")
WORKSPACE_ROOT = Path(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation")
PROMPTS_DIR = WORKSPACE_ROOT / "antigravity_prompts"
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

def list_antigravity_chats() -> List[Dict[str, Any]]:
    """
    Scans local Antigravity IDE brain directory on the laptop and returns all conversation threads.
    """
    chats = []
    if not BRAIN_DIR.exists():
        return []

    for p in BRAIN_DIR.iterdir():
        if p.is_dir():
            transcript_path = p / ".system_generated" / "logs" / "transcript.jsonl"
            if transcript_path.exists():
                stat = transcript_path.stat()
                mtime_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                
                first_prompt = ""
                last_prompt = ""
                msg_count = 0
                
                try:
                    with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            try:
                                data = json.loads(line)
                                if data.get("type") == "USER_INPUT":
                                    msg_count += 1
                                    c = data.get("content", "")
                                    if "<USER_REQUEST>" in c:
                                        c = c.split("<USER_REQUEST>")[1].split("</USER_REQUEST>")[0].strip()
                                    if not first_prompt:
                                        first_prompt = c[:90]
                                    last_prompt = c[:120]
                            except Exception:
                                pass
                except Exception:
                    pass

                # Derive a friendly topic title
                title = first_prompt or f"Conversation {p.name[:8]}"
                if "Automation" in title or p.name.startswith("4c862611"):
                    title = "Student OS & Academic Copilot (Active)"
                elif "Misinformation" in title or p.name.startswith("e94bfe44"):
                    title = "Aegis Protocol — Autonomous Defense"
                elif "Portfolio" in title or p.name.startswith("fb4d074e"):
                    title = "Shaunak Portfolio Development"

                chats.append({
                    "id": p.name,
                    "title": title,
                    "last_prompt": last_prompt or first_prompt,
                    "message_count": msg_count,
                    "updated_at": mtime_str,
                    "timestamp": stat.st_mtime,
                    "is_current": p.name.startswith("4c862611")
                })

    # Sort descending by last updated
    chats.sort(key=lambda x: (x.get("is_current", False), x["timestamp"]), reverse=True)
    return chats

def get_chat_messages(conversation_id: str, max_messages: int = 40) -> List[Dict[str, Any]]:
    """
    Parses and returns structured chat messages for a specific Antigravity conversation.
    """
    transcript_path = BRAIN_DIR / conversation_id / ".system_generated" / "logs" / "transcript.jsonl"
    if not transcript_path.exists():
        return []

    messages = []
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    step_type = data.get("type", "")
                    content = data.get("content", "")
                    
                    if step_type == "USER_INPUT":
                        if "<USER_REQUEST>" in content:
                            content = content.split("<USER_REQUEST>")[1].split("</USER_REQUEST>")[0].strip()
                        if content and not content.startswith("[Message]") and not content.startswith("Task id "):
                            messages.append({
                                "id": f"u_{len(messages)}",
                                "sender": "user",
                                "text": content,
                                "timestamp": datetime.fromtimestamp(data.get("timestamp", time.time()) if isinstance(data.get("timestamp"), (int, float)) else time.time()).strftime("%H:%M")
                            })
                    elif step_type == "PLANNER_RESPONSE":
                        if content and len(content.strip()) > 0:
                            messages.append({
                                "id": f"a_{len(messages)}",
                                "sender": "assistant",
                                "text": content,
                                "tool_calls": data.get("tool_calls", []),
                                "timestamp": datetime.now().strftime("%H:%M")
                            })
                except Exception:
                    pass
    except Exception as e:
        print(f"Error reading transcript for {conversation_id}: {e}")

    # Return the most recent max_messages
    return messages[-max_messages:] if len(messages) > max_messages else messages

def append_to_transcript(conversation_id: str, prompt: str, reply: str):
    """
    Appends the user prompt and assistant response into the local Antigravity brain transcript.jsonl.
    """
    transcript_path = BRAIN_DIR / conversation_id / ".system_generated" / "logs" / "transcript.jsonl"
    try:
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        last_step_index = 0
        if transcript_path.exists():
            try:
                with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            idx = data.get("step_index", 0)
                            if isinstance(idx, int) and idx > last_step_index:
                                last_step_index = idx
                        except Exception:
                            pass
            except Exception:
                pass

        now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        user_entry = {
            "step_index": last_step_index + 1,
            "source": "USER_EXPLICIT",
            "type": "USER_INPUT",
            "status": "DONE",
            "created_at": now_iso,
            "content": f"<USER_REQUEST>\n{prompt}\n</USER_REQUEST>\n<ADDITIONAL_METADATA>\n[Source: Mobile Workstation Controller]\n</ADDITIONAL_METADATA>"
        }
        assistant_entry = {
            "step_index": last_step_index + 2,
            "source": "MODEL",
            "type": "PLANNER_RESPONSE",
            "status": "DONE",
            "created_at": now_iso,
            "content": reply
        }

        with open(transcript_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(user_entry) + "\n")
            f.write(json.dumps(assistant_entry) + "\n")
    except Exception as e:
        print(f"Failed to append to transcript for {conversation_id}: {e}")

def execute_chat_prompt_on_workstation(conversation_id: str, prompt: str) -> Dict[str, Any]:
    """
    Acts as the direct remote control execution engine for Shaunak's laptop workstation codebase.
    Directly executes Git commands, shell/PowerShell tools, file operations, test runners,
    app launchers, and contextual AI reasoning from mobile.
    """
    import re

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    directive_file = PROMPTS_DIR / f"mobile_directive_{timestamp_str}.md"
    latest_file = PROMPTS_DIR / "latest_active_directive.md"

    # Formulate directive content
    directive_content = f"""# Mobile Coding Directive from Shaunak Rane
- **Conversation Target:** {conversation_id}
- **Timestamp:** {datetime.now().isoformat()}
- **Workspace:** {WORKSPACE_ROOT}

## Prompt / Task:
{prompt}

## Execution Instruction:
Execute this prompt on the laptop codebase ({WORKSPACE_ROOT}).
"""

    directive_file.write_text(directive_content, encoding="utf-8")
    latest_file.write_text(directive_content, encoding="utf-8")

    # Sync to Windows clipboard
    try:
        subprocess.run("clip.exe", input=prompt.encode("utf-8"), check=False)
    except Exception:
        pass

    clean_p = prompt.strip()
    lower_p = clean_p.lower()
    reply = ""

    # Fetch recent history so we have conversational context (e.g. if user says "you do it" or "push it")
    recent_messages = get_chat_messages(conversation_id, max_messages=8)
    last_assistant_text = ""
    for msg in reversed(recent_messages):
        if msg.get("sender") == "assistant":
            last_assistant_text = msg.get("text", "")
            break

    # 1. ACTION: Direct "You do it" / "do it" / "run it" / "apply it"
    if lower_p in ["you do it", "do it", "run it", "execute it", "apply it", "push it", "do that", "please do it"]:
        if "git add" in last_assistant_text or "git push" in last_assistant_text or "git commit" in last_assistant_text or "git" in last_assistant_text.lower():
            # Run full git commit & push
            cmd = 'git add . ; git commit -m "update from mobile remote control" ; git push origin main'
            res = subprocess.run(["powershell", "-Command", cmd], cwd=WORKSPACE_ROOT, capture_output=True, text=True, timeout=25)
            out = (res.stdout.strip() + "\n" + res.stderr.strip()).strip()
            reply = f"⚡ **Autonomous Workstation Action Executed: Git Push**\n\n```powershell\n{out or 'Code committed and pushed to remote main branch.'}\n```\n\n*Exit Code:* `{res.returncode}` • *Workspace:* `{WORKSPACE_ROOT}`"
        else:
            # Look for code blocks in the previous assistant message
            code_blocks = re.findall(r'```(?:powershell|bash|sh|cmd)?\s*\n(.*?)```', last_assistant_text, re.DOTALL)
            if code_blocks:
                extracted_cmd = code_blocks[0].strip()
                res = subprocess.run(["powershell", "-Command", extracted_cmd], cwd=WORKSPACE_ROOT, capture_output=True, text=True, timeout=30)
                reply = f"⚡ **Autonomous Action Executed on Laptop Workstation (`{extracted_cmd}`)**\n\n```powershell\n{res.stdout.strip() or 'Command executed successfully.'}\n```\n"
                if res.stderr.strip():
                    reply += f"\n**Stderr:**\n```powershell\n{res.stderr.strip()}\n```\n"
                reply += f"\n*Exit Code:* `{res.returncode}`"

    # 2. ACTION: Git operations (e.g. push current code, git push, commit and push)
    if not reply and any(k in lower_p for k in ["push current code", "push code", "push to git", "git push", "git commit", "commit and push", "stage and push"]):
        commit_msg = "update from mobile remote controller"
        if "message" in lower_p or "-m" in lower_p:
            parts = clean_p.split("message", 1)
            if len(parts) > 1:
                commit_msg = parts[1].strip(" :\"'")
        cmd = f'git status ; git add . ; git commit -m "{commit_msg}" ; git push origin main'
        res = subprocess.run(["powershell", "-Command", cmd], cwd=WORKSPACE_ROOT, capture_output=True, text=True, timeout=25)
        out = (res.stdout.strip() + "\n" + res.stderr.strip()).strip()
        reply = f"⚡ **Git Push Executed on Laptop Workstation**\n\n```powershell\n{out}\n```\n\n*Branch:* `main` • *Exit Code:* `{res.returncode}`"

    # 3. ACTION: Git Status / Git Diff / Git Log
    if not reply and lower_p in ["git status", "status", "check git status", "check git", "git diff", "git log"]:
        cmd = "git status" if "diff" not in lower_p and "log" not in lower_p else ("git diff" if "diff" in lower_p else "git log -n 5")
        res = subprocess.run(["powershell", "-Command", cmd], cwd=WORKSPACE_ROOT, capture_output=True, text=True, timeout=15)
        reply = f"⚡ **`{cmd}` on Workstation (`{WORKSPACE_ROOT}`)**\n\n```powershell\n{res.stdout.strip() or res.stderr.strip()}\n```"

    # 4. ACTION: Direct Terminal & PowerShell commands
    if not reply and lower_p.startswith(("run ", "exec ", "cmd ", "ps ", "powershell ")):
        cmd = clean_p.split(" ", 1)[1]
        try:
            res = subprocess.run(["powershell", "-Command", cmd], cwd=WORKSPACE_ROOT, capture_output=True, text=True, timeout=30)
            stdout = res.stdout.strip()
            stderr = res.stderr.strip()
            reply = f"⚡ **Executed on Laptop Terminal (`{cmd}`)**\n\n"
            if stdout:
                reply += f"```powershell\n{stdout}\n```\n"
            if stderr:
                reply += f"\n**Stderr:**\n```powershell\n{stderr}\n```\n"
            reply += f"\n*Exit Code:* `{res.returncode}` • *Workspace:* `{WORKSPACE_ROOT}`"
        except Exception as e:
            reply = f"⚠️ **Command execution failed:** {e}"

    # 5. ACTION: Build & Tests
    if not reply and lower_p in ["npm build", "build frontend", "run build", "build apk", "gradle build", "run tests", "pytest"]:
        if "apk" in lower_p or "gradle" in lower_p:
            cmd = r"cd Student_OS\frontend\android ; .\gradlew.bat assembleRelease"
        elif "frontend" in lower_p or "npm" in lower_p or "build" in lower_p:
            cmd = r"cd Student_OS\frontend ; npm run build"
        else:
            cmd = "pytest"
        res = subprocess.run(["powershell", "-Command", cmd], cwd=WORKSPACE_ROOT, capture_output=True, text=True, timeout=40)
        reply = f"⚡ **Build & Execution on Workstation (`{cmd}`)**\n\n```powershell\n{res.stdout.strip() or res.stderr.strip()}\n```\n*Exit Code:* `{res.returncode}`"

    # 6. ACTION: Desktop App Launching
    if not reply and any(lower_p.startswith(pfx) for pfx in ["open ", "launch ", "start "]):
        target = lower_p.split(" ", 1)[1].strip()
        if "vs code" in target or "code" in target:
            subprocess.Popen(["code", str(WORKSPACE_ROOT)], shell=True)
            reply = f"⚡ **Launched VS Code** on laptop with workspace `{WORKSPACE_ROOT}`."
        elif "chrome" in target or "browser" in target:
            subprocess.Popen(["start", "chrome"], shell=True)
            reply = "⚡ **Launched Google Chrome** on laptop."
        elif "terminal" in target or "powershell" in target:
            subprocess.Popen(["start", "powershell", "-NoExit", "-Command", f"Set-Location '{WORKSPACE_ROOT}'"], shell=True)
            reply = f"⚡ **Launched PowerShell Terminal** at `{WORKSPACE_ROOT}`."
        elif "antigravity" in target or "ide" in target:
            subprocess.Popen([r"C:\Users\Shaunak Rane\AppData\Local\Programs\Antigravity\Antigravity.exe", str(WORKSPACE_ROOT)], shell=True)
            reply = "⚡ **Spawned Google Antigravity IDE** on laptop."

    # 7. General AI Reasoning & Tool Synthesis (Gemini + Local GPU)
    if not reply:
        system_instruction = (
            f"You are Antigravity Autonomous Agent Remote Controller operating directly on Shaunak Rane's laptop workstation ({WORKSPACE_ROOT}). "
            f"Shaunak is interacting via his mobile phone to control this exact workstation. "
            f"Be decisive, technical, and action-oriented. Provide direct terminal commands or code ready for execution. "
            f"When you suggest PowerShell/terminal actions, provide them clearly in fenced code blocks so the remote control can execute them if commanded."
        )

        reply = generate_gemini_response(
            prompt=prompt,
            system_prompt=system_instruction,
            history=recent_messages
        )

    if not reply:
        reply = (
            f"⚡ **Directive Synced to Laptop Workstation**\n\n"
            f"Your command has been written to `{latest_file}` and copied to Windows clipboard.\n\n"
            f"```markdown\n{prompt}\n```"
        )

    # Persist directly into the Antigravity conversation transcript
    append_to_transcript(conversation_id, prompt, reply)

    return {
        "success": True,
        "conversation_id": conversation_id,
        "reply": reply,
        "directive_file": str(directive_file),
        "timestamp": datetime.now().strftime("%H:%M")
    }
