import asyncio
import json
import os
import re
from pathlib import Path
from playwright.async_api import async_playwright

LOCAL_3RD_YEAR = Path(r"c:\Users\Shaunak Rane\Desktop\3rd Year")

# All 15 DigiCampus courses mapped strictly into C:\Users\Shaunak Rane\Desktop\3rd Year
FOLDER_MAPPING = {
    "AIM5.52001": ("NLP", LOCAL_3RD_YEAR / "NLP"),
    "AIM5.52002": ("NLP Lab", LOCAL_3RD_YEAR / "NLP Lab"),
    "CSG5.52001": ("AWT", LOCAL_3RD_YEAR / "AWT"),
    "AIM5.53001": ("Time Series", LOCAL_3RD_YEAR / "Time Series"),
    "AIM5.52005": ("Time Series", LOCAL_3RD_YEAR / "Time Series"),
    "SKD5.52001": ("SEPM", LOCAL_3RD_YEAR / "SEPM"),
    "DSC5.52001": ("Deep Learning", LOCAL_3RD_YEAR / "Deep Learning"),
    "DSC5.52002": ("Deep Learning", LOCAL_3RD_YEAR / "Deep Learning"),
    "CSG5.52003": ("AJP", LOCAL_3RD_YEAR / "AJP"),
    "CSG5.52004": ("AJP", LOCAL_3RD_YEAR / "AJP"),
    "DSC5.52003": ("BDA", LOCAL_3RD_YEAR / "BDA"),
    "SKD5.52002": ("Summer Internship", LOCAL_3RD_YEAR / "Summer Internship"),
    "SKD5.52005": ("Minor Project", LOCAL_3RD_YEAR / "Minor Project"),
    "ADT5.00002": ("Mentoring", LOCAL_3RD_YEAR / "Mentoring"),
    "UAITP01": ("Training & Placement", LOCAL_3RD_YEAR / "Training & Placement"),
}

IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".vscode", "dist", "build"}

def get_academic_files(local_dir: Path):
    if not local_dir.exists():
        return []
    files = []
    for p in local_dir.rglob("*"):
        if p.is_file() and not any(part in IGNORE_DIRS or part.startswith(".") for part in p.parts):
            files.append(p.name)
    return files

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

