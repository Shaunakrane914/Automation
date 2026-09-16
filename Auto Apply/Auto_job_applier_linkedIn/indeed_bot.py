"""
indeed_bot.py — Indeed Auto-Apply Bot (India)

Strategy:
  • Uses undetected-chromedriver to bypass Cloudflare
  • Searches each keyword+location separately (Indeed doesn't support OR queries)
  • For each search page, clicks job card titles to load the right-side detail panel
  • Applies to Easy Apply jobs immediately (no waiting for all searches to finish)
  • Deduplicates across keywords/locations via job-key (data-jk) set
"""

import os, csv, time, urllib.parse, tempfile
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException
)

# ──────────────────────────────────────────────
#  CONFIGURATION
# ──────────────────────────────────────────────
EMAIL    = "shaunakrane914@gmail.com"
PASSWORD = "shaunak43rane"

SEARCH_KEYWORDS = [
    "Software Developer Intern",
    "Python Developer Intern",
    "Backend Developer Intern",
    "Full Stack Intern",
    "Machine Learning Intern",
    "AI Intern",
    "Data Engineer Intern",
    "Django Intern",
    "DevOps Intern",
    "Deep Learning Intern",
]

LOCATIONS   = ["Mumbai District", "Thane", "Navi Mumbai"]
DATE_POSTED = "7"   # last N days

# ── Whitelist: title must contain at least one ──
TITLE_MUST_HAVE = [
    "software", "developer", "engineer", "dev",
    "python", "django", "fastapi", "flask",
    "backend", "full stack", "fullstack",
    "machine learning", "ml", "ai", "artificial intelligence",
    "deep learning", "nlp", "computer vision",
    "data engineer", "data science",
    "devops", "cloud", "docker", "kubernetes", "aws",
    "react", "node", "frontend", "web dev",
    "intern",
]

# ── Blacklist: skip if any present ──────────────
TITLE_BAD_WORDS = [
    "marketing", "sales", "business development", "bd intern",
    "social media", "content", "seo", "digital marketing",
    "graphic", "interior", "fashion", "animation", "video",
    "hr ", "human resource", "recruiter", "talent",
    "finance", "accounting", "ca ", "chartered",
    "legal", "law", "compliance",
    "customer support", "customer success", "client servicing",
    "operations", "supply chain", "logistics",
    "real estate", "realty",
    "research analyst", "market research",
    "data entry", "data collection",
    "event", "public relation", "volunteer", "ngo",
    "teaching", "tutor", "education",
    "mechanical", "civil", "electrical", "hardware", "embedded",
    "admin", "e-commerce", "ecommerce", "management",
    "community", "coordinator", "assistant", "support",
    "manager", "lead ", "director", "head of",
]

COVER_NOTE = (
    "I am a B.Tech (2028) student with hands-on Python, ML, and Full Stack skills. "
    "I've built data pipelines and deployed REST APIs in production. "
    "Excited to contribute to {company}!"
)

LOG_FILE = os.path.join(os.path.dirname(__file__), "indeed_applied_jobs.csv")
MANUAL_LOGIN_WAIT_SECONDS = 120


# ──────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────
import sys

def log(msg: str):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        # Fallback for Windows cmd/powershell that can't handle emojis
        clean_msg = msg.encode('ascii', 'ignore').decode('ascii')
        print(clean_msg, flush=True)


def can_prompt_user() -> bool:
    """Return True only when stdin is interactive (TTY)."""
    try:
        return bool(sys.stdin) and sys.stdin.isatty()
    except Exception:
        return False


def write_csv(row: dict):
    fieldnames = ["timestamp", "title", "company", "location", "url", "status", "notes"]
    exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            w.writeheader()
        w.writerow(row)


def is_relevant_title(title: str) -> tuple[bool, str]:
    tl = title.lower()
    if not any(w in tl for w in TITLE_MUST_HAVE):
        return False, "no tech keyword in title"
    for word in TITLE_BAD_WORDS:
        if word in tl:
            return False, f"blocked word '{word}'"
    return True, ""


