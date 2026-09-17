import time
import os
import sys
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"
CODE_FILE = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\indeed_code.txt"
READY_FLAG = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\indeed_waiting.flag"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

if os.path.exists(CODE_FILE):
    try:
        os.remove(CODE_FILE)
    except Exception:
        pass
if os.path.exists(READY_FLAG):
    try:
        os.remove(READY_FLAG)
    except Exception:
        pass

print("Starting Indeed Code Flow in visible Chrome...")
sys.stdout.flush()

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()

    print("Navigating to https://in.indeed.com/account/login ...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    try:
        page.locator("#onetrust-accept-btn-handler, button:has-text('Accept All Cookies')").first.click(timeout=1500)
        time.sleep(1)
    except Exception:
        pass

    # Check if already on code screen
    if not page.locator("text=/sign in with login code/i").first.is_visible():
        email_inp = page.locator("input[type='email'], input[name='__email']").first
        if email_inp.is_visible(timeout=3000):
            print("Filling shaunakrane914@gmail.com...")
            email_inp.fill("shaunakrane914@gmail.com")
            time.sleep(1)
            cont_btn = page.locator("button[type='submit']").first
            cont_btn.scroll_into_view_if_needed()
            cont_btn.click()
            print("Clicked Continue button. Waiting for next step...")

            for _ in range(15):
                time.sleep(1)
                if page.locator("a:has-text('Sign in with a code'), button:has-text('Sign in with a code')").first.is_visible():
                    break
                if page.locator("text=/sign in with login code/i").first.is_visible():
                    break

            code_btn = page.locator("a:has-text('Sign in with a code'), button:has-text('Sign in with a code')").first
            if code_btn.is_visible():
                print("Clicking 'Sign in with a code'...")
                code_btn.click()
                time.sleep(4)

    # Now verify we are on the code entry screen
    code_screen_shot = os.path.join(SCREENSHOT_DIR, "indeed_waiting_for_user_code.png")
    page.screenshot(path=code_screen_shot)
    print(f"Code screen screenshot saved to: {code_screen_shot}")
    print("Page URL:", page.url)

    # Signal ready
    with open(READY_FLAG, "w") as f:
        f.write("WAITING_FOR_CODE")

    print("\n=======================================================")
    print("INDEED IS WAITING FOR 6-DIGIT CODE FROM GMAIL!")
    print(f"Waiting for code in {CODE_FILE} (timeout: 600s)...")
    print("=======================================================")
    sys.stdout.flush()

    user_code = ""
    for _ in range(600):
        if os.path.exists(CODE_FILE):
            try:
                with open(CODE_FILE, "r") as f:
                    c = f.read().strip()
                if len(c) >= 6:
                    user_code = c[:6]
                    print(f"Detected code from file: {user_code}")
                    break
            except Exception:
                pass
        time.sleep(1)

    if not user_code:
        print("Timeout waiting for user code.")
        context.close()
        sys.exit(1)

    print(f"Typing 6-digit code: {user_code} into Indeed...")
    # The input box on this screen is named or tagged
    inp = page.locator("input[type='text'], input[type='number'], input[name*='code'], input[id*='code']").first
    if inp.is_visible(timeout=3000):
        inp.scroll_into_view_if_needed()
        inp.fill(user_code)
        time.sleep(1)
        inp.press("Enter")

    time.sleep(1)
    # Scroll down and click submit if still present
    page.evaluate("window.scrollBy(0, 300)")
    time.sleep(1)
    sub = page.locator("button[type='submit'], button:has-text('Sign in'), button:has-text('Verify')").first
    if sub.is_visible(timeout=2000):
        sub.click()

    time.sleep(7)

    result_shot = os.path.join(SCREENSHOT_DIR, "indeed_post_login_result.png")
    page.screenshot(path=result_shot)
    print(f"Saved post login result: {result_shot}")
    print("Post-auth URL:", page.url)

    # Navigate to My Jobs to confirm authenticated state
    print("Verifying session on https://in.indeed.com/myjobs ...")
    page.goto("https://in.indeed.com/myjobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    myjobs_shot = os.path.join(SCREENSHOT_DIR, "indeed_authenticated_myjobs.png")
    page.screenshot(path=myjobs_shot)
    print(f"My Jobs verified and saved to: {myjobs_shot}")

    if os.path.exists(READY_FLAG):
        try:
            os.remove(READY_FLAG)
        except Exception:
            pass

    context.close()
    print("SUCCESS: Indeed authentication permanently completed!")
