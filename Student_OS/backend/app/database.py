import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DATABASE_PATH, timeout=30.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")


    # 1. Subjects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        code TEXT,
        attendance_percentage REAL DEFAULT 0.0,
        last_synced TEXT
    );
    """)

    # 2. Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        file_name TEXT NOT NULL,
        local_path TEXT NOT NULL,
        upload_date TEXT,
        summary_path TEXT,
        FOREIGN KEY (subject_id) REFERENCES subjects (id),
        UNIQUE(subject_id, file_name)
    );
    """)

    # 3. Assignments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        deadline TEXT,
        is_lab INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        local_lab_dir TEXT,
        FOREIGN KEY (subject_id) REFERENCES subjects (id),
        UNIQUE(subject_id, title)
    );
    """)

    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_assignments_subject_title 
    ON assignments(subject_id, title);
    """)

    # 4. Career Radar table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS career_radar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        deadline TEXT,
        benefits_credits TEXT,
        status TEXT DEFAULT 'open',
        url TEXT,
        eligibility TEXT,
        UNIQUE(category, name)
    );
    """)

    # 5. Daily Todos table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        due_date TEXT,
        completed INTEGER DEFAULT 0
    );
    """)

    # 6. Agent Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        level TEXT NOT NULL,
        message TEXT NOT NULL
    );
    """)

    # 7. Labworks and Code Practice table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS labworks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        subject_name TEXT NOT NULL,
        lab_number TEXT,
        title TEXT NOT NULL,
        file_path TEXT NOT NULL,
        code_type TEXT NOT NULL,
        concepts TEXT,
        problem_statement TEXT,
        code_summary TEXT,
        practice_todos TEXT,
        starter_code TEXT,
        status TEXT DEFAULT 'ready',
        completed_tasks TEXT DEFAULT '[]',
        created_at TEXT,
        FOREIGN KEY (subject_id) REFERENCES subjects (id)
    );
    """)

    conn.commit()

    # Pre-seed initial career radar from verified 16 Sept 2026 data if empty
    cursor.execute("SELECT COUNT(*) FROM career_radar")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO career_radar (category, name, deadline, benefits_credits, status, url, eligibility)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            ("hackathon", "Amazon ML Challenge 2026", "2026-09-20 23:59:00", "₹2,25,000 cash pool + Amazon Applied Scientist Pre-Placement Interviews", "open", "https://unstop.com/hackathons/crp-amazon-ml-challenge-2026-amazon-1743604", "2027/2028 B.Tech"),
            ("fellowship", "Microsoft Research India Intern", "Rolling", "Industry stipend + 1-on-1 MSR mentorship + PPO pipeline", "open", "https://careers.microsoft.com", "B.Tech/M.Tech (2027/2028)"),
            ("internship", "Postman AI Engineer Intern", "Rolling", "Competitive stipend + production Agentic AI benchmarks", "open", "https://wellfound.com", "Undergrad with Python & APIs"),
            ("internship", "SCORR AI/ML Intern (Mumbai)", "Rolling", "Paid in-office internship (Mumbai/Thane)", "open", "https://unstop.com", "Current B.Tech students"),
            ("hackathon", "AssemblyAI Voice Agent Hackathon", "2026-09-30 23:59:00", "$10,000+ prize pool + Voice AI exposure", "open", "https://lablab.ai/event/assemblyai-hackathon", "Global developers"),
            ("fellowship", "MLH Fellowship (Spring 2027)", "2026-11-15 00:00:00", "Educational stipend + global open-source pod", "upcoming", "https://fellowship.mlh.io", "Enrolled students"),
            ("fellowship", "LFX Mentorship (Term 1 / Spring 2027)", "2027-01-31 00:00:00", "$3,000 stipend + CNCF/Linux Foundation mentorship", "upcoming", "https://mentorship.lfx.linuxfoundation.org", "Open to all students"),
            ("certification", "AWS ML Engineer Associate (MLA-C02 Beta)", "2026-10-31 00:00:00", "$75 Beta price (50% off standard $150)", "open", "https://aws.amazon.com/certification/", "All candidates")
        ])

        # Pre-seed initial high-priority todos
        cursor.executemany("""
        INSERT INTO daily_todos (title, category, due_date, completed)
        VALUES (?, ?, ?, ?)
        """, [
            ("Register for Amazon ML Challenge 2026 on Unstop & create AWS Builder ID", "Career", "2026-09-20", 0),
            ("Submit application for Postman AI Engineer Intern via Wellfound", "Career", "2026-09-17", 0),
            ("Submit application for Microsoft Research India (MSRI) on careers.microsoft.com", "Career", "2026-09-18", 0),
            ("Check DigiCampus for new lecture uploads in 3rd year subjects", "Academic", "2026-09-16", 0)
        ])

        conn.commit()

    conn.close()

def log_agent_event(level: str, message: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agent_logs (timestamp, level, message) VALUES (?, ?, ?)",
                   (datetime.now().isoformat(), level, message))
    conn.commit()
    conn.close()
