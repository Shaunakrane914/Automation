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
    page = context.pages[0] if context.pages else context.new_page()

    # Search for remote internships in India
    search_url = "https://in.indeed.com/jobs?q=internship+remote&l=India&sc=0kf%3Aattr%28DSQF7%29%3B"
    print(f"Navigating to {search_url}...")
    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "indeed_search_remote_internships.png"))

    # Inspect job cards
    job_cards = page.locator("div.job_seen_beacon, div.cardOutline, td.resultContent").all()
    print(f"Total job cards found: {len(job_cards)}")

    for i, card in enumerate(job_cards[:10]):
        try:
            title = card.locator("h2.jobTitle, a[data-jk]").inner_text().strip()
            comp = card.locator("[data-testid='company-name']").inner_text().strip() if card.locator("[data-testid='company-name']").count() > 0 else "Unknown"
            has_easy_apply = card.locator("text=/easily apply/i, span:has-text('Easily apply')").count() > 0
            print(f"[{i}] {title} at {comp} | Easily Apply: {has_easy_apply}")
        except Exception as e:
            print(f"[{i}] Error reading card: {e}")

    context.close()
