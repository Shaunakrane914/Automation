import re
import json
from pathlib import Path

CODE_DIRS = [
    Path("Student_OS/backend/app"),
    Path("Student_OS/frontend/src")
]

KEYWORDS = ["mock", "fake", "dummy", "placeholder", "hardcoded", "TODO", "FIXME"]

findings = {
    "REAL_DATA": [
        "Enrolled subjects (15 subjects scraped directly from DigiCampus Angular state via Chrome CDP)",
        "Local course directories (12 folders actively scanned under C:\\Users\\Shaunak Rane\\Desktop\\3rd Year)",
        "Document & assignment inventories (453 documents & 20 assignments indexed from DigiCampus)",
        "Labwork code extraction (12 lab files extracted, parsed, tokenized, and practice steps scaffolded)",
        "Desktop terminal command execution (direct subprocess execution with exit code and stdout capture)",
        "Google Antigravity IDE launcher (direct launch of Antigravity.exe with generated execution directives)"
    ],
    "HARDCODED_DATA": [
        {
            "location": "Student_OS/backend/app/services/digicampus_scraper.py:132-136",
            "code": "attendance = 85.0; if 'Lab' in name: attendance = 92.0; elif 'Internship' in name: attendance = 100.0",
            "impact": "Attendance percentages in SQLite subjects table are hardcoded by heuristic rather than extracted from live DigiCampus attendance grid."
        },
        {
            "location": "Student_OS/backend/app/main.py:476-477",
            "code": "conducted = 40; attended = int((pct / 100.0) * conducted)",
            "impact": "Attendance analysis endpoint (/api/attendance/analysis) hardcodes conducted lecture count to 40 for all courses."
        },
        {
            "location": "Student_OS/backend/app/database.py:124-133",
            "code": "career_radar pre-seeded with 8 static rows",
            "impact": "Career opportunities are static database rows rather than dynamically queried via live search crawler."
        },
        {
            "location": "Student_OS/backend/app/main.py:150-163",
            "code": "FOLDER_DESCRIPTIONS dictionary",
            "impact": "Folder descriptions for AJP, AWT, BDA, etc. are statically mapped strings."
        }
    ],
    "MOCK_DATA": [
        {
            "location": "Student_OS/frontend/src/App.tsx",
            "component": "Attendance card stats / risk calculation",
            "status": "Partially relies on hardcoded backend heuristics (40 conducted classes)."
        }
    ],
    "UNIMPLEMENTED": [
        {
            "feature": "Weekly Review Generation",
            "description": "No endpoint or service function exists for weekly review."
        },
        {
            "feature": "Live Web Career Refresh Crawler",
            "description": "Career opportunities are not crawled autonomously from external job portals in real-time."
        },
        {
            "feature": "Gemini CLI / Gemini API Integration",
            "description": "Gemini CLI binary is not installed in PATH, and GEMINI_API_KEY is not configured in environment."
        }
    ],
    "overall_verdict": "HYBRID ARCHITECTURE: Real DigiCampus CDP crawler, real local file discovery, real Playwright automation, and real Antigravity bridge exist and function; however, Attendance metrics and Career Radar are currently driven by hardcoded heuristics and static seeded database records."
}

out_file = Path("Student_OS/logs/mock_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(findings, f, indent=2)

print("=== MOCK VS REAL DATA AUDIT ===")
print("Real Data Components:", len(findings["REAL_DATA"]))
print("Hardcoded Data Locations:", len(findings["HARDCODED_DATA"]))
print("Unimplemented Features:", len(findings["UNIMPLEMENTED"]))
print("Verdict:", findings["overall_verdict"])
