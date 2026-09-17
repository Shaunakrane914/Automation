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
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    # Dismiss cookie banner
    try:
        page.locator("#onetrust-accept-btn-handler").click(timeout=1500)
        time.sleep(1)
    except Exception:
        pass

    # Find bounding box of Google button
    g_target = page.locator("span:has-text('Continue with Google'), div[role='button']:has-text('Continue with Google')").first
    box = g_target.bounding_box()
    print("Google button bounding box:", box)

    if box:
        cx = box['x'] + box['width'] / 2
        cy = box['y'] + box['height'] / 2
        print(f"Simulating real mouse click at ({cx}, {cy})...")
        page.mouse.move(cx, cy)
        time.sleep(0.5)
        page.mouse.down()
        time.sleep(0.2)
        page.mouse.up()
        print("Mouse click dispatched!")
    else:
        print("Falling back to locator.click()...")
        g_target.click()

    # Wait 6 seconds
    time.sleep(6)

    print("Main page URL:", page.url)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_after_mouse_click.png"))

    print(f"Total open pages in context: {len(context.pages)}")
    for i, p_item in enumerate(context.pages):
        print(f"  Tab {i}: {p_item.url}")
        p_item.screenshot(path=os.path.join(SCREENSHOT_DIR, f"indeed_tab_{i}_mouse.png"))

    context.close()
    print("Done!")
