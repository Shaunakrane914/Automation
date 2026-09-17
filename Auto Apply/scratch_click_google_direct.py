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
    time.sleep(3)

    # Dismiss cookie banner
    try:
        page.locator("#onetrust-accept-btn-handler").click(timeout=2000)
        time.sleep(1)
    except Exception:
        pass

    # Inspect all elements with 'Continue with Google'
    els = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('*'))
            .filter(e => e.innerText && e.innerText.includes('Continue with Google'))
            .map(e => ({
                tag: e.tagName,
                id: e.id,
                className: e.className,
                rect: e.getBoundingClientRect()
            }));
    }""")
    print("Found elements:", els)

    # Click the button
    btn = page.locator("text='Continue with Google'").first
    print("Clicking button via text locator...")
    btn.click()
    time.sleep(5)

    print("After click URL:", page.url)
    page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\indeed_google_clicked_direct.png")

    # Check for popup or new tabs
    print(f"Total open pages: {len(context.pages)}")
    for i, p_item in enumerate(context.pages):
        print(f"Page {i}: {p_item.url}")
        p_item.screenshot(path=rf"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\indeed_page_{i}.png")

    context.close()
