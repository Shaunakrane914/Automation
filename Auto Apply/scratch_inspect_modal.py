import time
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME_EXE)
    page = b.new_page(viewport={"width": 1600, "height": 950})
    page.goto("http://localhost:5173/")
    time.sleep(2)
    page.locator("button:has-text('Career & Opportunities')").click()
    page.wait_for_selector("button:has-text('Proof')")
    btns = page.locator("button:has-text('Proof')").all()
    btns[4].click()
    
    # Wait for img to finish loading
    page.wait_for_function("() => { const img = document.querySelector('.fixed img'); return img && img.complete && img.naturalWidth > 0; }", timeout=10000)
    img = page.locator(".fixed img").first
    print("img src:", img.get_attribute("src"))
    print("naturalWidth:", img.evaluate("e => e.naturalWidth"))
    print("naturalHeight:", img.evaluate("e => e.naturalHeight"))
    
    shot_path = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\student_os_proof_modal_linkedin_loaded.png"
    page.screenshot(path=shot_path)
    print(f"Captured: {shot_path}")
    b.close()
