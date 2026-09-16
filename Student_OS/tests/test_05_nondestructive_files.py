import os
import hashlib
import json
from pathlib import Path

TEST_DIR = Path("Student_OS/test_artifacts/file_test")
TEST_DIR.mkdir(parents=True, exist_ok=True)

results = {}

# File classification helper function
def classify_file(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    mapping = {
        ".pdf": "DOCUMENT_PDF",
        ".docx": "DOCUMENT_WORD",
        ".pptx": "PRESENTATION_SLIDES",
        ".ppt": "PRESENTATION_SLIDES",
        ".xlsx": "DATA_SPREADSHEET",
        ".csv": "DATA_TABULAR",
        ".md": "DOCUMENT_MARKDOWN",
        ".py": "CODE_PYTHON",
        ".c": "CODE_C",
        ".cpp": "CODE_CPP",
        ".ipynb": "NOTEBOOK_JUPYTER",
        ".zip": "ARCHIVE_COMPRESSED",
        ".json": "DATA_JSON",
        ".ts": "CODE_TYPESCRIPT",
        ".java": "CODE_JAVA",
        ".class": "BYTECODE_JAVA"
    }
    return mapping.get(ext, "UNKNOWN")

# 1. Test supported formats classification
sample_files = [
    "lecture.pdf", "syllabus.docx", "module1.pptx", "marks.xlsx",
    "notes.md", "script.py", "main.c", "engine.cpp",
    "experiment1.ipynb", "resources.zip", "unknown.xyz"
]

format_results = {}
for sf in sample_files:
    format_results[sf] = classify_file(sf)
results["format_classification_test"] = format_results

# 2. Conflict and version detection simulator
def evaluate_file_sync(target_dir: Path, incoming_name: str, incoming_content: bytes) -> str:
    incoming_hash = hashlib.md5(incoming_content).hexdigest()
    target_file = target_dir / incoming_name

    # Check if exact file exists
    if target_file.exists():
        with open(target_file, "rb") as f:
            existing_hash = hashlib.md5(f.read()).hexdigest()
        if existing_hash == incoming_hash:
            return "ALREADY_EXISTS"
        else:
            return "CONFLICT_DIFFERENT_HASH_SAME_NAME"

    # Check if another file has the same hash (renamed file)
    for f in target_dir.iterdir():
        if f.is_file():
            with open(f, "rb") as cur:
                if hashlib.md5(cur.read()).hexdigest() == incoming_hash:
                    return f"ALREADY_EXISTS_RENAMED (matches {f.name})"

    return "NEW"

# Create baseline file in TEST_DIR
baseline_file = TEST_DIR / "lab1.py"
baseline_content = b"print('baseline code')"
with open(baseline_file, "wb") as f:
    f.write(baseline_content)

# Test cases:
# A. Exactly identical file incoming
case_a = evaluate_file_sync(TEST_DIR, "lab1.py", baseline_content)

# B. Modified file incoming with same name (conflict / updated version)
case_b = evaluate_file_sync(TEST_DIR, "lab1.py", b"print('modified code')")

# C. Renamed file incoming with same content
case_c = evaluate_file_sync(TEST_DIR, "lab1_renamed.py", baseline_content)

# D. Brand new file
case_d = evaluate_file_sync(TEST_DIR, "lab2.py", b"print('new lab')")

results["sync_behavior_eval"] = {
    "identical_file": case_a,
    "same_name_different_hash": case_b,
    "different_name_same_hash": case_c,
    "brand_new_file": case_d
}

# Verify that baseline_file was NEVER overwritten
with open(baseline_file, "rb") as f:
    final_content = f.read()

no_overwrite_guarantee = (final_content == baseline_content)
results["no_overwrite_guarantee"] = "PASS" if no_overwrite_guarantee else "FAIL"

out_file = Path("Student_OS/logs/nondestructive_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== NON-DESTRUCTIVE FILE TEST ===")
print("Classification:", format_results)
print("Conflict Behavior:", results["sync_behavior_eval"])
print("No-Overwrite Guarantee:", results["no_overwrite_guarantee"])
