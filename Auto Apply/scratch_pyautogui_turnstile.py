import time
import os
import pyautogui
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://in.indeed.com/", wait_until="domcontentloaded")
    time.sleep(4)

    # Bring Chrome window to foreground
    page.bring_to_front()
    time.sleep(1)

    stage = page.locator("#challenge-stage, #cf-box-container").first
    if stage.is_visible():
        box = stage.bounding_box()
        print("Stage box:", box)

        # In Chrome with top bar (~80px) and window margins:
        # Let's get the absolute screen position via evaluate
        rect = page.evaluate("""() => {
            const el = document.querySelector('#challenge-stage') || document.querySelector('#cf-box-container');
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return {
                left: r.left + window.screenX,
                top: r.top + (window.outerHeight - window.innerHeight) + window.screenY,
                width: r.width,
                height: r.height
            };
        }""")
        print("Computed screen rect:", rect)

        if rect:
            target_x = int(rect['left'] + 25)
            target_y = int(rect['top'] + rect['height'] / 2)
            print(f"Moving mouse to ({target_x}, {target_y}) and clicking...")
            pyautogui.moveTo(target_x, target_y, duration=0.6)
            time.sleep(0.2)
            pyautogui.click()
            time.sleep(6)

    shot = os.path.join(SCREENSHOT_DIR, "after_pyautogui_turnstile.png")
    page.screenshot(path=shot)
    print("Post-click URL:", page.url)
    print(f"Saved screenshot: {shot}")

    context.close()
