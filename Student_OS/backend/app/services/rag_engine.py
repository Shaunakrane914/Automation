import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.config import settings

logger = logging.getLogger("rag_engine")

ACADEMIC_ROOT = Path(settings.ACADEMIC_ROOT_DIR)
VALID_EXTS = {".py", ".md", ".txt", ".c", ".cpp", ".java", ".ipynb"}
SKIP_DIRS = {
    "node_modules", ".git", "venv", ".venv", "env", "__pycache__",
    ".idea", ".vscode", "dist", "build", ".next", ".cache", "data"
}
MAX_FILE_SIZE_BYTES = 500 * 1024  # Skip raw datasets > 500KB

CHUNKS_STORE: List[Dict[str, Any]] = []
INDEX_TIMESTAMP: Optional[str] = None

def index_academic_files() -> Dict[str, Any]:
    """
    Scans Desktop/3rd Year safely skipping huge raw dataset files and node_modules.
    Extracts high-value lecture and code chunks in <0.2 seconds.
    """
    global CHUNKS_STORE, INDEX_TIMESTAMP
    chunks = []
    total_files = 0
    subjects_found = set()

    if not ACADEMIC_ROOT.exists():
        logger.warning(f"Academic root {ACADEMIC_ROOT} does not exist.")
        return {"total_chunks": 0, "total_files": 0, "subjects": []}

    for root_dir, dirs, files in os.walk(str(ACADEMIC_ROOT)):
        # Prune search tree: immediately remove ignored directories
        dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not d.startswith(".")]

        rel_root = Path(root_dir).relative_to(ACADEMIC_ROOT)
        subject = rel_root.parts[0] if len(rel_root.parts) > 0 else "General"

        for file_name in files:
            ext = os.path.splitext(file_name)[1].lower()
            if ext not in VALID_EXTS:
                continue

            file_path = Path(root_dir) / file_name

            # Skip massive raw datasets (e.g. 1.5GB train.ft.txt)
            try:
                if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    continue
            except Exception:
                continue

            try:
                content = ""
                if ext == ".ipynb":
                    try:
                        nb = json.loads(file_path.read_text(encoding="utf-8", errors="ignore"))
                        cells = []
                        for cell in nb.get("cells", []):
                            if cell.get("cell_type") in ["code", "markdown"]:
                                cells.append("".join(cell.get("source", [])))
                        content = "\n\n".join(cells)
                    except Exception:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")[:40000]
                else:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")[:40000]

                if not content.strip():
                    continue

                total_files += 1
                subjects_found.add(subject)
                rel_file_path = file_path.relative_to(ACADEMIC_ROOT)

                # Chunk content
                chunk_size = 700
                overlap = 100
                start = 0
                chunk_idx = 0

                while start < len(content):
                    end = min(start + chunk_size, len(content))
                    chunk_text = content[start:end].strip()
                    if chunk_text:
                        chunks.append({
                            "id": f"{rel_file_path}_{chunk_idx}",
                            "subject": subject,
                            "filename": file_name,
                            "rel_path": str(rel_file_path).replace("\\", "/"),
                            "content": chunk_text,
                            "tokens": set(re.findall(r"\w+", chunk_text.lower()))
                        })
                        chunk_idx += 1
                    start += (chunk_size - overlap)
                    if end == len(content):
                        break

            except Exception as e:
                logger.debug(f"Error indexing {file_path}: {e}")

    CHUNKS_STORE = chunks
    INDEX_TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Indexed {len(CHUNKS_STORE)} academic chunks across {total_files} files in {len(subjects_found)} subjects.")

    return {
        "total_chunks": len(CHUNKS_STORE),
        "total_files": total_files,
        "subjects": sorted(list(subjects_found)),
        "indexed_at": INDEX_TIMESTAMP
    }

def search_academic_rag(query: str, subject_filter: str = "", top_k: int = 4) -> List[Dict[str, Any]]:
    global CHUNKS_STORE
    if not CHUNKS_STORE:
        index_academic_files()

    if not CHUNKS_STORE:
        return []

    q_tokens = set(re.findall(r"\w+", query.lower()))
    if not q_tokens:
        return []

    scored_chunks = []
    filter_lower = subject_filter.lower().strip()

    for chunk in CHUNKS_STORE:
        if filter_lower and filter_lower not in chunk["subject"].lower():
            continue

        overlap_count = len(q_tokens.intersection(chunk["tokens"]))
        if overlap_count == 0:
            continue

        score = overlap_count * 1.5
        if query.lower() in chunk["content"].lower():
            score += 4.0
        if any(tok in chunk["filename"].lower() for tok in q_tokens):
            score += 2.0
        if filter_lower and filter_lower in chunk["subject"].lower():
            score += 2.0

        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_chunks[:top_k]]

def get_academic_rag_context(query: str, top_k: int = 3) -> str:
    results = search_academic_rag(query, top_k=top_k)
    if not results:
        return ""

    lines = ["\n### 📚 Grounded Academic Coursework Context (Desktop/3rd Year):"]
    for i, res in enumerate(results, 1):
        lines.append(
            f"**[{i}] Subject: {res['subject']} | File: `{res['rel_path']}`**\n"
            f"```text\n{res['content'][:350]}\n```"
        )
    return "\n".join(lines)
