import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()

    print("Navigating to login page...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    # Accept cookies
    try:
        page.locator("#onetrust-accept-btn-handler, button:has-text('Accept All Cookies')").first.click(timeout=2000)
        time.sleep(1)
    except Exception:
        pass

    email_input = page.locator("input[type='email'], input[name='__email'], #ifl-InputFormField-3").first
    if email_input.is_visible(timeout=3000):
        print("Found email input. Filling shaunakrane914@gmail.com...")
        email_input.fill("shaunakrane914@gmail.com")
        time.sleep(1)

        # Look for the Continue button
        continue_btn = page.locator("button[type='submit'], button:has-text('Continue')").first
        if continue_btn.is_visible(timeout=2000):
            print("Clicking Continue button...")
            continue_btn.click()
        else:
            print("Continue button not directly visible, pressing Enter...")
            email_input.press("Enter")
        
        time.sleep(5)

    shot1 = os.path.join(SCREENSHOT_DIR, "step1_after_email_continue.png")
    page.screenshot(path=shot1)
    print(f"Step 1 screenshot: {shot1}, URL: {page.url}")

    # Now look for "Sign in with a code instead" or password / code screen
    print("Page title/url:", page.title(), page.url)
    
    # Check all buttons and links
    links = page.locator("a, button").all_inner_texts()
    print("Available buttons/links:", [t.strip() for t in links if t.strip()][:25])

    code_btn = page.locator("a:has-text('Sign in with a code'), button:has-text('Sign in with a code')").first
    if code_btn.is_visible(timeout=5000):
        print("Found code button! Clicking it...")
        code_btn.click()
        time.sleep(5)
    else:
        print("Searching with regex...")
        try:
            page.locator("text=/sign in with a code/i").first.click(timeout=5000)
            time.sleep(5)
        except Exception as e:
            print("Regex click error:", e)

    shot2 = os.path.join(SCREENSHOT_DIR, "step2_after_code_click.png")
    page.screenshot(path=shot2)
    print(f"Step 2 screenshot: {shot2}")

    context.close()
