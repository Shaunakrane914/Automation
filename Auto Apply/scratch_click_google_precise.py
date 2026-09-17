import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    print("Launching visible Chrome with 1280x720 viewport...")
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        viewport={"width": 1280, "height": 720},
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()

    new_tabs = []
    def on_page(p_item):
        print("NEW TAB DETECTED:", p_item.url)
        new_tabs.append(p_item)

    context.on("page", on_page)

    print("Navigating to Indeed login...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    shot_before = os.path.join(SCREENSHOT_DIR, "indeed_precise_before_click.png")
    page.screenshot(path=shot_before)
    print(f"Saved pre-click screenshot: {shot_before}")

    print("Dispatching real mouse click at exact center of Continue with Google: (632, 366)...")
    page.mouse.move(632, 366)
    time.sleep(0.3)
    page.mouse.down()
    time.sleep(0.15)
    page.mouse.up()
    print("Mouse click dispatched!")

    time.sleep(5)

    shot_after = os.path.join(SCREENSHOT_DIR, "indeed_precise_after_click.png")
    page.screenshot(path=shot_after)
    print(f"Saved post-click main page screenshot: {shot_after}")
    print(f"Main page URL: {page.url}")

    print(f"\nTotal open tabs in context: {len(context.pages)}")
    for i, tab in enumerate(context.pages):
        print(f"  Tab {i}: {tab.url}")
        tab_shot = os.path.join(SCREENSHOT_DIR, f"indeed_precise_tab_{i}.png")
        tab.screenshot(path=tab_shot)
        print(f"  Saved Tab {i} screenshot: {tab_shot}")

        # If tab is Google accounts, look for Shaunak's account
        if "accounts.google.com" in tab.url:
            print(f"  --> Interacting with Google Accounts tab {i}...")
            time.sleep(2)
            # Find Shaunak Rane account option
            acc = tab.locator("div:has-text('shaunakrane914@gmail.com'), li:has-text('shaunakrane914@gmail.com'), div:has-text('Shaunak Rane')").first
            if acc.is_visible(timeout=3000):
                print("  --> Clicking Shaunak Rane account card!")
                acc.click()
                time.sleep(6)
            else:
                email_f = tab.locator("input[type='email']").first
                if email_f.is_visible(timeout=2000):
                    print("  --> Entering shaunakrane914@gmail.com on Google tab...")
                    email_f.fill("shaunakrane914@gmail.com")
                    tab.locator("button:has-text('Next')").first.click()
                    time.sleep(4)
            # Check for password
            pw_f = tab.locator("input[type='password']").first
            if pw_f.is_visible(timeout=3000):
                print("  --> Entering password on Google tab...")
                pw_f.fill("shaunak43rane")
                tab.locator("button:has-text('Next')").first.click()
                time.sleep(5)

            shot_g_after = os.path.join(SCREENSHOT_DIR, f"indeed_precise_tab_{i}_post_auth.png")
            tab.screenshot(path=shot_g_after)
            print(f"  Saved post-auth tab screenshot: {shot_g_after}")

    print("\nWaiting 10 seconds for session to settle...")
    time.sleep(10)

    # Check Indeed home and My Jobs
    print("Navigating to Indeed home...")
    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    shot_h = os.path.join(SCREENSHOT_DIR, "indeed_precise_final_home.png")
    page.screenshot(path=shot_h)
    print(f"Saved home verification: {shot_h}")

    print("Navigating to Indeed My Jobs...")
    page.goto("https://in.indeed.com/myjobs", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    shot_j = os.path.join(SCREENSHOT_DIR, "indeed_precise_final_myjobs.png")
    page.screenshot(path=shot_j)
    print(f"Saved My Jobs verification: {shot_j}")

    context.close()
    print("Done!")
