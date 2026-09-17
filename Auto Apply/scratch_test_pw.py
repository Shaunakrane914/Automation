import time
from playwright.sync_api import sync_playwright

user_data_dir = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    try:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            executable_path=chrome_exe,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://internshala.com/student/dashboard", timeout=20000)
        time.sleep(3)
        print("Playwright Internshala URL:", page.url)
        print("Playwright Internshala Title:", page.title())
        page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\pw_internshala_test.png")

        page.goto("https://www.linkedin.com/feed/", timeout=20000)
        time.sleep(3)
        print("Playwright LinkedIn URL:", page.url)
        print("Playwright LinkedIn Title:", page.title())
        page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\pw_linkedin_test.png")

        context.close()
    except Exception as e:
        print("Playwright test error:", e)
