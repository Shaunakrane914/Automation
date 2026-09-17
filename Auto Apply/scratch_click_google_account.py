import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    print("Launching visible Chrome to authenticate Indeed via Google account clicker...")
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    
    page = context.pages[0] if context.pages else context.new_page()

    google_tab = None
    def on_new_page(new_p):
        global google_tab
        print(f"\n>>> New browser tab opened! URL: {new_p.url}")
        google_tab = new_p

    context.on("page", on_new_page)

    print("Navigating to Indeed login...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    # Accept cookie banner if present
    try:
        cookie_btn = page.locator("#onetrust-accept-btn-handler, button:has-text('Accept All Cookies')").first
        if cookie_btn.is_visible(timeout=1500):
            cookie_btn.click()
            time.sleep(1)
    except Exception:
        pass

    # Click Continue with Google
    g_btn = page.locator("div[role='button']:has-text('Continue with Google'), #button-label, span:has-text('Continue with Google')").first
    print("Clicking 'Continue with Google' button...")
    g_btn.click()
    time.sleep(4)

    # If google_tab opened, interact with it
    active_tab = google_tab if google_tab else page
    print(f"Active authentication tab URL: {active_tab.url}")
    
    time.sleep(3)
    shot1 = os.path.join(SCREENSHOT_DIR, "indeed_google_tab_initial.png")
    active_tab.screenshot(path=shot1)
    print(f"Saved initial Google tab screenshot: {shot1}")

    # Check for Shaunak's account card in Google account chooser
    print("Looking for Shaunak Rane / shaunakrane914@gmail.com account chooser...")
    account_card = active_tab.locator("div:has-text('shaunakrane914@gmail.com'), li:has-text('shaunakrane914@gmail.com'), div:has-text('Shaunak Rane')").first
    
    if account_card.is_visible(timeout=4000):
        print("Found Shaunak Rane account card! Clicking it now...")
        account_card.click()
        time.sleep(5)
    else:
        # Check if email input field is present
        email_inp = active_tab.locator("input[type='email']").first
        if email_inp.is_visible(timeout=2000):
            print("Typing shaunakrane914@gmail.com into Google login...")
            email_inp.fill("shaunakrane914@gmail.com")
            time.sleep(1)
            active_tab.locator("button:has-text('Next')").first.click()
            time.sleep(4)

    # Check if password is requested
    pw_inp = active_tab.locator("input[type='password']").first
    if pw_inp.is_visible(timeout=3000):
        print("Password prompt detected! Entering password...")
        pw_inp.fill("shaunak43rane")
        time.sleep(1)
        next_btn = active_tab.locator("button:has-text('Next')").first
        if next_btn.is_visible():
            next_btn.click()
            time.sleep(5)

    shot2 = os.path.join(SCREENSHOT_DIR, "indeed_google_tab_after_action.png")
    active_tab.screenshot(path=shot2)
    print(f"Saved post-action Google tab screenshot: {shot2}")

    # Keep visible browser open for 15 seconds to let OAuth redirect complete or allow user to tap prompt on phone if Google asks
    print("\nKeeping visible Chrome open for 15 seconds for OAuth redirect to finish...")
    time.sleep(15)

    # Verify on Indeed Home and My Jobs
    print("Navigating to Indeed Home to verify session...")
    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    shot_home = os.path.join(SCREENSHOT_DIR, "indeed_logged_in_home_verified.png")
    page.screenshot(path=shot_home)
    print(f"Saved home verification: {shot_home}")

    print("Navigating to Indeed My Jobs...")
    page.goto("https://in.indeed.com/myjobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    shot_myjobs = os.path.join(SCREENSHOT_DIR, "indeed_myjobs_verified.png")
    page.screenshot(path=shot_myjobs)
    print(f"Saved My Jobs verification: {shot_myjobs}")

    context.close()
    print("Execution complete!")
