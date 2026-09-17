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
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    print("Checking iframes on page...")
    frames = page.frames
    print(f"Total frames: {len(frames)}")
    for i, f in enumerate(frames):
        print(f"Frame {i}: url={f.url}")
        if "cloudflare" in f.url or "turnstile" in f.url or "challenges" in f.url:
            print(f"Found Cloudflare frame {i}!")
            try:
                # Find checkbox
                cb = f.locator("input[type='checkbox'], #cf-stage, .ctp-checkbox-label").first
                if cb.is_visible(timeout=3000):
                    print("Found checkbox! Clicking it...")
                    cb.click()
                    time.sleep(4)
            except Exception as e:
                print("Error clicking frame checkbox:", e)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "after_turnstile_click_attempt.png"))
    print("URL after attempt:", page.url)
    time.sleep(3)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "after_turnstile_click_attempt2.png"))
    print("URL after 3s:", page.url)

    context.close()
