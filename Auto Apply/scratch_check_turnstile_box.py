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

    iframes = page.locator("iframe").all()
    print(f"Iframe count: {len(iframes)}")
    for i, ifr in enumerate(iframes):
        try:
            box = ifr.bounding_box()
            print(f"Iframe {i}: box={box}, src={ifr.get_attribute('src')}")
        except Exception as e:
            print(f"Iframe {i} err: {e}")

    context.close()
