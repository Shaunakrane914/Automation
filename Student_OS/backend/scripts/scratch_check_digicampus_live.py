import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from playwright.async_api import async_playwright
from app.config import settings

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        print("Navigating to DigiCampus login...")
        await page.goto("https://uai.digiicampus.com/login", timeout=30000)
        await page.wait_for_timeout(3000)
        print("Page Title:", await page.title())
        print("Current URL:", page.url)

        # Inspect inputs
        inputs = await page.locator("input").all()
        print(f"Found {len(inputs)} inputs")
        for i, inp in enumerate(inputs):
            name = await inp.get_attribute("name")
            t = await inp.get_attribute("type")
            placeholder = await inp.get_attribute("placeholder")
            print(f" - Input {i}: name={name}, type={t}, placeholder={placeholder}")

        # Fill credentials
        email_field = page.locator("input[type='text'], input[type='email'], input[name*='user']").first
        pass_field = page.locator("input[type='password']").first
        
        await email_field.fill(settings.DIGICAMPUS_USER)
        await pass_field.fill(settings.DIGICAMPUS_PASS)
        
        btn = page.locator("button:has-text('Sign In'), button:has-text('Login'), button[type='submit']").first
        await btn.click()
        await page.wait_for_timeout(6000)
        
        print("Post login URL:", page.url)
        await page.screenshot(path="digicampus_post_login.png")
        print("Saved digicampus_post_login.png")

        # Now navigate to assignments
        # In DigiCampus V2, assignments are at: https://uai.digiicampus.com/V2/#/feed or classroom
        await page.goto("https://uai.digiicampus.com/V2/#/classroom/assignments", timeout=20000)
        await page.wait_for_timeout(4000)
        print("Assignments URL:", page.url)
        await page.screenshot(path="digicampus_assignments_live.png")
        print("Saved digicampus_assignments_live.png")

        # Extract text content
        body_text = await page.inner_text("body")
        print("Body text snippet:\n", body_text[:1000])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
