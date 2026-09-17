import time
import os
import sys
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
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    try:
        page.locator("#onetrust-accept-btn-handler, button:has-text('Accept All Cookies')").first.click(timeout=1500)
        time.sleep(1)
    except Exception:
        pass

    email_inp = page.locator("input[type='email'], input[name='__email']").first
    if email_inp.is_visible(timeout=3000):
        email_inp.fill("shaunakrane914@gmail.com")
        time.sleep(1)
        cont_btn = page.locator("button[type='submit']").first
        cont_btn.scroll_into_view_if_needed()
        cont_btn.click()
        print("Clicked continue button. Waiting for next screen...")

        # Wait up to 15 seconds for url change or password/code input or code button
        for i in range(15):
            time.sleep(1)
            # Check if "Sign in with a code" or password or code box appeared
            found = False
            for selector in [
                "a:has-text('Sign in with a code')",
                "button:has-text('Sign in with a code')",
                "input[type='password']",
                "text=/enter code/i",
                "text=/sign in with login code/i"
            ]:
                if page.locator(selector).first.is_visible():
                    print(f"Detected screen element: {selector} after {i+1}s")
                    found = True
                    break
            if found:
                break

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "screen_after_wait.png"))
    print("URL after wait:", page.url)

    # If code button visible, click it!
    code_btn = page.locator("a:has-text('Sign in with a code'), button:has-text('Sign in with a code')").first
    if code_btn.is_visible():
        print("Clicking 'Sign in with a code'...")
        code_btn.click()
        time.sleep(5)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "final_code_screen.png"))
    print("Final screen shot saved to final_code_screen.png")
    context.close()
