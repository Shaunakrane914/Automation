import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    # Mask webdriver
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    page = context.pages[0] if context.pages else context.new_page()

    print("Navigating to https://in.indeed.com/ ...")
    page.goto("https://in.indeed.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_home_start.png"))

    # Check if logged in
    print("Page URL:", page.url)

    # Type query in 'What' input
    what_inp = page.locator("input#text-input-what, input[name='q']").first
    where_inp = page.locator("input#text-input-where, input[name='l']").first

    if what_inp.is_visible():
        print("Typing job search: Python Intern...")
        what_inp.click()
        what_inp.fill("Python Intern")
        time.sleep(1)

        if where_inp.is_visible():
            print("Typing location: Remote...")
            where_inp.click()
            where_inp.fill("Remote")
            time.sleep(1)

        page.locator("button[type='submit'], button:has-text('Find jobs')").first.click()
        time.sleep(5)

    search_result_shot = os.path.join(SCREENSHOT_DIR, "indeed_search_result_page.png")
    page.screenshot(path=search_result_shot)
    print("Search result URL:", page.url)
    print(f"Screenshot saved to {search_result_shot}")

    # Inspect job cards
    cards = page.locator("div.cardOutline, div.job_seen_beacon").all()
    print(f"Total job cards: {len(cards)}")
    for i, c in enumerate(cards[:5]):
        try:
            print(f"Card {i}: {c.inner_text()[:120].replace(chr(10), ' | ')}")
        except Exception:
            pass

    context.close()
