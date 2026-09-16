import os
import sys
import json
import sqlite3
import platform
import subprocess
import urllib.request
from pathlib import Path

results = {}

# 1. OS
results["OS"] = {
    "status": "PASS",
    "version": f"{platform.system()} {platform.release()} ({platform.version()})"
}

# 2. Python
results["Python"] = {
    "status": "PASS",
    "version": sys.version.split()[0],
    "executable": sys.executable
}

# 3. Node & NPM
try:
    node_v = subprocess.check_output(["node", "--version"], text=True).strip()
    npm_v = subprocess.check_output(["npm", "--version"], text=True, shell=True).strip()
    results["Node"] = {"status": "PASS", "version": node_v}
    results["npm"] = {"status": "PASS", "version": npm_v}
except Exception as e:
    results["Node"] = {"status": "FAIL", "error": str(e)}
    results["npm"] = {"status": "FAIL", "error": str(e)}

# 4. Git
try:
    git_v = subprocess.check_output(["git", "--version"], text=True).strip()
    results["Git"] = {"status": "PASS", "version": git_v}
except Exception as e:
    results["Git"] = {"status": "FAIL", "error": str(e)}

# 5. FastAPI & Uvicorn
try:
    import fastapi
    import uvicorn
    results["FastAPI"] = {"status": "PASS", "version": fastapi.__version__}
    results["Uvicorn"] = {"status": "PASS", "version": uvicorn.__version__}
except Exception as e:
    results["FastAPI"] = {"status": "FAIL", "error": str(e)}

# 6. React & Vite
try:
    pkg_path = Path("Student_OS/frontend/package.json")
    if pkg_path.exists():
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
        react_v = pkg.get("dependencies", {}).get("react", "unknown")
        vite_v = pkg.get("devDependencies", {}).get("vite", "unknown")
        results["React"] = {"status": "PASS", "version": react_v}
        results["Vite"] = {"status": "PASS", "version": vite_v}
    else:
        results["React"] = {"status": "FAIL", "error": "package.json not found"}
except Exception as e:
    results["React"] = {"status": "FAIL", "error": str(e)}

# 7. SQLite
try:
    results["SQLite"] = {
        "status": "PASS",
        "version": sqlite3.sqlite_version,
        "python_module": sqlite3.version
    }
except Exception as e:
    results["SQLite"] = {"status": "FAIL", "error": str(e)}

# 8. Playwright
try:
    import playwright
    results["Playwright"] = {"status": "PASS", "version": playwright.__version__}
except Exception as e:
    results["Playwright"] = {"status": "FAIL", "error": str(e)}

# 9. Gemini CLI
try:
    res = subprocess.run(["gemini", "--version"], capture_output=True, text=True, shell=True)
    if res.returncode == 0 and res.stdout.strip():
        results["Gemini_CLI"] = {"status": "PASS", "version": res.stdout.strip()}
    else:
        # Check if agy CLI exists
        res_agy = subprocess.run(["agy", "--version"], capture_output=True, text=True, shell=True)
        if res_agy.returncode == 0:
            results["Gemini_CLI"] = {"status": "PARTIAL", "version": f"agy {res_agy.stdout.strip()} (gemini cli binary not in PATH)"}
        else:
            results["Gemini_CLI"] = {"status": "FAIL — NOT INSTALLED", "details": "gemini binary not found in PATH"}
except Exception as e:
    results["Gemini_CLI"] = {"status": "FAIL — NOT INSTALLED", "error": str(e)}

# 10. Gemini API Configuration
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if api_key:
    results["Gemini_API_Config"] = {
        "status": "PASS",
        "details": f"Configured (length: {len(api_key)}, starts with {api_key[:4]}...)"
    }
else:
    results["Gemini_API_Config"] = {
        "status": "FAIL — NOT CONFIGURED",
        "details": "Neither GEMINI_API_KEY nor GOOGLE_API_KEY environment variable is set."
    }

