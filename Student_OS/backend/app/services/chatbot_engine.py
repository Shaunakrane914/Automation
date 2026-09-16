import json
from datetime import datetime
from typing import Dict, Any, List
from app.database import get_db_connection
from app.services.academic_engine import calculate_attendance_metrics

def generate_daily_briefing() -> Dict[str, Any]:
    """
    Generates the exact Daily Briefing structure specified in Section 36 of Task.md.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM subjects")
    subjects = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM assignments WHERE status = 'pending'")
    assignments = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM career_radar WHERE status = 'open' LIMIT 5")
    career_opps = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM daily_todos WHERE completed = 0 LIMIT 5")
    todos = [dict(r) for r in cursor.fetchall()]

    conn.close()

    total_pct = sum(s["attendance_percentage"] for s in subjects) / max(1, len(subjects))
    at_risk = [s["name"] for s in subjects if s["attendance_percentage"] < 75.0]

    return {
        "date": datetime.now().strftime("%A, %d %B %Y"),
        "academics": {
            "pending_assignments": len(assignments),
            "subjects_tracked": len(subjects)
        },
        "attendance": {
            "overall_pct": round(total_pct, 1),
            "subjects_at_risk": at_risk
        },
        "career": {
            "top_opportunities": [c["name"] for c in career_opps]
        },
        "top_5_priorities": [t["title"] for t in todos]
    }

def process_chat_query(query: str) -> Dict[str, Any]:
    """
    Processes natural language commands from the dashboard chatbot according to Section 26.
    """
    q = query.lower().strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    if "attendance" in q:
        cursor.execute("SELECT name, attendance_percentage FROM subjects")
        rows = cursor.fetchall()
        conn.close()
        lines = ["📊 **Current Subject Attendance Status:**"]
        for r in rows:
            pct = r["attendance_percentage"]
            metric = calculate_attendance_metrics(attended=int(pct * 0.4), conducted=40, target_pct=80.0)
            status_badge = "🔴 RISK (<75%)" if pct < 75.0 else "🟡 WATCH" if pct < 80.0 else "🟢 SAFE"
            lines.append(f"- **{r['name']}**: {pct}% — {status_badge} (Missed: {metric['missed']}, Needed for 80%: {metric['needed_for_target']} lectures)")
        return {"response": "\n".join(lines), "tool_used": "query_database"}

    elif "assignment" in q or "pending" in q:
        cursor.execute("""
        SELECT a.title, a.deadline, s.name as subject_name, a.is_lab 
        FROM assignments a 
        JOIN subjects s ON a.subject_id = s.id 
        WHERE a.status = 'pending'
        """)
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return {"response": "✅ You have no pending assignments right now!", "tool_used": "query_database"}
        lines = ["⏳ **Pending Assignments & Labs:**"]
        for r in rows:
            lab_tag = " [LAB PRACTICE]" if r["is_lab"] == 1 else ""
            lines.append(f"- **{r['title']}** ({r['subject_name']}){lab_tag} — Due: {r['deadline']}")
        return {"response": "\n".join(lines), "tool_used": "query_database"}

    elif "solo" in q or "competition" in q or "hackathon" in q:
        cursor.execute("SELECT name, category, deadline, benefits_credits, url FROM career_radar WHERE status = 'open'")
        rows = cursor.fetchall()
        conn.close()
        lines = ["🏆 **Verified Active Opportunities & Competitions:**"]
        for r in rows:
            lines.append(f"- **{r['name']}** ({r['category'].upper()}): {r['benefits_credits']} | Deadline: {r['deadline']}")
        return {"response": "\n".join(lines), "tool_used": "search_opportunities"}

    elif "do today" in q or "briefing" in q or "priorities" in q:
        briefing = generate_daily_briefing()
        conn.close()
        lines = [
            f"🌅 **Good Morning Shaunak — Briefing for {briefing['date']}**\n",
            f"**Academics:** {briefing['academics']['pending_assignments']} assignments pending across {briefing['academics']['subjects_tracked']} subjects.",
            f"**Attendance:** Overall {briefing['attendance']['overall_pct']}%. " + (f"⚠️ Attention required: {', '.join(briefing['attendance']['subjects_at_risk'])}" if briefing['attendance']['subjects_at_risk'] else "All subjects safe!"),
            "\n**Today's Top Action Items:**"
        ]
        for i, item in enumerate(briefing["top_5_priorities"], 1):
            lines.append(f"{i}. {item}")
        return {"response": "\n".join(lines), "tool_used": "generate_briefing"}

    else:
        conn.close()
        return {
            "response": f"I received your request: *\"{query}\"*. You can ask me about:\n- *'Check my attendance'*\n- *'What assignments are pending?'*\n- *'What do I need to do today?'*\n- *'Find solo competitions'*",
            "tool_used": "fallback"
        }

def global_search(query_str: str) -> Dict[str, Any]:
    """
    Executes global search across all entities (Section 39).
    """
    term = f"%{query_str.lower().strip()}%"
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, attendance_percentage FROM subjects WHERE LOWER(name) LIKE ?", (term,))
    matched_subjects = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
    SELECT a.id, a.title, a.deadline, s.name as subject_name 
    FROM assignments a JOIN subjects s ON a.subject_id = s.id 
    WHERE LOWER(a.title) LIKE ? OR LOWER(s.name) LIKE ?
    """, (term, term))
    matched_assignments = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT id, name, category, benefits_credits, url FROM career_radar WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?", (term, term))
    matched_career = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT id, title, category FROM daily_todos WHERE LOWER(title) LIKE ?", (term,))
    matched_todos = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "query": query_str,
        "subjects": matched_subjects,
        "assignments": matched_assignments,
        "opportunities": matched_career,
        "todos": matched_todos
    }
