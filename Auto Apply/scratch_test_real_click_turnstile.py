import time
import os
import ctypes
from ctypes import wintypes
import pyautogui
from playwright.sync_api import sync_playwright

pyautogui.FAILSAFE = False

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

# Function to get Chrome window rect on screen
def get_chrome_rect():
    user32 = ctypes.windll.user32
    rect = wintypes.RECT()
    # Find window
    hwnd = user32.FindWindowW(None, "Indeed - Google Chrome")
    if not hwnd:
        # Fallback find by class
        hwnd = user32.FindWindowW("Chrome_WidgetWin_1", None)
    if hwnd:
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        user32.SetForegroundWindow(hwnd)
        return rect.left, rect.top, rect.right, rect.bottom
    return None

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://in.indeed.com/jobs?q=AI+intern&l=Remote", wait_until="domcontentloaded")
    time.sleep(4)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "turnstile_before_hw_click.png"))

    # Check window rect
    win_rect = get_chrome_rect()
    print("Chrome window rect:", win_rect)

    # Find checkbox in page
    stage = page.locator("#challenge-stage, #cf-box-container").first
    if stage.is_visible():
        box = stage.bounding_box()
        print("Playwright stage bounding box:", box)

        # Get client rect relative to page
        pos = page.evaluate("""() => {
            const el = document.querySelector('#challenge-stage') || document.querySelector('#cf-box-container');
            const r = el.getBoundingClientRect();
            return { x: r.left, y: r.top, w: r.width, h: r.height };
        }""")
        print("Pos relative to page client area:", pos)

        # Calculate exact hardware mouse coordinates
        if win_rect:
            wl, wt, wr, wb = win_rect
            # On maximized Chrome, toolbar/tabs is ~85px
            # The checkbox is ~28px from stage left, and middle of stage
            target_x = wl + int(pos['x'] + 28)
            target_y = wt + 85 + int(pos['y'] + pos['h'] / 2)
            print(f"Clicking at real screen coordinate: ({target_x}, {target_y})...")

            pyautogui.moveTo(target_x, target_y, duration=0.6)
            time.sleep(0.2)
            pyautogui.click()
            print("Real hardware click executed!")

            # Wait and check if Turnstile clears
            for i in range(10):
                time.sleep(1)
                print(f"Waiting {i+1}s: URL is {page.url}")
                cards = page.locator("div.cardOutline, div.job_seen_beacon, td.resultContent").count()
                if cards > 0:
                    print(f"Turnstile bypassed! Job cards count = {cards}")
                    break

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "turnstile_after_hw_click.png"))
    print("Final URL:", page.url)

    context.close()
