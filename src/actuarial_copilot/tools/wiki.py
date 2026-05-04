from __future__ import annotations

from pathlib import Path

from .common import ensure_dir


def read_wiki(page: str | None = None, wiki_dir: str = "wiki") -> dict:
    root = Path(wiki_dir).resolve()
    if page is None:
        pages = sorted(path.relative_to(root).as_posix() for path in root.rglob("*.md")) if root.exists() else []
        return {"wiki_dir": str(root), "pages": pages}
    path = safe_wiki_path(root, page)
    return {"path": str(path), "content": path.read_text(encoding="utf-8")}


def write_wiki_page(page: str, content: str, wiki_dir: str = "wiki") -> dict:
    root = Path(wiki_dir).resolve()
    path = safe_wiki_path(root, page)
    ensure_dir(path.parent)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return {"path": str(path), "status": "written"}


def search_wiki(query: str, wiki_dir: str = "wiki", limit: int = 20) -> dict:
    root = Path(wiki_dir).resolve()
    needle = query.lower()
    matches = []
    if root.exists():
        for path in sorted(root.rglob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            lower = text.lower()
            idx = lower.find(needle)
            if idx == -1:
                continue
            start = max(0, idx - 120)
            end = min(len(text), idx + len(query) + 120)
            matches.append({"path": path.relative_to(root).as_posix(), "excerpt": text[start:end].strip()})
            if len(matches) >= limit:
                break
    return {"query": query, "matches": matches}


def safe_wiki_path(root: Path, page: str) -> Path:
    candidate = (root / page).resolve()
    if candidate.suffix != ".md":
        candidate = candidate.with_suffix(".md")
    if root not in candidate.parents and candidate != root:
        raise ValueError(f"Wiki path escapes wiki directory: {page}")
    return candidate

