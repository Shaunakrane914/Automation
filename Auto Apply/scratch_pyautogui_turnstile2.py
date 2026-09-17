import time
import os
import pyautogui
from playwright.sync_api import sync_playwright

pyautogui.FAILSAFE = False

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

print("Screen size:", pyautogui.size())

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

    page.bring_to_front()
    time.sleep(1)

    stage = page.locator("#challenge-stage, #cf-box-container").first
    if stage.is_visible():
        box = stage.bounding_box()
        print("Stage box:", box)

        # Chrome window screen position
        pos = page.evaluate("""() => {
            const el = document.querySelector('#challenge-stage') || document.querySelector('#cf-box-container');
            const r = el.getBoundingClientRect();
            return {
                x: window.screenX + r.left,
                y: window.screenY + (window.outerHeight - window.innerHeight) + r.top,
                w: r.width,
                h: r.height
            };
        }""")
        print("Element pos:", pos)

        # Target the checkbox: 30px from left of box, vertical center
        tx = int(pos['x'] + 30)
        ty = int(pos['y'] + pos['h'] / 2)
        print(f"Targeting ({tx}, {ty})")

        pyautogui.moveTo(tx, ty, duration=0.8)
        time.sleep(0.3)
        pyautogui.click()
        print("Clicked!")

        for i in range(10):
            time.sleep(1)
            print(f"Waiting {i+1}s: URL is {page.url}")
            if "Verification" not in page.content():
                print("Cloudflare cleared!")
                break

    shot = os.path.join(SCREENSHOT_DIR, "after_turnstile_cleared.png")
    page.screenshot(path=shot)
    print("Final URL:", page.url)

    context.close()
