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

    new_tabs = []
    context.on("page", lambda p_tab: new_tabs.append(p_tab))

    print("Navigating to Indeed login...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    # Dismiss cookie banner
    try:
        page.locator("#onetrust-accept-btn-handler").click(timeout=1500)
        time.sleep(1)
    except Exception:
        pass

    print("Clicking exact center of Continue with Google: (632, 451)...")
    page.mouse.click(632, 451)
    time.sleep(5)

    print(f"Total tabs in context: {len(context.pages)}")
    for i, tab in enumerate(context.pages):
        print(f"  Tab {i}: {tab.url}")
        tab.screenshot(path=os.path.join(SCREENSHOT_DIR, f"indeed_google_clicked_tab_{i}.png"))

    # If new tab opened or redirected to Google accounts
    target_tab = new_tabs[0] if new_tabs else (context.pages[1] if len(context.pages) > 1 else page)
    print(f"Target tab URL: {target_tab.url}")

    if "accounts.google.com" in target_tab.url:
        print("Handling Google OAuth on target tab...")
        time.sleep(3)
        # Look for Shaunak Rane account card
        acc = target_tab.locator("div:has-text('shaunakrane914@gmail.com'), li:has-text('shaunakrane914@gmail.com'), div:has-text('Shaunak Rane')").first
        if acc.is_visible(timeout=3000):
            print("Found Shaunak Rane account card! Clicking it...")
            acc.click()
            time.sleep(6)
        else:
            email_f = target_tab.locator("input[type='email']").first
            if email_f.is_visible(timeout=2000):
                print("Entering shaunakrane914@gmail.com...")
                email_f.fill("shaunakrane914@gmail.com")
                time.sleep(1)
                target_tab.locator("button:has-text('Next')").first.click()
                time.sleep(4)
        
        # Check for password
        pw_f = target_tab.locator("input[type='password']").first
        if pw_f.is_visible(timeout=3000):
            print("Entering password...")
            pw_f.fill("shaunak43rane")
            time.sleep(1)
            target_tab.locator("button:has-text('Next')").first.click()
            time.sleep(5)

        target_tab.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_google_auth_result.png"))

    print("\nWaiting 10 seconds for Indeed session...")
    time.sleep(10)

    # Check Indeed Home and My Jobs
    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    shot_home = os.path.join(SCREENSHOT_DIR, "indeed_home_auth_verified.png")
    page.screenshot(path=shot_home)
    print(f"Saved home verification: {shot_home}")

    page.goto("https://in.indeed.com/myjobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    shot_myjobs = os.path.join(SCREENSHOT_DIR, "indeed_myjobs_auth_verified.png")
    page.screenshot(path=shot_myjobs)
    print(f"Saved myjobs verification: {shot_myjobs}")

    context.close()
    print("Done!")
