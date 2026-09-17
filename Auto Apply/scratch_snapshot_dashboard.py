import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:5173/")
    time.sleep(3)
    
    # Click Career Radar or Auto Apply tab
    radar_btn = page.locator("button:has-text('Career Radar'), [data-tab='career-radar']").first
    if radar_btn.is_visible():
        radar_btn.click()
        time.sleep(2)
        
    page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\dashboard_career_radar_updated.png")
    
    # Click Auto-Apply tab if present
    auto_btn = page.locator("button:has-text('Auto-Apply'), button:has-text('Auto Apply'), [data-tab='auto-apply']").first
    if auto_btn.is_visible():
        auto_btn.click()
        time.sleep(2)
        page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\dashboard_auto_apply_updated.png")
        
    browser.close()
    print("Dashboard snapshots taken!")
