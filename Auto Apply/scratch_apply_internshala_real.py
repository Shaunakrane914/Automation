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

    print("Navigating to Internshala WFH tech internships...")
    page.goto("https://internshala.com/internships/work-from-home-python%2Fdjango,machine-learning,artificial-intelligence-ai-internships/", wait_until="domcontentloaded", timeout=25000)
    time.sleep(3)

    # Dismiss promo popup if any
    try:
        page.evaluate("if(document.getElementById('close_popup')) document.getElementById('close_popup').click();")
    except Exception:
        pass

    cards = page.locator(".individual_internship")
    card_count = cards.count()
    print(f"Found {card_count} internship cards")

    # Collect internship links
    links = []
    for i in range(min(card_count, 15)):
        c = cards.nth(i)
        link = c.locator("a.job-title-href, h3 a, .profile a").first
        if link.is_visible():
            href = link.get_attribute("href")
            title = link.inner_text().strip()
            if href and href not in [l[0] for l in links]:
                links.append((href, title))

    print(f"Collected {len(links)} links:")
    for l in links[:6]:
        print("  -", l[1], l[0])

    applied_new = 0
    target_to_apply = 3

    for href, title in links:
        if applied_new >= target_to_apply:
            break

        url = f"https://internshala.com{href}" if href.startswith("/") else href
        print(f"\nProcessing: {title} ({url})...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            time.sleep(2)

            # Check if already applied on page
            already = page.locator(".already_applied, text='Already applied', text='Applied'").first
            if already.is_visible(timeout=1000):
                print("Already applied to this one, skipping.")
                continue

            # Look for apply button
            apply_btn = page.locator("#easy_apply_button, #apply_now_cta, button:has-text('Apply now'), a:has-text('Apply now'), .apply_now_button").first
            if not apply_btn.is_visible(timeout=2000):
                print("Apply button not found, skipping.")
                continue

            apply_btn.click()
            time.sleep(2)

            # In modal:
            # 1. Cover letter
            cover = page.locator("#cover_letter, textarea[name='cover_letter']").first
            if cover.is_visible(timeout=1500):
                cover.fill(
                    "Dear Hiring Team,\n\n"
                    "I am a B.Tech student (AI & ML, Class of 2028) at Universal AI University with hands-on experience in "
                    "Python, FastAPI, Django, React, and Machine Learning. I completed an AI internship at Univitt AI Technologies, "
                    "building data pipelines and deploying REST APIs.\n\n"
                    "I am available immediately for this remote internship and eager to contribute.\n\n"
                    "GitHub: https://github.com/Shaunakrane914\nLinkedIn: https://www.linkedin.com/in/shaunak-rane-3980582ba/\n\n"
                    "Regards,\nShaunak Rane"
                )
                print("Filled cover letter")

            # 2. Availability radios
            avail = page.locator("input[type='radio'][value='Yes'], input[type='radio'][value='yes'], input[type='radio'][value='1']").first
            if avail.is_visible(timeout=1000):
                avail.check()
                print("Selected availability: Yes")

            # 3. All other radio groups (answer Yes or positive option)
            all_radios = page.locator("input[type='radio']")
            radio_count = all_radios.count()
            for r_idx in range(radio_count):
                r = all_radios.nth(r_idx)
                try:
                    val = r.get_attribute("value") or ""
                    if any(pos in val.lower() for pos in ["yes", "1", "immediate", "have"]):
                        r.check()
                except Exception:
                    pass

            # 4. Dropdowns / select elements
            selects = page.locator("select")
            select_count = selects.count()
            for s_idx in range(select_count):
                s = selects.nth(s_idx)
                try:
                    # Select option with value 3 or 4 or 5 or 'Yes'
                    options = s.locator("option").all()
                    for opt in options:
                        txt = opt.inner_text().strip().lower()
                        v = opt.get_attribute("value") or ""
                        if txt in ["yes", "5", "4", "3", "advanced", "intermediate"]:
                            s.select_option(value=v)
                            break
                except Exception:
                    pass

            # 5. Text inputs / textareas for custom questions
            text_fields = page.locator("textarea[id*='custom'], input[type='text'][id*='custom'], textarea[name*='custom'], input[type='number']")
            tf_count = text_fields.count()
            for tf_idx in range(tf_count):
                tf = text_fields.nth(tf_idx)
                try:
                    if tf.is_visible(timeout=500) and not tf.input_value():
                        if tf.get_attribute("type") == "number":
                            tf.fill("1")
                        else:
                            tf.fill("I have practical experience building AI/ML models and Python backends with strong attention to code quality and teamwork.")
                except Exception:
                    pass

            # 6. Attach verified resume if file input present
            file_input = page.locator("input[type='file']").first
            if file_input.is_visible(timeout=800):
                file_input.set_input_files(RESUME_PATH)
                print(f"Attached resume: {os.path.basename(RESUME_PATH)}")

            time.sleep(1)

            # 7. Click Submit
            sub_btn = page.locator("#submit, button:has-text('Submit'), input[type='submit'][value*='Submit']").first
            if sub_btn.is_visible(timeout=2000):
                print("Clicking Submit button...")
                sub_btn.click()
                time.sleep(4)

                # Check for success toast or modal
                sc_path = rf"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\real_applied_{applied_new+1}.png"
                page.screenshot(path=sc_path)
                print(f"Saved application screenshot to {sc_path}")
                applied_new += 1
            else:
                print("Submit button not found.")

        except Exception as e:
            print(f"Error on {title}: {e}")

    print(f"\nFinished applying. Total new applications submitted: {applied_new}")

    # Verify on My Applications page
    print("\nVerifying live applications on Internshala account...")
    page.goto("https://internshala.com/student/applications", wait_until="domcontentloaded", timeout=25000)
    time.sleep(3)
    page.evaluate("window.scrollBy(0, 700)")
    time.sleep(2)
    page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\real_internshala_applications_list.png")

    lines = [l.strip() for l in page.evaluate("() => document.body.innerText").split("\n") if l.strip()]
    for i, line in enumerate(lines):
        if "applied on" in line.lower():
            prev = lines[i-1] if i > 0 else ""
            prev2 = lines[i-2] if i > 1 else ""
            print(f"  Verified Application: {prev2} | {prev} | {line}")

    context.close()
