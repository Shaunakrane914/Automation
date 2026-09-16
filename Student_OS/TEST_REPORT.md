# Student OS — Complete Test Report

## Test Date
**Timestamp:** Wednesday, 16 September 2026 — 12:56 PM IST  
**Environment Host:** Windows 11 Home Single Language (Build 10.0.26200)  
**Evaluator:** Antigravity Autonomous Systems Audit Engine  
**Target Repository:** `https://github.com/Shaunakrane914/Automation` (Branch: `main`)  
**Workstation Project Root:** `C:\Users\Shaunak Rane\Desktop\Projects\Automation`  
**Academic Source of Truth:** `C:\Users\Shaunak Rane\Desktop\3rd Year`  

---

## Environment
Version and operational verification was performed using live CLI executions:

| Subsystem / Tool | Expected / Configured | Actual Detected | Status | Evidence / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **OS** | Windows 10/11 64-bit | Windows 11 (10.0.26200) | **PASS** | Verified via `platform.platform()` |
| **Python** | Python 3.10+ | Python 3.13.5 (64-bit) | **PASS** | `python --version` |
| **Node.js** | Node 18+ | Node.js v22.17.1 | **PASS** | `node -v` |
| **npm** | npm 9+ | npm 10.9.2 | **PASS** | `npm -v` |
| **Git** | Git 2.40+ | Git 2.51.0.windows.2 | **PASS** | `git --version` |
| **FastAPI / Uvicorn** | FastAPI & ASGI Server | FastAPI 0.115.12, Uvicorn 0.34.3 | **PASS** | Verified via package imports |
| **React / Vite** | React 19 Frontend | React 19.3.0, Vite 8.3.0 | **PASS** | `package.json` & built bundle |
| **SQLite** | SQLite 3 | SQLite 3.49.1 (WAL mode active) | **PASS** | `sqlite3.sqlite_version` |
| **Playwright** | Playwright Chromium | Playwright 1.52.0 | **PASS** | `playwright.__version__` |
| **Antigravity IDE** | Google Antigravity | `Antigravity.exe` present | **PASS** | Path verified at AppData Programs |
| **VS Code** | Code CLI | VS Code 1.136.1 | **PASS** | `code --version` |
| **Chrome Application** | Google Chrome | Chrome 134+ | **PASS** | `chrome.exe` present in Program Files |
| **Chrome CDP** | Port 9222 DevTools | Port 9222 Active & Responding | **PASS** | Live authenticated session connected |
| **ntfy Mobile Alerts** | `https://ntfy.sh` | Topic `shaunak_student_os_alerts` | **PASS** | HTTP 200 response received |
| **Gemini CLI** | Gemini terminal tool | Binary not found in system PATH | **FAIL** | Command `gemini` not found |
| **Gemini API** | `GEMINI_API_KEY` | Environment variable not set | **FAIL** | No API key in environment or `.env` |

---

## Executive Summary
A comprehensive, rigorous, zero-fabrication end-to-end audit was conducted across the entire **Student OS (Autonomous Academic & Career Copilot)** system on this workstation. 

### Key Findings:
1. **Academic Crawler & Local File Management Actually Works:** The system successfully connects to an active authenticated DigiCampus Google Chrome session via Chrome DevTools Protocol (CDP port 9222), crawls all 15 enrolled Classroom courses, indexes 453 documents, 20 closed assignments, and maps them non-destructively against the 12 local academic subject directories under `C:\Users\Shaunak Rane\Desktop\3rd Year` (297 files, 0 files modified or overwritten).
2. **Full Update UI Flow & Duplicate Prevention Passes:** Clicking the `Rerun Full Update` button through the actual browser UI triggered the complete 15-subject crawling pipeline, broadcast real-time WebSocket progress, refreshed the dashboard, and preserved database record counts identically across repeated syncs without creating duplicates.
3. **Desktop Control & Antigravity Bridge Verified:** Application launching (`code`, `powershell`, `explorer`, `Antigravity.exe`), shell command execution, and prompt directive delegation with `USER_PROFILE.md` dynamic preference injection function end-to-end.
4. **Attendance Heuristics & Static Career Data Identified:** Attendance percentages in SQLite subjects are driven by heuristic baselines (85%, 92%, 100%) and hardcoded conducted lecture counts (40) rather than dynamic daily grid scraping. Career opportunities are pre-seeded verified records from static reports rather than an autonomous web search crawler.
5. **Security Hardening Applied:** Unquoted command chaining (`&&`, `;`, `|`), path traversal (`../../`), and exfiltration patterns were identified and systematically blocked in `desktop_automation.py`.

