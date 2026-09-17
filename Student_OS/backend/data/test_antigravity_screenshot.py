from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:5173")
    page.wait_for_timeout(2000)
    
    # Locate chat input
    chat_input = page.locator("input[placeholder*='Ask Copilot']").or_(page.locator("input[type='text']")).first
    chat_input.fill("escalate to antigravity: Complete Advance Java Lab Servlets practice and write test script")
    chat_input.press("Enter")
    page.wait_for_timeout(4000)
    
    out_file = Path(r"C:\Users\Shaunak Rane\.gemini\antigravity-ide\brain\4c862611-5a11-4b3c-bc77-b72ad2056302\antigravity_escalation_powers_verified.png")
    page.screenshot(path=str(out_file))
    print("Saved successfully:", out_file.exists())
    browser.close()
