import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"

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

    # Fill email
    email_inp = page.locator("input[type='email'], input[name='__email']").first
    email_inp.fill("shaunakrane914@gmail.com")
    time.sleep(1)

    # Scroll down to reveal buttons
    page.evaluate("window.scrollBy(0, 400)")
    time.sleep(1)

    # Find buttons
    buttons = page.locator("button").all()
    print(f"Total buttons: {len(buttons)}")
    for i, btn in enumerate(buttons):
        try:
            print(f"Button {i}: text='{btn.text_content().strip()}' is_visible={btn.is_visible()}")
        except Exception:
            pass

    # Try clicking the Continue button specifically
    cont_btn = page.locator("button[type='submit']").first
    if cont_btn.is_visible():
        print("Clicking submit button...")
        cont_btn.click()
    else:
        print("Submit button not visible, scrolling into view...")
        cont_btn.scroll_into_view_if_needed()
        cont_btn.click()

    time.sleep(5)
    page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\after_submit_click.png")
    print("New URL:", page.url)

    # Check for 'Sign in with a code'
    code_links = page.locator("a, button").all()
    for l in code_links:
        try:
            txt = l.text_content().strip()
            if "code" in txt.lower():
                print(f"Found code element: text='{txt}'")
                l.click()
                time.sleep(4)
                break
        except Exception:
            pass

    page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\after_code_link_click.png")
    context.close()