# 11. Antigravity Executable
antigravity_paths = [
    Path(r"C:\Users\Shaunak Rane\AppData\Local\Programs\Antigravity\Antigravity.exe"),
    Path(r"C:\Users\Shaunak Rane\AppData\Local\Programs\Antigravity.exe")
]
antigravity_found = None
for ap in antigravity_paths:
    if ap.exists():
        antigravity_found = ap
        break

if antigravity_found:
    results["Antigravity"] = {
        "status": "PASS",
        "path": str(antigravity_found),
        "size_bytes": antigravity_found.stat().st_size
    }
else:
    # check via where command
    try:
        where_res = subprocess.run(["where", "Antigravity"], capture_output=True, text=True, shell=True)
        if where_res.returncode == 0 and where_res.stdout.strip():
            results["Antigravity"] = {"status": "PASS", "path": where_res.stdout.strip().splitlines()[0]}
        else:
            results["Antigravity"] = {"status": "FAIL — NOT INSTALLED", "details": "Antigravity.exe not found at standard path"}
    except Exception as e:
        results["Antigravity"] = {"status": "FAIL — NOT INSTALLED", "error": str(e)}

# 12. VS Code
try:
    code_res = subprocess.run(["code", "--version"], capture_output=True, text=True, shell=True)
    if code_res.returncode == 0:
        results["VS_Code"] = {"status": "PASS", "version": code_res.stdout.splitlines()[0]}
    else:
        results["VS_Code"] = {"status": "FAIL", "details": "code command returned non-zero"}
except Exception as e:
    results["VS_Code"] = {"status": "FAIL", "error": str(e)}

# 13. Chrome & Chrome CDP
chrome_paths = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"))
]
chrome_found = next((cp for cp in chrome_paths if cp.exists()), None)
if chrome_found:
    results["Chrome"] = {"status": "PASS", "path": str(chrome_found)}
else:
    results["Chrome"] = {"status": "FAIL — NOT INSTALLED"}

# Check Chrome CDP port 9222
try:
    req = urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=2.0)
    cdp_info = json.loads(req.read())
    results["Chrome_CDP"] = {
        "status": "PASS",
        "browser": cdp_info.get("Browser"),
        "webSocketDebuggerUrl": cdp_info.get("webSocketDebuggerUrl", "")[:40] + "..."
    }
except Exception as e:
    results["Chrome_CDP"] = {
        "status": "FAIL — PORT 9222 INACTIVE",
        "details": f"No active Chrome CDP session on port 9222 ({e})"
    }

# 14. ntfy Notification Mechanism
try:
    sys.path.insert(0, str(Path("Student_OS/backend").resolve()))
    from app.config import settings
    topic = settings.NTFY_TOPIC
    # Send test ping
    ntfy_url = f"https://ntfy.sh/{topic}"
    test_req = urllib.request.Request(
        ntfy_url,
        data="[AUDIT] Environment verification ping".encode("utf-8"),
        headers={"Title": "Student OS Environment Audit", "Priority": "1"}
    )
    with urllib.request.urlopen(test_req, timeout=5.0) as resp:
        if resp.getcode() == 200:
            results["ntfy_Notification"] = {
                "status": "PASS (NETWORK DELIVERY VERIFIED; DEVICE RECEIPT NOT DIRECTLY VERIFIABLE)",
                "topic": topic,
                "http_status": resp.getcode()
            }
        else:
            results["ntfy_Notification"] = {"status": "FAIL", "http_status": resp.getcode()}
except Exception as e:
    results["ntfy_Notification"] = {"status": "FAIL", "error": str(e)}

out_file = Path("Student_OS/logs/env_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== ENVIRONMENT TEST RESULTS ===")
for k, v in results.items():
    print(f"{k}: {v.get('status')} | {v.get('version') or v.get('details') or v.get('path') or v.get('error') or ''}")
