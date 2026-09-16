import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

LOCAL_ROOT = Path(r"c:\Users\Shaunak Rane\Desktop\3rd Year")

# Mapping course codes / names to local folder names
FOLDER_MAPPING = {
    "AIM5.52001": "NLP",
    "AIM5.52002": "NLP Lab",
    "CSG5.52001": "AWT",
    "AIM5.53001": "Time Series",
    "AIM5.52005": "Time Series",
    "SKD5.52001": "SEPM",
    "DSC5.52001": "Deep Learning",
    "DSC5.52002": "Deep Learning",
    "CSG5.52003": "AJP",
    "CSG5.52004": "AJP",
    "DSC5.52003": "BDA",
    "SKD5.52002": "Summer Internship",
    "SKD5.52005": "Minor Project",
}

async def audit_all_courses():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "digiicampus.com" in pg.url][0]
        await page.bring_to_front()

        print("Navigating to https://uai.digiicampus.com/classroom ...")
        await page.goto("https://uai.digiicampus.com/classroom", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # Get list of course titles and codes
        courses_data = await page.eval_on_selector_all("*", r'''els => {
            const list = [];
            for (const e of els) {
                const t = (e.innerText || '').trim();
                const m = t.match(/^([A-Za-z\s&()-]+)\s*\[([A-Z0-9.]+)\]$/m);
                if (m && t.length < 80) {
                    if (!list.some(x => x.code === m[2])) {
                        list.push({
                            fullName: t,
                            title: m[1].trim(),
                            code: m[2].trim()
                        });
                    }
                }
            }
            return list;
        }''')

        print(f"Found {len(courses_data)} courses to audit:")
        for c in courses_data:
            print(f"  • {c['title']} [{c['code']}]")

        audit_results = []

        for idx, course in enumerate(courses_data):
            code = course["code"]
            name = course["title"]
            full_title = course["fullName"]
            print(f"\n[{idx+1}/{len(courses_data)}] Auditing {name} [{code}]...")

            # Make sure we are on classroom page
            if "classroom" not in page.url or "courseWork" in page.url or "resources" in page.url:
                await page.goto("https://uai.digiicampus.com/classroom", wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)

            # Click the course
            course_elem = page.get_by_text(f"[{code}]", exact=False).first
            try:
                await course_elem.click(timeout=5000)
                await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"  Could not click {name}: {e}")
                continue

            current_url = page.url
            course_id_match = current_url.split("/classroom/")
            course_id = course_id_match[1].split("/")[0] if len(course_id_match) > 1 else ""

            course_record = {
                "course_name": name,
                "course_code": code,
                "course_id": course_id,
                "classroom_url": current_url,
                "local_folder": FOLDER_MAPPING.get(code, name),
                "resources": [],
                "ongoing_assignments": [],
                "closed_assignments": []
            }

            # 1. Check Resources
            try:
                # Click Resources in left subnav
                res_tab = page.get_by_text("Resources", exact=True).first
                await res_tab.click(timeout=4000)
                await page.wait_for_timeout(2500)

                # Extract resources list from table
                resources = await page.eval_on_selector_all("table tr, .ant-table-row", r'''rows => {
                    const res = [];
                    for (const row of rows) {
                        const text = (row.innerText || '').trim();
                        const lines = text.split('\n').map(x => x.trim()).filter(Boolean);
                        if (lines.length >= 2 && !text.includes('Resource\tSession')) {
                            res.push({
                                raw: lines,
                                name: lines[0],
                                details: lines.slice(1).join(' | ')
                            });
                        }
                    }
                    return res;
                }''')
                course_record["resources"] = resources
                print(f"  Found {len(resources)} resources.")
            except Exception as e:
                print(f"  Note checking resources: {e}")

            # 2. Check Assignments
            try:
                # Click Assignments in subnav
                assign_tab = page.get_by_text("Assignments", exact=True).first
                await assign_tab.click(timeout=4000)
                await page.wait_for_timeout(2000)

                # Check Ongoing
                ongoing_count_text = await page.eval_on_selector("*", r'''e => {
                    const els = Array.from(document.querySelectorAll('*'));
                    const ongoing = els.find(x => (x.innerText || '').trim() === 'Ongoing');
                    if (ongoing && ongoing.nextElementSibling) {
                        return ongoing.nextElementSibling.innerText.trim();
                    }
                    return '0';
                }''')
                
                # Extract ongoing items
                ongoing_cards = await page.eval_on_selector_all(".ant-card, [class*='assignment-card']", r'''els => {
                    return els.map(e => (e.innerText || '').trim()).filter(t => t.length > 0 && !t.includes('Ongoing\n'));
                }''')
                
                # Click Closed tab
                try:
                    closed_tab = page.get_by_text("Closed", exact=False).first
                    await closed_tab.click(timeout=3000)
                    await page.wait_for_timeout(2000)
                    
                    closed_cards_text = await page.eval_on_selector(".ant-app, body", "e => e.innerText")
                    # Parse closed items
                    closed_items = []
                    lines = [l.strip() for l in closed_cards_text.splitlines() if l.strip()]
                    for i, l in enumerate(lines):
                        if l in ["Submitted", "Submission Pending", "Evaluated", "Graded", "Not Submitted"]:
                            title = lines[i-1] if i > 0 else "Unknown"
                            status = l
                            due = ""
                            for j in range(i, min(i+8, len(lines))):
                                if lines[j] == "Due Date" and j+1 < len(lines):
                                    due = lines[j+1]
                                    break
                            closed_items.append({"title": title, "status": status, "due_date": due})
                    course_record["closed_assignments"] = closed_items
                    print(f"  Found {len(closed_items)} closed assignments (Sample: {[c['title'] + ': ' + c['status'] for c in closed_items[:3]]})")
                except Exception as e:
                    print(f"  Note clicking Closed: {e}")

                course_record["ongoing_count"] = ongoing_count_text
                print(f"  Ongoing assignments: {ongoing_count_text}")
            except Exception as e:
                print(f"  Note checking assignments: {e}")

            # Check local files for this subject
            local_subj_dir = LOCAL_ROOT / course_record["local_folder"]
            if local_subj_dir.exists():
                local_files = [f.name for f in local_subj_dir.rglob("*") if f.is_file() and not f.name.startswith(".")]
                course_record["local_files_found"] = local_files
            else:
                course_record["local_files_found"] = []

            audit_results.append(course_record)

        # Save results to json
        out_file = Path("digicampus_full_audit.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(audit_results, f, indent=2)
        print(f"\nAll courses audited! Saved to {out_file.absolute()}")

if __name__ == "__main__":
    asyncio.run(audit_all_courses())
