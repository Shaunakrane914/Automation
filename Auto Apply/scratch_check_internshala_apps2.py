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

    page.goto("https://internshala.com/student/applications", wait_until="domcontentloaded", timeout=25000)
    time.sleep(3)
    page.evaluate("window.scrollBy(0, 800)")
    time.sleep(2)
    page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\internshala_my_applications_scrolled.png")
    
    # Print any table or list text
    text = page.evaluate("() => document.body.innerText")
    for line in text.split("\n"):
        if any(w in line.lower() for w in ["applied", "internship", "company", "status", "basti", "pledge", "hope", "no application"]):
            print("Line:", line.strip())

    context.close()
