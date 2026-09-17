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

    print("Navigating to https://www.indeed.com/ ...")
    page.goto("https://www.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    shot = os.path.join(SCREENSHOT_DIR, "indeed_us_home.png")
    page.screenshot(path=shot)
    print("US URL:", page.url)

    context.close()
