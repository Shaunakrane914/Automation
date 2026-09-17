import sqlite3

conn = sqlite3.connect('Student_OS/backend/student_os.db')
c = conn.cursor()
c.execute("SELECT id, category, name, status, url, proof_screenshot FROM career_radar WHERE status='applied'")
rows = c.fetchall()
print(f"Total applied rows in DB: {len(rows)}")
for r in rows:
    print(r)
