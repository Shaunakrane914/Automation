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
        viewport={"width": 1280, "height": 720}
    )
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://profile.indeed.com/", wait_until="domcontentloaded")
    time.sleep(3)

    # Find matching link or all nav links
    links = page.locator("a").all()
    for l in links:
        try:
            txt = l.text_content().strip()
            href = l.get_attribute("href")
            if any(k in txt.lower() or (href and k in href.lower()) for k in ["match", "job", "recommend", "feed"]):
                print(f"Match/Job link: '{txt}' -> {href}")
        except Exception:
            pass

    context.close()
