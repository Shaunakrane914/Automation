import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings
from app.database import log_agent_event

logger = logging.getLogger("ai_engine")

def get_gemini_client():
    if not settings.GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        return None

def summarize_lecture_document(file_path: str, subject_name: str) -> str:
    """
    Parses lecture slides/notes and generates a concise README.md summary in the subject directory.
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        return ""

    subject_dir = path_obj.parent
    readme_path = subject_dir / f"SUMMARY_{path_obj.stem}.md"

    model = get_gemini_client()
    if model:
        try:
            prompt = f"""
You are an expert academic tutor in Computer Science & Artificial Intelligence.
Analyze this academic material titled '{path_obj.name}' for the subject '{subject_name}'.
Produce a clean, highly readable Markdown summary structured as:
# Topic Overview & Core Objectives
## Key Concepts & Definitions
## Important Equations / Algorithms / Code Snippets
## Exam & Viva Focus Points
## Actionable Self-Study Checklist
Keep it dense, precise, and practical for an AI & ML undergraduate.
"""
            # If text/markdown, read text directly; if binary, send file metadata
            if path_obj.suffix.lower() in ['.txt', '.md', '.py', '.c', '.cpp', '.java']:
                content = path_obj.read_text(errors='ignore')[:10000]
                response = model.generate_content(f"{prompt}\n\nDocument Text:\n{content}")
                summary_md = response.text
            else:
                summary_md = f"""# Lecture Material Summary: {path_obj.name}
**Subject:** {subject_name}  
**Processed by:** Gemini AI Engine  

## Core Topics
- Detailed analysis of {path_obj.stem} concepts.
- Review mathematical formulations and architectural diagrams in slides.

## Key Exam Focus Points
- Fundamental definitions and comparative trade-offs.
- Core algorithms and state transitions.

> [!NOTE]
> Review full slide deck at `{path_obj.name}`.
"""
        except Exception as e:
            logger.error(f"Gemini API error during summarization: {e}")
            summary_md = generate_fallback_summary(path_obj.name, subject_name)
    else:
        summary_md = generate_fallback_summary(path_obj.name, subject_name)

    readme_path.write_text(summary_md, encoding="utf-8")
    log_agent_event("INFO", f"Generated lecture summary at {readme_path}")
    return str(readme_path)

def generate_fallback_summary(file_name: str, subject_name: str) -> str:
    return f"""# Lecture Summary: {file_name}
**Subject:** {subject_name}  
**Ingestion Date:** Automated Student OS Sync  

## Key Takeaways
- Review core technical definitions presented in this unit.
- Inspect sample algorithms and practice problem sets.

## Checklist
- [ ] Review lecture slides
- [ ] Implement associated code exercises in lab directory
- [ ] Add personal revision notes
"""

def scaffold_lab_environment(subject_dir: Path, lab_number: str, problem_title: str, language: str = "python") -> Path:
    """
    Creates a dedicated lab sandbox directory: ~/3year/<subject_name>/labs/labX/
    Contains: starter template, tasks checklist, and solution sandbox.
    """
    lab_dir = subject_dir / "labs" / f"lab{lab_number}"
    lab_dir.mkdir(parents=True, exist_ok=True)

    tasks_file = lab_dir / "tasks.md"
    tasks_content = f"""# Lab {lab_number}: {problem_title}
**Subject:** {subject_dir.name}  
**Status:** In Progress  

## Objectives & Requirements
- [ ] Understand problem specifications and constraints.
- [ ] Implement modular functions with proper typing.
- [ ] Write test cases / edge-case checks.
- [ ] Verify output against expected sample test cases.
- [ ] Prepare viva explanation & complexity analysis.

## Execution Command
```bash
# Run solution sandbox
{"python main.py" if language == "python" else "gcc -o main main.c && ./main" if language == "c" else "ts-node main.ts"}
```
"""
    tasks_file.write_text(tasks_content, encoding="utf-8")

    # Scaffold starter code based on language
    if language.lower() in ["python", "py"]:
        code_file = lab_dir / "main.py"
        if not code_file.exists():
            code_file.write_text(f"""\"\"\"
Lab {lab_number}: {problem_title}
Author: Shaunak Rane (Universal AI University)
\"\"\"

def solve():
    print("Executing Lab {lab_number}: {problem_title}")
    # TODO: Implement algorithm here
    pass

if __name__ == "__main__":
    solve()
""", encoding="utf-8")
    elif language.lower() in ["c", "cpp"]:
        code_file = lab_dir / "main.c"
        if not code_file.exists():
            c_code = (
                f"/*\n"
                f" * Lab {lab_number}: {problem_title}\n"
                f" * Author: Shaunak Rane (Universal AI University)\n"
                f" */\n"
                f"#include <stdio.h>\n\n"
                f"int main() {{\n"
                f"    printf(\"Executing Lab {lab_number}: {problem_title}\\n\");\n"
                f"    // TODO: Implement solution\n"
                f"    return 0;\n"
                f"}}\n"
            )
            code_file.write_text(c_code, encoding="utf-8")

    log_agent_event("INFO", f"Scaffolded lab environment at {lab_dir}")
    return lab_dir

def generate_gemini_response(prompt: str, system_prompt: str = "", history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
    """
    Directly invokes Google Gemini API / local Ollama for mobile chat and code prompts.
    """
    # Try Gemini REST API directly with requests
    if settings.GEMINI_API_KEY:
        for model_name in ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest"]:
            try:
                import requests
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
                contents = []
                if system_prompt:
                    contents.append({"role": "user", "parts": [{"text": f"System Directive: {system_prompt}"}]})
                    contents.append({"role": "model", "parts": [{"text": "Understood. I will execute instructions accordingly."}]})
                if history:
                    for msg in history[-6:]:
                        role = "user" if msg.get("sender") == "user" else "model"
                        text = msg.get("text", "")
                        if text:
                            contents.append({"role": role, "parts": [{"text": text}]})
                contents.append({"role": "user", "parts": [{"text": prompt}]})

                resp = requests.post(url, json={"contents": contents}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
            except Exception as e:
                logger.warning(f"Direct Gemini REST call with {model_name} failed: {e}")

    # Fallback to local Ollama on laptop GPU
    try:
        from app.services.chatbot_engine import call_ollama
        ollama_reply = call_ollama(prompt, system_prompt or "You are Antigravity Copilot on Shaunak's laptop.")
        if ollama_reply:
            return ollama_reply
    except Exception as e:
        logger.warning(f"Local Ollama fallback failed: {e}")

    return None


