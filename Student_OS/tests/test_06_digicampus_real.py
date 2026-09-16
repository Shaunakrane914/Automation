import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

results = {
    "cdp_connection": "PENDING",
    "session_state": "PENDING",
    "enrolled_subjects_count": 0,
    "subjects": [],
    "audit_success": False,
    "error": None
}

async def audit_digicampus():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            results["cdp_connection"] = "PASS"
            context = browser.contexts[0]

            # Look for existing digi tab or open one
            digi_page = None
            for pg in context.pages:
                if "digiicampus.com" in pg.url:
                    digi_page = pg
                    break

            if not digi_page:
                digi_page = await context.new_page()
                await digi_page.goto("https://uai.digiicampus.com", wait_until="domcontentloaded", timeout=15000)
                await digi_page.wait_for_timeout(3000)

            current_url = digi_page.url
            results["url"] = current_url

            # Check if login page or authenticated portal
            if "login" in current_url or "#/login" in current_url or "registrationId" in await digi_page.content():
                results["session_state"] = "FAIL — AUTHENTICATION SESSION EXPIRED / NOT LOGGED IN"
                results["error"] = "Browser redirected to login screen. Active authenticated session not present."
                # Take screenshot to verify
                screenshot_path = Path("Student_OS/logs/digicampus_session_state.png")
                await digi_page.screenshot(path=str(screenshot_path))
                results["screenshot"] = str(screenshot_path)
            else:
                # We are in the portal! Verify classroom
                await digi_page.goto("https://uai.digiicampus.com/V2/#/classroom", wait_until="domcontentloaded", timeout=15000)
                await digi_page.wait_for_timeout(3000)
                
                # Check for courses
                course_cards = await digi_page.locator(".course-card, .classroom-card, .ant-card").all()
                results["session_state"] = "PASS (Authenticated)"
                results["enrolled_subjects_count"] = len(course_cards)
                results["audit_success"] = True

        except Exception as e:
            results["session_state"] = f"FAIL ({e})"
            results["error"] = str(e)

    out_file = Path("Student_OS/logs/digicampus_audit.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("=== DIGICAMPUS REAL-WORLD TEST ===")
    print("CDP Connection:", results["cdp_connection"])
    print("Session State:", results["session_state"])
    print("Error:", results["error"])

if __name__ == "__main__":
    asyncio.run(audit_digicampus())
