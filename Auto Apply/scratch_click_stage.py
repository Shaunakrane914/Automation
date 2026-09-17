import time
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"

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
    time.sleep(3)

    # Let's inspect challenge-stage bounding box and click it!
    stage = page.locator("#challenge-stage, #cf-box-container").first
    if stage.is_visible():
        box = stage.bounding_box()
        print(f"Stage box: {box}")
        # Inside the stage box, the checkbox is on the left side
        # Let's click at box['x'] + 30, box['y'] + box['height'] / 2
        click_x = box['x'] + 30
        click_y = box['y'] + box['height'] / 2
        print(f"Clicking at ({click_x}, {click_y})...")
        page.mouse.click(click_x, click_y)
        time.sleep(5)
        print("URL after click:", page.url)
        page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\after_stage_click.png")

    context.close()
