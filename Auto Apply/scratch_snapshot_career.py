import time
import os
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME_EXE)
    page = b.new_page(viewport={"width": 1600, "height": 950})
    page.goto("http://localhost:5173/")
    time.sleep(3)
    
    # Click Career & Opportunities tab
    page.locator("button:has-text('Career & Opportunities')").click()
    page.wait_for_selector("button:has-text('Proof')", timeout=10000)
    time.sleep(2)

    proof_btns = page.locator("button:has-text('Proof')").all()
    print(f"Total proof buttons found: {len(proof_btns)}")
    
    # Click index 2 (Indeed Associate AI Engineer)
    print("Clicking proof_btns[2] (Indeed)...")
    proof_btns[2].click()
    time.sleep(2)
    
    modal_img = page.locator("img[alt='Application Proof']").first
    print("Modal img is visible?", modal_img.is_visible())
    print("Modal img src:", modal_img.get_attribute("src"))
    
    shot = os.path.join(SCREENSHOT_DIR, "student_os_proof_modal_indeed_verified.png")
    page.screenshot(path=shot)
    print(f"Saved snapshot to: {shot}")

    b.close()