async def run_sync():
    config_file = DATA_DIR / "all_angular_classes.json"
    with open(config_file, "r", encoding="utf-8") as f:
        classes = json.load(f)

    print(f"Loaded {len(classes)} classes from DigiCampus configuration.")

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        matching_pages = [pg for pg in context.pages if "digiicampus.com" in pg.url]
        if matching_pages:
            page = matching_pages[0]
            await page.bring_to_front()
        else:
            page = await context.new_page()
            await page.goto("https://uai.digiicampus.com/feed", timeout=20000)

        if "login" in page.url.lower():
            raise RuntimeError("FAIL — AUTHENTICATION SESSION EXPIRED: DigiCampus redirected to login.")

        results = []

        for idx, c in enumerate(classes):
            cid = c.get("id")
            cname = c.get("courseName")
            ccode = c.get("courseCode")
            ctype = c.get("courseComponentTypeName", "Lecture")
            faculty = c.get("className", "")
            print(f"\n==================================================")
            print(f"[{idx+1}/{len(classes)}] Auditing: {cname} (ID: {cid})")
            print(f"==================================================")

            folder_name, local_dir = FOLDER_MAPPING.get(ccode, (cname, LOCAL_3RD_YEAR / cname))
            local_dir.mkdir(parents=True, exist_ok=True)
            
            # Genuine academic files (ignoring node_modules, git, venv)
            local_files = get_academic_files(local_dir)
            
            subject_report = {
                "course_name": cname,
                "course_code": ccode,
                "course_type": ctype,
                "faculty_info": faculty,
                "digicampus_id": cid,
                "local_folder_name": folder_name,
                "local_folder_path": str(local_dir),
                "local_folder_exists": local_dir.exists(),
                "local_files_count": len(local_files),
                "local_files": local_files,
                "resources": [],
                "ongoing_assignments": [],
                "closed_assignments": [],
                "ongoing_count": 0,
                "pending_assignments_count": 0,
                "missing_resources": []
            }

            # 1. Fetch Resources
            res_url = f"https://uai.digiicampus.com/V2/#/classroom/{cid}/resources"
            try:
                await page.goto(res_url, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)

                resources = await page.evaluate('''() => {
                    const trs = Array.from(document.querySelectorAll('table tbody tr, .ant-table-row'));
                    const list = [];
                    for (const tr of trs) {
                        const cells = Array.from(tr.querySelectorAll('td')).map(td => (td.innerText || '').trim());
                        if (cells.length >= 4) {
                            const name = cells[0] ? cells[0] : cells[1];
                            const session = cells[0] ? cells[1] : cells[2];
                            const size = cells.length >= 5 ? cells[3] : cells[2];
                            const date = cells.length >= 5 ? cells[4] : cells[3];
                            if (name && name !== 'Resource' && !list.some(x => x.resource_name === name)) {
                                list.push({
                                    resource_name: name,
                                    session: session,
                                    file_size: size,
                                    added_on: date
                                });
                            }
                        }
                    }
                    return list;
                }''')
                subject_report["resources"] = resources
                print(f"  • Resources on DigiCampus: {len(resources)}")
                for r in resources:
                    r_name = r['resource_name']
                    # Check match in local files
                    clean_r = re.sub(r'[\.\s_-]', '', r_name.lower())
                    matched = any(
                        r_name.lower() in lf.lower() or 
                        lf.lower() in r_name.lower() or
                        clean_r in re.sub(r'[\.\s_-]', '', lf.lower()) or
                        re.sub(r'[\.\s_-]', '', lf.lower()) in clean_r
                        for lf in local_files
                    )
                    if not matched:
                        subject_report["missing_resources"].append(r_name)
                    print(f"     - {r_name} ({r['file_size']}) -> {'[FOUND LOCALLY]' if matched else '[NOT IN FOLDER]'}")
            except Exception as e:
                print(f"  Error fetching resources: {e}")

            # 2. Fetch Assignments
            assign_url = f"https://uai.digiicampus.com/V2/#/classroom/{cid}/assignments"
            try:
                await page.goto(assign_url, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)

                # Check Ongoing
                ongoing_count_str = await page.eval_on_selector("*", r'''() => {
                    const els = Array.from(document.querySelectorAll('*'));
                    const o = els.find(x => (x.innerText || '').trim() === 'Ongoing');
                    if (o && o.nextElementSibling) return o.nextElementSibling.innerText.trim();
                    return '0';
                }''')
                subject_report["ongoing_count"] = int(ongoing_count_str) if ongoing_count_str.isdigit() else 0
                print(f"  • Ongoing assignments count: {subject_report['ongoing_count']}")

                # Extract Ongoing Assignments cards if any exist
                try:
                    ongoing_text = await page.eval_on_selector(".ant-app, body", "e => e.innerText")
                    lines = [l.strip() for l in ongoing_text.splitlines() if l.strip()]
                    ongoing_list = []
                    for i, l in enumerate(lines):
                        if any(term in l.lower() for term in ["due date", "submission pending", "due on", "expires"]):
                            title = lines[i-1] if i > 0 else "Pending Assignment"
                            if title in ["Ongoing", "Closed", "Assignments", "Classroom"]:
                                continue
                            due = ""
                            for j in range(i, min(i+6, len(lines))):
                                if "due" in lines[j].lower() and j+1 < len(lines):
                                    due = lines[j+1]
                                    break
                            if title and not any(oa["title"] == title for oa in ongoing_list):
                                ongoing_list.append({"title": title, "status": "pending", "due_date": due})
                    if ongoing_list:
                        subject_report["ongoing_assignments"] = ongoing_list
                        subject_report["pending_assignments_count"] += len(ongoing_list)
                        print(f"  • Scraped {len(ongoing_list)} ongoing assignments: {[x['title'] for x in ongoing_list]}")
                except Exception as oe:
                    print(f"  Note parsing ongoing assignments: {oe}")

                # Check Closed Assignments
                try:
                    closed_btn = page.get_by_text("Closed", exact=False).first
                    if await closed_btn.is_visible():
                        await closed_btn.click(timeout=3000)
                        await page.wait_for_timeout(1800)

                        closed_text = await page.eval_on_selector(".ant-app, body", "e => e.innerText")
                        lines = [l.strip() for l in closed_text.splitlines() if l.strip()]
                        closed_list = []
                        for i, l in enumerate(lines):
                            if l in ["Submitted", "Submission Pending", "Evaluated", "Graded", "Not Submitted"]:
                                title = lines[i-1] if i > 0 else "Unknown"
                                if title in ["Closed", "Ongoing", "Assignments"]:
                                    continue
                                status = l
                                due = ""
                                for j in range(i, min(i+8, len(lines))):
                                    if lines[j] == "Due Date" and j+1 < len(lines):
                                        due = lines[j+1]
                                        break
                                closed_list.append({"title": title, "status": status, "due_date": due})
                                if status in ["Submission Pending", "Not Submitted"]:
                                    subject_report["pending_assignments_count"] += 1

                        subject_report["closed_assignments"] = closed_list
                        print(f"  • Closed assignments: {len(closed_list)}")
                        for ca in closed_list:
                            print(f"     - [{ca['status']}] {ca['title']} (Due: {ca['due_date']})")
                except Exception as ce:
                    print(f"  Note parsing closed assignments: {ce}")

            except Exception as e:
                print(f"  Error fetching assignments: {e}")

            results.append(subject_report)

        out_file = DATA_DIR / "digicampus_complete_audit.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nAudit complete! Saved all 15 subjects to {out_file}")

if __name__ == "__main__":
    asyncio.run(run_sync())