# ──────────────────────────────────────────────
#  BOT CLASS
# ──────────────────────────────────────────────
class IndeedBot:
    def __init__(self):
        self.driver = None
        self.wait   = None
        self.applied_count = 0
        self.skipped_count = 0
        self.failed_count  = 0
        self.applied_jks: set[str] = set()   # dedup via job key

    # ── Driver ────────────────────────────────
    def setup_driver(self):
        log("🚀 Starting Chrome (undetected)...")
        profile_dir = os.path.join(os.path.dirname(__file__), "chrome_profile_indeed_2")
        fallback_profile = tempfile.mkdtemp(prefix="indeed_uc_")
        launch_profiles = [profile_dir, fallback_profile, None]
        last_error = None

        for idx, pdir in enumerate(launch_profiles, start=1):
            try:
                opts = uc.ChromeOptions()
                if pdir:
                    opts.add_argument(f"--user-data-dir={pdir}")
                opts.add_argument("--start-maximized")
                opts.add_argument("--no-sandbox")
                opts.add_argument("--disable-dev-shm-usage")
                self.driver = uc.Chrome(options=opts)
                self.wait = WebDriverWait(self.driver, 15)
                mode = "saved profile" if pdir == profile_dir else ("temp profile" if pdir else "default profile")
                log(f"✅ Chrome ready! ({mode})")
                return
            except Exception as e:
                last_error = e
                log(f"  ⚠️  Chrome launch attempt {idx} failed: {e}")

        raise RuntimeError(f"Unable to start Chrome driver after retries: {last_error}")

    def _is_logged_in(self) -> bool:
        """Best-effort check for active Indeed session."""
        if not self.driver:
            return False
        if "account/login" in self.driver.current_url:
            return False
        for sel in [
            "[data-gnav-element-name='AccountMenu']",
            ".gnav-LoggedInDropdown",
            "[aria-label='Account Options']",
            "a[href*='/account/']",
        ]:
            try:
                self.driver.find_element(By.CSS_SELECTOR, sel)
                return True
            except NoSuchElementException:
                continue
        return False

    # ── Auto Google login ──────────────────────
    def login(self):
        log("\n🔐 Navigating to Indeed login...")
        self.driver.get("https://in.indeed.com/account/login")
        time.sleep(4)

        if self._is_logged_in():
            log("✅ Already logged in (session restored)!")
            return

        # Try direct Indeed email/password form first (more stable than Google chooser).
        log("  🔑 Trying direct Indeed email/password login...")
        auto_login_ok = False
        email_selectors = [
            (By.ID, "ifl-InputFormField-3"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.NAME, "__email"),
        ]
        password_selectors = [
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.NAME, "__password"),
            (By.ID, "ifl-InputFormField-6"),
        ]
        submit_selectors = [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(., 'Sign in') or contains(., 'Continue')]"),
        ]

        try:
            email_el = None
            for by, sel in email_selectors:
                try:
                    email_el = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((by, sel))
                    )
                    break
                except TimeoutException:
                    continue

            if email_el:
                email_el.clear()
                email_el.send_keys(EMAIL)
                for by, sel in submit_selectors:
                    try:
                        btn = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((by, sel))
                        )
                        self.driver.execute_script("arguments[0].click();", btn)
                        break
                    except TimeoutException:
                        continue
                time.sleep(2)

                password_el = None
                for by, sel in password_selectors:
                    try:
                        password_el = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((by, sel))
                        )
                        break
                    except TimeoutException:
                        continue
                if password_el:
                    password_el.clear()
                    password_el.send_keys(PASSWORD)
                    for by, sel in submit_selectors:
                        try:
                            btn = WebDriverWait(self.driver, 2).until(
                                EC.element_to_be_clickable((by, sel))
                            )
                            self.driver.execute_script("arguments[0].click();", btn)
                            break
                        except TimeoutException:
                            continue
                    time.sleep(4)
                    auto_login_ok = self._is_logged_in()
        except Exception as e:
            log(f"  ⚠️  Direct login attempt failed: {e}")

        if auto_login_ok:
            log("✅ Logged in!")
            return

        # Fallback to manual login; avoid input() in non-interactive runs.
        if can_prompt_user():
            log("⚠️  Auto-login failed. Please login manually in the browser, then press Enter...")
            try:
                input()
            except EOFError:
                log("⚠️  Input stream unavailable; skipping manual prompt.")
        else:
            log(f"⚠️  Auto-login failed in non-interactive mode; waiting {MANUAL_LOGIN_WAIT_SECONDS}s for manual login in browser...")
            time.sleep(MANUAL_LOGIN_WAIT_SECONDS)

        if self._is_logged_in():
            log("✅ Logged in (manual/session)!")
        else:
            log("⚠️  Login still uncertain — continuing anyway")

    # ── Build URL for one keyword + location ──
    def build_search_url(self, keyword: str, location: str) -> str:
        q   = urllib.parse.quote(keyword)
        loc = urllib.parse.quote(location)
        return (
            f"https://in.indeed.com/jobs"
            f"?q={q}&l={loc}&fromage={DATE_POSTED}"
            # Easy Apply filter via URL causes 0 results on IN Indeed — detect on card
        )

    # ── Get Easy Apply cards from search page ─
    def get_easy_apply_cards(self) -> list[tuple[str, object]]:
        """Return list of (job_key, card_element) from current results page.
        Easy-apply eligibility is decided in the job detail panel."""
        result = []
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".job_seen_beacon, [data-jk]")))
            time.sleep(2)
            cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-jk]")
            for card in cards:
                try:
                    jk = card.get_attribute("data-jk") or ""
                    if jk and jk not in self.applied_jks:
                        result.append((jk, card))
                except Exception:
                    continue
        except TimeoutException:
            pass
        return result

    # ── Handle multi-step Easy Apply modal ────
    def handle_easy_apply(self, title: str, company: str) -> bool:
        try:
            for step in range(10):
                time.sleep(2)

                # Already applied?
                try:
                    self.driver.find_element(By.XPATH,
                        "//*[contains(text(),'already applied')]")
                    log("  ℹ️  Already applied")
                    return False
                except NoSuchElementException:
                    pass

                # Success?
                try:
                    self.driver.find_element(By.XPATH,
                        "//*[contains(text(),'application was sent') or "
                        "contains(text(),'Application submitted') or "
                        "contains(text(),'Your application')]")
                    log("  ✅ Application submitted!")
                    return True
                except NoSuchElementException:
                    pass

                # Fill cover note if present
                try:
                    cov = self.driver.find_element(By.CSS_SELECTOR,
                        "textarea[name*='cover'], textarea[id*='cover'], "
                        "textarea[aria-label*='over']")
                    if not cov.get_attribute("value"):
                        cov.send_keys(COVER_NOTE.format(company=company))
                        log("  ✍️  Cover note filled")
                except NoSuchElementException:
                    pass

                # Click Submit / Continue / Next
                clicked = False
                for label, sel in [
                    ("Submit", "//button[normalize-space()='Submit your application']"),
                    ("Submit", "//button[normalize-space()='Submit']"),
                    ("Continue", "//button[normalize-space()='Continue']"),
                    ("Next",     "//button[normalize-space()='Next']"),
                    ("Apply",    "//button[contains(@class,'ia-continueButton')]"),
                ]:
                    try:
                        btn = WebDriverWait(self.driver, 4).until(
                            EC.element_to_be_clickable((By.XPATH, sel)))
                        self.driver.execute_script("arguments[0].click();", btn)
                        log(f"  ➡️  Clicked '{label}'")
                        clicked = True
                        time.sleep(2)
                        break
                    except (TimeoutException, NoSuchElementException):
                        continue

                if not clicked:
                    log(f"  ⚠️  No action button at step {step+1}")
                    return False

            log("  ⚠️  Max steps reached without success")
            return False
        except Exception as e:
            log(f"  ❌ Modal error: {e}")
            return False

    # ── Process one job card ──────────────────
    def process_card(self, jk: str, card) -> str:
        """Click card title → read right panel → apply. Returns 'applied'/'skipped'/'failed'."""
        if jk in self.applied_jks:
            return "skipped"
        try:
            # Click card / title to load right-panel detail.
            clicked = False
            for sel in [
                "a.jcs-JobTitle",
                "h2.jobTitle a",
                "h2 a",
                "a[data-jk]",
                "[role='link']",
            ]:
                try:
                    el = card.find_element(By.CSS_SELECTOR, sel)
                    self.driver.execute_script("arguments[0].click();", el)
                    clicked = True
                    break
                except Exception:
                    continue
            if not clicked:
                # Fallback: click the card container itself (Indeed sometimes uses JS handlers)
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
                    self.driver.execute_script("arguments[0].click();", card)
                    clicked = True
                except Exception:
                    pass
            if not clicked:
                # Final fallback: locate by jk in DOM and click.
                try:
                    self.driver.execute_script(
                        "var el=document.querySelector('[data-jk=\"'+arguments[0]+'\"]'); if(el){el.click(); return true;} return false;",
                        jk,
                    )
                    clicked = True
                except Exception:
                    pass

            if not clicked:
                log("  ❌ Could not click job card/title")
                return "failed"

            # Wait for right panel to render something that looks like a job header
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1, [data-testid='simonsJobTitle']"))
                )
            except TimeoutException:
                pass
            time.sleep(1.5)

            # Extract title from right-hand panel
            title = "Unknown"
            for sel in [
                ".jobsearch-JobInfoHeader-title span",
                "[data-testid='simonsJobTitle']",
                ".jobsearch-ViewJobLayout--embedded h1",
                ".jobsearch-JobComponent-description h1",
                "[class*='jobInfoHeader'] h1",
                "h1",
            ]:
                try:
                    t = self.driver.find_element(By.CSS_SELECTOR, sel).text.strip()
                    if t and t not in ("Search results", "Jobs"):
                        title = t
                        break
                except Exception:
                    pass

            company = "Unknown"
            for sel in [
                "[data-testid='inlineHeader-companyName']",
                ".jobsearch-InlineCompanyRating-companyHeader a",
                "[data-company-name]",
                "[class*='companyName']",
            ]:
                try:
                    c = self.driver.find_element(By.CSS_SELECTOR, sel).text.strip()
                    if c:
                        company = c
                        break
                except Exception:
                    pass

            location = "Unknown"
            for sel in [
                "[data-testid='job-location']",
                ".jobsearch-JobInfoHeader-subtitle .css-1tlrkfh",
                "[class*='companyLocation']",
            ]:
                try:
                    l = self.driver.find_element(By.CSS_SELECTOR, sel).text.strip()
                    if l:
                        location = l
                        break
                except Exception:
                    pass

            ok, reason = is_relevant_title(title)
            if not ok:
                log(f"  ⏭️  Skipped '{title}' — {reason}")
                return "skipped"

            log(f"\n  📌 {title} @ {company} | {location}")

            # Click "Apply now" / "Easy Apply" in the panel
            apply_clicked = False
            for sel, by in [
                ("indeedApplyButton",                          By.ID),
                (".ia-IndeedApplyButton",                      By.CSS_SELECTOR),
                ("[id*='applyButton']",                        By.CSS_SELECTOR),
                ("//button[contains(.,'Apply now')]",          By.XPATH),
                ("//a[contains(.,'Apply now')]",               By.XPATH),
                ("//button[contains(@class,'IndeedApply')]",   By.XPATH),
                ("//button[contains(@class,'indeedApply')]",   By.XPATH),
            ]:
                try:
                    btn = WebDriverWait(self.driver, 6).until(
                        EC.element_to_be_clickable((by, sel)))
                    self.driver.execute_script("arguments[0].click();", btn)
                    apply_clicked = True
                    log("  🖱️  Clicked 'Apply now'")
                    time.sleep(3)
                    break
                except (TimeoutException, NoSuchElementException):
                    continue

            if not apply_clicked:
                log("  ❌ No Easy Apply button found in panel")
                write_csv({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "title": title, "company": company, "location": location,
                    "url": f"https://in.indeed.com/viewjob?jk={jk}",
                    "status": "no_button", "notes": "",
                })
                return "skipped"

            success = self.handle_easy_apply(title, company)
            status = "applied" if success else "failed"
            if success:
                self.applied_jks.add(jk)

            write_csv({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "title": title, "company": company, "location": location,
                "url": f"https://in.indeed.com/viewjob?jk={jk}",
                "status": status, "notes": "",
            })

            # Close any extra tabs that the apply flow opened
            self._close_extra_tabs()
            time.sleep(2)
            return status

        except StaleElementReferenceException:
            return "skipped"
        except Exception as e:
            log(f"  ❌ Error processing card: {e}")
            return "failed"

    def _close_extra_tabs(self):
        """Close all extra tabs, leaving only the first one."""
        try:
            while len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception:
            pass

    def _print_summary(self):
        log("\n" + "="*60)
        log(f"  ✅ Applied  : {self.applied_count}")
        log(f"  ⏭️  Skipped  : {self.skipped_count}")
        log(f"  ❌ Failed   : {self.failed_count}")
        log(f"  📄 Log      : {LOG_FILE}")
        log("="*60)

    # ── Main run ──────────────────────────────
    def run(self):
        try:
            self.setup_driver()
            self.login()

            log(f"\n{'='*60}")
            log(f"🔍 {len(SEARCH_KEYWORDS)} keywords × {len(LOCATIONS)} locations")
            log(f"   Locations   : {', '.join(LOCATIONS)}")
            log(f"   Date filter : Last {DATE_POSTED} days | Easy Apply only")
            log(f"{'='*60}")

            seen_jks: set[str] = set()   # global dedup across all searches

            for loc in LOCATIONS:
                for kw in SEARCH_KEYWORDS:
                    url = self.build_search_url(kw, loc)
                    log(f"\n{'─'*55}")
                    log(f"🔎 '{kw}' in {loc}")
                    log(f"{'─'*55}")
                    self.driver.get(url)
                    time.sleep(4)

                    for page in range(1, 4):   # max 3 pages per combo
                        card_items = self.get_easy_apply_cards()
                        new_cards  = [(jk, c) for jk, c in card_items
                                      if jk not in seen_jks]
                        for jk, _ in new_cards:
                            seen_jks.add(jk)

                        log(f"  📋 Page {page}: {len(new_cards)} new jobs")

                        if not new_cards:
                            break

                        # Apply to each card immediately
                        for i, (jk, card) in enumerate(new_cards):
                            log(f"\n  [{i+1}/{len(new_cards)}]")
                            result = self.process_card(jk, card)
                            if result == "applied":
                                self.applied_count += 1
                            elif result == "skipped":
                                self.skipped_count += 1
                            else:
                                self.failed_count += 1
                            time.sleep(1)

                        # Navigate to next page
                        try:
                            nxt = self.driver.find_element(By.CSS_SELECTOR,
                                "a[data-testid='pagination-page-next'], "
                                "a[aria-label='Next Page']")
                            nxt.click()
                            time.sleep(4)
                        except NoSuchElementException:
                            break   # no more pages for this keyword

        except KeyboardInterrupt:
            log("\n⛔ Interrupted by user")
        except Exception as e:
            import traceback
            log(f"\n❌ Fatal error: {e}")
            traceback.print_exc()
        finally:
            self._print_summary()
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    IndeedBot().run()
