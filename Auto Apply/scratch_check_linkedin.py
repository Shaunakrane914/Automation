import os
import time
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto("https://www.linkedin.com/feed/", wait_until="load", timeout=30000)
    time.sleep(3)
    
    print("LinkedIn current URL:", page.url)
    screenshot_path = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\linkedin_check_live.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    
    if "login" in page.url or "checkpoint" in page.url:
        print("Not logged in yet. Attempting login...")
        page.goto("https://www.linkedin.com/login", wait_until="load", timeout=30000)
        time.sleep(2)
        try:
            page.fill("#username", "shaunakrane914@gmail.com")
            time.sleep(0.5)
            page.fill("#password", "Shaunak34@ra")
            time.sleep(0.5)
            page.click("button[type='submit']")
            time.sleep(5)
            print("After submit URL:", page.url)
            page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\linkedin_after_login_attempt.png")
        except Exception as e:
            print("Login fill error:", e)
    else:
        print("Already logged in to LinkedIn!")
        
    browser.close()
