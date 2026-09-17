import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    print("Launching visible Chrome to log in to Indeed via Google...")
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    
    page = context.pages[0] if context.pages else context.new_page()
    
    popup_page = None
    def on_new_page(new_p):
        global popup_page
        print("Popup opened:", new_p.url)
        popup_page = new_p

    context.on("page", on_new_page)

    print("Navigating to Indeed login...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    # First screenshot
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_step1_login_page.png"))
    print("Current URL:", page.url)

    # If email input is shown, type email
    email_input = page.locator("input[type='email'], #ifl-InputFormField-3, input[name='__email']").first
    if email_input.is_visible(timeout=2000):
        print("Typing email shaunakrane914@gmail.com...")
        email_input.fill("shaunakrane914@gmail.com")
        time.sleep(1)
        sub = page.locator("button[type='submit']").first
        if sub.is_visible():
            sub.click()
            time.sleep(4)

    # Look for "Continue with Google"
    print("Looking for 'Continue with Google' button...")
    g_btn = page.locator("button:has-text('Continue with Google'), a:has-text('Continue with Google'), [data-testid='continue-with-google'], div[role='button']:has-text('Continue with Google')").first
    
    if g_btn.is_visible(timeout=3000):
        print("Clicking 'Continue with Google'...")
        g_btn.click()
        time.sleep(4)
    else:
        # Check if inside an iframe or Google One Tap
        print("Checking if Google button is inside iframe...")
        frames = page.frames
        clicked_iframe = False
        for f in frames:
            try:
                btn = f.locator("button:has-text('Continue with Google'), div[role='button']:has-text('Continue as'), [id*='google']").first
                if btn.is_visible(timeout=1000):
                    print("Found Google button in frame, clicking...")
                    btn.click()
                    clicked_iframe = True
                    time.sleep(4)
                    break
            except Exception:
                pass
        if not clicked_iframe:
            print("Trying generic click by text...")
            txt_el = page.locator("text='Continue with Google'").first
            if txt_el.is_visible(timeout=1000):
                txt_el.click()
                time.sleep(4)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_step2_after_google_click.png"))
    print("After Google click URL:", page.url)

    # Check if a popup opened or page redirected to google accounts
    target_page = popup_page if popup_page else page
    print(f"Target page URL: {target_page.url}")

    if "accounts.google.com" in target_page.url:
        print("Handling Google OAuth page/popup...")
        time.sleep(2)
        target_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_step3_google_oauth.png"))
        
        # Check if Shaunak's account card is visible
        acc_choice = target_page.locator("text='shaunakrane914@gmail.com', div:has-text('shaunakrane914@gmail.com'), div:has-text('Shaunak Rane')").first
        if acc_choice.is_visible(timeout=3000):
            print("Clicking Shaunak Rane Google account card...")
            acc_choice.click()
            time.sleep(5)
        else:
            # Enter email if prompted
            g_email = target_page.locator("input[type='email']").first
            if g_email.is_visible(timeout=2000):
                print("Entering Google email...")
                g_email.fill("shaunakrane914@gmail.com")
                target_page.locator("button:has-text('Next')").first.click()
                time.sleep(4)

    # Wait for redirect back to indeed
    print("Waiting 10 seconds for Indeed authentication to settle...")
    time.sleep(10)

    # Final check
    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_step4_final_home.png"))
    print("Final Indeed Home URL:", page.url)

    # Check My Jobs page
    page.goto("https://in.indeed.com/myjobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_step5_myjobs.png"))
    print("Indeed My Jobs URL:", page.url)

    context.close()
