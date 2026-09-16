import math
from typing import Dict, Any, List
from pathlib import Path
from app.config import settings

def calculate_attendance_metrics(attended: int, conducted: int, target_pct: float = 80.0) -> Dict[str, Any]:
    """
    Calculates exact attendance statistics according to Section 11 of Task.md:
    - Current percentage
    - Lectures attended, conducted, missed
    - Lectures needed to reach target (75% or 80%)
    - Maximum lectures that can be safely missed
    - Status: SAFE (>= target), WATCH (75% to target), RISK (< 75%)
    """
    if conducted <= 0:
        return {
            "current_pct": 100.0,
            "attended": 0,
            "conducted": 0,
            "missed": 0,
            "needed_for_75": 0,
            "needed_for_target": 0,
            "max_can_miss": 0,
            "status": "SAFE"
        }

    current_pct = (attended / conducted) * 100.0
    missed = conducted - attended

    # Status classification
    if current_pct >= target_pct:
        status = "SAFE"
    elif current_pct >= 75.0:
        status = "WATCH"
    else:
        status = "RISK"

    # Lectures needed to reach 75%
    # (attended + x) / (conducted + x) >= 0.75  =>  x >= (0.75 * conducted - attended) / 0.25
    if current_pct < 75.0:
        needed_75 = max(0, math.ceil((0.75 * conducted - attended) / 0.25))
    else:
        needed_75 = 0

    # Lectures needed to reach target%
    target_ratio = target_pct / 100.0
    if current_pct < target_pct:
        needed_target = max(0, math.ceil((target_ratio * conducted - attended) / (1.0 - target_ratio)))
    else:
        needed_target = 0

    # Max lectures that can be missed while staying above 75%
    # attended / (conducted + y) >= 0.75  =>  y <= (attended / 0.75) - conducted
    if current_pct >= 75.0:
        max_can_miss = max(0, math.floor((attended / 0.75) - conducted))
    else:
        max_can_miss = 0

    return {
        "current_pct": round(current_pct, 1),
        "attended": attended,
        "conducted": conducted,
        "missed": missed,
        "needed_for_75": needed_75,
        "needed_for_target": needed_target,
        "max_can_miss": max_can_miss,
        "status": status
    }

def scaffold_special_lab_practice(subject_dir: Path, lab_name: str, task_description: str) -> Path:
    """
    Creates enhanced practice workflow strictly adhering to Section 9 of Task.md for Special Lab 1 & 2.
    """
    lab_dir = subject_dir / "labs" / lab_name.lower().replace(" ", "_")
    lab_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = lab_dir / "tasks.md"
    tasks_content = f"""# {lab_name}: Practice Workflow
**Lab Task:** {task_description}  
**Candidate:** Student OS (Universal AI University)  
**Mode:** Mandatory Hands-On Practice Mode  

## Tasks Checklist
- [ ] Read problem specifications & constraints
- [ ] Understand required algorithm & architectural trade-offs
- [ ] Recreate implementation from scratch
- [ ] Run code locally
- [ ] Debug & benchmark performance
- [ ] Modify parameters & test edge cases
- [ ] Write short explanation
- [ ] Save practice code
- [ ] Final submission readiness check

## Code Execution
```bash
python solution.py
```
"""
    tasks_file.write_text(tasks_content, encoding="utf-8")

    code_file = lab_dir / "solution.py"
    if not code_file.exists():
        code_file.write_text(f"""\"\"\"
{lab_name}: {task_description}
Author: Student OS
\"\"\"

def main():
    print("Executing {lab_name} practice sandbox...")
    # TODO: Implement hands-on solution from scratch
    pass

if __name__ == "__main__":
    main()
""", encoding="utf-8")

    return lab_dir
