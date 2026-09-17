import time
import os
import pyautogui
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    print("Launching maximized visible Chrome...")
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    
    page = context.pages[0] if context.pages else context.new_page()

    print("Opening Indeed login...")
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    # Bring window to focus
    page.bring_to_front()
    time.sleep(1)

    # Find the Google button bounding box in the viewport
    g_btn = page.locator("div[role='button']:has-text('Continue with Google'), #button-label, span:has-text('Continue with Google')").first
    box = g_btn.bounding_box()
    print("Google button viewport box:", box)

    if box:
        # In Chrome maximized on 1920x1080, the browser address bar & tabs take ~85px on Windows
        # Let's compute screen coordinates
        click_x = box['x'] + box['width'] / 2
        click_y = box['y'] + box['height'] / 2 + 85  # account for Chrome top bar
        print(f"Clicking at screen coordinates: ({click_x}, {click_y}) using PyAutoGUI...")
        pyautogui.moveTo(click_x, click_y, duration=0.5)
        time.sleep(0.3)
        pyautogui.click()
        print("Clicked!")
    else:
        # Fallback to direct center-of-screen calculation if locator didn't return box
        print("Using center-screen fallback for Continue with Google (x=960, y=560)...")
        pyautogui.moveTo(960, 560, duration=0.5)
        time.sleep(0.3)
        pyautogui.click()

    time.sleep(5)

    # Take screenshot of screen
    pyautogui.screenshot(os.path.join(SCREENSHOT_DIR, "indeed_pyautogui_after_first_click.png"))
    print("Saved post-click desktop screenshot.")

    # Check if Google account chooser appeared
    # In Google account chooser, Shaunak's account card or 'shaunakrane914@gmail.com' is displayed
    print("Checking for Shaunak Rane account card on screen...")
    time.sleep(3)
    pyautogui.screenshot(os.path.join(SCREENSHOT_DIR, "indeed_pyautogui_account_screen.png"))

    # If Shaunak Rane is displayed, click it
    # On typical Google account chooser dialog, the first account is at center (x=960, y=490) or similar
    # Let's keep visible browser open for 15 seconds so user can see it live or let clicker finish
    print("Waiting 15 seconds...")
    time.sleep(15)

    context.close()
    print("Finished.")
