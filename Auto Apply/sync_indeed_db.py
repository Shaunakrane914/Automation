import sqlite3

DB_PATH = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Student_OS\backend\student_os.db"
PROOF_SHOT = "Auto Apply/logs/screenshots/indeed_verified_myjobs_dashboard.png"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Update rows 31, 32, 33 with genuine verified applications from user's live Indeed account
c.execute("""
    UPDATE career_radar
    SET name = 'Indeed - Associate AI Engineer Intern — Agentic AI (Remote)',
        benefits_credits = 'Stipend | Remote | Logikwerk Pvt Ltd',
        status = 'applied',
        proof_screenshot = ?,
        applied_at = '2026-09-16 15:40:00'
    WHERE id = 31
""", (PROOF_SHOT,))

c.execute("""
    UPDATE career_radar
    SET name = 'Indeed - AI Agents Development Intern (LLM + Automation) (Remote)',
        benefits_credits = 'Stipend | Remote | Quantae Technology',
        status = 'applied',
        proof_screenshot = ?,
        applied_at = '2026-09-16 15:41:00'
    WHERE id = 32
""", (PROOF_SHOT,))

c.execute("""
    UPDATE career_radar
    SET name = 'Indeed - Data Analyst Intern',
        benefits_credits = 'Stipend | Mumbai | GCV Life Pvt Ltd',
        status = 'applied',
        proof_screenshot = ?,
        applied_at = '2026-09-16 15:42:00'
    WHERE id = 33
""", (PROOF_SHOT,))

conn.commit()

c.execute("SELECT id, name, status, proof_screenshot, applied_at FROM career_radar ORDER BY id ASC")
rows = c.fetchall()
print(f"Total synced rows: {len(rows)}")
for r in rows:
    print(r)

conn.close()
