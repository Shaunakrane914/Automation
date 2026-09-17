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

    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    print("Initial URL:", page.url)

    # Wait up to 10 seconds to see if Turnstile auto-passes
    for i in range(10):
        time.sleep(1)
        print(f"Second {i+1}, URL: {page.url}")
        if "challenge" not in page.url and "Verification Required" not in page.content():
            print("Turnstile passed automatically!")
            break

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "turnstile_after_10s.png"))

    # Also check what happens if we navigate to https://myjobs.indeed.com/
    print("Navigating to https://myjobs.indeed.com/ ...")
    page.goto("https://myjobs.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "turnstile_myjobs_test.png"))
    print("MyJobs URL:", page.url)

    # From My Jobs, what links exist?
    find_jobs_btn = page.locator("a:has-text('Find jobs'), a:has-text('Home')").first
    if find_jobs_btn.is_visible():
        print("Clicking Find jobs from inside logged-in My Jobs...")
        find_jobs_btn.click()
        time.sleep(5)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "after_find_jobs_from_myjobs.png"))
        print("URL after Find jobs click:", page.url)

    context.close()
