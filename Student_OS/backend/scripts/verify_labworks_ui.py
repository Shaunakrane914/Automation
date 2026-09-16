from playwright.sync_api import sync_playwright
import time
from pathlib import Path

ARTIFACT_DIR = Path(r"C:\Users\Shaunak Rane\.gemini\antigravity-ide\brain\4c862611-5a11-4b3c-bc77-b72ad2056302")

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 960})
        page.goto("http://127.0.0.1:8000/")
        page.wait_for_timeout(2500)

        # Click the Labworks tab
        labs_tab = page.locator("button:has-text('Labworks')").first
        labs_tab.click()
        page.wait_for_timeout(1500)

        # 1. Capture full labworks overview
        screenshot1 = ARTIFACT_DIR / "labworks_overview.png"
        page.screenshot(path=str(screenshot1))
        print("Captured overview screenshot:", screenshot1)

        # 2. Filter by Deep Learning
        dl_btn = page.locator("button:has-text('Deep Learning')").first
        if dl_btn.count() > 0:
            dl_btn.click()
            page.wait_for_timeout(1000)

        # 3. Expand Starter Code on Exp 1
        code_btn = page.locator("button:has-text('Inspect Code')").first
        if code_btn.count() > 0:
            code_btn.click()
            page.wait_for_timeout(1000)

        # 4. Toggle practice to-do task
        task_item = page.locator("div:has-text('Import numpy and initialize binary truth table')").first
        if task_item.count() > 0:
            task_item.click()
            page.wait_for_timeout(1000)

        # 5. Capture active practice view
        screenshot2 = ARTIFACT_DIR / "labworks_practice_interactive.png"
        page.screenshot(path=str(screenshot2))
        print("Captured practice interactive screenshot:", screenshot2)

        browser.close()

if __name__ == "__main__":
    verify()
