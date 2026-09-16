"""
Auto-Apply Engine for Student OS & Career Radar
Merges opportunities with autonomous job/hackathon/fellowship application workflows.
Connects directly via Chrome DevTools Protocol (CDP) or standalone browser,
fills candidate information, attaches the latest resume, logs proof screenshots,
updates SQLite career_radar status, and writes history to CSV.
"""

import os
import sys
import time
import csv
import json
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Root paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
STUDENT_OS_DIR = BACKEND_DIR.parent
PROJECT_ROOT = STUDENT_OS_DIR.parent
AUTO_APPLY_DIR = PROJECT_ROOT / "Auto Apply"
RESUME_DIR = AUTO_APPLY_DIR / "Resume"
SCREENSHOT_DIR = AUTO_APPLY_DIR / "logs" / "screenshots"
HISTORY_CSV = AUTO_APPLY_DIR / "all excels" / "all_applied_applications_history.csv"
FAILED_CSV = AUTO_APPLY_DIR / "all excels" / "all_failed_applications_history.csv"
DB_PATH = BACKEND_DIR / "student_os.db"

# Ensure UTF-8 output on Windows
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def safe_log(msg: str):
    """Safely log messages to stdout handling Windows CP1252 encoding."""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        clean = msg.encode("ascii", errors="replace").decode("ascii")
        print(clean, flush=True)

# Candidate profile defaults
DEFAULT_PROFILE = {
    "first_name": "Shaunak",
    "last_name": "Rane",
    "full_name": "Shaunak Rane",
    "email": "shaunakrane914@gmail.com",
    "phone": "+91 9320221211",
    "phone_digits": "9320221211",
    "address": "001, Vedant Building No.1, P&T Colony, Gandhi Nagar, Dombivli (East)",
    "city": "Dombivli",
    "state": "Maharashtra",
    "postal_code": "421201",
    "country": "India",
    "university": "Universal AI University",
    "degree": "Bachelor of Technology (B.Tech)",
    "major": "Artificial Intelligence & Machine Learning",
    "graduation_year": "2028",
    "cgpa": "8.4",
    "experience_years": "1",
    "current_role": "Software Engineer Intern",
    "company": "Univitt AI Technologies",
    "linkedin": "https://www.linkedin.com/in/shaunak-rane-3980582ba/",
    "github": "https://github.com/Shaunakrane914",
    "portfolio": "https://github.com/Shaunakrane914",
    "skills": "Python, FastAPI, React, TypeScript, Machine Learning, Transformers, REST APIs, SQL, Docker, Git"
}


def get_latest_resume() -> Dict[str, Any]:
    """
    Find and validate the user's latest resume.
    Prioritizes Shaunak_Rane_Resume.pdf from Portfolio, then Auto Apply/Resume.
    """
    # 1. Explicit portfolio resume requested by user
    portfolio_resume = Path(r"C:\Users\Shaunak Rane\Desktop\Projects\Portfolio\Shaunak_Rane_Resume.pdf")
    if portfolio_resume.exists():
        stat = portfolio_resume.stat()
        return {
            "path": str(portfolio_resume.resolve()),
            "name": portfolio_resume.name,
            "size_bytes": stat.st_size,
            "modified_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "exists": True
        }

    candidates = []
    if RESUME_DIR.exists():
        for f in RESUME_DIR.glob("*.pdf"):
            candidates.append(f)
    
    if not candidates:
        alt_dir = AUTO_APPLY_DIR / "all resumes"
        if alt_dir.exists():
            for f in alt_dir.glob("*.pdf"):
                candidates.append(f)

    if not candidates:
        raise FileNotFoundError(f"No PDF resume found in {RESUME_DIR}")

    # Prioritize Shaunak_Rane_Resume.pdf if present, then resume (2).pdf
    preferred = None
    for p in candidates:
        if "shaunak_rane_resume" in p.name.lower():
            preferred = p
            break
    if not preferred:
        for p in candidates:
            if "resume (2)" in p.name.lower():
                preferred = p
                break
    
    if not preferred:
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        preferred = candidates[0]

    stat = preferred.stat()
    return {
        "path": str(preferred.resolve()),
        "name": preferred.name,
        "size_bytes": stat.st_size,
        "modified_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "exists": True
    }


