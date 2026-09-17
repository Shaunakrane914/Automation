import os
import time
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
RESUME_PATH = r"C:\Users\Shaunak Rane\Desktop\Projects\Portfolio\Shaunak_Rane_Resume.pdf"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def handle_screening_questions(modal):
    """Answers common LinkedIn screening questions."""
    # 1. Radio buttons: Check 'Yes'
    radios = modal.locator("input[type='radio']").all()
    for r in radios:
        try:
            val = (r.get_attribute("value") or "").lower()
            label = modal.locator(f"label[for='{r.get_attribute('id')}']").inner_text().lower() if r.get_attribute('id') else ""
            if "yes" in val or "yes" in label:
                r.check(timeout=800)
        except Exception:
            pass

    # 2. Text / numeric fields
    text_inputs = modal.locator("input[type='text'], input[type='number']").all()
    for ti in text_inputs:
        try:
            if ti.is_visible(timeout=500) and not ti.input_value().strip():
                ti_id = (ti.get_attribute("id") or "").lower()
                ti_name = (ti.get_attribute("name") or "").lower()
                if "phone" in ti_id or "phone" in ti_name:
                    ti.fill("9320221211")
                else:
                    ti.fill("1")  # default 1 year of experience
        except Exception:
            pass

    # 3. Textareas
    textareas = modal.locator("textarea").all()
    for ta in textareas:
        try:
            if ta.is_visible(timeout=500) and not ta.input_value().strip():
                ta.fill("I have extensive practical experience in Python, Machine Learning, and backend API development from my academic coursework and internship.")
        except Exception:
            pass

    # 4. Dropdowns
    selects = modal.locator("select").all()
    for s in selects:
        try:
            options = s.locator("option").all()
            for opt in options:
                txt = opt.inner_text().strip().lower()
                val = opt.get_attribute("value") or ""
                if "yes" in txt or "intermediate" in txt or "professional" in txt or "1" in txt:
                    s.select_option(value=val)
                    break
        except Exception:
            pass

def main():
    print("Launching visible Chrome with persistent profile for LinkedIn Easy Apply...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            executable_path=CHROME_EXE,
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            viewport=None
        )
        page = context.pages[0] if context.pages else context.new_page()

        # Remote AI & Python internships with Easy Apply filter enabled
        search_url = "https://www.linkedin.com/jobs/search/?keywords=AI%20Intern&f_WT=2&f_AL=true"
        print(f"Navigating to LinkedIn search: {search_url}")
        page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(4)

        if "login" in page.url or "authwall" in page.url:
            print("Not logged in. Current URL:", page.url)
            context.close()
            return

        print("LinkedIn search loaded successfully.")
        cards = page.locator(".job-card-container, .jobs-search-results__list-item").all()
        print(f"Found {len(cards)} job cards on page.")

        applied_success = 0
        target_count = 2

        for idx, card in enumerate(cards):
            if applied_success >= target_count:
                break
            try:
                card.scroll_into_view_if_needed()
                card.click()
                time.sleep(2.5)

                job_title = page.locator(".job-details-jobs-unified-top-card__job-title, .jobs-unified-top-card__job-title").inner_text().strip()
                company = page.locator(".job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name").inner_text().strip()
                print(f"\nEvaluating: {job_title} at {company}")

                # Check if Easy Apply button is present
                apply_btn = page.locator("button.jobs-apply-button").first
                if not apply_btn.is_visible(timeout=2000):
                    print("No Easy Apply button visible (or already applied). Skipping.")
                    continue

                btn_text = apply_btn.inner_text().strip()
                if "Easy Apply" not in btn_text:
                    print(f"Button text is '{btn_text}', skipping non-Easy-Apply.")
                    continue

                print("Clicking Easy Apply...")
                apply_btn.click()
                time.sleep(2)

                modal = page.locator("div.jobs-easy-apply-modal, div[role='dialog']")
                if not modal.is_visible(timeout=3000):
                    print("Modal did not open.")
                    continue

                # Step-by-step through wizard (max 7 steps)
                submitted = False
                for step in range(7):
                    time.sleep(1)
                    # Check if 'Submit application' is present
                    submit_btn = modal.locator("button:has-text('Submit application'), button[aria-label='Submit application']").first
                    if submit_btn.is_visible(timeout=1000):
                        print("Found 'Submit application' button. Clicking...")
                        submit_btn.click()
                        time.sleep(3)
                        submitted = True
                        break

                    # Handle screening questions & inputs on this step
                    handle_screening_questions(modal)

                    # Check for Resume upload if needed
                    file_input = modal.locator("input[type='file']").first
                    if file_input.is_visible(timeout=500):
                        try:
                            file_input.set_input_files(RESUME_PATH)
                            print(f"Uploaded resume: {os.path.basename(RESUME_PATH)}")
                            time.sleep(1)
                        except Exception:
                            pass

                    # Click 'Review' or 'Next'
                    next_btn = modal.locator("button:has-text('Review'), button:has-text('Next'), button[aria-label='Continue to next step']").first
                    if next_btn.is_visible(timeout=1500):
                        print(f"Step {step+1}: Clicking '{next_btn.inner_text().strip()}'...")
                        next_btn.click()
                        time.sleep(1.5)
                    else:
                        print("Neither Next nor Submit button found. Stopping steps.")
                        break

                if submitted:
                    shot_path = os.path.join(SCREENSHOT_DIR, f"real_linkedin_applied_{applied_success+1}_{int(time.time())}.png")
                    page.screenshot(path=shot_path)
                    print(f"SUCCESS! Application submitted. Proof screenshot: {shot_path}")
                    applied_success += 1

                    # Dismiss confirmation
                    dismiss_btn = page.locator("button[aria-label='Dismiss'], button:has-text('Done')").first
                    if dismiss_btn.is_visible(timeout=2000):
                        dismiss_btn.click()
                        time.sleep(1)
                else:
                    # Close incomplete modal
                    print("Could not complete application wizard automatically. Closing dialog.")
                    dismiss = modal.locator("button[aria-label='Dismiss']").first
                    if dismiss.is_visible(timeout=1000):
                        dismiss.click()
                        time.sleep(1)
                        discard = page.locator("button:has-text('Discard')").first
                        if discard.is_visible(timeout=1000):
                            discard.click()
                            time.sleep(1)

            except Exception as e:
                print(f"Error on card {idx}: {e}")

        print(f"\nFinished LinkedIn run. Total genuine submissions: {applied_success}")
        context.close()

if __name__ == "__main__":
    main()
