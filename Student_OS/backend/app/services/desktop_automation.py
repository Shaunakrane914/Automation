import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from app.database import log_agent_event

logger = logging.getLogger("desktop_automation")

ALLOWED_COMMAND_PREFIXES = [
    "python", "py", "pytest", "git", "dir", "ls", "node", "npm", "npx",
    "code", "echo", "cat", "pip", "tasklist", "curl", "where", "whoami",
    "ipconfig", "powershell", "type", "ver", "systeminfo", "findstr", "head", "tail"
]

DANGEROUS_PATTERNS = [
    "rm -rf", "del /s", "del /f", "format ", "rmdir /s", "drop table", "shutdown", ">nul 2>&1"
]

CHAINING_OPERATORS = ["&&", "||", ";", "|", "&"]
DISALLOWED_PATTERNS = ["../", "..\\", "curl -x post", "curl -d", "wget --post"]

def is_safe_command(command: str) -> bool:
    cmd_clean = command.strip().lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in cmd_clean:
            return False

    # Block directory traversal
    for dis in DISALLOWED_PATTERNS:
        if dis in cmd_clean:
            return False

    # Block unquoted command chaining
    for op in CHAINING_OPERATORS:
        if op in cmd_clean:
            # Check if it's chained rather than inside a quoted argument
            parts = cmd_clean.split(op)
            if len(parts) > 1 and any(p.strip() for p in parts[1:]):
                return False

    for prefix in ALLOWED_COMMAND_PREFIXES:
        if cmd_clean == prefix or cmd_clean.startswith(prefix + " "):
            return True
    return False

def execute_desktop_command(command: str, working_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes an approved CLI command safely on the host system.
    """
    if not is_safe_command(command):
        msg = f"Command '{command}' blocked by safety policy. Only development and system inspection commands are permitted."
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
        output = process.stdout if process.returncode == 0 else (process.stderr or process.stdout)
        success = process.returncode == 0
        return {
            "success": success,
            "exit_code": process.returncode,
            "output": output or "Command completed successfully."
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
    Spawns local applications such as VS Code, Terminal, Explorer, or Antigravity.
    """
    try:
        path_arg = f'"{target_path}"' if target_path else ""
        app_clean = app_name.lower().strip()

        if app_clean in ["code", "vscode"]:
            cmd = f"code {path_arg}"
        elif app_clean in ["terminal", "cmd", "powershell"]:
            cmd = f"start powershell -NoExit -Command \"cd '{target_path or os.getcwd()}'\""
        elif app_clean in ["explorer", "folder"]:
            cmd = f"explorer \"{target_path or os.getcwd()}\""
        elif app_clean in ["antigravity", "agy"]:
            antigravity_exe = r"C:\Users\Shaunak Rane\AppData\Local\Programs\Antigravity\Antigravity.exe"
            if Path(antigravity_exe).exists():
                cmd = f'"{antigravity_exe}" {path_arg}'
            else:
                cmd = f"start antigravity {path_arg}"
        else:
            cmd = f"{app_name} {path_arg}"

        log_agent_event("INFO", f"Launching application: {app_name}")
        subprocess.Popen(cmd, shell=True)
        return {"success": True, "message": f"Launched {app_name} successfully."}
    except Exception as e:
        logger.error(f"Failed to launch app {app_name}: {e}")
        return {"success": False, "error": str(e)}
