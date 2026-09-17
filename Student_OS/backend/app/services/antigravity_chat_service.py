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
    Executes a coding prompt from mobile on the laptop workstation codebase.
    Uses Gemini API on the laptop to generate code/solutions, runs terminal commands if needed,
    updates local files, and records the conversation update locally.
    """
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

    reply = ""

    # Check for direct terminal commands (e.g. run git status, exec dir, ps ...)
    lower_p = prompt.strip().lower()
    if lower_p.startswith(("run ", "exec ", "cmd ", "ps ", "powershell ")):
        cmd = prompt.strip().split(" ", 1)[1]
        try:
            res = subprocess.run(["powershell", "-Command", cmd], cwd=WORKSPACE_ROOT, capture_output=True, text=True, timeout=20)
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

    if not reply:
        # Generate full code execution response with Gemini on laptop
        system_instruction = (
            f"You are Antigravity Autonomous Coding Assistant running on Shaunak Rane's laptop workstation at {WORKSPACE_ROOT}. "
            f"Shaunak is controlling you from his mobile phone. "
            f"Provide complete, production-ready code, file modifications, terminal instructions, or explanations. "
            f"Format your response in clean GitHub Markdown with syntax highlighted code blocks."
        )

        reply = generate_gemini_response(
            prompt=prompt,
            system_prompt=system_instruction,
            history=[]
        )

    if not reply:
        reply = (
            f"⚡ **Directive Queued on Laptop Workstation**\n\n"
            f"Your coding prompt has been synchronized to `{latest_file}` and copied to your laptop clipboard.\n\n"
            f"```markdown\n{prompt}\n```\n\n"
            f"You can execute this immediately in Antigravity IDE on your PC."
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
