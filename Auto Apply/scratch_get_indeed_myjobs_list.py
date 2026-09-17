import time
import os
import sqlite3
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"
DB_PATH = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Student_OS\backend\student_os.db"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        viewport={"width": 1280, "height": 720}
    )
    page = context.pages[0] if context.pages else context.new_page()

    print("Loading https://myjobs.indeed.com/applied ...")
    page.goto("https://myjobs.indeed.com/applied", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    # Screenshot full view of applied jobs
    shot_path = os.path.join(SCREENSHOT_DIR, "indeed_verified_myjobs_dashboard.png")
    page.screenshot(path=shot_path)
    print(f"Captured dashboard shot: {shot_path}")

    # Extract applied job cards
    # Each applied card has job title and company
    cards = page.locator("header.atw-JobInfo, div[data-testid='job-card']").all()
    print(f"Found {len(cards)} applied job elements on page")

    extracted_jobs = []
    # Let's inspect headers
    headers = page.locator("header.atw-JobInfo").all()
    for h in headers[:10]:
        try:
            txt = h.inner_text().strip()
            lines = [line.strip() for line in txt.split("\n") if line.strip()]
            print("Job card lines:", lines)
            # Example: ['Applied', 'Associate AI Engineer Intern — Agentic AI', 'Logikwerk Pvt Ltd', 'Remote', 'Applied on Indeed on Tuesday']
            if len(lines) >= 3:
                role = lines[1] if lines[0].lower() == 'applied' else lines[0]
                company = lines[2] if lines[0].lower() == 'applied' else lines[1]
                extracted_jobs.append((role, company))
        except Exception as e:
            print("Error parsing header:", e)

    print("Extracted real applied jobs:", extracted_jobs)

    context.close()
