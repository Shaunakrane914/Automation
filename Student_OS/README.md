# Student OS & Autonomous Academic Copilot
**Author:** Shaunak Rane (Universal AI University)  
**Target Architecture:** Local FastAPI Backend + Real-Time WebSocket Server + Playwright Headless Agent + React TypeScript Dashboard

Student OS is a unified developer-and-student system designed to eliminate academic friction, automate assignment tracking, monitor attendance safety thresholds, scan for top career/GSoC opportunities, and run desktop automation scripts.

---

## 🚀 Key Features

1. **Academic Engine (DigiCampus UAI Integration):**
   - Headless Playwright crawler with persistent cookie sessions.
   - Automatically synchronizes course materials to `~/3year/<subject_name>/`.
   - Attendance tracking with warning alerts if attendance drops below 75%.
   - Smart Lab differentiator: automatically scaffolds `~/3year/<subject_name>/labs/labX/` with starter templates and `tasks.md` checklists.
   - Generates lecture summaries (`SUMMARY_<topic>.md`) using Gemini AI.

2. **Career, GSoC & Competition Radar:**
   - Real-time tracker for GSoC 2027, LFX Mentorship, and high-impact hackathons (e.g. Amazon ML Challenge 2026).
   - Keeps track of deadline alerts, free cloud compute credits, and team prerequisites.

3. **Desktop Automation & Execution Agent:**
   - Whitelisted safe command execution (`git`, `pytest`, `python`, `code`).
   - One-click app launching (VS Code, terminal, file explorer).
   - Live WebSocket event log streamed directly to your browser.

4. **Mobile Push Alert Pipeline:**
   - Instant notifications via **ntfy.sh** (free, no account needed, works with the official ntfy iOS/Android app).
   - Optional Telegram Bot webhook integration.
   - Triggers: Attendance < 75%, assignment due in < 48h/24h, new lecture uploaded.

---

## 🛠️ Step-by-Step Setup Guide

### 1. Environment Configuration
Copy `.env.example` to `.env` inside `Student_OS/`:
```bash
cp .env.example .env
```
Ensure your credentials and settings are configured:
```env
DIGICAMPUS_URL=https://uai.digiicampus.com
DIGICAMPUS_USER=shaunak.rane@universalai.in
DIGICAMPUS_PASS=Sharan@2007

ACADEMIC_ROOT_DIR=~/3year

# Optional: Add your Gemini API Key for dynamic lecture slide summarization
GEMINI_API_KEY=

# ntfy.sh push channel (Install ntfy on your phone and subscribe to this topic name)
NTFY_TOPIC=shaunak_student_os_alerts
```

### 2. Backend Installation & Launch
```bash
cd backend
pip install -r requirements.txt

# Run FastAPI backend with Uvicorn (Port 8000)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger API Documentation: `http://localhost:8000/docs`
- Live WebSocket Event Feed: `ws://localhost:8000/ws`

### 3. Frontend Installation & Launch
```bash
cd frontend
npm install
npm run dev
```
- Open your browser at: `http://localhost:5173`

---

## 📱 Setting Up Mobile Push Alerts via ntfy.sh
1. Download **ntfy** from Google Play Store or Apple App Store.
2. Open the app and tap **+ (Subscribe to topic)**.
3. Enter `shaunak_student_os_alerts` (or your custom `NTFY_TOPIC`).
4. You will instantly receive high-priority alerts whenever:
   - Your attendance drops below 75%.
   - An assignment deadline is within 24 hours.
   - A high-impact hackathon registration is closing.
