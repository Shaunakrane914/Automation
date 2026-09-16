"""
Standalone CLI & Worker Runner for Student OS Auto-Apply Pipeline
Executes auto-apply against Career Radar opportunities with latest verified resume.
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure Windows Proactor event loop policy for Playwright subprocess compatibility
if sys.platform == "win32":
    import asyncio
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

# Setup import path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.services.auto_apply_engine import run_auto_apply_pipeline, get_latest_resume

def main():
    parser = argparse.ArgumentParser(description="Autonomous Auto-Apply Pipeline")
    parser.add_argument("--ids", nargs="*", type=int, help="Specific opportunity IDs to apply for")
    parser.add_argument("--all", action="store_true", help="Apply to all open opportunities")
    args = parser.parse_args()

    resume = get_latest_resume()
    print(f"[Runner] Using verified resume: {resume['name']} ({resume['path']})")

    summary = run_auto_apply_pipeline(opportunity_ids=args.ids if args.ids else None)
    print("\n[Runner] Execution Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
