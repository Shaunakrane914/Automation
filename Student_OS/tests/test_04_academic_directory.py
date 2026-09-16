import os
import sys
import hashlib
import json
from pathlib import Path

TARGET_DIR = Path(r"C:\Users\Shaunak Rane\Desktop\3rd Year")
results = {}

# 1. Path existence and verification
if not TARGET_DIR.exists():
    results["path_status"] = "FAIL — Directory does not exist"
    print("Academic dir does not exist!")
    sys.exit(1)

results["path_status"] = "PASS"
results["path"] = str(TARGET_DIR)

# 2. Count files before scan
def inventory_directory(path: Path):
    file_map = {}
    for root, dirs, files in os.walk(path):
        if ".git" in root or "node_modules" in root:
            continue
        for f in files:
            fp = Path(root) / f
            try:
                stat = fp.stat()
                file_map[str(fp.relative_to(path))] = {
                    "size": stat.st_size,
                    "mtime": stat.st_mtime
                }
            except Exception:
                pass
    return file_map

files_before = inventory_directory(TARGET_DIR)
results["file_count_before"] = len(files_before)

# 3. Subject folder discovery
discovered_folders = [f.name for f in TARGET_DIR.iterdir() if f.is_dir() and not f.name.startswith(".")]
results["discovered_subject_folders"] = discovered_folders

# 4. File extension classification
ext_counts = {}
for rel_path in files_before.keys():
    ext = Path(rel_path).suffix.lower() or "no_ext"
    ext_counts[ext] = ext_counts.get(ext, 0) + 1
results["file_classification"] = ext_counts

# 5. Hashing & Duplicate detection sample (test 50 files for speed)
hash_map = {}
duplicates = []
sample_keys = list(files_before.keys())[:100]
for rel in sample_keys:
    fp = TARGET_DIR / rel
    try:
        if fp.is_file() and fp.stat().st_size < 5 * 1024 * 1024:
            hasher = hashlib.md5()
            with open(fp, "rb") as f:
                hasher.update(f.read())
            file_hash = hasher.hexdigest()
            if file_hash in hash_map:
                duplicates.append({"original": hash_map[file_hash], "duplicate": rel, "hash": file_hash})
            else:
                hash_map[file_hash] = rel
    except Exception:
        pass

results["sample_hash_duplicates_found"] = len(duplicates)
results["sample_duplicates"] = duplicates[:5]

# 6. Run academic sync scanner
sys.path.insert(0, str(Path("Student_OS/backend").resolve()))
from app.services.labwork_engine import sync_labworks_to_db

scan_res = sync_labworks_to_db(force_rescan=False)
results["scanner_execution"] = scan_res

# 7. Count files after scan
files_after = inventory_directory(TARGET_DIR)
results["file_count_after"] = len(files_after)

# 8. Check non-destructive invariant
is_non_destructive = (len(files_before) == len(files_after))
results["non_destructive_invariant"] = "PASS" if is_non_destructive else f"FAIL (before: {len(files_before)}, after: {len(files_after)})"

out_file = Path("Student_OS/logs/academic_directory_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== ACADEMIC DIRECTORY TEST ===")
print("Path:", results["path"])
print("Discovered Subject Folders (Count:", len(discovered_folders), "):", discovered_folders)
print("Files Before:", results["file_count_before"])
print("Files After:", results["file_count_after"])
print("Non-Destructive Invariant:", results["non_destructive_invariant"])
print("File Classification:", results["file_classification"])
