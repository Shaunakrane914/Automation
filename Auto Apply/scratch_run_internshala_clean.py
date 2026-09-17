import os
import time
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"
RESUME_PATH = r"C:\Users\Shaunak Rane\Desktop\Projects\Portfolio\Shaunak_Rane_Resume.pdf"
SCREENSHOT_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        viewport=None
    )
    page = context.pages[0] if context.pages else context.new_page()

    # Step 1: Open search for remote Python / AI internships
    search_url = "https://internshala.com/internships/work-from-home-python-django,artificial-intelligence-ai,data-science-internships/"
    print("Navigating to Internshala search:", search_url)
    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    # Collect job cards
    links = page.locator("a.view_detail_button, a[href*='/internship/detail/']").all()
    job_urls = []
    for lnk in links:
        href = lnk.get_attribute("href") or ""
        if "/internship/detail/" in href and href not in job_urls:
            full_url = href if href.startswith("http") else f"https://internshala.com{href}"
            job_urls.append(full_url)

    print(f"Found {len(job_urls)} jobs to inspect.")
    
    submitted_count = 0
    target_new = 3

    for url in job_urls:
        if submitted_count >= target_new:
            break
        print(f"\n--- Checking: {url} ---")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            time.sleep(2)

            # Check if already applied
            body_text = page.locator("body").inner_text()
            if "Already applied" in body_text or "You have already applied" in body_text:
                print("Already applied to this one. Moving to next.")
                continue

            # Look for apply button
            apply_btn = page.locator("#easy_apply_button, #apply_now_cta, button:has-text('Apply now'), a:has-text('Apply now')").first
            if not apply_btn.is_visible(timeout=2000):
                print("No active Apply now button found.")
                continue

            print("Clicking Apply now...")
            apply_btn.click()
            time.sleep(2)

            # Case A: If there's an intermediate 'Proceed to application' button
            proceed_btn = page.locator("#proceed_to_application, button:has-text('Proceed to application'), a:has-text('Proceed to application')").first
            if proceed_btn.is_visible(timeout=2000):
                print("Clicking 'Proceed to application'...")
                proceed_btn.click()
                time.sleep(2)

            # Check modal
            # 1. Fill Cover letter if present
            cover = page.locator("#cover_letter, textarea[name='cover_letter']").first
            if cover.is_visible(timeout=1500):
                val = cover.input_value()
                if len(val.strip()) < 10:
                    cover.fill(
                        "Dear Hiring Team,\n\n"
                        "I am a B.Tech student (AI & ML) at Universal AI University with hands-on experience in "
                        "Python, FastAPI, Django, and Machine Learning. I completed an AI internship at Univitt AI Technologies, "
                        "building production data pipelines and deploying REST APIs.\n\n"
                        "I am available immediately for this remote internship and excited to contribute.\n\n"
                        "GitHub: https://github.com/Shaunakrane914\nLinkedIn: https://www.linkedin.com/in/shaunak-rane-3980582ba/\n\n"
                        "Regards,\nShaunak Rane"
                    )
                    print("Filled cover letter.")

            # 2. Radios (Availability / Yes)
            radios = page.locator("input[type='radio']").all()
            for r in radios:
                try:
                    r_val = (r.get_attribute("value") or "").lower()
                    if any(x in r_val for x in ["yes", "1", "immediate"]):
                        r.check(timeout=500)
                except Exception:
                    pass

            # 3. Dropdowns / Selects
            selects = page.locator("select").all()
            for s in selects:
                try:
                    options = s.locator("option").all()
                    for opt in options:
                        txt = opt.inner_text().strip().lower()
                        val = opt.get_attribute("value") or ""
                        if txt in ["yes", "5", "4", "3", "advanced", "intermediate"]:
                            s.select_option(value=val)
                            break
                except Exception:
                    pass

            # 4. Textareas / custom questions
            textareas = page.locator("textarea").all()
            for ta in textareas:
                try:
                    if ta.is_visible(timeout=500) and not ta.input_value().strip():
                        ta.fill("I have extensive practical experience with Python and AI development from my internship and coursework, and I can deliver high-quality work independently.")
                except Exception:
                    pass

            # 5. Text inputs
            inputs = page.locator("input[type='text'], input[type='number']").all()
            for inp in inputs:
                try:
                    if inp.is_visible(timeout=500) and not inp.input_value().strip():
                        if inp.get_attribute("type") == "number":
                            inp.fill("1")
                        else:
                            inp.fill("Yes, available immediately")
                except Exception:
                    pass

            # 6. File input
            file_inp = page.locator("input[type='file']").first
            if file_inp.is_visible(timeout=500):
                file_inp.set_input_files(RESUME_PATH)
                print("Attached resume.")

            time.sleep(1)

            # 7. Submit
            sub_btn = page.locator("#submit, button[type='submit'], input[type='submit']").first
            if sub_btn.is_visible(timeout=2000):
                print("Clicking Submit...")
                sub_btn.click()
                time.sleep(4)

                # Capture proof screenshot
                shot_name = f"real_internshala_applied_{submitted_count+1}_{int(time.time())}.png"
                shot_path = os.path.join(SCREENSHOT_DIR, shot_name)
                page.screenshot(path=shot_path)
                print(f"Captured submission screenshot: {shot_path}")
                submitted_count += 1
            else:
                print("Submit button not clickable.")

        except Exception as err:
            print(f"Error on job: {err}")

    print(f"\nSuccessfully submitted {submitted_count} new Internshala applications.")

    # Live verification
    print("\nNavigating to Internshala Applications Dashboard to verify live status...")
    page.goto("https://internshala.com/student/applications", wait_until="domcontentloaded", timeout=25000)
    time.sleep(3)
    page.evaluate("window.scrollBy(0, 600)")
    time.sleep(2)
    verify_shot = os.path.join(SCREENSHOT_DIR, "live_internshala_dashboard_verified.png")
    page.screenshot(path=verify_shot)
    print(f"Saved live dashboard verification screenshot: {verify_shot}")

    context.close()
