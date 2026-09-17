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

    print("Navigating to Indeed login...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    # Dismiss cookie banner
    try:
        cookie_btn = page.locator("#onetrust-accept-btn-handler, button:has-text('Accept All Cookies')").first
        if cookie_btn.is_visible(timeout=1500):
            cookie_btn.click()
            time.sleep(1)
    except Exception:
        pass

    # Click Continue with Google with expect_popup
    print("Clicking 'Continue with Google' and capturing popup...")
    with page.expect_popup() as popup_info:
        page.locator("div[role='button']:has-text('Continue with Google'), #button-label").first.click()
    
    popup = popup_info.value
    print("Popup captured! Initial URL:", popup.url)
    time.sleep(4)
    print("Popup URL after wait:", popup.url)

    shot1 = os.path.join(SCREENSHOT_DIR, "indeed_google_popup_screen.png")
    popup.screenshot(path=shot1)
    print(f"Saved popup screenshot: {shot1}")

    # Inspect popup elements
    els = popup.evaluate("""() => {
        return Array.from(document.querySelectorAll('div, li, span, button'))
            .map(e => (e.innerText || '').trim())
            .filter(t => t.includes('shaunak') || t.includes('Shaunak') || t.includes('Use another account') || t.includes('Next'));
    }""")
    print("Matching text in Google popup:", els[:10])

    # Check for Shaunak's account card or email
    acc = popup.locator("div:has-text('shaunakrane914@gmail.com'), li:has-text('shaunakrane914@gmail.com'), div:has-text('Shaunak Rane')").first
    if acc.is_visible(timeout=3000):
        print("Clicking Shaunak Rane account card in Google popup...")
        acc.click()
        time.sleep(6)
    else:
        # Check if email field
        email_inp = popup.locator("input[type='email']").first
        if email_inp.is_visible(timeout=2000):
            print("Typing shaunakrane914@gmail.com in Google popup...")
            email_inp.fill("shaunakrane914@gmail.com")
            time.sleep(1)
            popup.locator("button:has-text('Next')").first.click()
            time.sleep(4)

    # Check if password
    pw_inp = popup.locator("input[type='password']").first
    if pw_inp.is_visible(timeout=2500):
        print("Entering password in Google popup...")
        pw_inp.fill("shaunak43rane")
        time.sleep(1)
        popup.locator("button:has-text('Next')").first.click()
        time.sleep(5)

    shot2 = os.path.join(SCREENSHOT_DIR, "indeed_google_popup_after_click.png")
    try:
        popup.screenshot(path=shot2)
        print(f"Saved post-click popup screenshot: {shot2}")
    except Exception as e:
        print("Popup may have closed after successful login:", e)

    print("Waiting 10 seconds for Indeed authentication redirect...")
    time.sleep(10)

    # Check main page URL and profile
    print("Main page current URL:", page.url)
    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    shot_home = os.path.join(SCREENSHOT_DIR, "indeed_home_after_google_auth.png")
    page.screenshot(path=shot_home)
    print(f"Saved home page proof: {shot_home}")

    page.goto("https://in.indeed.com/myjobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    shot_myjobs = os.path.join(SCREENSHOT_DIR, "indeed_myjobs_after_google_auth.png")
    page.screenshot(path=shot_myjobs)
    print(f"Saved myjobs page proof: {shot_myjobs}")

    context.close()
    print("Done!")
