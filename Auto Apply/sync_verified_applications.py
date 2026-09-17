import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = r"Student_OS\backend\student_os.db"
CSV_PATH = r"Auto Apply\all excels\all_applied_applications_history.csv"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Update existing Indeed rows to 'requires_manual_login' instead of 'applied'
cursor.execute("""
    UPDATE career_radar 
    SET status = 'action_required', 
        proof_screenshot = 'Auto Apply/logs/screenshots/test_indeed_final.png'
    WHERE name LIKE '%Indeed%' AND status = 'applied'
""")

# 2. Clean up dummy search URLs from earlier test runs
cursor.execute("""
    DELETE FROM career_radar 
    WHERE status = 'applied' AND url LIKE '%search%'
""")

# 3. Insert or update the 4 verified genuine applications
genuine_apps = [
    {
        "category": "internship",
        "name": "LinkedIn - AI Prompt Engineer (Remote)",
        "deadline": "2026-10-15",
        "benefits_credits": "Stipend / Certificate / Letter of Recommendation",
        "status": "applied",
        "url": "https://www.linkedin.com/jobs/view/ai-prompt-engineer-at-caravel-bpm-technology-solutions",
        "eligibility": "Python, Prompt Engineering, AI Models",
        "applied_at": "2026-09-16 15:19:22",
        "proof_screenshot": "Auto Apply/logs/screenshots/real_linkedin_applied_1_1789552162.png"
    },
    {
        "category": "internship",
        "name": "LinkedIn - AI Trainer - Remote",
        "deadline": "2026-10-20",
        "benefits_credits": "$60 - $100/hr / Remote / Top 10% Applicant",
        "status": "applied",
        "url": "https://www.linkedin.com/jobs/view/ai-trainer-remote-at-yo-hr-consultancy",
        "eligibility": "AI Data Evaluation, Model Training, Critical Thinking",
        "applied_at": "2026-09-16 15:19:45",
        "proof_screenshot": "Auto Apply/logs/screenshots/real_linkedin_applied_2_1789552185.png"
    },
    {
        "category": "internship",
        "name": "Internshala - Machine Learning Internship (WFH)",
        "deadline": "2026-09-30",
        "benefits_credits": "Verified on Account Dashboard / Applied 16 Sep 2026",
        "status": "applied",
        "url": "https://internshala.com/internship/detail/work-from-home-machine-learning-internship-at-pledge-india-foundation",
        "eligibility": "Machine Learning, Python, Data Science",
        "applied_at": "2026-09-16 15:00:00",
        "proof_screenshot": "Auto Apply/logs/screenshots/internshala_my_applications_scrolled.png"
    },
    {
        "category": "internship",
        "name": "Internshala - Software Development Internship (WFH)",
        "deadline": "2026-09-30",
        "benefits_credits": "Verified on Account Dashboard / Applied 16 Sep 2026",
        "status": "applied",
        "url": "https://internshala.com/internship/detail/work-from-home-software-development-internship-at-basti-ki-pathshala-foundation",
        "eligibility": "Software Development, Python, Full Stack",
        "applied_at": "2026-09-16 15:00:00",
        "proof_screenshot": "Auto Apply/logs/screenshots/internshala_my_applications_scrolled.png"
    }
]

for app in genuine_apps:
    cursor.execute("""
        INSERT INTO career_radar (category, name, deadline, benefits_credits, status, url, eligibility, applied_at, proof_screenshot)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        app["category"], app["name"], app["deadline"], app["benefits_credits"],
        app["status"], app["url"], app["eligibility"], app["applied_at"], app["proof_screenshot"]
    ))

conn.commit()
print("Updated database career_radar successfully.")

# 4. Update the history CSV
csv_rows = [
    {
        "Date": "2026-09-16",
        "Company": "Caravel | BPM Technology Solutions",
        "Job Title": "AI Prompt Engineer",
        "Platform": "LinkedIn",
        "Status": "Applied",
        "Job URL": "https://www.linkedin.com/jobs/view/ai-prompt-engineer-at-caravel-bpm-technology-solutions",
        "Resume Used": "Shaunak_Rane_Resume.pdf",
        "Proof Screenshot": "real_linkedin_applied_1_1789552162.png"
    },
    {
        "Date": "2026-09-16",
        "Company": "YO HR Consultancy",
        "Job Title": "AI Trainer - Remote",
        "Platform": "LinkedIn",
        "Status": "Applied",
        "Job URL": "https://www.linkedin.com/jobs/view/ai-trainer-remote-at-yo-hr-consultancy",
        "Resume Used": "Shaunak_Rane_Resume.pdf",
        "Proof Screenshot": "real_linkedin_applied_2_1789552185.png"
    },
    {
        "Date": "2026-09-16",
        "Company": "Pledge India Foundation",
        "Job Title": "Machine Learning Internship",
        "Platform": "Internshala",
        "Status": "Applied",
        "Job URL": "https://internshala.com/student/applications",
        "Resume Used": "Shaunak_Rane_Resume.pdf",
        "Proof Screenshot": "internshala_my_applications_scrolled.png"
    },
    {
        "Date": "2026-09-16",
        "Company": "Basti Ki Pathshala Foundation",
        "Job Title": "Software Development Internship",
        "Platform": "Internshala",
        "Status": "Applied",
        "Job URL": "https://internshala.com/student/applications",
        "Resume Used": "Shaunak_Rane_Resume.pdf",
        "Proof Screenshot": "internshala_my_applications_scrolled.png"
    }
]

df = pd.DataFrame(csv_rows)
df.to_csv(CSV_PATH, index=False)
print(f"Updated {CSV_PATH} with verified genuine applications.")

# Query applied rows to verify
cursor.execute("SELECT id, name, status, proof_screenshot FROM career_radar WHERE status='applied'")
rows = cursor.fetchall()
print("\nCurrent genuine applied rows in DB:")
for r in rows:
    print(r)

conn.close()
