import time
import os
import pyautogui
from playwright.sync_api import sync_playwright

pyautogui.FAILSAFE = False
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent",
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=False,
        args=["--start-maximized"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://in.indeed.com/", wait_until="domcontentloaded")
    time.sleep(4)
    page.bring_to_front()
    time.sleep(1)

    # Take full desktop screenshot
    desktop_shot = pyautogui.screenshot()
    desktop_shot_path = os.path.join(SCREENSHOT_DIR, "desktop_screen_actual.png")
    desktop_shot.save(desktop_shot_path)
    print(f"Saved full desktop screenshot: {desktop_shot_path}")
    print(f"Desktop size: {desktop_shot.size}")

    context.close()
