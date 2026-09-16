import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path("Student_OS/backend").resolve()))
from app.services.academic_engine import scaffold_special_lab_practice
from app.services.labwork_engine import build_default_lab_curriculum, LAB_SUBJECT_MAPPINGS

results = {}

TEST_ARTIFACTS = Path("Student_OS/test_artifacts/special_lab_test")
TEST_ARTIFACTS.mkdir(parents=True, exist_ok=True)

# 1. Test scaffolding for Special Lab 1 (Deep Learning)
lab1_dir = scaffold_special_lab_practice(
    TEST_ARTIFACTS / "Deep Learning",
    "Special Lab 1 Perceptron",
    "Implement binary logic gates using Heaviside step activation"
)

tasks_file_1 = lab1_dir / "tasks.md"
results["special_lab_1_created"] = tasks_file_1.exists()
if tasks_file_1.exists():
    content = tasks_file_1.read_text(encoding="utf-8")
    required_steps = [
        "problem specifications",
        "algorithm",
        "implementation",
        "locally",
        "Debug",
        "edge cases",
        "explanation",
        "submission"
    ]
    results["special_lab_1_workflow_steps_present"] = all(s.lower() in content.lower() for s in required_steps)
else:
    results["special_lab_1_workflow_steps_present"] = False

# 2. Test scaffolding for Special Lab 2 (NLP)
lab2_dir = scaffold_special_lab_practice(
    TEST_ARTIFACTS / "NLP Lab",
    "Special Lab 2 Text Preprocessing",
    "IMDB dataset text preprocessing with contractions and lemmatization"
)
tasks_file_2 = lab2_dir / "tasks.md"
results["special_lab_2_created"] = tasks_file_2.exists()
if tasks_file_2.exists():
    content2 = tasks_file_2.read_text(encoding="utf-8")
    results["special_lab_2_workflow_steps_present"] = all(s.lower() in content2.lower() for s in required_steps)
else:
    results["special_lab_2_workflow_steps_present"] = False

# 3. Test curriculum isolation: verify that normal theory subjects do NOT get lab curricula
curriculum = build_default_lab_curriculum()
lab_subject_keys = {lab["mapping_key"] for lab in curriculum}

theory_subjects = ["SEPM", "Mentoring", "Summer Internship", "Training & Placement"]
theory_has_lab_curriculum = any(ts.lower() in [m["key"] for m in LAB_SUBJECT_MAPPINGS] for ts in theory_subjects)

results["theory_subjects_isolated"] = not theory_has_lab_curriculum
results["configured_lab_subjects"] = [m["display_name"] for m in LAB_SUBJECT_MAPPINGS]

# Overall evaluation
if (results["special_lab_1_workflow_steps_present"] and 
    results["special_lab_2_workflow_steps_present"] and 
    results["theory_subjects_isolated"]):
    results["overall_status"] = "PASS"
else:
    results["overall_status"] = "PARTIAL"

out_file = Path("Student_OS/logs/special_labs_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== SPECIAL LAB 1 & 2 TEST ===")
print("Lab 1 Workflow:", results["special_lab_1_workflow_steps_present"])
print("Lab 2 Workflow:", results["special_lab_2_workflow_steps_present"])
print("Theory Subjects Isolated:", results["theory_subjects_isolated"])
print("Overall Status:", results["overall_status"])
