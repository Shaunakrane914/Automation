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

    # Inspect shadow roots or challenge container
    html = page.content()
    print("Page length:", len(html))
    print("Contains challenge-stage?", "challenge-stage" in html)
    print("Contains turnstile?", "turnstile" in html)

    # Let's see all divs with id or class
    divs = page.locator("div[id], div[class]").all()
    for d in divs[:15]:
        try:
            print("DIV:", d.get_attribute("id"), d.get_attribute("class"))
        except Exception:
            pass

    context.close()
