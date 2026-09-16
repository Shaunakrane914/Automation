from pydantic import BaseModel
from typing import Optional, List

class SubjectModel(BaseModel):
    id: Optional[int] = None
    name: str
    code: Optional[str] = None
    attendance_percentage: float = 0.0
    last_synced: Optional[str] = None

class DocumentModel(BaseModel):
    id: Optional[int] = None
    subject_id: int
    file_name: str
    local_path: str
    upload_date: Optional[str] = None
    summary_path: Optional[str] = None

class AssignmentModel(BaseModel):
    id: Optional[int] = None
    subject_id: int
    title: str
    deadline: Optional[str] = None
    is_lab: int = 0
    status: str = "pending"
    local_lab_dir: Optional[str] = None

class CareerRadarModel(BaseModel):
    id: Optional[int] = None
    category: str
    name: str
    deadline: Optional[str] = None
    benefits_credits: Optional[str] = None
    status: str = "open"
    url: Optional[str] = None
    eligibility: Optional[str] = None

class DailyTodoModel(BaseModel):
    id: Optional[int] = None
    title: str
    category: str = "general"
    due_date: Optional[str] = None
    completed: int = 0

class AgentLogModel(BaseModel):
    id: Optional[int] = None
    timestamp: str
    level: str
    message: str

class DesktopCommandRequest(BaseModel):
    command: str
    working_dir: Optional[str] = None

class ScaffoldLabRequest(BaseModel):
    subject_name: str
    lab_number: str
    problem_title: str
    language: str = "python"

class AutoApplyRunRequest(BaseModel):
    opportunity_ids: Optional[List[int]] = None
    run_all: bool = True
