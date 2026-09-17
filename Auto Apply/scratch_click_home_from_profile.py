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

    print("Going to profile...")
    page.goto("https://profile.indeed.com/", wait_until="domcontentloaded")
    time.sleep(3)

    print("Clicking 'Home' in navigation header...")
    home_link = page.locator("a:has-text('Home'), a[data-gnav-element='primary-logo']").first
    home_link.click()
    time.sleep(5)

    shot = os.path.join(SCREENSHOT_DIR, "indeed_home_from_profile.png")
    page.screenshot(path=shot)
    print("New URL:", page.url)
    print("Content preview:", page.inner_text("body")[:200].replace(chr(10), " | "))

    context.close()
