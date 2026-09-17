import time
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://www.linkedin.com/jobs/", wait_until="load", timeout=30000)
    time.sleep(3)
    
    # Click 'My Jobs'
    my_jobs = page.locator("a:has-text('My Jobs'), button:has-text('My Jobs'), a[href*='/my-items/']").first
    if my_jobs.is_visible(timeout=3000):
        print("Clicking My Jobs...")
        my_jobs.click()
        time.sleep(3)
    else:
        print("Direct navigating to /my-items/...")
        page.goto("https://www.linkedin.com/my-items/", wait_until="load", timeout=30000)
        time.sleep(3)

    print("Current URL:", page.url)
    # Check for 'Applied' tab
    applied_tab = page.locator("button:has-text('Applied'), a:has-text('Applied')").first
    if applied_tab.is_visible(timeout=3000):
        print("Clicking Applied tab...")
        applied_tab.click()
        time.sleep(3)

    shot_path = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\real_linkedin_applied_tab_verified.png"
    page.screenshot(path=shot_path)
    print(f"Captured LinkedIn My Jobs -> Applied to: {shot_path}")
    context.close()
