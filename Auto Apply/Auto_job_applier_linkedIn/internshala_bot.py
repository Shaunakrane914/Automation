"""
Internshala Auto-Apply Bot
Auto-applies to tech internships on Internshala with title filtering,
cover letter autofill, and full tracking.
"""

import time
import sys
import csv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    StaleElementReferenceException, ElementClickInterceptedException
)

# ──────────────────────────────────────────────
#  CONFIGURATION — edit these as needed
# ──────────────────────────────────────────────
EMAIL    = "shaunakrane914@gmail.com"
PASSWORD = "shaunak43rane"

SEARCH_KEYWORDS = [
    "AI Intern",
    "Machine Learning Intern",
    "Backend Developer Intern",
    "Python Developer Intern",
    "Full Stack Intern",
    "Django Developer Intern",
    "Data Engineer Intern",
    "DevOps Intern",
    "Software Developer Intern",
    "Deep Learning Intern",
]

# Work from Home search (True = WFH only, False = all locations including on-site)
WFH_ONLY = False

# Location filter — leave empty string "" for all India
LOCATION = "Mumbai"   # e.g. "Mumbai", "Bangalore", "Delhi", "" for all

# ── WHITELIST: title must contain at least one of these ──────────────
# If NONE of these appear in the title, the job is skipped immediately.
# This is the primary filter — catches everything the blacklist misses.
TITLE_MUST_HAVE = [
    "software", "developer", "engineer", "dev",
    "python", "django", "fastapi", "flask",
    "backend", "full stack", "fullstack",
    "machine learning", "ml ", "ai ", "artificial intelligence",
    "deep learning", "nlp", "computer vision",
    "data engineer", "data science", "data pipeline",
    "devops", "cloud", "docker", "kubernetes", "aws",
    "react", "node", "frontend", "web dev",
    "intern",  # broad fallback — intern in the title is still fine
]

# ── BLACKLIST: skip if any of these appear in the title ─────────────
# Applied AFTER the whitelist, to remove false positives like
# "Marketing Intern" (passes whitelist via "intern", blocked here).
TITLE_BAD_WORDS = [
    # Non-tech functions
    "marketing", "sales", "business development", "bd intern",
    "social media", "content", "seo", "digital marketing",
    "graphic", "design", "ui/ux", "ux research",
    "interior", "fashion", "animation", "video edit", "video",
    "hr ", "human resource", "recruiter", "talent",
    "finance", "accounting", "ca ", "chartered",
    "legal", "law", "compliance",
    "customer support", "customer success", "client servicing",
    "operations", "supply chain", "logistics", "scm",
    "real estate", "realty",
    "research analyst", "market research", "primary research",
    "data entry", "data collection",
    "event", "pr intern", "public relation",
    "volunteer", "volunteering", "ngo",
    "teaching", "tutor", "education",
    "mechanical", "civil", "electrical", "hardware", "embedded",
    # Business ops / admin (false positives from "intern" whitelist)
    "admin", "e-commerce", "ecommerce", "management",
    "community", "coordinator", "assistant", "support",
    "procurement", "purchase", "vendor",
    # Senior/leadership
    "manager", "lead ", "director", "head of", "vp ", "vice president",
    "architect", "principal", "staff ",
]

# Cover letter template — {keyword} and {company} are replaced at runtime
COVER_LETTER = """Dear Hiring Team,

I am a B.Tech student (2028) at Universal AI Technology with hands-on experience in Python, FastAPI, Django, React, Machine Learning, and NLP. I have completed an end-to-end AI internship at Univitt AI Technologies (Sodexo), where I built data pipelines, trained ML models, and deployed REST APIs.

I am excited to apply for the {keyword} role at {company} and am confident I can contribute meaningfully from day one.

LinkedIn: https://www.linkedin.com/in/shaunak-rane-3980582ba/
GitHub  : https://github.com/Shaunakrane914

Regards,
Shaunak Rane
"""

# ──────────────────────────────────────────────
#  CSV log file
# ──────────────────────────────────────────────
LOG_FILE = os.path.join(os.path.dirname(__file__), "internshala_applied_jobs.csv")


def log(msg: str):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        clean_msg = msg.encode('ascii', 'ignore').decode('ascii')
        print(clean_msg, flush=True)


def can_prompt_user() -> bool:
    """Return True only when stdin is interactive (TTY)."""
    try:
        return bool(sys.stdin) and sys.stdin.isatty()
    except Exception:
        return False


