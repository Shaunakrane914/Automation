import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        USER_DATA_DIR,
        headless=False,
        executable_path=CHROME_EXE,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()

    print("Checking Internshala My Applications page...")
    page.goto("https://internshala.com/student/applications", wait_until="domcontentloaded", timeout=25000)
    time.sleep(4)
    print("URL:", page.url)
    page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\internshala_my_applications.png")
    
    # Extract application titles/companies
    rows = page.locator(".application_status, tr.applied_job, tr, .individual_internship")
    print(f"Found {rows.count()} application elements on Internshala")
    
    context.close()
