import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db, get_db_connection, log_agent_event
from app.models import (
    SubjectModel, AssignmentModel, CareerRadarModel, DailyTodoModel,
    DesktopCommandRequest, ScaffoldLabRequest, AutoApplyRunRequest
)
from app.services.digicampus_scraper import sync_digicampus
from app.services.desktop_automation import execute_desktop_command, launch_application
from app.services.ai_engine import scaffold_lab_environment
from app.services.notifications import dispatch_alert
from app.services.scheduler import background_scheduler_loop
from app.services.auto_apply_engine import (
    get_latest_resume, get_candidate_profile, run_auto_apply_pipeline
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("student_os")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                pass

ws_manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Student OS database...")
    init_db()
    log_agent_event("INFO", "Student OS backend started successfully.")
    scheduler_task = asyncio.create_task(background_scheduler_loop(1800))
    yield
    # Shutdown
    scheduler_task.cancel()
    logger.info("Student OS backend shutdown.")

app = FastAPI(
    title="Student OS & Autonomous Academic Copilot",
    description="Unified API for academic monitoring, career radar, and desktop automation.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- WebSocket Live Feeds -----------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process incoming ping
            await websocket.send_json({"type": "PONG", "message": "Connected to Student OS Event Stream"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# ----------------- Academic Endpoints -----------------
@app.get("/api/academic/overview")
async def get_academic_overview():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM subjects ORDER BY name ASC")
    raw_subjects = [dict(row) for row in cursor.fetchall()]

    # Mapping course codes to local folders
    from app.services.digicampus_scraper import FOLDER_MAPPING, IGNORE_DIRS
    academic_root = Path(settings.ACADEMIC_ROOT_DIR)

    subjects = []
    for s in raw_subjects:
        code = s.get("code") or ""
        folder_info = FOLDER_MAPPING.get(code)
        folder_name = folder_info[0] if folder_info else s["name"]
        local_path = str(folder_info[1]) if folder_info else str(academic_root / folder_name)
        subjects.append({
            **s,
            "folder_name": folder_name,
            "local_path": local_path
        })

    cursor.execute("""
    SELECT a.*, s.name as subject_name 
    FROM assignments a 
    JOIN subjects s ON a.subject_id = s.id 
    ORDER BY a.deadline ASC
    """)
    assignments = [dict(row) for row in cursor.fetchall()]

    cursor.execute("""
    SELECT d.*, s.name as subject_name 
    FROM documents d 
    JOIN subjects s ON d.subject_id = s.id 
    ORDER BY d.id DESC LIMIT 100
    """)
    documents = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Dynamic scan of C:\Users\Shaunak Rane\Desktop\3rd Year
    folders = []
    audit_file = Path(__file__).resolve().parent.parent / "data" / "digicampus_complete_audit.json"
    audit_lookup = {}
    if audit_file.exists():
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    fname = item.get("local_folder_name")
                    if fname:
                        if fname not in audit_lookup:
                            audit_lookup[fname] = {"resources": 0, "missing": 0}
                        audit_lookup[fname]["resources"] += len(item.get("resources", []))
                        audit_lookup[fname]["missing"] += len(item.get("missing_resources", []))
        except Exception:
            pass

    FOLDER_DESCRIPTIONS = {
        "AJP": "Advance Java Programming, JDBC, Lambda & Collections",
        "AWT": "Advanced Web Technology, React, TypeScript, DOM APIs",
        "BDA": "Big Data Analytics, Hadoop, MapReduce, PySpark",
        "Deep Learning": "Deep Learning Neural Networks, Perceptrons, PyTorch",
        "NLP": "Natural Language Processing, Sentiment Pipelines, N-Grams",
        "NLP Lab": "NLP Experiments, TF-IDF, Bag of Words, Tokenization",
        "SEPM": "Software Engineering & Project Management, UML & Agile",
        "Time Series": "Time Series Modelling & Forecasting, Smoothing, Moving Averages",
        "Summer Internship": "Summer Internship-I Industry Project & Reports",
        "Minor Project": "Minor Project System Development & Prototype",
        "Mentoring": "Mentoring, Mentee Journal & Career Guidance Forms",
        "Training & Placement": "Training & Placement Preparation, Aptitude & Drives"
    }

    if academic_root.exists():
        for d in sorted(academic_root.iterdir()):
            if d.is_dir():
                clean_files = [f.name for f in d.rglob("*") if f.is_file() and not any(part in IGNORE_DIRS or part.startswith(".") for part in f.parts)]
                audit_info = audit_lookup.get(d.name, {"resources": 0, "missing": 0})
                folders.append({
                    "name": d.name,
                    "path": str(d),
                    "files_count": len(clean_files),
                    "online_resources_count": audit_info["resources"],
                    "missing_resources_count": audit_info["missing"],
                    "description": FOLDER_DESCRIPTIONS.get(d.name, "Academic subject directory"),
                    "sample_files": clean_files[:5]
                })

    return {
        "subjects": subjects,
        "assignments": assignments,
        "documents": documents,
        "folders": folders,
        "academic_root": str(academic_root)
    }

@app.post("/api/academic/sync")
async def trigger_academic_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_digicampus, ws_manager.broadcast)
    await ws_manager.broadcast({"type": "SYNC_STARTED", "message": "Initiating complete DigiCampus audit & update..."})
    return {"status": "Sync initiated", "message": "Running live DigiCampus crawler & database update"}

@app.post("/api/academic/scaffold-lab")
async def scaffold_lab_endpoint(req: ScaffoldLabRequest):
    clean_name = req.subject_name.replace(" ", "_")
    target_dir = Path(settings.ACADEMIC_ROOT_DIR).expanduser() / clean_name
    lab_dir = scaffold_lab_environment(target_dir, req.lab_number, req.problem_title, req.language)
    await ws_manager.broadcast({
        "type": "LAB_SCAFFOLDED",
        "subject": req.subject_name,
        "lab": req.lab_number,
        "path": str(lab_dir)
    })
    return {"status": "success", "lab_path": str(lab_dir)}

# ----------------- Assignments Management Endpoints -----------------
@app.get("/api/assignments")
async def get_assignments(status: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT a.*, s.name as subject_name 
    FROM assignments a 
    JOIN subjects s ON a.subject_id = s.id 
    """
    params = []
    if status and status.lower() != "all":
        query += " WHERE LOWER(a.status) = ?"
        params.append(status.lower())
    query += " ORDER BY CASE WHEN LOWER(a.status) = 'pending' THEN 0 ELSE 1 END, a.deadline ASC"
    cursor.execute(query, params)
    assignments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return assignments

@app.post("/api/assignments")
async def create_assignment(asg: AssignmentModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    subject_id = asg.subject_id
    if not subject_id and asg.subject_name:
        cursor.execute("SELECT id FROM subjects WHERE LOWER(name) = LOWER(?)", (asg.subject_name,))
        row = cursor.fetchone()
        if row:
            subject_id = row["id"]
        else:
            cursor.execute("INSERT INTO subjects (name, code, attendance_percentage) VALUES (?, ?, ?)",
                           (asg.subject_name, "CUSTOM", 100.0))
            subject_id = cursor.lastrowid

    if not subject_id:
        cursor.execute("SELECT id FROM subjects LIMIT 1")
        row = cursor.fetchone()
        subject_id = row["id"] if row else 1

    cursor.execute("""
    INSERT INTO assignments (subject_id, title, deadline, is_lab, status, local_lab_dir)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (subject_id, asg.title, asg.deadline or "", asg.is_lab, asg.status or "pending", asg.local_lab_dir or ""))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    log_agent_event("INFO", f"Assignment created: '{asg.title}' (ID: {new_id})")
    await ws_manager.broadcast({
        "type": "ASSIGNMENT_CREATED",
        "id": new_id,
        "title": asg.title
    })
    return {"id": new_id, "status": "created"}

@app.patch("/api/assignments/{assignment_id}/toggle")
async def toggle_assignment(assignment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, title FROM assignments WHERE id = ?", (assignment_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Assignment not found")

    current_status = (row["status"] or "").lower()
    new_status = "completed" if current_status == "pending" else "pending"
    cursor.execute("UPDATE assignments SET status = ? WHERE id = ?", (new_status, assignment_id))
    conn.commit()
    conn.close()

    log_agent_event("INFO", f"Assignment {assignment_id} status toggled to '{new_status}'")
    await ws_manager.broadcast({
        "type": "ASSIGNMENT_UPDATED",
        "id": assignment_id,
        "status": new_status
    })
    return {"id": assignment_id, "status": new_status}

@app.delete("/api/assignments/{assignment_id}")
async def delete_assignment(assignment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM assignments WHERE id = ?", (assignment_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Assignment not found")

    cursor.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
    conn.commit()
    conn.close()

    log_agent_event("INFO", f"Assignment {assignment_id} deleted")
    await ws_manager.broadcast({
        "type": "ASSIGNMENT_DELETED",
        "id": assignment_id
    })
    return {"id": assignment_id, "status": "deleted"}

# ----------------- Labworks & Code Practice Endpoints -----------------
from app.services.labwork_engine import get_all_labworks, toggle_practice_task, sync_labworks_to_db

@app.get("/api/labs")
async def get_labs_endpoint(subject_id: Optional[int] = None):
    return get_all_labworks(subject_id=subject_id)

@app.post("/api/labs/todo/toggle")
async def toggle_lab_todo_endpoint(payload: Dict[str, Any]):
    labwork_id = payload.get("labwork_id")
    task_id = payload.get("task_id")
    if not labwork_id or not task_id:
        raise HTTPException(status_code=400, detail="labwork_id and task_id are required")
    try:
        res = toggle_practice_task(int(labwork_id), str(task_id))
        await ws_manager.broadcast({"type": "LAB_TASK_TOGGLED", "labwork_id": labwork_id, "task_id": task_id})
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/labs/rescan")
async def rescan_labs_endpoint():
    res = sync_labworks_to_db(force_rescan=True)
    await ws_manager.broadcast({"type": "LABS_RESCANNED"})
    return res

@app.post("/api/labs/open")
async def open_lab_file_endpoint(payload: Dict[str, str]):
    path_str = payload.get("path", "")
    target = Path(path_str)
    if not target.exists():
        raise HTTPException(status_code=404, detail="Target path does not exist")
    import os
    import subprocess
    try:
        if os.name == 'nt':
            if target.is_dir():
                os.startfile(str(target))
            else:
                # Open directory in explorer with file selected, or open file
                subprocess.Popen(["explorer", f"/select,{str(target)}"])
        return {"status": "opened", "path": str(target)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- Career Radar Endpoints -----------------
@app.get("/api/career/radar")
async def get_career_radar():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM career_radar ORDER BY deadline ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/career/radar")
async def add_career_entry(entry: CareerRadarModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO career_radar (category, name, deadline, benefits_credits, status, url, eligibility)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (entry.category, entry.name, entry.deadline, entry.benefits_credits, entry.status, entry.url, entry.eligibility))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    await ws_manager.broadcast({"type": "NEW_CAREER_OPPORTUNITY", "name": entry.name})
    return {"status": "created"}

# ----------------- Auto-Apply Engine Endpoints -----------------
@app.get("/api/auto-apply/status")
async def get_auto_apply_status():
    resume_info = get_latest_resume()
    profile = get_candidate_profile()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, count(*) as count FROM career_radar GROUP BY status")
    counts = {r["status"]: r["count"] for r in cursor.fetchall()}
    cursor.execute("SELECT COUNT(*) as total FROM career_radar")
    total = cursor.fetchone()["total"]
    conn.close()
    
    csv_path = Path(__file__).resolve().parent.parent.parent.parent / "Auto Apply" / "all excels" / "all_applied_applications_history.csv"
    history = []
    if csv_path.exists():
        import csv
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = list(csv.DictReader(f))
            history = reader[-10:] if reader else []

    return {
        "status": "ready",
        "resume": resume_info,
        "candidate": {
            "name": profile.get("full_name"),
            "email": profile.get("email"),
            "university": profile.get("university"),
            "graduation_year": profile.get("graduation_year")
        },
        "stats": {
            "total": total,
            "applied": counts.get("applied", 0),
            "open": counts.get("open", 0),
            "upcoming": counts.get("upcoming", 0)
        },
        "recent_history": history
    }

@app.post("/api/auto-apply/run")
async def trigger_auto_apply(req: AutoApplyRunRequest, background_tasks: BackgroundTasks):
    resume_info = get_latest_resume()
    log_agent_event("INFO", f"Triggered autonomous auto-apply pipeline using {resume_info['name']}")

    def run_job():
        import sys
        import subprocess
        runner_script = Path(__file__).resolve().parent.parent / "scripts" / "run_auto_apply.py"
        cmd = [sys.executable, str(runner_script)]
        if req.opportunity_ids:
            cmd.extend(["--ids"] + [str(i) for i in req.opportunity_ids])
        else:
            cmd.append("--all")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        if proc.stdout:
            for line in proc.stdout:
                line_str = line.strip()
                if line_str:
                    logger.info(f"[AutoApply Worker] {line_str}")
        proc.wait()
        try:
            asyncio.run(ws_manager.broadcast({
                "type": "CAREER_OPPORTUNITIES_UPDATED"
            }))
        except Exception:
            pass

    background_tasks.add_task(run_job)
    return {
        "status": "started",
        "message": f"Autonomous auto-apply initiated using latest resume ({resume_info['name']})",
        "resume": resume_info
    }

@app.post("/api/auto-apply/opportunity/{opp_id}")
async def apply_single_opportunity(opp_id: int):
    resume_info = get_latest_resume()
    log_agent_event("INFO", f"Triggered auto-apply for single opportunity ID {opp_id}")
    import sys
    import subprocess
    runner_script = Path(__file__).resolve().parent.parent / "scripts" / "run_auto_apply.py"
    proc = await asyncio.to_thread(
        subprocess.run,
        [sys.executable, str(runner_script), "--ids", str(opp_id)],
        capture_output=True,
        text=True
    )
    await ws_manager.broadcast({
        "type": "CAREER_OPPORTUNITIES_UPDATED"
    })
    return {"status": "completed", "output": proc.stdout}

from fastapi.responses import FileResponse

@app.get("/api/screenshots/{filename}")
async def get_screenshot(filename: str):
    screenshot_dir = Path(__file__).resolve().parent.parent.parent.parent / "Auto Apply" / "logs" / "screenshots"
    target_file = screenshot_dir / filename
    if not target_file.exists():
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return FileResponse(str(target_file))

# ----------------- Daily Todos Endpoints -----------------
@app.get("/api/todos")
async def get_daily_todos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_todos ORDER BY completed ASC, due_date ASC")
    todos = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return todos

@app.post("/api/todos")
async def create_todo(todo: DailyTodoModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO daily_todos (title, category, due_date, completed)
    VALUES (?, ?, ?, ?)
    """, (todo.title, todo.category, todo.due_date, todo.completed))
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()
    return {"id": todo_id, "status": "created"}

@app.patch("/api/todos/{todo_id}/toggle")
async def toggle_todo(todo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT completed FROM daily_todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    new_val = 1 if row["completed"] == 0 else 0
    cursor.execute("UPDATE daily_todos SET completed = ? WHERE id = ?", (new_val, todo_id))
    conn.commit()
    conn.close()
    return {"id": todo_id, "completed": new_val}

# ----------------- Desktop Automation Endpoints -----------------
@app.post("/api/desktop/execute")
async def execute_command_endpoint(req: DesktopCommandRequest):
    result = execute_desktop_command(req.command, req.working_dir)
    await ws_manager.broadcast({
        "type": "COMMAND_EXECUTED",
        "command": req.command,
        "success": result["success"]
    })
    return result

@app.post("/api/desktop/launch")
async def launch_app_endpoint(payload: Dict[str, str]):
    app_name = payload.get("app", "code")
    target_path = payload.get("path", "")
    result = launch_application(app_name, target_path)
    return result

# ----------------- Notifications & Logs -----------------
@app.post("/api/notifications/test")
async def test_notification():
    success = await dispatch_alert(
        "Student OS Test Alert",
        "✅ Student OS automation system is connected and functioning normally.",
        priority="default",
        tags="white_check_mark"
    )
    return {"success": success, "ntfy_topic": settings.NTFY_TOPIC}

@app.get("/api/logs")
async def get_logs(limit: int = 50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_logs ORDER BY id DESC LIMIT ?", (limit,))
    logs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return logs

# ----------------- Chatbot, Search & Briefing Endpoints -----------------
from fastapi.responses import StreamingResponse
from app.services.chatbot_engine import process_chat_query, generate_daily_briefing, global_search, stream_ollama_tokens
from app.services.academic_engine import calculate_attendance_metrics
from app.services.rag_engine import get_academic_rag_context
from app.services.notification_service import send_windows_notification
from app.services.scheduler_service import workstation_daemon

@app.post("/api/chat")
async def chat_endpoint(payload: Dict[str, str]):
    query = payload.get("query", "")
    return process_chat_query(query)

@app.get("/api/chat/stream")
async def chat_stream_endpoint(q: str = ""):
    rag_context = get_academic_rag_context(q, top_k=2)
    system_prompt = (
        "You are Shaunak Rane's Autonomous Student OS Copilot at Universal AI University. "
        "Provide direct, concise, well-formatted markdown answers. "
        f"{rag_context}"
    )
    def event_stream():
        for token in stream_ollama_tokens(q, system_prompt):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/api/notify")
async def notify_endpoint(payload: Dict[str, str]):
    title = payload.get("title", "Student OS Alert")
    msg = payload.get("message", "")
    success = send_windows_notification(title, msg)
    return {"status": "success" if success else "failed"}

@app.get("/api/daemon/status")
async def daemon_status_endpoint():
    return workstation_daemon.get_status()

@app.post("/api/daemon/toggle")
async def daemon_toggle_endpoint(payload: Dict[str, bool]):
    enable = payload.get("enable", True)
    if enable:
        workstation_daemon.start()
    else:
        workstation_daemon.stop()
    return workstation_daemon.get_status()

@app.get("/api/briefing")
async def briefing_endpoint():
    return generate_daily_briefing()

@app.get("/api/search")
async def search_endpoint(q: str = ""):
    return global_search(q)

@app.get("/api/attendance/analysis")
async def attendance_analysis_endpoint(target_pct: float = 80.0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()

    analyzed = []
    for r in rows:
        pct = r["attendance_percentage"]
        conducted = 40
        attended = int((pct / 100.0) * conducted)
        metrics = calculate_attendance_metrics(attended=attended, conducted=conducted, target_pct=target_pct)
        analyzed.append({
            "subject_id": r["id"],
            "subject_name": r["name"],
            "attendance_percentage": pct,
            **metrics
        })
    return analyzed


# ----------------- Screenshots Static Mount -----------------
screenshots_dir = Path(__file__).resolve().parent.parent.parent.parent / "Auto Apply" / "logs" / "screenshots"
screenshots_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/screenshots", StaticFiles(directory=str(screenshots_dir)), name="screenshots")

# ----------------- Frontend Static Files Mount -----------------
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

