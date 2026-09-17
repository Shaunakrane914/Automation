import time
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized"]
    )
    page = context.pages[0]
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded")
    time.sleep(4)

    # List all frames
    frames = page.frames
    print(f"Total frames on page: {len(frames)}")
    for i, f in enumerate(frames):
        print(f"Frame {i}: name='{f.name}', url='{f.url}'")
        try:
            texts = f.evaluate("() => document.body ? document.body.innerText : ''")
            if texts.strip():
                print(f"   Frame {i} text: {texts[:100]}")
            # Look for button inside frame
            g_el = f.locator("div[role='button'], button, span:has-text('Continue with Google')").first
            if g_el.is_visible(timeout=1000):
                print(f"   >>> FOUND Google button in Frame {i}! Clicking it...")
                g_el.click()
                time.sleep(5)
                print("   After frame click page URL:", page.url)
                break
        except Exception as e:
            print(f"   Frame {i} error: {e}")

    page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\indeed_after_iframe_click.png")

    print(f"Total open pages now: {len(context.pages)}")
    for i, p_item in enumerate(context.pages):
        print(f"Page {i}: {p_item.url}")
        p_item.screenshot(path=rf"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\indeed_frame_page_{i}.png")

    context.close()
