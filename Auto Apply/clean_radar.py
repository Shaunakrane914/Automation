import sqlite3

conn = sqlite3.connect('Student_OS/backend/student_os.db')
c = conn.cursor()
c.execute("DELETE FROM career_radar WHERE id IN (28, 29, 30)")
conn.commit()

c.execute("SELECT id, name, status, proof_screenshot FROM career_radar WHERE status='applied'")
rows = c.fetchall()
print("Final applied rows:")
for r in rows:
    print(r)
conn.close()
