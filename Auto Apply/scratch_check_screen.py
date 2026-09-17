import time
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized"]
    )
    page = context.pages[0]
    page.goto("https://in.indeed.com/account/login", wait_until="commit", timeout=20000)
    time.sleep(5)
    page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\indeed_current_actual_screen.png")
    print("Current URL:", page.url)
    print("Page Title:", page.title())
    body = page.evaluate("() => document.body ? document.body.innerText : 'NO BODY'")
    print("Body snippet:", body[:200])
    context.close()
