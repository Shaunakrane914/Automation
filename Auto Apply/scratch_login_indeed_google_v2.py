import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    print("Launching visible Chrome with persistent profile...")
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    
    page = context.pages[0] if context.pages else context.new_page()

    google_popup = None
    def handle_popup(new_p):
        global google_popup
        print("Popup opened! URL:", new_p.url)
        google_popup = new_p

    context.on("page", handle_popup)

    print("Opening Indeed login...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    # 1. Dismiss cookies banner
    try:
        cookie_btn = page.locator("#onetrust-accept-btn-handler, button:has-text('Accept All Cookies'), button:has-text('Accept')").first
        if cookie_btn.is_visible(timeout=2000):
            print("Accepting cookies...")
            cookie_btn.click()
            time.sleep(1)
    except Exception as e:
        print("Cookie banner note:", e)

    # 2. If 'Continue with Google' is already visible directly on main login
    g_main = page.locator("button:has-text('Continue with Google'), a:has-text('Continue with Google')").first
    if g_main.is_visible(timeout=2000):
        print("Direct 'Continue with Google' visible on login! Clicking it...")
        g_main.click()
        time.sleep(4)
    else:
        # Enter email
        email_inp = page.locator("input[type='email'], #ifl-InputFormField-3, input[name='__email']").first
        if email_inp.is_visible(timeout=2000):
            print("Entering shaunakrane914@gmail.com...")
            email_inp.fill("shaunakrane914@gmail.com")
            time.sleep(1)
            page.locator("button[type='submit']").first.click()
            time.sleep(4)

        # Look for "Continue with Google" after entering email
        g_btn = page.locator("button:has-text('Continue with Google'), a:has-text('Continue with Google'), div[role='button']:has-text('Continue with Google')").first
        if g_btn.is_visible(timeout=4000):
            print("Clicking 'Continue with Google' after email entry...")
            g_btn.click()
            time.sleep(4)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_after_click_google.png"))
    print("Page URL after click:", page.url)

    # Check if popup opened or if page redirected to google accounts
    active_p = google_popup if google_popup else page
    print("Active page URL:", active_p.url)

    if "accounts.google.com" in active_p.url:
        print("Handling Google OAuth on active page...")
        time.sleep(2)
        active_p.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_google_oauth_screen.png"))

        # Look for Shaunak's account or click Next
        acc_div = active_p.locator("div:has-text('shaunakrane914@gmail.com'), div:has-text('Shaunak Rane')").first
        if acc_div.is_visible(timeout=3000):
            print("Clicking Shaunak Rane Google account...")
            acc_div.click()
            time.sleep(5)
        else:
            print("Trying to fill email on Google...")
            try:
                active_p.locator("input[type='email']").fill("shaunakrane914@gmail.com")
                active_p.locator("button:has-text('Next')").click()
                time.sleep(4)
            except Exception as ge:
                print("Google email enter note:", ge)

    # Wait for user or redirect to settle
    print("Holding visible browser open for 15 seconds so session settles or user can complete any Google 2FA...")
    time.sleep(15)

    # Navigate to Indeed home and My Jobs to check logged in status
    print("Navigating to Indeed Home...")
    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_logged_in_home_proof.png"))

    print("Navigating to Indeed My Jobs...")
    page.goto("https://in.indeed.com/myjobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_logged_in_myjobs_proof.png"))

    context.close()
    print("Done!")
