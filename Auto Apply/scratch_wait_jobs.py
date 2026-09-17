import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized"],
        viewport={"width": 1280, "height": 720}
    )
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://in.indeed.com/jobs?q=AI+intern&l=Remote", wait_until="domcontentloaded", timeout=30000)
    
    print("Waiting 12 seconds to see if jobs page loads...")
    for i in range(12):
        time.sleep(1)
        cards = page.locator("div.cardOutline, div.job_seen_beacon, td.resultContent").count()
        print(f"Sec {i+1}: URL={page.url} | Cards={cards}")
        if cards > 0:
            print("Found job cards!")
            break

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "jobs_after_wait12.png"))
    context.close()
