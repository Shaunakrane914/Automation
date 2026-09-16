import asyncio
from playwright.async_api import async_playwright

async def login_digi():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        digi_page = None
        for page in context.pages:
            if "digiicampus.com" in page.url:
                digi_page = page
                break
        
        if not digi_page:
            print("No digi page found, creating new page...")
            digi_page = await context.new_page()
            await digi_page.goto("https://uai.digiicampus.com", wait_until="domcontentloaded")
            await digi_page.wait_for_timeout(3000)

        print("Current Digi page URL:", digi_page.url)
        await digi_page.bring_to_front()

        # Fill inputs
        await digi_page.fill("#registrationId", "shaunak.rane@universalai.in")
        await digi_page.fill("#password", "Sharan@2007")
        print("Filled credentials. Waiting for Cloudflare...")
        await digi_page.wait_for_timeout(4000)

        await digi_page.screenshot(path="digi_ready_to_submit.png")
        
        submit_btn = await digi_page.query_selector('button[type="submit"]')
        if submit_btn:
            is_disabled = await submit_btn.is_disabled()
            print("Submit button disabled?", is_disabled)
            print("Clicking submit...")
            await submit_btn.click()
            await digi_page.wait_for_timeout(6000)
        else:
            print("No submit button found!")

        print("After login URL:", digi_page.url)
        await digi_page.screenshot(path="digi_after_login.png")

if __name__ == "__main__":
    asyncio.run(login_digi())
