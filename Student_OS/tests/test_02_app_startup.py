import time
import json
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

results = {
    "backend_status": "PENDING",
    "api_docs_status": "PENDING",
    "frontend_http_status": "PENDING",
    "websocket_status": "PENDING",
    "browser_console_errors": [],
    "browser_failed_requests": [],
    "overall_status": "PENDING"
}

# 1. Backend root & /api/academic/overview
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/academic/overview", timeout=5) as resp:
        results["backend_status"] = f"PASS (HTTP {resp.getcode()})"
except Exception as e:
    results["backend_status"] = f"FAIL ({e})"

# 2. API Docs
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=5) as resp:
        results["api_docs_status"] = f"PASS (HTTP {resp.getcode()})"
except Exception as e:
    results["api_docs_status"] = f"FAIL ({e})"

# 3. Frontend UI & Browser Console/Network Audit
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type in ["error", "warning"] else None)

        failed_requests = []
        page.on("requestfailed", lambda req: failed_requests.append(f"{req.method} {req.url} - {req.failure}"))

        resp = page.goto("http://127.0.0.1:8000/", timeout=10000)
        results["frontend_http_status"] = f"PASS (HTTP {resp.status if resp else 'None'})"

        # Wait for dashboard to settle
        page.wait_for_timeout(3000)

        # Check title and elements
        title = page.title()
        has_title = "Student OS" in title or len(title) > 0

        # Check WebSocket connection pill in UI
        ws_pill = page.locator("text=LIVE FEED")
        is_ws_connected = ws_pill.count() > 0

        results["websocket_status"] = "PASS (LIVE FEED active in UI)" if is_ws_connected else "PARTIAL (STANDBY/Reconnecting)"
        results["browser_console_errors"] = console_errors[:10]
        results["browser_failed_requests"] = failed_requests[:10]

        # Filter severe JS errors (excluding minor dev warnings)
        severe_errors = [e for e in console_errors if "TypeError" in e or "Uncaught" in e or "SyntaxError" in e]
        if severe_errors:
            results["overall_status"] = f"PARTIAL (UI rendered but {len(severe_errors)} JS errors)"
        elif not is_ws_connected:
            results["overall_status"] = "PARTIAL (UI rendered, WS standby)"
        else:
            results["overall_status"] = "PASS"

        browser.close()
except Exception as e:
    results["overall_status"] = f"FAIL ({e})"

out_file = Path("Student_OS/logs/startup_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== APPLICATION STARTUP TEST ===")
print(f"Backend: {results['backend_status']}")
print(f"API Docs: {results['api_docs_status']}")
print(f"Frontend: {results['frontend_http_status']}")
print(f"WebSocket: {results['websocket_status']}")
print(f"Console Errors: {len(results['browser_console_errors'])}")
print(f"Failed Requests: {len(results['browser_failed_requests'])}")
print(f"Overall Status: {results['overall_status']}")
