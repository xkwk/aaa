from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import ProjectPaths
from .filesystem import ensure_dir, read_csv, read_json, safe_stem, write_json
from .ingestion import load_manifest


@dataclass(frozen=True)
class WikiSummary:
    run_id: str
    source_pages: int
    log_updated: bool
    index_updated: bool
    open_questions_updated: bool


def update_wiki(run_id: str, paths: ProjectPaths | None = None) -> WikiSummary:
    paths = paths or ProjectPaths.discover()
    wiki_dir = paths.wiki_dir
    ensure_dir(wiki_dir)
    entries = load_manifest(run_id, paths)
    conversion_manifest = read_optional_csv(paths.run_dir(run_id) / "conversion_manifest.csv")
    conversion_by_source = {row["source_relative_path"]: row for row in conversion_manifest}

    source_dir = ensure_dir(wiki_dir / "sources" / run_id)
    page_count = 0
    for entry in entries:
        conversion = conversion_by_source.get(entry.relative_path, {})
        source_page = source_dir / f"{safe_stem(entry.relative_path)}.md"
        source_page.write_text(source_page_text(entry, conversion), encoding="utf-8")
        page_count += 1

    update_index(wiki_dir, run_id, entries)
    update_log(wiki_dir, run_id, f"Updated wiki from {len(entries)} source file(s).")
    open_questions = update_open_questions(wiki_dir, run_id, paths.run_dir(run_id) / "validation_results.csv")

    summary = WikiSummary(
        run_id=run_id,
        source_pages=page_count,
        log_updated=True,
        index_updated=True,
        open_questions_updated=open_questions,
    )
    write_json(paths.run_dir(run_id) / "wiki_summary.json", asdict(summary))
    return summary


def source_page_text(entry, conversion: dict[str, str]) -> str:
    converted_path = conversion.get("converted_path", "")
    status = conversion.get("status", "not_converted")
    converter = conversion.get("converter", "")
    preview = ""
    if converted_path and Path(converted_path).exists():
        text = Path(converted_path).read_text(encoding="utf-8", errors="replace")
        preview = "\n".join(text.splitlines()[:80])
    return f"""---
run_id: {entry.run_id}
file_id: {entry.file_id}
source_path: {entry.relative_path}
role: {entry.role}
sha256: {entry.sha256}
conversion_status: {status}
---

# {entry.file_name}

- Source path: `{entry.relative_path}`
- Role: `{entry.role}`
- SHA256: `{entry.sha256}`
- Converted artifact: `{converted_path}`
- Converter: `{converter}`

## Preview

{preview or "No converted preview available."}
"""


def update_index(wiki_dir: Path, run_id: str, entries) -> None:
    index_path = wiki_dir / "index.md"
    existing = index_path.read_text(encoding="utf-8") if index_path.exists() else "# Wiki Index\n"
    source_lines = ["## Source Summaries", ""]
    source_root = wiki_dir / "sources"
    for run_folder in sorted(p for p in source_root.iterdir() if p.is_dir()):
        source_lines.append(f"### Run `{run_folder.name}`")
        for page in sorted(run_folder.glob("*.md")):
            source_lines.append(f"- [[sources/{run_folder.name}/{page.stem}]]")
        source_lines.append("")
    source_section = "\n".join(source_lines).rstrip() + "\n\n"
    index_path.write_text(replace_section(existing, "## Source Summaries", "## Assumptions", source_section), encoding="utf-8")


def update_log(wiki_dir: Path, run_id: str, message: str) -> None:
    log_path = wiki_dir / "log.md"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    entry = f"\n## [{timestamp}] wiki | {run_id}\n\n{message}\n"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(entry)


def update_open_questions(wiki_dir: Path, run_id: str, validation_path: Path) -> bool:
    if not validation_path.exists():
        return False
    rows = [row for row in read_csv(validation_path) if row.get("status") in {"FAIL", "WARN"}]
    if not rows:
        return False
    questions_dir = ensure_dir(wiki_dir / "questions")
    lines = [
        f"# Open Validation Questions: {run_id}",
        "",
        "The following validation items require human review.",
        "",
    ]
    for row in rows:
        lines.append(f"- **{row['status']}** `{row['check_name']}`: {row['message']} {row.get('details', '')}".strip())
    (questions_dir / f"{safe_stem(run_id)}-validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def replace_section(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1 or end <= start:
        return text.rstrip() + "\n\n" + replacement
    return text[:start] + replacement + text[end:]


def read_optional_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return read_csv(path)

