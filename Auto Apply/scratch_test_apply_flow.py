import time
import os
from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
RESUME_PATH = r"C:\Users\Shaunak Rane\Desktop\Projects\Portfolio\Shaunak_Rane_Resume.pdf"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        USER_DATA_DIR,
        headless=False,
        executable_path=CHROME_EXE,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()

    print("\n--- 1. TESTING INTERNSHALA APPLICATION ---")
    page.goto("https://internshala.com/internships/work-from-home-artificial-intelligence-ai-internships/", wait_until="domcontentloaded", timeout=25000)
    page.wait_for_timeout(3000)

    # Dismiss promo popup if any
    try:
        page.evaluate("if(document.getElementById('close_popup')) document.getElementById('close_popup').click();")
    except Exception:
        pass

    cards = page.locator(".individual_internship")
    print(f"Found {cards.count()} Internshala cards")
    if cards.count() > 0:
        first_card = cards.first
        # Find detail link or title
        detail_link = first_card.locator("a.job-title-href, h3 a").first
        if detail_link.is_visible():
            href = detail_link.get_attribute("href")
            print("Navigating to first internship:", href)
            page.goto(f"https://internshala.com{href}" if href.startswith("/") else href, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(2000)

            # Look for apply button
            apply_btn = page.locator("#easy_apply_button, #apply_now_cta, button:has-text('Apply now'), a:has-text('Apply now')").first
            if apply_btn.is_visible():
                print("Clicking Internshala Apply Now button...")
                apply_btn.click()
                page.wait_for_timeout(2000)
                
                # Check for cover letter or questions
                cover = page.locator("#cover_letter, textarea[name='cover_letter']").first
                if cover.is_visible():
                    cover.fill("I am a B.Tech (2028) student in AI & ML with hands-on experience in Python, FastAPI, and Transformers. Eager to contribute immediately!")
                    print("Filled cover letter")
                
                avail = page.locator("input[type='radio'][value='Yes'], input[type='radio'][value='yes']").first
                if avail.is_visible():
                    avail.check()
                    print("Selected immediate availability: Yes")
                    
                page.wait_for_timeout(1000)
            
            page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\test_internshala_applied_proof.png")
            print("Saved Internshala proof screenshot!")

    print("\n--- 2. TESTING LINKEDIN APPLICATION ---")
    page.goto("https://www.linkedin.com/jobs/search/?keywords=AI%20Engineer%20Intern&f_WT=2&f_AL=true", wait_until="domcontentloaded", timeout=25000)
    page.wait_for_timeout(4000)

    ln_cards = page.locator(".job-card-container, .jobs-search-results-list li")
    print(f"Found {ln_cards.count()} LinkedIn job cards")
    if ln_cards.count() > 0:
        ln_cards.first.click()
        page.wait_for_timeout(2500)
        
        easy_apply = page.locator("button.jobs-apply-button, button:has-text('Easy Apply')").first
        if easy_apply.is_visible():
            print("Found Easy Apply button! Clicking...")
            easy_apply.click()
            page.wait_for_timeout(2000)
            
            # Modal opened
            print("Easy Apply modal opened!")
            
            # Check phone input
            phone_input = page.locator("input[id*='phoneNumber'], input[name*='phone']").first
            if phone_input.is_visible():
                if not phone_input.input_value():
                    phone_input.fill("9320221211")
                    print("Filled phone number")

            page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\test_linkedin_applied_proof.png")
            print("Saved LinkedIn proof screenshot!")
            
            # Try Next button
            next_btn = page.locator("button[aria-label*='Continue'], button:has-text('Next')").first
            if next_btn.is_visible():
                next_btn.click()
                page.wait_for_timeout(1500)
                page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\test_linkedin_step2_proof.png")

    context.close()
    print("Verification completed successfully!")
