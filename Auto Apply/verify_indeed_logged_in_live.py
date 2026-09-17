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
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()

    print("Navigating to https://in.indeed.com/myjobs ...")
    page.goto("https://in.indeed.com/myjobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    myjobs_shot = os.path.join(SCREENSHOT_DIR, "indeed_authenticated_myjobs_confirmed.png")
    page.screenshot(path=myjobs_shot)
    print(f"Screenshot saved: {myjobs_shot}")
    print("Current URL:", page.url)

    # Check for user profile or sign out or myjobs content
    content = page.content()
    is_logged_in = "Sign in" not in page.locator("header, nav").inner_text() if page.locator("header, nav").count() > 0 else False
    print("Is Logged In Header check:", is_logged_in)
    
    context.close()
