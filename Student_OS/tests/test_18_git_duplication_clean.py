import subprocess
import json
from pathlib import Path

REPO_ROOT = Path(".").resolve()

results = {
    "git_remote": {},
    "git_branch": {},
    "git_status": {},
    "tracked_sensitive_files": [],
    "privacy_security_concerns": [],
    "overall_status": "PENDING"
}

# 1. Check remote
r_remote = subprocess.run(["git", "remote", "-v"], cwd=REPO_ROOT, capture_output=True, text=True)
results["git_remote"] = {
    "output": r_remote.stdout.strip(),
    "has_correct_repo": "Shaunakrane914/Automation" in r_remote.stdout
}

# 2. Check branch
r_branch = subprocess.run(["git", "branch", "--show-current"], cwd=REPO_ROOT, capture_output=True, text=True)
results["git_branch"] = {
    "branch": r_branch.stdout.strip()
}

# 3. Check git ls-files for sensitive patterns
r_files = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True)
all_tracked = r_files.stdout.splitlines()

sensitive_keywords = [
    ".env", "secret", "token", "password", "credential", "id_rsa", "cookie",
    "session.json", "student_os.db"
]

for f in all_tracked:
    f_lower = f.lower()
    for kw in sensitive_keywords:
        if kw in f_lower:
            results["tracked_sensitive_files"].append(f)
            break

# 4. Check auto-push privacy risks
if any("student_os.db" in f for f in results["tracked_sensitive_files"]):
    results["privacy_security_concerns"].append(
        "CRITICAL/HIGH: 'student_os.db' (live SQLite database with local audit data) is actively tracked in git and automatically pushed to public/remote repo during sync"
    )

if any(".env" in f for f in results["tracked_sensitive_files"]):
    results["privacy_security_concerns"].append(
        "CRITICAL: .env file containing API tokens is tracked in git repository"
    )

# 5. Git status check
r_status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True)
results["git_status"] = {
    "clean": (len(r_status.stdout.strip()) == 0),
    "uncommitted_lines": len(r_status.stdout.splitlines())
}

if len(results["privacy_security_concerns"]) > 0:
    results["overall_status"] = "PARTIAL — Git connected and functional, but security/privacy concern detected (student_os.db tracked in remote repo)"
elif results["git_remote"]["has_correct_repo"]:
    results["overall_status"] = "PASS"
else:
    results["overall_status"] = "FAIL"

out_file = Path("Student_OS/logs/git_security_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== GIT & SENSITIVE FILES AUDIT ===")
print("Remote Repo:", results["git_remote"]["has_correct_repo"])
print("Branch:", results["git_branch"]["branch"])
print("Tracked Sensitive Files:", results["tracked_sensitive_files"])
print("Privacy/Security Concerns:", results["privacy_security_concerns"])
print("Overall Status:", results["overall_status"])
