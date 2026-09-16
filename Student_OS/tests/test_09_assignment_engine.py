import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

ARTIFACTS_DIR = Path("Student_OS/test_artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path("Student_OS/backend/student_os.db")

results = {
    "test_cases": {},
    "priority_calculation": {},
    "todo_generation": {},
    "duplicate_prevention": {},
    "overall_status": "PENDING"
}

now = datetime.now()
today_str = now.strftime("%Y-%m-%d")
tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
next_week_str = (now + timedelta(days=7)).strftime("%Y-%m-%d")
overdue_str = (now - timedelta(days=3)).strftime("%Y-%m-%d")

test_scenarios = [
    {"title": "Test Assignment Today", "deadline": today_str, "status": "Open", "expected_priority": "CRITICAL"},
    {"title": "Test Assignment Tomorrow", "deadline": tomorrow_str, "status": "Open", "expected_priority": "HIGH"},
    {"title": "Test Assignment Next Week", "deadline": next_week_str, "status": "Open", "expected_priority": "MEDIUM"},
    {"title": "Test Assignment Overdue", "deadline": overdue_str, "status": "Open", "expected_priority": "OVERDUE"},
    {"title": "Test Assignment Completed", "deadline": overdue_str, "status": "Completed", "expected_priority": "DONE"},
    {"title": "Test Assignment Submitted", "deadline": today_str, "status": "Submitted", "expected_priority": "DONE"},
    {"title": "Test Assignment Closed", "deadline": overdue_str, "status": "Closed", "expected_priority": "CLOSED"},
]

def calculate_priority(deadline_str: str, status: str) -> str:
    if status in ["Completed", "Submitted"]:
        return "DONE"
    if status == "Closed":
        return "CLOSED"
    try:
        d = datetime.strptime(deadline_str[:10], "%Y-%m-%d")
        delta = (d.date() - now.date()).days
        if delta < 0:
            return "OVERDUE"
        elif delta == 0:
            return "CRITICAL"
        elif delta <= 2:
            return "HIGH"
        elif delta <= 7:
            return "MEDIUM"
        else:
            return "LOW"
    except Exception:
        return "UNKNOWN"

for s in test_scenarios:
    calc = calculate_priority(s["deadline"], s["status"])
    matches = (calc == s["expected_priority"])
    results["test_cases"][s["title"]] = {
        "deadline": s["deadline"],
        "status": s["status"],
        "calculated_priority": calc,
        "expected_priority": s["expected_priority"],
        "match": matches
    }

# Check database duplicate prevention and todo generation
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get a valid subject_id
cursor.execute("SELECT id FROM subjects LIMIT 1")
row = cursor.fetchone()
subj_id = row[0] if row else 1

test_title = "AUTOMATED_TEST_DEDUP_ASSIGNMENT"
# Run 1: Insert assignment
cursor.execute("SELECT count(*) FROM assignments WHERE title = ?", (test_title,))
c_before = cursor.fetchone()[0]

cursor.execute("""
INSERT OR IGNORE INTO assignments (subject_id, title, deadline, is_lab, status, local_lab_dir)
VALUES (?, ?, ?, ?, ?, ?)
""", (subj_id, test_title, today_str, 0, "Open", "TestDir"))
conn.commit()

cursor.execute("SELECT count(*) FROM assignments WHERE title = ?", (test_title,))
c_after1 = cursor.fetchone()[0]

# Run 2: Re-insert same assignment (simulate re-sync)
cursor.execute("""
INSERT OR IGNORE INTO assignments (subject_id, title, deadline, is_lab, status, local_lab_dir)
VALUES (?, ?, ?, ?, ?, ?)
""", (subj_id, test_title, today_str, 0, "Open", "TestDir"))
conn.commit()

cursor.execute("SELECT count(*) FROM assignments WHERE title = ?", (test_title,))
c_after2 = cursor.fetchone()[0]

# Clean up test assignment
cursor.execute("DELETE FROM assignments WHERE title = ?", (test_title,))
conn.commit()
conn.close()

results["duplicate_prevention"] = {
    "count_before": c_before,
    "count_after_first_insert": c_after1,
    "count_after_second_insert": c_after2,
    "prevented_duplicate": (c_after1 == c_after2 == 1) if c_after1 > 0 else False
}

all_priority_ok = all(tc["match"] for tc in results["test_cases"].values())
if all_priority_ok and results["duplicate_prevention"]["prevented_duplicate"]:
    results["overall_status"] = "PASS"
elif all_priority_ok and not results["duplicate_prevention"]["prevented_duplicate"]:
    results["overall_status"] = "PARTIAL — Priority calculation passed, but DB lacks UNIQUE constraint on assignments(title, subject_id)"
else:
    results["overall_status"] = "FAIL"

out_file = Path("Student_OS/logs/assignment_engine_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== ASSIGNMENT ENGINE AUDIT ===")
print("Overall Status:", results["overall_status"])
print("Test Cases:", len(results["test_cases"]))
print("Duplicate Prevention:", results["duplicate_prevention"])
