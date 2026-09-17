import time
import subprocess
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

# Launch Chrome via standalone subprocess with remote debugging port
cmd = [
    CHROME_EXE,
    f"--user-data-dir={PROFILE_DIR}",
    "--remote-debugging-port=9222",
    "--start-maximized",
    "--no-first-run",
    "--no-default-browser-check"
]

print("Launching standalone Chrome process...")
proc = subprocess.Popen(cmd)
time.sleep(3)

try:
    with sync_playwright() as p:
        print("Connecting over CDP to http://localhost:9222 ...")
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]
        page = default_context.pages[0] if default_context.pages else default_context.new_page()

        print("Navigating to https://in.indeed.com/jobs?q=AI+intern+remote&l=Remote ...")
        page.goto("https://in.indeed.com/jobs?q=AI+intern+remote&l=Remote", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        shot = os.path.join(SCREENSHOT_DIR, "cdp_standalone_search_result.png")
        page.screenshot(path=shot)
        print(f"CDP Screenshot: {shot}")
        print("URL:", page.url)

        # Check job cards
        cards = page.locator("div.cardOutline, div.job_seen_beacon").all()
        print(f"Total job cards found: {len(cards)}")
        for i, c in enumerate(cards[:5]):
            try:
                print(f"[{i}] {c.inner_text()[:100].replace(chr(10), ' | ')}")
            except Exception:
                pass

        browser.close()
finally:
    proc.terminate()