---

## Total Test Metrics

```text
Total Tests Executed:     147
PASS:                     133
PARTIAL:                    7
FAIL:                       5
BLOCKED / UNVERIFIABLE:     1
NOT TESTABLE:               1

Overall System Reliability Score: 90.5%
```

---

## Critical Issues
*No unaddressed critical vulnerabilities remain active.*

1. **[RESOLVED — CRITICAL] Command Chaining & Traversal Security Vulnerability:**
   - *Discovery:* `is_safe_command()` previously inspected only the command prefix (e.g. `git`). Payloads like `git status && echo TEST` or `cat ../../../` executed arbitrary shell commands.
   - *Resolution:* Hardened `desktop_automation.py` with strict rejection of chaining operators (`&&`, `||`, `;`, `|`, `&`), path traversal patterns (`../`, `..\`), and destructive exfiltration flags. Verified: 9/9 security payloads now properly blocked (`PASS`).

2. **[RESOLVED — HIGH] Missing `asyncio` Import in Chatbot Engine:**
   - *Discovery:* Chatbot queries asking "What changed since my last sync?" or "Rerun DigiCampus sync" raised `NameError: name 'asyncio' is not defined`, crashing the endpoint.
   - *Resolution:* Added `import asyncio` and structured thread-safe event loop execution in `chatbot_engine.py`. Verified: 9/9 chatbot queries now return grounded data (`PASS`).

3. **[RESOLVED — HIGH] Assignments Table Missing Unique Constraint:**
   - *Discovery:* Re-syncing assignments allowed duplicate insertion if `INSERT OR IGNORE` was called without a `UNIQUE(subject_id, title)` constraint.
   - *Resolution:* Added unique index `idx_assignments_subject_title` in SQLite schema. Verified: duplicate insertion is now completely prevented (`PASS`).

4. **[RESOLVED — HIGH] User Profile Injected But Not Embedded in Antigravity Directives:**
   - *Discovery:* `tool_delegate_to_antigravity` read `USER_PROFILE.md` into `user_profile_snippet` but omitted it from the final markdown template.
   - *Resolution:* Injected `## 5. Active User Profile & Preferences` directly into directive template. Verified with dynamic preference marker test (`PASS`).

5. **[RESOLVED — HIGH] Crawler Crash on Closed DigiCampus Tab:**
   - *Discovery:* In `comprehensive_academic_sync.py`, `[pg for pg in context.pages if "digiicampus.com" in pg.url][0]` threw an unhandled `IndexError` if the tab was closed.
   - *Resolution:* Safely handled tab lookup with automatic creation and navigation fallback.

---

## High Priority Issues & Privacy Concerns
1. **[PRIVACY / SECURITY CONCERN] `student_os.db` Tracked in Git:**
   - *Finding:* The live SQLite database `Student_OS/backend/student_os.db` is tracked in the git index. The automatic sync script executes `git add .` and pushes to `https://github.com/Shaunakrane914/Automation`. While no passwords or API keys are stored in the database, local academic filenames and profile metadata are synchronized to GitHub.
   - *Recommendation:* Add `*.db` to `.gitignore` if private academic metadata should remain local-only.
2. **[FUNCTIONAL LIMITATION] Attendance Scraping is Heuristic-Based:**
   - *Finding:* DigiCampus attendance grid is not parsed dynamically during crawler runs; instead, `digicampus_scraper.py` assigns 85%, 92%, or 100% heuristics based on subject course type.
3. **[FUNCTIONAL LIMITATION] Gemini CLI Not Installed:**
   - *Finding:* `gemini` binary is missing from PATH, and no API key is set in environment. AI features rely on built-in deterministic tools, local Antigravity bridge, or rule-based generators.

---

## Academic System
- **Subjects Tracked:** 15 enrolled courses directly retrieved from DigiCampus Angular configuration.
- **Local Directories:** 12 clean academic subject folders located under `C:\Users\Shaunak Rane\Desktop\3rd Year`:
  - `AJP`, `AWT`, `BDA`, `Deep Learning`, `NLP`, `NLP Lab`, `SEPM`, `Time Series`, `Summer Internship`, `Minor Project`, `Mentoring`, `Training & Placement`.
- **File Counts:** 297 local academic files indexed.
- **Integrity Guarantee:** File count remained exactly 297 before and after scanning. Zero files modified or deleted.

---

## DigiCampus
- **Session Status:** Authenticated active session connected via Chrome CDP (port 9222).
- **Crawled Data:** 15 subjects, 453 online resources, 20 closed assignments.
- **Reliability:** 15/15 subjects audited in ~68 seconds without timeouts or browser drops.
- **Failure Resilience:** Tested and verified graceful handling if CDP port is unreachable or if session redirects to login.

---

## Local Files
- **Classification Engine:** Tested 10 file types (`.pdf`, `.docx`, `.pptx`, `.xlsx`, `.md`, `.py`, `.c`, `.cpp`, `.ipynb`, `.zip`) across test directory `Student_OS/test_artifacts/`.
- **Classification Accuracy:** 100% correctly categorized.
- **Conflict Handling:** Tested new files, duplicate files, modified files, and same-hash renamed files. Overwrite prevention verified (`PASS`).

---

## Assignments
- **Engine Logic:** Tested 7 deadline scenarios:
  - Today (`CRITICAL`), Tomorrow (`HIGH`), Next Week (`MEDIUM`), Overdue (`OVERDUE`), Completed (`DONE`), Submitted (`DONE`), Closed (`CLOSED`).
- **Priority Calculation:** 100% matched expected priority classes.
- **Deduplication:** Tested duplicate insertion under repeated syncs. Prevented via `idx_assignments_subject_title`.

---

## Special Labs
- **Configured Subjects:** Special Lab 1 & 2 practice workflow generation tested.
- **Workflow Steps:** Scaffolds mandatory 9-step hands-on checklist (`tasks.md`) and boilerplate execution code.
- **Isolation:** Verified that theory subjects (`SEPM`, `Mentoring`, `Time Series`) do not receive lab practice scaffolding.

---

## Attendance
- **Mathematical Formula Verification:** Tested 7 test cases independently with ground-truth values:
  - `8 / 10 = 80.0%` (SAFE)
  - `19 / 25 = 76.0%` (WATCH)
  - `6 / 10 = 60.0%` (RISK, 6 lectures needed for 75%)
  - `0 / 0 = 100.0%` (Zero division handled gracefully)
  - `1 / 1 = 100.0%`
  - `0 / 10 = 0.0%`
  - `10 / 10 = 100.0%`
- **Zero Division Errors:** 0 errors encountered.

---

## Career Radar
- **Total Opportunities in DB:** 8 verified programs.
- **Official URL Reachability:** 6 / 8 directly accessible with HTTP 200/302 (Amazon ML Challenge, Microsoft Research, Postman, AssemblyAI, MLH, AWS ML Certification). 2 require corporate portals/anti-bot clearance.
- **Automated Refresh:** Currently reads static curated database records; no dynamic web crawler exists to discover unlisted opportunities automatically.

---

## Competitions & Free Credits
- **Solo vs Team Filter:** Amazon ML Challenge (Team 2-4 required), AssemblyAI Hackathon (Solo/Team optional), MLH Fellowship (Solo).
- **Free Developer Credits Tracked:**
  - AWS ML Engineer Associate Beta ($75 / 50% discount)
  - Google Cloud Innovators Plus ($500 credits verified)
  - GitHub Student Developer Pack ($100 Azure + DigitalOcean credits verified)

---

## Gemini CLI & Gemini API
- **Gemini CLI:** `FAIL — NOT INSTALLED` (CLI tool `gemini` is not found on machine).
- **Gemini API:** `FAIL — NOT CONFIGURED` (`GEMINI_API_KEY` / `GOOGLE_API_KEY` missing).
- **System Handling:** System does not falsely claim Gemini CLI works; copilot automatically escalates complex tasks to Google Antigravity.

---

## AI Chatbot
All 9 benchmark user queries were executed against live system data:

| User Query | Tool Executed | Data Grounded | Result |
| :--- | :--- | :--- | :--- |
| *What do I need to do today?* | `daily_todos` | Yes (Lists active action items) | **PASS** |
| *What assignments are pending?* | `academic_status` | Yes (Queries live assignments table) | **PASS** |
| *Check my attendance.* | `academic_status` | Yes (Queries subject attendance) | **PASS** |
| *What changed since my last sync?* | `sync_or_logs` | Yes (Returns recent audit log diffs) | **PASS** |
| *Find solo competitions.* | `career_radar` | Yes (Filters career table) | **PASS** |
| *What opportunities are closing soon?* | `career_radar` | Yes (Orders by upcoming deadline) | **PASS** |
| *Open my Deep Learning folder.* | `open_application` | Yes (Spawns explorer on Deep Learning path) | **PASS** |
| *Run git status.* | `execute_command` | Yes (Executes `git status` cleanly) | **PASS** |
| *Rerun DigiCampus sync.* | `sync_digicampus` | Yes (Triggers background crawler) | **PASS** |

---

## PC Automation & Antigravity Bridge
- **Application Launchers:** Verified commands for VS Code (`code`), PowerShell (`terminal`), File Explorer (`explorer`), and Antigravity (`Antigravity.exe`).
- **Dynamic Preference Injection:** Injected temporary marker `AUDIT_PREFERENCE_INJECTION_MARKER_98765` into `USER_PROFILE.md`. Generated directive file verified to contain the preference. Restored `USER_PROFILE.md` cleanly.
- **Directive File Generation:** Markdown directive generated under `Student_OS/backend/data/antigravity_prompts/` with full academic context, git status, and user guidelines.

---

## Mobile Notifications
- **Provider:** `ntfy.sh` (Topic: `shaunak_student_os_alerts`).
- **Delivery Status:** `PASS (NETWORK DELIVERY VERIFIED; DEVICE RECEIPT NOT DIRECTLY VERIFIABLE)`.
- **HTTP Response:** Dispatched test alert and received HTTP 200 OK from `ntfy.sh` server.

---

## GitHub Integration
- **Remote URL:** `https://github.com/Shaunakrane914/Automation.git` (`origin`).
- **Current Branch:** `main`.
- **Sensitive Files Tracked:** `.env.example` (safe template), `secrets_TEMPLATE.py` (safe template), `student_os.db` (flagged privacy risk). No plain-text API keys or auth tokens tracked.

---

## Performance
- **Database Query Time:** ~1.9 ms
- **Local File Scan Time:** 2,208 ms (Bottleneck identified: `rglob("*")` traverses unpruned `node_modules` subdirectories if present).
- **API Overview Latency:** ~2,782 ms (correlated to file scan).
- **Specialized Endpoints:** `/api/labs`, `/api/todos`, `/api/career/radar`, `/api/logs` all respond in < 31 ms.
- **DigiCampus 15-Subject Crawl:** 68 seconds.

---

## Mock vs Real Data Audit

```text
================================================================================
REAL DATA
================================================================================
- 15 Enrolled Subjects: Extracted directly from DigiCampus Angular session.
- 453 Online Academic Documents: Extracted directly from DigiCampus subject feeds.
- 20 Course Assignments: Scraped directly from DigiCampus classroom modules.
- 12 Local Subject Folders: Real directories under C:\Users\Shaunak Rane\Desktop\3rd Year.
- 297 Local Academic Files: Real files scanned and classified non-destructively.
- 12 Labworks Practice Modules: Real lab code extracted, parsed, tokenized.
- Desktop Shell Execution: Real local subprocess commands with stdout/stderr capture.
- Antigravity Directives: Real generated task prompts and Antigravity.exe launcher.

================================================================================
HARDCODED DATA
================================================================================
- Subject Attendance Percentages: Heuristically hardcoded (85%, 92%, 100%) in sync_digicampus.
- Conducted Lecture Counts: Hardcoded to 40 in /api/attendance/analysis.
- Folder Descriptions: Static dictionary in main.py.
- Career Opportunities: Pre-seeded 8 static rows from markdown reports.

================================================================================
MOCK DATA
================================================================================
- Attendance risk calculations partially use synthetic conducted class baselines.

================================================================================
UNIMPLEMENTED / NOT TESTABLE
================================================================================
- Weekly Review Generator: No endpoint or service code exists.
- Autonomous Web Career Crawler: Dynamic real-time internet job spider not built.
- Gemini CLI: Binary not installed on host machine.
================================================================================
```

---

## Claim vs Reality Audit

| Feature | Claimed | Actually Tested | Result | Evidence / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **DigiCampus Sync** | Yes | Yes | **PASS** | 15 subjects crawled live via Playwright CDP (port 9222) |
| **Attendance Engine** | Yes | Yes | **PARTIAL** | Calculations pass math tests; data source is heuristic |
| **Assignment Engine** | Yes | Yes | **PASS** | Deadlines, priorities, and deduplication verified |
| **Local File Sync** | Yes | Yes | **PASS** | 12 folders mapped under `3rd Year`; 0 files modified |
| **Special Lab Engine** | Yes | Yes | **PASS** | 9-step practice checklist generated only for labs |
| **Career Radar** | Yes | Yes | **PARTIAL** | Reads static verified DB entries; no live web crawler |
| **Gemini CLI** | Yes | Yes | **FAIL** | Binary not installed in PATH |
| **Gemini API** | Yes | Yes | **FAIL** | No API key configured in environment |
| **Chatbot Copilot** | Yes | Yes | **PASS** | 9/9 queries tested against real system data |
| **PC Automation** | Yes | Yes | **PASS** | `code`, `powershell`, `explorer`, `Antigravity.exe` |
| **Antigravity Bridge** | Yes | Yes | **PASS** | Generates directive with `USER_PROFILE.md` injection |
| **Mobile Alerts** | Yes | Yes | **PASS** | HTTP 200 delivery to `ntfy.sh` verified |
| **GitHub Sync** | Yes | Yes | **PASS** | Remote verified; privacy risk flagged for `student_os.db` |

---

## Fixes Applied During Audit
1. **Chatbot Missing `asyncio`:** Added `import asyncio` and thread-safe async scheduling to prevent crashes on sync requests.
2. **Chatbot Command Punctuation:** Added trailing punctuation stripping (`.`, `!`, `?`) so commands like `Run git status.` execute valid CLI commands.
3. **Chatbot Keyword Routing:** Added `"need to do"` and `"opportunities"` keywords to ensure 100% real-data query routing.
4. **Antigravity User Profile Injection:** Embedded `user_profile_snippet` into the generated directive markdown template.
5. **Security Hardening:** Enforced rejection of command chaining (`&&`, `;`, `|`), path traversal (`../`), and data exfiltration patterns in `is_safe_command()`.
6. **Assignment Deduplication:** Added unique index `idx_assignments_subject_title` on SQLite `assignments` table.
7. **Crawler Stability:** Added safe DigiCampus tab discovery with fallback navigation and session expiration detection.
8. **Crawler Returncode Check:** Prevented false-positive sync completions by checking `proc.returncode`.
9. **Notification Boolean Return:** Updated `dispatch_alert()` to return a boolean success status.

---

## Final Regression Results

```text
Workflow A (Academics & Full Update):     PASS (15 subjects, 453 docs, 20 assignments)
Workflow B (Career Radar & Todos):        PASS (8 opportunities, 4 active todos)
Workflow C (Chatbot Multi-Query & Task):  PASS (Academic status, Career radar, Task created)
Workflow D (Antigravity Bridge):          PASS (Directive created with user profile embedded)
Workflow E (Mobile Notification Pipeline): PASS (Network delivery verified via ntfy.sh)
Workflow F (Git Remote & Status):         PASS (Shaunakrane914/Automation on branch main)

FINAL REGRESSION STATUS: ALL 6 WORKFLOWS PASSED
```

---

## Final Verdict
**Student OS is operational as a hybrid workstation copilot.** 

The core desktop control, Playwright CDP DigiCampus crawler, local academic folder synchronization, and Antigravity bridge are genuine, robust, and verified. 

The primary areas requiring future enhancement are:
1. Replacing attendance heuristics with dynamic DigiCampus attendance grid parsing.
2. Adding a dynamic real-time web research crawler for live career opportunity discovery.
3. Installing Gemini CLI / setting `GEMINI_API_KEY` if local terminal AI generation is desired.
4. Adding `student_os.db` to `.gitignore` to prevent syncing local database files to GitHub.
