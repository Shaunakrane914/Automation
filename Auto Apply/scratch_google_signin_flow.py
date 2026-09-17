import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    print("Launching visible Chrome...")
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        viewport={"width": 1280, "height": 720},
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()

    print("Opening Indeed login...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    # Dismiss cookie banner
    try:
        page.locator("#onetrust-accept-btn-handler").click(timeout=1500)
        time.sleep(1)
    except Exception:
        pass

    print("Clicking Continue with Google at (632, 451)...")
    page.mouse.click(632, 451)

    print("Waiting for navigation to Google Sign In...")
    try:
        page.wait_for_url(lambda u: "accounts.google.com" in u, timeout=15000)
        print("Successfully navigated to Google! URL:", page.url)
    except Exception as e:
        print("wait_for_url note:", e)

    time.sleep(3)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_google_email_prompt.png"))

    # Step 1: Email
    email_input = page.locator("#identifierId, input[type='email']").first
    if email_input.is_visible(timeout=4000):
        print("Entering email shaunakrane914@gmail.com...")
        email_input.fill("shaunakrane914@gmail.com")
        time.sleep(1)
        next_btn = page.locator("#identifierNext, button:has-text('Next')").first
        print("Clicking Next...")
        next_btn.click()
        time.sleep(5)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_google_after_email_next.png"))
    print("After email Next URL:", page.url)

    # Step 2: Password
    pw_input = page.locator("input[name='Passwd'], input[type='password']").first
    if pw_input.is_visible(timeout=5000):
        print("Password input visible! Typing password...")
        pw_input.fill("shaunak43rane")
        time.sleep(1)
        pw_next = page.locator("#passwordNext, button:has-text('Next')").first
        print("Clicking Password Next...")
        pw_next.click()
        time.sleep(6)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_google_after_password_next.png"))
    print("After password Next URL:", page.url)

    # Keep visible browser open for 20 seconds so user can see prompt or complete phone 2FA
    print("Keeping visible Chrome open for 20 seconds so 2FA or OAuth redirect can complete...")
    time.sleep(20)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_final_status.png"))

    # Check Indeed home
    print("Navigating to Indeed Home...")
    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_home_post_google.png"))

    # Check Indeed My Jobs
    print("Navigating to Indeed My Jobs...")
    page.goto("https://in.indeed.com/myjobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_myjobs_post_google.png"))

    context.close()
    print("Execution complete!")
