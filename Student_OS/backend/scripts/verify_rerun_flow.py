import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

DOCS_SCREENSHOTS = Path(__file__).resolve().parent.parent.parent / "docs" / "screenshots"
DOCS_SCREENSHOTS.mkdir(parents=True, exist_ok=True)

async def test_button_and_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "8000" in pg.url][0]
        page.on("console", lambda msg: print("PAGE CONSOLE:", msg.text))
        page.on("pageerror", lambda err: print("PAGE ERROR:", err))
        page.on("request", lambda req: print("PAGE REQ:", req.method, req.url))
        await page.bring_to_front()
        await page.reload(wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # 1. Capture Initial State showing the Rerun Full Update button
        shot1 = DOCS_SCREENSHOTS / "rerun_button_ready.png"
        await page.screenshot(path=str(shot1), full_page=True)
        print(f"Captured initial ready state: {shot1}")

        # 2. Click the 'Rerun Full Update' button
        btn = page.locator("button:has-text('Rerun Full Update')").first
        print("Clicking 'Rerun Full Update' button...")
        await btn.click()
        await page.wait_for_timeout(3500)

        # 3. Capture Active Progress State
        shot2 = DOCS_SCREENSHOTS / "rerun_active_progress.png"
        await page.screenshot(path=str(shot2), full_page=True)
        print(f"Captured active progress state: {shot2}")

if __name__ == "__main__":
    asyncio.run(test_button_and_screenshot())