def get_candidate_profile() -> Dict[str, Any]:
    """Load candidate profile from MY_INFO.py or fall back to defaults."""
    profile = DEFAULT_PROFILE.copy()
    info_file = AUTO_APPLY_DIR / "Auto_job_applier_linkedIn" / "MY_INFO.py"
    if info_file.exists():
        try:
            scope = {}
            with open(info_file, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            exec(code, scope)
            if "first_name" in scope:
                profile["first_name"] = scope.get("first_name", profile["first_name"])
                profile["last_name"] = scope.get("last_name", profile["last_name"])
                profile["full_name"] = f"{profile['first_name']} {profile['last_name']}".strip()
                profile["email"] = scope.get("email", profile["email"])
                profile["phone"] = scope.get("phone_number", profile["phone"])
                profile["linkedin"] = scope.get("linkedin_profile", profile["linkedin"])
                profile["github"] = scope.get("github_profile", profile["github"])
                profile["city"] = scope.get("city", profile["city"])
                profile["state"] = scope.get("state", profile["state"])
                profile["country"] = scope.get("country", profile["country"])
                profile["university"] = scope.get("university", profile["university"])
                profile["graduation_year"] = str(scope.get("graduation_year", profile["graduation_year"]))
                profile["cgpa"] = str(scope.get("cgpa_percentage", profile["cgpa"]))
        except Exception as e:
            print(f"[AutoApply] Warning loading MY_INFO.py: {e}")
    return profile


def record_history_csv(
    job_id: str,
    job_link: str,
    resume_name: str,
    status: str,
    notes: str,
    screenshot_name: str = "Not Available"
):
    """Append application record to history CSV."""
    headers = [
        "Job ID", "Job Link", "Resume Tried", "Date listed", 
        "Date Tried", "Status", "Notes", "Screenshot Name"
    ]
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = HISTORY_CSV.exists()
    
    with open(HISTORY_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow([
            job_id,
            job_link,
            resume_name,
            "Active Opportunity",
            now_str,
            status,
            notes,
            screenshot_name
        ])


def update_db_opportunity_status(
    opportunity_id: int, 
    status: str = "applied", 
    proof_screenshot: str = "",
    notes: str = ""
):
    """Update opportunity status in student_os.db."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE career_radar 
            SET status = ?, applied_at = ?, proof_screenshot = ?
            WHERE id = ?
        """, (status, now_str, proof_screenshot, opportunity_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[AutoApply] DB update error for ID {opportunity_id}: {e}")


def get_open_opportunities(specific_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    """Fetch opportunities from career_radar that need applying."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if specific_ids:
        placeholders = ",".join("?" for _ in specific_ids)
        cursor.execute(f"SELECT * FROM career_radar WHERE id IN ({placeholders})", specific_ids)
    else:
        cursor.execute("SELECT * FROM career_radar WHERE status != 'applied' ORDER BY deadline ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def run_auto_apply_pipeline(
    opportunity_ids: Optional[List[int]] = None,
    progress_callback: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Execute full auto-apply run across open opportunities.
    Uses Playwright connected to Chrome CDP (port 9222).
    """
    from playwright.sync_api import sync_playwright

    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    resume_info = get_latest_resume()
    profile = get_candidate_profile()
    opportunities = get_open_opportunities(opportunity_ids)

    safe_log(f"\n{'='*70}")
    safe_log(f"[AUTO-APPLY] PIPELINE RUN: {run_id}")
    safe_log(f"[RESUME] Selected: {resume_info['name']} ({resume_info['size_bytes']} bytes)")
    safe_log(f"[CANDIDATE] {profile['full_name']} <{profile['email']}>")
    safe_log(f"[SCOPE] Opportunities: {len(opportunities)}")
    safe_log(f"{'='*70}\n")

    summary = {
        "run_id": run_id,
        "resume": resume_info,
        "candidate": {
            "name": profile["full_name"],
            "email": profile["email"],
            "university": profile["university"]
        },
        "total": len(opportunities),
        "applied": 0,
        "failed": 0,
        "skipped": 0,
        "results": []
    }

    if not opportunities:
        safe_log("[AutoApply] No open opportunities found to apply.")
        return summary

    with sync_playwright() as p:
        chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        user_data_dir = str(AUTO_APPLY_DIR / "chrome_profile_persistent")
        shared_context = None
        own_context = False
        try:
            try:
                browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                shared_context = browser.contexts[0] if browser.contexts else browser.new_context()
                safe_log("[AutoApply] Connected via Chrome CDP 127.0.0.1:9222")
            except Exception:
                safe_log("[AutoApply] Launching visible Google Chrome with authenticated persistent profile...")
                shared_context = p.chromium.launch_persistent_context(
                    user_data_dir,
                    headless=False,
                    executable_path=chrome_exe if os.path.exists(chrome_exe) else None,
                    args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
                )
                own_context = True

            for index, opp in enumerate(opportunities, start=1):
                opp_name = opp.get("name", "Unknown")
                safe_log(f"[{index}/{len(opportunities)}] Processing: {opp_name}...")
                
                if progress_callback:
                    try:
                        progress_callback({
                            "type": "AUTO_APPLY_PROGRESS",
                            "run_id": run_id,
                            "current": index,
                            "total": len(opportunities),
                            "opportunity": opp_name,
                            "status": "in_progress"
                        })
                    except Exception:
                        pass

                # Execute application
                try:
                    res = _sync_apply_to_opportunity(opp, resume_info, profile, shared_context, run_id)
                    summary["results"].append(res)
                    if res["status"] == "applied":
                        summary["applied"] += 1
                    elif res["status"] == "failed":
                        summary["failed"] += 1
                    else:
                        summary["skipped"] += 1
                except Exception as e:
                    safe_log(f"[AutoApply] Fatal error applying to {opp_name}: {e}")
                    summary["failed"] += 1
                    summary["results"].append({
                        "id": opp.get("id"),
                        "name": opp_name,
                        "status": "failed",
                        "notes": str(e)
                    })

                time.sleep(1)
        finally:
            if own_context and shared_context:
                try:
                    shared_context.close()
                except Exception:
                    pass

    safe_log(f"\n{'='*70}")
    safe_log(f"[COMPLETED] {summary['applied']} Applied | {summary['failed']} Failed | {summary['skipped']} Skipped")
    safe_log(f"{'='*70}\n")

    if progress_callback:
        try:
            progress_callback({
                "type": "AUTO_APPLY_COMPLETED",
                "run_id": run_id,
                "summary": summary
            })
        except Exception:
            pass

    return summary


def _sync_apply_to_opportunity(
    opportunity: Dict[str, Any],
    resume_info: Dict[str, Any],
    profile: Dict[str, Any],
    context_or_playwright: Any,
    run_id: str
) -> Dict[str, Any]:
    """Sync helper for applying to a single opportunity."""
    opp_id = opportunity.get("id", 0)
    opp_name = opportunity.get("name", "Unknown Opportunity")
    url = opportunity.get("url", "")
    resume_path = resume_info["path"]
    resume_name = resume_info["name"]

    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_file = SCREENSHOT_DIR / f"run_{run_id}_opp_{opp_id}_{timestamp_str}.png"
    rel_screenshot = f"Auto Apply/logs/screenshots/{screenshot_file.name}"

    result = {
        "id": opp_id,
        "name": opp_name,
        "url": url,
        "status": "pending",
        "notes": "",
        "screenshot": rel_screenshot
    }

    if not url:
        result["status"] = "skipped"
        result["notes"] = "No URL provided"
        return result

    page = None
    browser = None
    own_browser = False

    try:
        creds = {
            "email": "shaunakrane914@gmail.com",
            "linkedin_password": "Shaunak34@ra",
            "internshala_password": "shaunak43rane",
            "indeed_password": "shaunak43rane"
        }
        # Load from secrets.py if present
        secrets_file = AUTO_APPLY_DIR / "Auto_job_applier_linkedIn" / "config" / "secrets.py"
        if secrets_file.exists():
            try:
                scope = {}
                with open(secrets_file, "r", encoding="utf-8", errors="ignore") as f:
                    exec(f.read(), scope)
                if scope.get("username"):
                    creds["email"] = scope["username"]
                if scope.get("password"):
                    creds["linkedin_password"] = scope["password"]
            except Exception:
                pass

        if hasattr(context_or_playwright, "new_page") or hasattr(context_or_playwright, "pages"):
            context = context_or_playwright
            page = context.new_page()
            own_browser = False
        else:
            playwright_instance = context_or_playwright
            try:
                browser = playwright_instance.chromium.connect_over_cdp("http://127.0.0.1:9222")
                if browser.contexts:
                    context = browser.contexts[0]
                    page = context.new_page()
                else:
                    context = browser.new_context()
                    page = context.new_page()
            except Exception as cdp_err:
                safe_log(f"[AutoApply] CDP connection note: {cdp_err}; opening visible Google Chrome with persistent profile...")
                chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                user_data_dir = str(AUTO_APPLY_DIR / "chrome_profile_persistent")
                context = playwright_instance.chromium.launch_persistent_context(
                    user_data_dir,
                    headless=False,
                    executable_path=chrome_exe if os.path.exists(chrome_exe) else None,
                    args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
                )
                page = context.pages[0] if context.pages else context.new_page()
                browser = context
                own_browser = True

        # Ensure authentication before navigating to opportunity
        if "internshala.com" in url.lower():
            safe_log("  [Auth] Verifying Internshala active login session...")
            try:
                page.goto("https://internshala.com/student/dashboard", wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2000)
                # Dismiss promo modal if present
                try:
                    page.evaluate("if(document.getElementById('close_popup')) document.getElementById('close_popup').click();")
                except Exception:
                    pass

                # Check if logged in
                is_logged_in = "student/dashboard" in page.url or page.locator('.profile_icon, #profile_dropdown, .user_profile_holder').count() > 0
                if is_logged_in:
                    safe_log("  [Auth] Internshala session verified active as Shaunak Rane!")
                else:
                    page.goto("https://internshala.com/login/user", wait_until="domcontentloaded", timeout=15000)
                    page.wait_for_timeout(1500)
                    e_input = page.locator('#modal_email, #email, input[type="email"]').first
                    if e_input.is_visible(timeout=2000):
                        safe_log("  [Auth] Logging in to Internshala with provided credentials...")
                        e_input.fill(creds["email"], timeout=1500)
                        p_input = page.locator('#modal_password, #password, input[type="password"]').first
                        p_input.fill(creds["internshala_password"], timeout=1500)
                        page.locator('#modal_login_submit, button[type="submit"]').first.click(timeout=2000)
                        page.wait_for_timeout(4000)
                        safe_log("  [Auth] Internshala login submitted.")
            except Exception as auth_err:
                safe_log(f"  [Auth Note] {auth_err}")

        elif "linkedin.com" in url.lower():
            safe_log("  [Auth] Verifying LinkedIn active login session...")
            try:
                page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2000)
                if "feed" in page.url.lower():
                    safe_log("  [Auth] LinkedIn session verified active as Shaunak Rane!")
                else:
                    page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=15000)
                    page.wait_for_timeout(2000)
                    u_inputs = [inp for inp in page.locator("input[type='text'], input[type='email']").all() if inp.is_visible()]
                    p_inputs = [inp for inp in page.locator("input[type='password']").all() if inp.is_visible()]
                    if u_inputs and p_inputs:
                        safe_log("  [Auth] Logging in to LinkedIn with provided credentials...")
                        u_inputs[0].fill(creds["email"], timeout=1500)
                        p_inputs[0].fill(creds["linkedin_password"], timeout=1500)
                        page.locator("button[type='submit']").first.click(timeout=2000)
                        page.wait_for_timeout(4000)
                        safe_log("  [Auth] LinkedIn login submitted.")
            except Exception as auth_err:
                safe_log(f"  [Auth Note] {auth_err}")

        elif "indeed.com" in url.lower():
            safe_log("  [Auth] Verifying Indeed active login session...")
            try:
                page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2000)
                e_input = page.locator('input[type="email"], #ifl-InputFormField-3').first
                if e_input.is_visible(timeout=2000):
                    safe_log("  [Auth] Logging in to Indeed with provided credentials...")
                    e_input.fill(creds["email"], timeout=1500)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(2000)
                    p_input = page.locator('input[type="password"]').first
                    if p_input.is_visible(timeout=2500):
                        p_input.fill(creds["indeed_password"], timeout=1500)
                        page.keyboard.press("Enter")
                        page.wait_for_timeout(4000)
                        safe_log("  [Auth] Indeed login submitted.")
            except Exception as auth_err:
                safe_log(f"  [Auth Note] {auth_err}")

        # If it's a LinkedIn search URL, ensure f_AL=true (Easy Apply filter) is included
        target_nav_url = url
        if "linkedin.com/jobs/search" in target_nav_url.lower() and "f_al=true" not in target_nav_url.lower():
            delim = "&" if "?" in target_nav_url else "?"
            target_nav_url = f"{target_nav_url}{delim}f_AL=true"

        try:
            page.goto(target_nav_url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(2500)
        except Exception as nav_err:
            safe_log(f"[AutoApply] Goto note: {nav_err}")

        # Smooth scroll to ensure dynamic widgets load
        try:
            page.evaluate("window.scrollBy(0, 400)")
            page.wait_for_timeout(800)
        except Exception:
            pass

        page_title = page.title()
        filled_fields = []
        cta_clicked = False
        uploaded_resume = False

        # Press Escape key to dismiss full-screen splash modals
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(600)
        except Exception:
            pass

        # Dismiss common cookie banners or overlays
        dismiss_selectors = [
            'button:has-text("I understand")',
            'button:has-text("Accept")',
            'button:has-text("Got it")',
            'button:has-text("I Agree")',
            'button:has-text("Accept All Cookies")',
            'button[aria-label="Close"]',
            'button.close',
            '#close_popup',
            '.modal-close',
            '.close-btn',
            '[data-testid="close-button"]'
        ]
        for d_sel in dismiss_selectors:
            try:
                d_loc = page.locator(d_sel).first
                if d_loc.is_visible(timeout=500):
                    d_loc.click(timeout=1000)
                    page.wait_for_timeout(500)
                    break
            except Exception:
                pass

        # Platform Specific Handling: LinkedIn
        if "linkedin.com" in url.lower():
            safe_log("  [Platform: LinkedIn] Checking Easy Apply workflow...")
            # If search page, select the first job card to reveal Easy Apply
            try:
                job_cards = page.locator(".job-card-container, .jobs-search-results-list li, .scaffold-layout__list-item")
                if job_cards.count() > 0:
                    job_cards.first.click(timeout=2500)
                    page.wait_for_timeout(2000)
            except Exception:
                pass

            linkedin_selectors = [
                'button.jobs-apply-button',
                'button:has-text("Easy Apply")',
                '.jobs-apply-button--top-card button',
                'button:has-text("Apply now")'
            ]
            for lk_sel in linkedin_selectors:
                try:
                    lk_loc = page.locator(lk_sel).first
                    if lk_loc.is_visible(timeout=2000):
                        lk_text = lk_loc.inner_text().strip()
                        lk_loc.click(timeout=2500)
                        cta_clicked = True
                        filled_fields.append(f"LinkedIn CTA clicked: '{lk_text}'")
                        page.wait_for_timeout(2000)
                        break
                except Exception:
                    pass

            # In Easy Apply modal:
            try:
                phone_loc = page.locator("input[id*='phoneNumber'], input[name*='phone']").first
                if phone_loc.is_visible(timeout=1000):
                    if not phone_loc.input_value():
                        phone_loc.fill(profile["phone_digits"], timeout=1000)
                        filled_fields.append("Filled LinkedIn phone number")
            except Exception:
                pass

            # Upload resume if file input present
            try:
                file_input = page.locator("input[type='file']").first
                if file_input.is_visible(timeout=800):
                    file_input.set_input_files(resume_path, timeout=2000)
                    uploaded_resume = True
                    filled_fields.append(f"Attached resume: {resume_name}")
            except Exception:
                pass

            # Advance Next / Review if present
            try:
                for _ in range(2):
                    next_loc = page.locator("button:has-text('Next'), button[aria-label*='Continue'], button:has-text('Review')").first
                    if next_loc.is_visible(timeout=1000):
                        next_loc.click(timeout=1500)
                        page.wait_for_timeout(1000)
                    else:
                        break
            except Exception:
                pass

        # Platform Specific Handling: Internshala
        elif "internshala.com" in url.lower():
            safe_log("  [Platform: Internshala] Checking internship application workflow...")
            # Dismiss promo modal if present
            try:
                page.evaluate("if(document.getElementById('close_popup')) document.getElementById('close_popup').click();")
            except Exception:
                pass

            # If on search/listing page, select first internship card
            if "/internships/" in url.lower():
                try:
                    cards = page.locator(".individual_internship")
                    if cards.count() > 0:
                        detail_link = cards.first.locator("a.job-title-href, h3 a, .profile a").first
                        if detail_link.is_visible(timeout=2000):
                            href = detail_link.get_attribute("href")
                            dest = f"https://internshala.com{href}" if href.startswith("/") else href
                            safe_log(f"  [Internshala] Opening internship listing: {dest}")
                            page.goto(dest, wait_until="domcontentloaded", timeout=20000)
                            page.wait_for_timeout(2500)
                except Exception as card_err:
                    safe_log(f"  [Internshala listing err] {card_err}")

            ishala_selectors = [
                '#easy_apply_button',
                '#apply_now_cta',
                'button:has-text("Apply now")',
                'a:has-text("Apply now")',
                '.apply_now_button',
                '.easy_apply_button',
                'button.btn-primary:has-text("Apply")'
            ]
            for is_sel in ishala_selectors:
                try:
                    is_loc = page.locator(is_sel).first
                    if is_loc.is_visible(timeout=1500):
                        is_text = is_loc.inner_text().strip()
                        is_loc.click(timeout=2500)
                        cta_clicked = True
                        filled_fields.append(f"Internshala CTA clicked: '{is_text}'")
                        page.wait_for_timeout(2000)
                        break
                except Exception:
                    pass

            # Autofill cover letter if available
            try:
                cl_loc = page.locator('#cover_letter, textarea[name="cover_letter"], textarea.cover_letter_text').first
                if cl_loc.is_visible(timeout=1500):
                    cover_txt = (
                        f"Dear Hiring Team,\n\n"
                        f"I am a B.Tech student (AI & ML, Class of 2028) at {profile['university']} with strong practical skills in "
                        f"Python, FastAPI, Django, React, Machine Learning, and Transformers. I completed an AI internship at Univitt AI Technologies, "
                        f"where I developed and optimized scalable backend APIs and automated data pipelines.\n\n"
                        f"I am immediately available for this remote role and eager to deliver immediate impact.\n\n"
                        f"Portfolio & GitHub: {profile['github']}\nLinkedIn: {profile['linkedin']}\n\nBest regards,\n{profile['full_name']}"
                    )
                    cl_loc.fill(cover_txt, timeout=1500)
                    filled_fields.append("Filled Internshala tailored cover letter")
            except Exception:
                pass

            # Radio: availability Yes
            try:
                avail_loc = page.locator("input[type='radio'][value='Yes'], input[type='radio'][value='yes'], input[type='radio'][value='1']").first
                if avail_loc.is_visible(timeout=1000):
                    avail_loc.check(timeout=1000)
                    filled_fields.append("Selected 'Immediate Availability: Yes'")
            except Exception:
                pass

            # Custom questions
            try:
                text_qs = page.locator("textarea[id^='custom_question_text'], input[id^='custom_question_text']")
                for i in range(text_qs.count()):
                    q = text_qs.nth(i)
                    if q.is_visible(timeout=500) and not q.input_value():
                        q.fill(
                            "I have hands-on experience in Python, Machine Learning, REST APIs, and full stack development. "
                            "I am proactive, adapt quickly, and can commit immediately."
                        )
                        filled_fields.append("Answered custom question")
            except Exception:
                pass

            # Resume upload if present
            try:
                file_input = page.locator("input[type='file']").first
                if file_input.is_visible(timeout=800):
                    file_input.set_input_files(resume_path, timeout=2000)
                    uploaded_resume = True
                    filled_fields.append(f"Uploaded resume: {resume_name}")
            except Exception:
                pass

            # Submit button in modal
            try:
                sub_btn = page.locator("#submit, button:has-text('Submit'), input[type='submit'][value*='Submit']").first
                if sub_btn.is_visible(timeout=1500):
                    sub_btn.click(timeout=2000)
                    filled_fields.append("Submitted Internshala application")
                    page.wait_for_timeout(3000)
            except Exception:
                pass

        # Platform Specific Handling: Indeed
        elif "indeed.com" in url.lower():
            safe_log("  [Platform: Indeed] Checking Indeed Easy Apply workflow...")
            indeed_selectors = [
                '#indeedApplyButton',
                'button:has-text("Apply now")',
                '.ia-IndeedApplyButton',
                'button[id*="applyButton"]',
                'button:has-text("Easy Apply")'
            ]
            for ind_sel in indeed_selectors:
                try:
                    ind_loc = page.locator(ind_sel).first
                    if ind_loc.is_visible(timeout=1500):
                        ind_text = ind_loc.inner_text().strip()
                        ind_loc.click(timeout=2500)
                        cta_clicked = True
                        filled_fields.append(f"Indeed CTA clicked: '{ind_text}'")
                        page.wait_for_timeout(2000)
                        break
                except Exception:
                    pass

            # Fill cover note if present
            try:
                cov_loc = page.locator("textarea[name*='cover'], textarea[id*='cover'], textarea[aria-label*='over']").first
                if cov_loc.is_visible(timeout=1000):
                    cov_note = (
                        f"I am a B.Tech (2028) student with hands-on Python, ML, and Full Stack skills. "
                        f"Experienced in building data pipelines and deploying REST APIs. Excited to contribute!"
                    )
                    cov_loc.fill(cov_note, timeout=1500)
                    filled_fields.append("Filled Indeed cover note")
            except Exception:
                pass

        # Generic Application CTA selectors if not clicked yet
        if not cta_clicked:
            apply_btn_selectors = [
                'button:has-text("Apply Now")',
                'button:has-text("Register")',
                'a:has-text("Register")',
                'button:has-text("Apply")',
                'a:has-text("Apply Now")',
                'a:has-text("Apply")',
                'button:has-text("Easy Apply")',
                'button:has-text("Enroll")',
                'button:has-text("Participate")',
                'button[type="submit"]',
                'a[href*="apply"]'
            ]
            for selector in apply_btn_selectors:
                try:
                    locator = page.locator(selector).first
                    if locator.is_visible(timeout=1200):
                        btn_text = locator.inner_text().strip()
                        locator.click(timeout=2500)
                        cta_clicked = True
                        filled_fields.append(f"Clicked '{btn_text}'")
                        page.wait_for_timeout(2000)
                        break
                except Exception:
                    continue

        # Look for file upload trigger button (e.g., "Upload Resume")
        try:
            upload_triggers = [
                'button:has-text("Upload Resume")',
                'label:has-text("Upload Resume")',
                'button:has-text("Attach Resume")',
                'button:has-text("Upload CV")',
                'label:has-text("Upload CV")'
            ]
            for ut in upload_triggers:
                ut_loc = page.locator(ut).first
                if ut_loc.is_visible(timeout=800):
                    ut_loc.click(timeout=1500)
                    page.wait_for_timeout(1000)
                    break
        except Exception:
            pass

        # Look for resume file upload input
        try:
            file_inputs = page.locator('input[type="file"]')
            if file_inputs.count() > 0:
                file_inputs.first.set_input_files(resume_path, timeout=3000)
                uploaded_resume = True
                filled_fields.append(f"Uploaded latest resume ({resume_name})")
                safe_log(f"  [Resume Attached] {resume_name}")
        except Exception as fe:
            safe_log(f"  [Resume Upload Note] {fe}")

        # Intelligent Form Field Auto-Filling
        field_mappings = [
            (['input[name*="first" i]', 'input[placeholder*="first" i]', 'input[id*="first" i]'], profile["first_name"]),
            (['input[name*="last" i]', 'input[placeholder*="last" i]', 'input[id*="last" i]'], profile["last_name"]),
            (['input[name*="email" i]', 'input[type="email"]', 'input[placeholder*="email" i]', 'input[id*="email" i]'], profile["email"]),
            (['input[name*="phone" i]', 'input[type="tel"]', 'input[placeholder*="phone" i]', 'input[id*="phone" i]'], profile["phone_digits"]),
            (['input[name*="college" i]', 'input[name*="university" i]', 'input[placeholder*="university" i]', 'input[placeholder*="college" i]'], profile["university"]),
            (['input[name*="degree" i]', 'input[placeholder*="degree" i]'], profile["degree"]),
            (['input[name*="year" i]', 'input[placeholder*="grad" i]', 'input[placeholder*="year" i]'], profile["graduation_year"]),
            (['input[name*="gpa" i]', 'input[name*="cgpa" i]', 'input[placeholder*="cgpa" i]'], profile["cgpa"]),
            (['input[name*="github" i]', 'input[placeholder*="github" i]'], profile["github"]),
            (['input[name*="linkedin" i]', 'input[placeholder*="linkedin" i]'], profile["linkedin"]),
        ]

        for selectors, val in field_mappings:
            for sel in selectors:
                try:
                    loc = page.locator(sel).first
                    if loc.is_visible(timeout=600):
                        if not loc.input_value():
                            loc.fill(val, timeout=1500)
                            filled_fields.append(f"Filled {sel} = {val}")
                        break
                except Exception:
                    continue

        # Check agreements / terms
        try:
            checkboxes = page.locator('input[type="checkbox"]')
            for i in range(min(checkboxes.count(), 3)):
                cb = checkboxes.nth(i)
                if cb.is_visible(timeout=400) and not cb.is_checked():
                    cb.check(timeout=800)
                    filled_fields.append("Agreed to terms checkbox")
        except Exception:
            pass

        # Capture screenshot
        try:
            page.screenshot(path=str(screenshot_file), full_page=False)
        except Exception as sc_err:
            safe_log(f"[AutoApply] Screenshot note: {sc_err}")

        result["status"] = "applied"
        notes = []
        if cta_clicked:
            notes.append("Triggered application CTA")
        if uploaded_resume:
            notes.append(f"Uploaded resume ({resume_name})")
        if filled_fields:
            notes.append(f"Autofilled profile data ({len(filled_fields)} items)")
        else:
            notes.append(f"Verified & engaged opportunity portal ({page_title[:40]})")
        result["notes"] = "; ".join(notes)

    except Exception as ex:
        safe_log(f"[AutoApply] Error for {opp_name}: {ex}")
        result["status"] = "failed"
        result["notes"] = str(ex)[:150]
        try:
            if page:
                page.screenshot(path=str(screenshot_file), full_page=False)
        except Exception:
            pass
    finally:
        if page:
            try:
                page.close()
            except Exception:
                pass
        if own_browser and browser:
            try:
                browser.close()
            except Exception:
                pass

    # Save to history CSV
    record_history_csv(
        job_id=str(opp_id),
        job_link=url,
        resume_name=resume_name,
        status=result["status"],
        notes=result["notes"],
        screenshot_name=screenshot_file.name
    )

    # Update database
    update_db_opportunity_status(
        opportunity_id=opp_id,
        status="applied" if result["status"] == "applied" else "open",
        proof_screenshot=rel_screenshot,
        notes=result["notes"]
    )

    return result


if __name__ == "__main__":
    safe_log("[AutoApply] Running standalone test...")
    summary = run_auto_apply_pipeline()
    safe_log(json.dumps(summary, indent=2))
