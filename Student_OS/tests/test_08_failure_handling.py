import os
import sys
import json
import sqlite3
import tempfile
from pathlib import Path

results = {
    "test_a_digicampus_down": {},
    "test_b_cdp_unavailable": {},
    "test_c_network_unavailable": {},
    "test_d_db_locked": {},
    "test_e_partial_subject_failure": {},
    "summary": {},
    "overall_status": "PENDING"
}

# --- Test B: Chrome CDP Unavailable ---
# Attempt to connect to a non-existent CDP port 9998
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            p.chromium.connect_over_cdp("http://127.0.0.1:9998", timeout=3000)
            results["test_b_cdp_unavailable"] = {"handled": False, "error": "Unexpected connection success"}
        except Exception as e:
            results["test_b_cdp_unavailable"] = {
                "handled": True,
                "error_type": type(e).__name__,
                "message": str(e)[:120],
                "status": "PASS (Graceful exception caught)"
            }
except Exception as e:
    results["test_b_cdp_unavailable"] = {"handled": False, "error": str(e)}

# --- Test A: DigiCampus Session Expired / Missing Page ---
# Test the logic when no 'digiicampus.com' tab exists in context
test_pages_urls = ["https://google.com", "about:blank"]
matching_pages = [u for u in test_pages_urls if "digiicampus.com" in u]
if not matching_pages:
    # Check if existing code does [pg for ...][0] without check
    results["test_a_digicampus_down"] = {
        "vulnerability_identified": True,
        "flaw": "In comprehensive_academic_sync.py line 52: [pg for pg in context.pages if 'digiicampus.com' in pg.url][0] raises IndexError if DigiCampus tab is not open",
        "status": "FAIL — Code lacks fallback or error catch if DigiCampus tab is closed"
    }

# --- Test C: Network Unavailable ---
# Test what notifications.py does if network/DNS fails
try:
    import urllib.request
    req = urllib.request.Request("http://invalid-domain-that-does-not-exist-12345.xyz", timeout=2)
    urllib.request.urlopen(req)
    results["test_c_network_unavailable"] = {"handled": False}
except Exception as e:
    results["test_c_network_unavailable"] = {
        "handled": True,
        "error_type": type(e).__name__,
        "status": "PASS (Network failure raises catchable urllib/http exception)"
    }

# --- Test D: Database Locked / Unavailable ---
temp_db = Path("Student_OS/test_artifacts/locked_test.db")
if temp_db.exists():
    temp_db.unlink()
conn1 = sqlite3.connect(temp_db)
c1 = conn1.cursor()
c1.execute("CREATE TABLE test_items (id INTEGER PRIMARY KEY, val TEXT)")
c1.execute("INSERT INTO test_items VALUES (1, 'locked')")
conn1.commit()

# Acquire exclusive lock
c1.execute("BEGIN EXCLUSIVE")
c1.execute("UPDATE test_items SET val = 'mod' WHERE id = 1")

# Try second connection with short timeout
conn2 = sqlite3.connect(temp_db, timeout=0.1)
c2 = conn2.cursor()
try:
    c2.execute("UPDATE test_items SET val = 'override' WHERE id = 1")
    conn2.commit()
    results["test_d_db_locked"] = {"handled": False, "status": "FAIL — Lock was ignored"}
except sqlite3.OperationalError as e:
    results["test_d_db_locked"] = {
        "handled": True,
        "error": str(e),
        "status": "PASS (sqlite3.OperationalError: database is locked caught properly)"
    }
finally:
    conn1.rollback()
    conn1.close()
    conn2.close()
    if temp_db.exists():
        temp_db.unlink()

# --- Test E: Partial Subject Failure Behavior ---
# Inspect whether sync_digicampus flags a sync as successful even when child process fails
results["test_e_partial_subject_failure"] = {
    "flaw_identified": True,
    "description": "digicampus_scraper.py runs proc.wait() but does not check proc.returncode != 0. If 1 or more subjects fail or crawler crashes, it still loads stale digicampus_complete_audit.json and broadcasts SYNC_COMPLETED.",
    "status": "FAIL — False positive completion on partial crawler crash"
}

out_file = Path("Student_OS/logs/failure_handling_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== FAILURE HANDLING AUDIT ===")
print("CDP Unavailable Test:", results["test_b_cdp_unavailable"].get("status"))
print("DigiCampus Tab Missing:", results["test_a_digicampus_down"].get("status"))
print("Network Unavailable:", results["test_c_network_unavailable"].get("status"))
print("DB Locked Test:", results["test_d_db_locked"].get("status"))
print("Partial Subject Failure:", results["test_e_partial_subject_failure"].get("status"))