def write_csv(row: dict):
    fieldnames = ["timestamp", "keyword", "title", "company", "stipend", "duration", "url", "status", "notes"]
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def is_relevant_title(title: str) -> tuple[bool, str]:
    """
    Dual filter: whitelist-first, then blacklist.
    Returns (True, "") to apply, or (False, reason) to skip.
    """
    tl = title.lower()
    # 1. Must contain at least one tech keyword
    if not any(w in tl for w in TITLE_MUST_HAVE):
        return False, f"no tech keyword in title"
    # 2. Must not contain any bad word
    for word in TITLE_BAD_WORDS:
        if word in tl:
            return False, f"blocked word '{word}'"
    return True, ""


# ──────────────────────────────────────────────
#  BOT CLASS
# ──────────────────────────────────────────────
class InternshalaBot:
    def __init__(self):
        self.driver: webdriver.Chrome | None = None
        self.wait: WebDriverWait | None = None
        self.applied_count  = 0
        self.skipped_count  = 0
        self.failed_count   = 0
        self.applied_urls: set[str] = set()

    # ── Driver setup ──────────────────────────
    def setup_driver(self):
        log("🚀 Starting Chrome...")
        try:
            opts = Options()
            opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.driver = webdriver.Chrome(options=opts)
            self.wait = WebDriverWait(self.driver, 15)
            log("✅ Connected to active Chrome session on 127.0.0.1:9222!")
            return
        except Exception as cdp_err:
            log(f"  CDP session note: {cdp_err}. Initializing local Chrome driver...")

        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--start-maximized")
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        except Exception:
            self.driver = webdriver.Chrome(options=options)
        self.wait   = WebDriverWait(self.driver, 15)
        log("✅ Chrome ready!")

    # ── Login ─────────────────────────────────
    def login(self):
        log("\n🔐 Logging in to Internshala...")
        self.driver.get("https://internshala.com")
        time.sleep(3)

        try:
            # Open login modal — verified selector: .login-cta
            login_btn = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".login-cta")
            ))
            login_btn.click()
            time.sleep(2)
        except TimeoutException:
            log("⚠️  Login button not found — maybe already at login page, continuing...")

        try:
            # Fill email — verified: #modal_email
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "modal_email")))
            email_field.clear()
            email_field.send_keys(EMAIL)

            # Fill password — verified: #modal_password
            pw_field = self.driver.find_element(By.ID, "modal_password")
            pw_field.clear()
            pw_field.send_keys(PASSWORD)

            # Submit — verified: #modal_login_submit
            submit = self.driver.find_element(By.ID, "modal_login_submit")
            submit.click()
            time.sleep(5)
            log("✅ Logged in!")
        except Exception as e:
            if can_prompt_user():
                log(f"❌ Auto-login failed ({e}). Please login manually in the browser, then press Enter...")
                try:
                    input()
                except EOFError:
                    pass
            else:
                log(f"⚠️  Auto-login failed ({e}); waiting 10s for manual login or proceeding...")
                time.sleep(10)

    # ── Apply WFH filter ──────────────────────
    def apply_wfh_filter(self):
        if not WFH_ONLY:
            return
        try:
            checkbox = self.wait.until(EC.presence_of_element_located((By.ID, "work_from_home")))
            if not checkbox.is_selected():
                self.driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(2)
                log("✅ Applied 'Work from Home' filter")
        except Exception:
            try:
                label = self.driver.find_element(By.XPATH, "//label[contains(text(),'Work from home') or contains(text(),'Work From Home')]")
                label.click()
                time.sleep(2)
                log("✅ Applied WFH filter (label click)")
            except Exception as e:
                log(f"⚠️  Could not apply WFH filter: {e}")

    # ── Search ────────────────────────
    def do_search(self):
        """
        Build a single Internshala URL combining ALL keywords at once
        (Internshala supports /keywords-python,ai,ml/ syntax).
        Appends /location-city/ if LOCATION is set.
        """
        # Build comma-separated keyword slug: "AI Intern" -> "ai-intern"
        slugs = ["-".join(kw.lower().split()) for kw in SEARCH_KEYWORDS]
        kw_part = ",".join(slugs)

        url = f"https://internshala.com/internships/keywords-{kw_part}/"
        if LOCATION:
            loc_slug = "-".join(LOCATION.lower().split())
            url += f"location-{loc_slug}/"

        log(f"\n{'='*60}")
        log(f"🔍 Searching all keywords in one go")
        log(f"   Keywords : {', '.join(SEARCH_KEYWORDS)}")
        log(f"   Location : {LOCATION or 'All India'}")
        log(f"   WFH only : {WFH_ONLY}")
        log(f"   URL      : {url}")
        log(f"{'='*60}")

        self.driver.get(url)
        time.sleep(4)
        self.apply_wfh_filter()
        time.sleep(2)

    # ── Get listing IDs (stale-safe) ─────────
    def get_listing_ids(self) -> list[str]:
        """
        Collect internship IDs as strings — never go stale.
        Re-fetch the element fresh by ID right before processing.
        """
        try:
            raw = self.driver.find_elements(By.CSS_SELECTOR, ".individual_internship")
            ids = []
            for el in raw:
                try:
                    iid = el.get_attribute("id") or el.get_attribute("data-internship-id")
                    if not iid:
                        # Fallback: get the detail link href and use it as unique key
                        try:
                            a = el.find_element(By.CSS_SELECTOR, "a.job-title-href, h3 a")
                            iid = a.get_attribute("href") or ""
                        except Exception:
                            iid = ""
                    if iid:
                        ids.append(iid)
                except StaleElementReferenceException:
                    pass
            log(f"📋 Found {len(ids)} listings")
            return ids
        except Exception:
            return []

    def _get_card_by_id(self, iid: str):
        """Re-fetch a live card element by its ID/href key."""
        try:
            if iid.startswith("http"):
                # ID is a URL — find card containing that href
                return self.driver.find_element(
                    By.XPATH, f"//div[contains(@class,'individual_internship')][.//a[@href='{iid}']]"
                )
            return self.driver.find_element(
                By.CSS_SELECTOR, f".individual_internship#{iid}, [data-internship-id='{iid}']"
            )
        except Exception:
            return None

    # ── Try to extract text from a card ──────
    def _card_text(self, card, selector: str, default="Unknown") -> str:
        try:
            return card.find_element(By.CSS_SELECTOR, selector).text.strip()
        except Exception:
            return default

    def _card_title(self, card) -> str:
        """Extract internship title with fallback selectors."""
        for sel in [".job-title-href", "h3.profile a", ".heading_4_5.profile a", "h3.profile", "h3"]:
            val = self._card_text(card, sel)
            if val and val != "Unknown":
                return val
        return "Unknown"

    def _card_company(self, card) -> str:
        """Extract company name with fallback selectors."""
        for sel in [".company_name", "p.company-name", "h4.company-name", "h4"]:
            val = self._card_text(card, sel)
            if val and val != "Unknown":
                return val
        return "Unknown"

    # ── Handle Easy Apply modal ───────────────
    def handle_application_modal(self, keyword: str, company: str) -> bool:
        """
        Fill the #easy_apply_modal and submit.
        Handles: cover letter, availability radio, custom questions, submit.
        Returns True on success.
        """
        try:
            # Wait for the modal to appear
            modal = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "easy_apply_modal"))
            )
            time.sleep(1)
            log("  📋 Modal opened")

            # 1. Cover letter (some internships have it)
            try:
                cover = modal.find_element(
                    By.CSS_SELECTOR,
                    "#cover_letter, textarea[name='cover_letter'], "
                    "textarea.cover_letter_text, "
                    ".cover_letter_input textarea"
                )
                cover.clear()
                cover.send_keys(COVER_LETTER.format(keyword=keyword, company=company))
                log("  ✍️  Cover letter filled")
                time.sleep(0.5)
            except Exception:
                pass  # No cover letter field — that's OK

            # 2. Availability radio — click "Yes" (immediate availability)
            try:
                yes_radio = modal.find_element(
                    By.XPATH,
                    ".//input[@type='radio' and (@value='Yes' or @value='yes' or @value='1')]"
                )
                self.driver.execute_script("arguments[0].click();", yes_radio)
                log("  ✅ Availability: Yes")
            except Exception:
                pass

            # 3. Custom text questions — answer generically
            try:
                text_qs = modal.find_elements(
                    By.CSS_SELECTOR,
                    "textarea[id^='custom_question_text'], "
                    "input[id^='custom_question_text']"
                )
                for q in text_qs:
                    if not q.get_attribute("value"):
                        q.send_keys(
                            "I am a B.Tech (2028) student with hands-on experience in "
                            "Python, Machine Learning, FastAPI, Django, and Full Stack dev. "
                            "I am immediately available and eager to contribute."
                        )
                if text_qs:
                    log(f"  📝 Answered {len(text_qs)} text question(s)")
            except Exception:
                pass

            # 4. Custom numeric questions — answer with 1
            try:
                num_qs = modal.find_elements(
                    By.CSS_SELECTOR,
                    "input[id^='custom_question_numeric'], "
                    "input[type='number'][id^='custom_question']"
                )
                for q in num_qs:
                    if not q.get_attribute("value"):
                        q.clear()
                        q.send_keys("1")
                if num_qs:
                    log(f"  🔢 Answered {len(num_qs)} numeric question(s)")
            except Exception:
                pass

            # 5. Submit — confirmed selector: #submit
            submitted = False
            for sel, by in [
                ("submit",                                By.ID),
                ("//button[contains(text(),'Submit')]",   By.XPATH),
                ("//button[contains(text(),'Apply')]",    By.XPATH),
                ("//input[@type='submit']",               By.XPATH),
            ]:
                try:
                    btn = WebDriverWait(self.driver, 6).until(
                        EC.element_to_be_clickable((by, sel))
                    )
                    self.driver.execute_script("arguments[0].click();", btn)
                    submitted = True
                    log("  📤 Submitted!")
                    time.sleep(3)
                    break
                except Exception:
                    continue

            if not submitted:
                log("  ⚠️  Could not find submit button")
                return False

            # 6. Check for success confirmation
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                        ".success_message, .applied-message, "
                        "[class*='success'], #application-success"
                    ))
                )
                log("  ✅ Application confirmed!")
            except TimeoutException:
                log("  ✅ Submitted (no explicit confirmation shown)")

            return True

        except TimeoutException:
            log("  ❌ Modal did not open (TimeoutException)")
            return False
        except Exception as e:
            log(f"  ❌ Modal error: {e}")
            return False

    # ── Process one listing card ──────────────
    def process_card(self, card, keyword: str) -> str:
        """Returns 'applied', 'skipped', or 'failed'."""
        try:
            # Extract details from card (before opening)
            title   = self._card_title(card)
            company = self._card_company(card)
            stipend = self._card_text(card, ".stipend")
            dur     = self._card_text(card, ".item_body, .internship-other-details .item_body")

            if title == "Unknown":
                return "skipped"

            # Title filter — whitelist (must have tech keyword) + blacklist
            ok, reason = is_relevant_title(title)
            if not ok:
                log(f"  ⏭️  Skipped '{title}' — {reason}")
                return "skipped"

            # Get URL — look for the detail link in the card
            try:
                link_el = card.find_element(By.CSS_SELECTOR, 
                    "a.job-title-href, a.view_detail_button, a[href*='/internship/detail'], h3 a")
                url = link_el.get_attribute("href") or ""
            except Exception:
                url = ""

            if url in self.applied_urls:
                log(f"  🔁 Already applied to '{title}' — skipping")
                return "skipped"

            log(f"\n  📌 {title} @ {company}")
            log(f"     Stipend: {stipend}  |  Duration: {dur}")

            # Open listing detail page
            if url:
                self.driver.execute_script("window.open(arguments[0]);", url)
                self.driver.switch_to.window(self.driver.window_handles[-1])
                time.sleep(3)
            else:
                try:
                    card.find_element(By.CSS_SELECTOR, ".view_detail_button, a").click()
                    time.sleep(3)
                except Exception:
                    log("  ❌ Could not open listing")
                    return "failed"

            current_url = self.driver.current_url

            # Check if already applied
            try:
                if self.driver.find_element(By.XPATH, "//*[contains(text(),'You have already applied')]"):
                    log("  ℹ️  Already applied")
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.applied_urls.add(current_url)
                    return "skipped"
            except Exception:
                pass

            # Find and click Apply Now
            # Confirmed from live DOM: #top_easy_apply_button
            apply_clicked = False
            apply_selectors = [
                ("#top_easy_apply_button", By.ID),
                (".top_easy_apply_button", By.CSS_SELECTOR),
                (".top_apply_now_cta",     By.CSS_SELECTOR),
                ("//button[contains(text(),'Apply now')]", By.XPATH),
                ("//a[contains(text(),'Apply now')]",      By.XPATH),
            ]
            for sel, by in apply_selectors:
                try:
                    btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, sel))
                    )
                    self.driver.execute_script("arguments[0].click();", btn)
                    apply_clicked = True
                    log("  🖱️  Clicked 'Apply now'")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue

            if not apply_clicked:
                log("  ❌ No 'Apply Now' button found — skipping")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return "failed"

            # Handle the application form/modal
            success = self.handle_application_modal(keyword, company)
            status = "applied" if success else "failed"

            if success:
                self.applied_urls.add(current_url)

            write_csv({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "keyword": keyword,
                "title": title,
                "company": company,
                "stipend": stipend,
                "duration": dur,
                "url": current_url,
                "status": status,
                "notes": "",
            })

            # Close the detail tab, go back to listing
            try:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception:
                pass

            time.sleep(2)
            return status

        except StaleElementReferenceException:
            log("  ⚠️  Stale card element, skipping")
            return "skipped"
        except Exception as e:
            log(f"  ❌ Error processing card: {e}")
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception:
                pass
            return "failed"

    # ── Process by URL (fallback when card not in DOM) ────
    def process_url(self, url: str, keyword: str) -> str:
        """Navigate directly to URL and apply — used when card element isn't in DOM."""
        if url in self.applied_urls:
            log(f"  🔁 Already applied to {url} — skipping")
            return "skipped"

        try:
            self.driver.execute_script("window.open(arguments[0]);", url)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(3)

            # Extract details from page
            title = "Unknown"
            company = "Unknown"
            for sel in ["h1.profile-heading", "h1", ".profile h1"]:
                try:
                    title = self.driver.find_element(By.CSS_SELECTOR, sel).text.strip()
                    if title:
                        break
                except Exception:
                    pass
            for sel in [".company_name", ".company-name"]:
                try:
                    company = self.driver.find_element(By.CSS_SELECTOR, sel).text.strip()
                    if company:
                        break
                except Exception:
                    pass

            # Title filter — whitelist + blacklist
            ok, reason = is_relevant_title(title)
            if not ok:
                log(f"  ⏭️  Skipped '{title}' — {reason}")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return "skipped"

            log(f"\n  📌 {title} @ {company} (URL mode)")

            # Check already applied
            try:
                if self.driver.find_element(By.XPATH, "//*[contains(text(),'You have already applied')]"):
                    log("  ℹ️  Already applied")
                    self.applied_urls.add(url)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    return "skipped"
            except Exception:
                pass

            # Click Apply Now
            apply_clicked = False
            for sel in [".top_apply_now_cta", "#apply-button", ".apply_now_cta",
                        "//a[contains(text(),'Apply Now')]", "//button[contains(text(),'Apply Now')]"]:
                try:
                    if sel.startswith("//"):
                        btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, sel)))
                    else:
                        btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
                    self.driver.execute_script("arguments[0].click();", btn)
                    apply_clicked = True
                    log("  🖱️  Clicked 'Apply Now'")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue

            if not apply_clicked:
                log("  ❌ No Apply Now button found")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return "failed"

            success = self.handle_application_modal(keyword, company)
            status = "applied" if success else "failed"
            if success:
                self.applied_urls.add(url)

            write_csv({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "keyword": keyword, "title": title, "company": company,
                "stipend": "", "duration": "", "url": url,
                "status": status, "notes": "url-mode",
            })

            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            time.sleep(2)
            return status

        except Exception as e:
            log(f"  ❌ Error in process_url: {e}")
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception:
                pass
            return "failed"

    # ── Main run ──────────────────────────────
    def run(self):
        try:
            self.setup_driver()
            self.login()

            # Single combined search for all keywords + location
            self.do_search()
            time.sleep(2)

            # Collect IDs as strings first (never stale), then re-fetch each card fresh
            listing_ids = self.get_listing_ids()
            if not listing_ids:
                log("  ⚠️  No listings found. Check URL/selectors.")
            else:
                for i, lid in enumerate(listing_ids):
                    log(f"\n  [{i+1}/{len(listing_ids)}]")

                    # Try to get a live card reference; fall back to URL-based approach
                    card = self._get_card_by_id(lid)

                    if card is not None:
                        result = self.process_card(card, "tech-intern")
                    else:
                        # Card scrolled off / not in DOM — open URL directly
                        if lid.startswith("http"):
                            result = self.process_url(lid, "tech-intern")
                        else:
                            log(f"  ⚠️  Could not find card {lid}, skipping")
                            result = "skipped"

                    if result == "applied":
                        self.applied_count += 1
                    elif result == "skipped":
                        self.skipped_count += 1
                    else:
                        self.failed_count += 1
                    time.sleep(1)

        except KeyboardInterrupt:
            log("\n⛔ Interrupted by user")
        except Exception as e:
            import traceback
            log(f"\n❌ Fatal error: {e}")
            traceback.print_exc()
        finally:
            self._print_summary()
            if self.driver:
                if can_prompt_user():
                    try:
                        input("\nPress Enter to close browser...")
                    except EOFError:
                        pass
                else:
                    time.sleep(3)
                self.driver.quit()

    def _print_summary(self):
        log("\n" + "="*60)
        log("📊 INTERNSHALA BOT SUMMARY")
        log("="*60)
        log(f"  ✅ Applied   : {self.applied_count}")
        log(f"  ⏭️  Skipped   : {self.skipped_count}")
        log(f"  ❌ Failed    : {self.failed_count}")
        log(f"  📁 Log file  : {LOG_FILE}")
        log("="*60)


if __name__ == "__main__":
    bot = InternshalaBot()
    bot.run()
