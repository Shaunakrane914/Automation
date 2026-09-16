# ENVIRONMENT.md — System Discovery & Tooling Report
**Project:** Shaunak Command Center — Academic + Career + Opportunity OS  
**Date of Audit:** 16 September 2026  
**Candidate / User:** Shaunak Rane (3rd-Year B.Tech AI & ML, Universal AI University)  
**Host Machine:** Windows 11 (OS Architecture: x64)

---

## 1. Runtime & Language Toolchains

| Tool | Status | Version / Path | Verification Output |
| :--- | :--- | :--- | :--- |
| **Python** | ✅ Available | `3.13.5` (`C:\Users\Shaunak Rane\AppData\Local\Programs\Python\Python313\python.exe`) | Tested execution; pip 26.2.1 |
| **Node.js** | ✅ Available | `v22.17.1` | Node runtime active |
| **npm** | ✅ Available | `10.9.2` | Package manager verified |
| **Git** | ✅ Available | `2.51.0.windows.2` | Version control verified |
| **VS Code** | ✅ Available | `1.136.1` (`code`) | CLI and GUI editor available |
| **Antigravity IDE** | ✅ Available | Local program: `C:\Users\Shaunak Rane\AppData\Local\Programs\Antigravity\Antigravity.exe` | Detected |
| **Google Chrome** | ✅ Available | `C:\Program Files\Google\Chrome\Application\chrome.exe` | Primary browser |
| **Microsoft Edge**| ✅ Available | `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` | Secondary browser |

---

## 2. Python Environment & Library Audit

| Library | Status | Purpose in Architecture |
| :--- | :--- | :--- |
| `fastapi` | ✅ Installed | Core high-performance async REST & WebSocket server |
| `uvicorn` | ✅ Installed | ASGI production server |
| `playwright` | ✅ Installed | Headless browser automation for DigiCampus crawling |
| `pydantic` / `pydantic-settings` | ✅ Installed | Strongly-typed configuration and validation |
| `sqlite3` | ✅ Built-in | Local relational persistence with WAL mode |
| `httpx` | ✅ Installed | Async HTTP client for mobile webhooks (`ntfy.sh`) and API tests |
| `websockets` | ✅ Installed | Real-time bi-directional event bus to frontend dashboard |
| `google-generativeai` | ✅ Installed | Gemini AI SDK for lecture slide analysis and summaries |
| `pytest` | ✅ Installed | Automated test framework for test-driven phase verification |

---

## 3. Academic Filesystem Structure (`3year/`)

**Physical Location:** `C:\Users\Shaunak Rane\3year` (Read-only discovery; no destructive operations permitted).

### Detected Subject Directories:
1. `Cloud Computing & MLOps/`
2. `Deep Learning & Neural Networks/`
3. `Graph Machine Learning/`
4. `Natural Language Processing/`
5. `Reinforcement Learning/`
6. *(Upcoming / Registered Labs: `Special Lab 1`, `Special Lab 2`)*

---

## 4. Port & Network Availability
- **Port 8000:** Dedicated to FastAPI backend (`http://127.0.0.1:8000`)
- **Port 5173:** Dedicated to Vite + React dashboard frontend dev server
- **Local Database:** `student_os.db` (SQLite with WAL journal mode enabled)

---

## 5. Phase 0 Acceptance Test Verdict
- [x] Application host environment identified (Windows 11 x64).
- [x] Existing `3year` directory safely detected and mapped without modifications.
- [x] Python 3.13, Node 22, Git, VS Code, Antigravity, and Playwright validated.
- [x] Zero user files deleted or altered.
- **Verdict: PHASE 0 COMPLETE. Ready to execute sequential phases.**
