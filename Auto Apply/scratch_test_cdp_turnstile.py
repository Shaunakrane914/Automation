import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        viewport={"width": 1280, "height": 720}
    )
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://in.indeed.com/", wait_until="domcontentloaded")
    time.sleep(4)

    client = context.new_cdp_session(page)
    
    print("Dispatching CDP mouse click to (518, 211)...")
    # Move
    client.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": 518, "y": 211})
    time.sleep(0.2)
    # Down
    client.send("Input.dispatchMouseEvent", {"type": "mousePressed", "button": "left", "clickCount": 1, "x": 518, "y": 211})
    time.sleep(0.15)
    # Up
    client.send("Input.dispatchMouseEvent", {"type": "mouseReleased", "button": "left", "clickCount": 1, "x": 518, "y": 211})
    
    print("Clicked! Waiting 8s...")
    for i in range(8):
        time.sleep(1)
        print(f"Sec {i+1}, URL: {page.url}")

    shot = os.path.join(SCREENSHOT_DIR, "cdp_turnstile_result.png")
    page.screenshot(path=shot)
    print("Result URL:", page.url)

    context.close()
