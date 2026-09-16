import sqlite3
import json
import time
from pathlib import Path

DB_PATH = Path("Student_OS/backend/student_os.db")
results = {}

try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Inspect existing tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    existing_tables = [r[0] for r in cursor.fetchall()]
    results["existing_tables"] = existing_tables

    expected_entities = [
        "subjects", "assignments", "documents", "career_radar", 
        "daily_todos", "agent_logs", "labworks"
    ]
    extended_requested = [
        "classes", "attendance", "applications", "notifications", "sync_runs", "user_preferences"
    ]

    results["expected_entities_audit"] = {
        ent: (ent in existing_tables) for ent in expected_entities + extended_requested
    }

    # 2. Foreign key verification
    cursor.execute("PRAGMA foreign_key_check")
    fk_errors = cursor.fetchall()
    results["foreign_key_errors"] = len(fk_errors)

    # 3. Duplicate checks
    cursor.execute("SELECT name, count(*) FROM subjects GROUP BY name HAVING count(*) > 1")
    dup_subjects = cursor.fetchall()

    cursor.execute("SELECT subject_id, title, count(*) FROM assignments GROUP BY subject_id, title HAVING count(*) > 1")
    dup_assignments = cursor.fetchall()

    cursor.execute("SELECT category, name, count(*) FROM career_radar GROUP BY category, name HAVING count(*) > 1")
    dup_career = cursor.fetchall()

    results["duplicates"] = {
        "subjects": len(dup_subjects),
        "assignments": len(dup_assignments),
        "career_radar": len(dup_career)
    }

    # 4. Record counts & timestamp validation
    counts = {}
    for table in existing_tables:
        cursor.execute(f"SELECT count(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]
    results["record_counts"] = counts

    # 5. Persistence across write/close/reopen
    test_title = f"[TEST_PERSISTENCE_{int(time.time())}]"
    cursor.execute("INSERT INTO daily_todos (title, category, due_date, completed) VALUES (?, ?, ?, ?)",
                   (test_title, "Test", "2026-09-16", 0))
    test_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Reopen connection
    conn2 = sqlite3.connect(DB_PATH)
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT title FROM daily_todos WHERE id = ?", (test_id,))
    row = cursor2.fetchone()
    persisted = (row is not None and row[0] == test_title)

    # Clean up test row
    cursor2.execute("DELETE FROM daily_todos WHERE id = ?", (test_id,))
    conn2.commit()
    conn2.close()

    results["persistence_test"] = "PASS" if persisted else "FAIL"

    # Evaluation
    missing_tables = [t for t, present in results["expected_entities_audit"].items() if not present]
    if missing_tables:
        results["overall_status"] = f"PARTIAL (Tables present: {len(existing_tables)}, Tables absent: {missing_tables})"
    else:
        results["overall_status"] = "PASS"

except Exception as e:
    results["overall_status"] = f"FAIL ({e})"

out_file = Path("Student_OS/logs/database_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== DATABASE TEST RESULTS ===")
print("Existing Tables:", results.get("existing_tables"))
print("Record Counts:", results.get("record_counts"))
print("Duplicate Counts:", results.get("duplicates"))
print("FK Check Errors:", results.get("foreign_key_errors"))
print("Persistence Test:", results.get("persistence_test"))
print("Missing Expected Entities:", [t for t, p in results.get("expected_entities_audit", {}).items() if not p])
print("Overall Database Status:", results.get("overall_status"))
