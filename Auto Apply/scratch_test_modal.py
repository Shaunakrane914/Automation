import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:5173/")
    time.sleep(3)
    
    career_tab = page.locator("button:has-text('Career & Opportunities')").first
    if career_tab.is_visible():
        career_tab.click()
        time.sleep(2)
        
        # Click proof button on the second card (Internshala Python & Django)
        proof_btns = page.locator("button:has-text('Proof')")
        if proof_btns.count() > 1:
            proof_btns.nth(1).click()
            time.sleep(2)
            page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\proof_modal_verified.png")
            print("Captured proof modal screenshot!")
        
    browser.close()
