# ARCHITECTURE.md — Shaunak Command Center Design Specification
**Architecture Pattern:** Local-First, Event-Driven Modular Microservices with AI Orchestration  
**Primary Language:** Python 3.13 (Backend) + TypeScript / React 18 (Frontend)

---

## 1. High-Level Architecture Diagram

```text
                                 ┌─────────────────────────────────┐
                                 │   Frontend Dashboard (React)    │
                                 │   Tailwind CSS + Lucide Icons   │
                                 └───────────────┬─────────────────┘
                                                 │ REST & WebSockets (/ws)
                                                 ▼
                                 ┌─────────────────────────────────┐
                                 │      FastAPI Backend Engine     │
                                 │      Port 8000 (Localhost)      │
                                 └───────┬───────────────┬─────────┘
                                         │               │
                     ┌───────────────────┴───┐       ┌───┴───────────────────┐
                     ▼                       ▼       ▼                       ▼
            ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
            │ Academic Engine │     │ Career Radar    │     │ PC Automation   │
            │ Playwright      │     │ Verified Source │     │ Subprocess CLI  │
            │ DigiCampus Crawl│     │ Search Engine   │     │ App Launchers   │
            └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
                     │                       │                       │
                     └───────────────────────┼───────────────────────┘
                                             ▼
                                ┌─────────────────────────┐
                                │     SQLite Database     │
                                │   (student_os.db, WAL)  │
                                └─────────────────────────┘
```

---

## 2. Core Subsystems

### Subsystem 1: Academic Engine
- **DigiCampus Connector (`services/digicampus_scraper.py`):**
  - Session cookie caching (`digicampus_state.json`) to minimize authentication load.
  - Safe scraper with `domcontentloaded` wait states and fallback heuristics.
  - Subject attendance extraction & 75% safety threshold alert system.
  - Document synchronization to `~/3year/<subject_name>/` (virtual hash classification).
- **Special Lab Practice Engine:**
  - Dedicated workflow for `Special Lab 1` & `Special Lab 2` (practice loops, checklists, starter code).
- **AI Lecture Digest:**
  - Summarizes class notes into concise `SUMMARY_<topic>.md` files when no assignment exists.

### Subsystem 2: Career, GSoC & Competition Radar
- Tracks verified opportunities with source URLs, deadlines, and eligibility filters (May 2028 batch).
- Dedicated filter for **Solo Competitions** vs **Team Required**.
- Free compute/cloud credit tracking (AWS, Google Cloud, OpenAI, Anthropic, GitHub Student Developer Pack).

### Subsystem 3: PC Automation & Tooling
- Safe command runner with an approved command allowlist (`python`, `git`, `code`, `pytest`).
- Native app launcher for Antigravity, VS Code, and Windows File Explorer.

### Subsystem 4: Mobile Push Alert Pipeline
- Integration with **ntfy.sh** for instant push notifications to Shaunak's mobile device without API key barriers.
- Telegram Bot API fallback.

---

## 3. Database Schema (SQLite with WAL)

- `subjects`: ID, name, code, attendance_percentage, last_synced
- `documents`: ID, subject_id, file_name, local_path, upload_date, summary_path
- `assignments`: ID, subject_id, title, deadline, is_lab, status, local_lab_dir
- `career_radar`: ID, category, name, deadline, benefits_credits, status, url, eligibility
- `daily_todos`: ID, title, category, due_date, completed
- `agent_logs`: ID, timestamp, level, message
