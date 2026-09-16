import time
import json
import sqlite3
from pathlib import Path
from playwright.sync_api import sync_playwright

DB_PATH = Path("Student_OS/backend/student_os.db")
results = {
    "button_found": False,
    "first_run": {},
    "second_run": {},
    "ui_changes_observed": [],
    "duplication_detected": False,
    "overall_status": "PENDING"
}

def get_db_counts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM subjects")
    s_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM documents")
    d_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM assignments")
    a_cnt = cursor.fetchone()[0]
    conn.close()
    return {"subjects": s_cnt, "documents": d_cnt, "assignments": a_cnt}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://127.0.0.1:8000/", timeout=15000)
    page.wait_for_timeout(2000)

    # 1. Locate button
    btn = page.locator("button:has-text('Rerun Full Update')").first
    results["button_found"] = (btn.count() > 0)

    if not results["button_found"]:
        results["overall_status"] = "FAIL — Button 'Rerun Full Update' not found in UI"
    else:
        # Before run 1 counts
        counts_0 = get_db_counts()

        # Click 1
        print("Clicking 'Rerun Full Update' Run 1...")
        btn.click()
        page.wait_for_timeout(1000)

        # Check UI reaction
        text_content = page.content()
        if "Auditing" in text_content or "Syncing" in text_content:
            results["ui_changes_observed"].append("Progress text appeared on button / banner")

        # Wait up to 120 seconds for sync to complete or progress
        for i in range(120):
            page.wait_for_timeout(1000)
            btn_cnt = page.locator("button:has-text('Rerun Full Update')").count()
            cur_text = page.locator("header").inner_text()
            if "Auditing" in cur_text or "Syncing" in cur_text:
                if len(results["ui_changes_observed"]) < 3:
                    results["ui_changes_observed"].append(f"T+{i}s: {cur_text[:50]}...")
            if btn_cnt > 0 and not ("Syncing" in cur_text or "Auditing" in cur_text):
                results["ui_changes_observed"].append(f"Sync 1 completed around T+{i}s")
                break

        counts_1 = get_db_counts()
        results["first_run"] = {
            "counts_before": counts_0,
            "counts_after": counts_1
        }

        # Click 2 (to check duplicate creation)
        print("Clicking 'Rerun Full Update' Run 2...")
        btn = page.locator("button:has-text('Rerun Full Update')").first
        btn.wait_for(state="visible", timeout=10000)
        btn.click()
        page.wait_for_timeout(1000)

        for i in range(120):
            page.wait_for_timeout(1000)
            btn_cnt = page.locator("button:has-text('Rerun Full Update')").count()
            cur_text = page.locator("header").inner_text()
            if btn_cnt > 0 and not ("Syncing" in cur_text or "Auditing" in cur_text):
                results["ui_changes_observed"].append(f"Sync 2 completed around T+{i}s")
                break

        counts_2 = get_db_counts()
        results["second_run"] = {
            "counts_before": counts_1,
            "counts_after": counts_2
        }

        # Check for duplicates between run 1 and run 2
        dup_subjects = counts_2["subjects"] != counts_1["subjects"]
        dup_assignments = counts_2["assignments"] != counts_1["assignments"]

        if dup_subjects or dup_assignments:
            results["duplication_detected"] = True
            results["overall_status"] = f"PARTIAL — Sync executed but created duplicates (Assignments: {counts_1['assignments']} -> {counts_2['assignments']})"
        else:
            results["duplication_detected"] = False
            results["overall_status"] = "PASS"

    browser.close()

out_file = Path("Student_OS/logs/full_update_button_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== FULL UPDATE BUTTON TEST ===")
print("Button Found:", results["button_found"])
print("First Run Counts:", results["first_run"])
print("Second Run Counts:", results["second_run"])
print("Duplication Detected:", results["duplication_detected"])
print("Overall Status:", results["overall_status"])
