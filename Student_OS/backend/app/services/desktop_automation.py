import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from app.database import log_agent_event

logger = logging.getLogger("desktop_automation")

ALLOWED_COMMAND_PREFIXES = [
    "python", "py", "pytest", "git", "dir", "ls", "node", "npm", "code", "echo", "cat"
]

def is_safe_command(command: str) -> bool:
    cmd_clean = command.strip().lower()
    for prefix in ALLOWED_COMMAND_PREFIXES:
        if cmd_clean.startswith(prefix):
            return True
    return False

def execute_desktop_command(command: str, working_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes an approved CLI command safely on the host system.
    """
    if not is_safe_command(command):
        msg = f"Command '{command}' is not in the approved safe list."
        log_agent_event("WARNING", msg)
        return {"success": False, "error": msg, "output": ""}

    cwd = Path(working_dir).expanduser() if working_dir else Path.cwd()

    try:
        log_agent_event("INFO", f"Executing desktop command: {command} in {cwd}")
        process = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30
        )
        output = process.stdout if process.returncode == 0 else process.stderr
        success = process.returncode == 0
        return {
            "success": success,
            "exit_code": process.returncode,
            "output": output
        }
    except subprocess.TimeoutExpired:
        msg = f"Command timed out after 30s: {command}"
        log_agent_event("ERROR", msg)
        return {"success": False, "error": msg, "output": ""}
    except Exception as e:
        msg = f"Error running command: {str(e)}"
        log_agent_event("ERROR", msg)
        return {"success": False, "error": msg, "output": ""}

def launch_application(app_name: str, target_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Spawns local applications such as VS Code, Terminal, or Antigravity.
    """
    try:
        path_arg = f'"{target_path}"' if target_path else ""
        if app_name.lower() in ["code", "vscode"]:
            cmd = f"code {path_arg}"
        elif app_name.lower() in ["terminal", "cmd", "powershell"]:
            cmd = f"start powershell -NoExit -Command \"cd '{target_path or os.getcwd()}'\""
        elif app_name.lower() in ["explorer", "folder"]:
            cmd = f"explorer \"{target_path or os.getcwd()}\""
        else:
            cmd = f"{app_name} {path_arg}"

        log_agent_event("INFO", f"Launching application: {app_name}")
        subprocess.Popen(cmd, shell=True)
        return {"success": True, "message": f"Launched {app_name} successfully."}
    except Exception as e:
        logger.error(f"Failed to launch app {app_name}: {e}")
        return {"success": False, "error": str(e)}
