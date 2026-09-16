import sqlite3
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "student_os.db"
AUDIT_FILE = BASE_DIR / "data" / "digicampus_complete_audit.json"

def populate():
    if not AUDIT_FILE.exists():
        print("Audit file not found!")
        return

    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        audit_data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear previous mock subjects, documents, and assignments
    cursor.execute("DELETE FROM assignments")
    cursor.execute("DELETE FROM documents")
    cursor.execute("DELETE FROM subjects")
    conn.commit()

    print(f"Cleared old mock records. Inserting {len(audit_data)} real DigiCampus courses...")

    for item in audit_data:
        name = item["course_name"]
        code = item["course_code"]
        local_dir = item.get("local_folder_path", "")
        
        # Default attendance baseline or 85%
        attendance = 85.0
        if "Lab" in name:
            attendance = 92.0
        elif "Internship" in name or "Project" in name:
            attendance = 100.0

        cursor.execute("""
        INSERT INTO subjects (name, code, attendance_percentage, last_synced)
        VALUES (?, ?, ?, ?)
        """, (name, code, attendance, datetime.now().isoformat()))
        subject_id = cursor.lastrowid

        # Insert documents / resources
        for res in item.get("resources", []):
            rname = res["resource_name"]
            upload_date = res.get("added_on", "")
            cursor.execute("""
            INSERT OR IGNORE INTO documents (subject_id, file_name, local_path, upload_date, summary_path)
            VALUES (?, ?, ?, ?, ?)
            """, (subject_id, rname, local_dir, upload_date, ""))

        # Insert local files as documents too
        for lf in item.get("local_files", [])[:10]: # top 10 local files
            cursor.execute("""
            INSERT OR IGNORE INTO documents (subject_id, file_name, local_path, upload_date, summary_path)
            VALUES (?, ?, ?, ?, ?)
            """, (subject_id, lf, str(Path(local_dir) / lf), datetime.now().strftime("%Y-%m-%d"), ""))

        # Insert assignments
        for asg in item.get("closed_assignments", []):
            title = asg["title"]
            status = asg["status"]
            due = asg.get("due_date", "")
            is_lab = 1 if "lab" in name.lower() or "lab" in title.lower() else 0
            cursor.execute("""
            INSERT INTO assignments (subject_id, title, deadline, is_lab, status, local_lab_dir)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (subject_id, title, due, is_lab, status, local_dir))

    # Also make sure career_radar has clean non-personal descriptions
    cursor.execute("""
    UPDATE career_radar
    SET eligibility = REPLACE(eligibility, 'Shaunak Rane (', '')
    WHERE eligibility LIKE '%Shaunak Rane%'
    """)
    cursor.execute("""
    UPDATE career_radar
    SET eligibility = REPLACE(eligibility, ')', '')
    WHERE eligibility LIKE '%May 2028 batch%'
    """)

    conn.commit()
    conn.close()
    print("Database populated successfully with live DigiCampus courses, resources, and assignment history!")

if __name__ == "__main__":
    populate()
