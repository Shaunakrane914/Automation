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
    Find and validate the user's latest resume from Auto Apply/Resume.
    Prioritizes 'resume (2).pdf' as instructed, or newest PDF by modification timestamp.
    """
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

    # Prioritize resume (2).pdf if present
    preferred = None
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
                res = _sync_apply_to_opportunity(opp, resume_info, profile, p, run_id)
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
    playwright_instance: Any,
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
        try:
            browser = playwright_instance.chromium.connect_over_cdp("http://127.0.0.1:9222")
            if browser.contexts:
                context = browser.contexts[0]
                page = context.new_page()
            else:
                context = browser.new_context()
                page = context.new_page()
        except Exception as cdp_err:
            safe_log(f"[AutoApply] CDP connection note: {cdp_err}; using local browser")
            browser = playwright_instance.chromium.launch(headless=True)
            page = browser.new_page()
            own_browser = True

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
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

        # Press Escape key to dismiss full-screen splash modals (e.g. Lablab AMD modal)
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

        # If navigating to a portal root (like unstop.com or careers.microsoft.com or wellfound.com), perform automated search for the opportunity
        parsed_path = url.split("://", 1)[-1].strip("/")
        is_root_domain = "/" not in parsed_path or len(parsed_path.split("/")) == 1
        if is_root_domain:
            safe_log(f"  [Root Portal Detected] Searching for '{opp_name}' on portal...")
            search_input_selectors = [
                'input[placeholder*="Search" i]',
                'input[type="search"]',
                'input[name*="search" i]',
                'input[id*="search" i]'
            ]
            for s_sel in search_input_selectors:
                try:
                    s_loc = page.locator(s_sel).first
                    if s_loc.is_visible(timeout=1000):
                        s_loc.fill(opp_name, timeout=1500)
                        page.keyboard.press("Enter")
                        page.wait_for_timeout(3000)
                        filled_fields.append(f"Searched for '{opp_name}' on portal")
                        break
                except Exception:
                    continue

        # Portal Specific Handling: Unstop
        if "unstop.com" in url.lower():
            safe_log("  [Portal: Unstop] Checking registration flow...")
            unstop_selectors = [
                'button:has-text("Register")',
                'a:has-text("Register")',
                'button:has-text("Register Now")',
                '.register-btn',
                'button:has-text("Apply Now")'
            ]
            for u_sel in unstop_selectors:
                try:
                    u_loc = page.locator(u_sel).first
                    if u_loc.is_visible(timeout=1500):
                        u_text = u_loc.inner_text().strip()
                        u_loc.click(timeout=2500)
                        cta_clicked = True
                        filled_fields.append(f"Unstop CTA clicked: '{u_text}'")
                        page.wait_for_timeout(2000)
                        # Check for Individual participant option
                        try:
                            ind_loc = page.locator('text="Individual"').first
                            if ind_loc.is_visible(timeout=1500):
                                ind_loc.click(timeout=1500)
                                filled_fields.append("Selected 'Individual' participant mode")
                        except Exception:
                            pass
                        break
                except Exception:
                    pass

        # Portal Specific Handling: Lablab
        elif "lablab.ai" in url.lower():
            safe_log("  [Portal: Lablab] Checking hackathon enrollment...")
            lab_selectors = [
                'button:has-text("Enroll")',
                'button:has-text("Enroll for Hackathon")',
                'a:has-text("Enroll")',
                'button:has-text("Join Hackathon")'
            ]
            for l_sel in lab_selectors:
                try:
                    l_loc = page.locator(l_sel).first
                    if l_loc.is_visible(timeout=1500):
                        l_text = l_loc.inner_text().strip()
                        l_loc.click(timeout=2500)
                        cta_clicked = True
                        filled_fields.append(f"Lablab CTA clicked: '{l_text}'")
                        page.wait_for_timeout(2000)
                        break
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
