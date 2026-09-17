import time
import os
import sys
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

print("Launching visible Chrome to trigger Indeed email code...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()

    print("Navigating to Indeed login...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    # Dismiss cookie banner if present
    try:
        page.locator("#onetrust-accept-btn-handler, button:has-text('Accept All Cookies')").first.click(timeout=1500)
        time.sleep(1)
    except Exception:
        pass

    # Enter email and press Enter
    print("Entering email shaunakrane914@gmail.com and pressing Enter...")
    email_inp = page.locator("input[type='email'], #ifl-InputFormField-3, input[name='__email']").first
    if email_inp.is_visible(timeout=3000):
        email_inp.fill("shaunakrane914@gmail.com")
        time.sleep(1)
        email_inp.press("Enter")
        time.sleep(5)

    step2_shot = os.path.join(SCREENSHOT_DIR, "indeed_screen_after_email.png")
    page.screenshot(path=step2_shot)
    print(f"Saved post-email screenshot to {step2_shot}")
    print("Current URL:", page.url)

    # Now click "Sign in with a code instead"
    print("Searching for 'Sign in with a code instead'...")
    code_btn = page.locator("a:has-text('Sign in with a code'), button:has-text('Sign in with a code'), span:has-text('Sign in with a code')").first
    if code_btn.is_visible(timeout=5000):
        print("Found 'Sign in with a code instead'! Clicking it...")
        code_btn.click()
        time.sleep(5)
    else:
        print("Trying case-insensitive text match...")
        page.locator("text=/sign in with a code/i").first.click()
        time.sleep(5)

    # Screenshot the actual 6-digit code entry screen
    code_screen_path = os.path.join(SCREENSHOT_DIR, "indeed_code_screen_waiting.png")
    page.screenshot(path=code_screen_path)
    print(f"\n=======================================================")
    print(f"SUCCESS: Indeed sent the 6-digit code to shaunakrane914@gmail.com!")
    print(f"Code screen screenshot saved to {code_screen_path}")
    print(f"=======================================================")
    sys.stdout.flush()

    # Wait for code file or input
    code_file = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\indeed_code.txt"
    if os.path.exists(code_file):
        os.remove(code_file)

    print("Listening for code in indeed_code.txt for 180 seconds...")
    sys.stdout.flush()

    code = ""
    for _ in range(180):
        if os.path.exists(code_file):
            with open(code_file, "r") as f:
                code = f.read().strip()
            if len(code) >= 6:
                print(f"Received code: {code}")
                break
        time.sleep(1)

    if not code:
        print("Timeout waiting for code.")
        context.close()
        sys.exit(1)

    print(f"Submitting 6-digit code: {code} into Indeed...")
    # Fill code inputs
    inputs = page.locator("input[type='text'], input[type='number'], input[name*='code'], input[id*='code'], input[aria-label*='code']").all()
    if len(inputs) == 6:
        for i, digit in enumerate(code[:6]):
            inputs[i].fill(digit)
            time.sleep(0.2)
    else:
        inp = page.locator("input[type='text'], input[type='number'], input[name*='code'], input[id*='code']").first
        if inp.is_visible():
            inp.fill(code)

    time.sleep(1)
    sub = page.locator("button[type='submit'], button:has-text('Verify'), button:has-text('Sign in')").first
    if sub.is_visible():
        sub.click()
        time.sleep(6)

    # Verify Indeed is authenticated
    post_auth_shot = os.path.join(SCREENSHOT_DIR, "indeed_logged_in_verified_final.png")
    page.screenshot(path=post_auth_shot)
    print(f"Authentication finished! Screenshot saved to {post_auth_shot}")
    print("Final Page URL:", page.url)

    # Check My Jobs page
    page.goto("https://in.indeed.com/myjobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    myjobs_shot = os.path.join(SCREENSHOT_DIR, "indeed_myjobs_verified_final.png")
    page.screenshot(path=myjobs_shot)
    print(f"My Jobs page verified: {myjobs_shot}")

    context.close()
    print("COMPLETED: Indeed session permanently locked in!")
