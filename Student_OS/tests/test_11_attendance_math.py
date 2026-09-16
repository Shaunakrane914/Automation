import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path("Student_OS/backend").resolve()))
from app.services.academic_engine import calculate_attendance_metrics

results = {}

# Test cases
test_cases = [
    {"name": "standard_80_percent", "attended": 8, "conducted": 10, "target": 80.0, "expected_pct": 80.0, "expected_status": "SAFE"},
    {"name": "watch_76_percent", "attended": 19, "conducted": 25, "target": 80.0, "expected_pct": 76.0, "expected_status": "WATCH"},
    {"name": "risk_60_percent", "attended": 6, "conducted": 10, "target": 80.0, "expected_pct": 60.0, "expected_status": "RISK"},
    {"name": "zero_classes", "attended": 0, "conducted": 0, "target": 80.0, "expected_pct": 100.0, "expected_status": "SAFE"},
    {"name": "single_class_perfect", "attended": 1, "conducted": 1, "target": 80.0, "expected_pct": 100.0, "expected_status": "SAFE"},
    {"name": "zero_attendance", "attended": 0, "conducted": 10, "target": 80.0, "expected_pct": 0.0, "expected_status": "RISK"},
    {"name": "perfect_10_of_10", "attended": 10, "conducted": 10, "target": 80.0, "expected_pct": 100.0, "expected_status": "SAFE"}
]

passed = 0
failed = 0
evaluations = {}

for tc in test_cases:
    res = calculate_attendance_metrics(tc["attended"], tc["conducted"], tc["target"])
    pct_ok = (abs(res["current_pct"] - tc["expected_pct"]) < 0.01)
    status_ok = (res["status"] == tc["expected_status"])
    
    # Mathematical invariant checks
    if tc["conducted"] > 0:
        inv_missed = (res["missed"] == tc["conducted"] - tc["attended"])
    else:
        inv_missed = (res["missed"] == 0)

    if pct_ok and status_ok and inv_missed:
        evaluations[tc["name"]] = {"status": "PASS", "output": res}
        passed += 1
    else:
        evaluations[tc["name"]] = {
            "status": "FAIL",
            "output": res,
            "expected": tc
        }
        failed += 1

results["test_cases"] = evaluations
results["passed"] = passed
results["failed"] = failed
results["overall_status"] = "PASS" if failed == 0 else "FAIL"

out_file = Path("Student_OS/logs/attendance_math_audit.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("=== ATTENDANCE MATHEMATICAL ENGINE TEST ===")
print(f"Passed: {passed}/{len(test_cases)}, Failed: {failed}")
for k, v in evaluations.items():
    print(f" - {k}: {v['status']} (pct: {v['output']['current_pct']}%, status: {v['output']['status']})")
