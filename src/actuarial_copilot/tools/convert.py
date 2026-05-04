from __future__ import annotations

from pathlib import Path
import csv

from .common import ensure_dir, iter_files, safe_name


def convert_documents(source: str, output_dir: str = "converted") -> dict:
    """Convert documents to markdown previews.

    This is a capability tool. It does not summarize, classify, or decide how
    the converted material should be used.
    """
    source_path = Path(source).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Source does not exist: {source_path}")

    destination = ensure_dir(Path(output_dir).resolve() / safe_name(source_path.stem))
    results = []
    for path in iter_files(source_path):
        relative = path.name if source_path.is_file() else path.relative_to(source_path).as_posix()
        target = destination / f"{safe_name(relative)}.md"
        try:
            text, converter = convert_one(path)
            status = "converted"
            error = ""
        except Exception as exc:
            text = f"# Conversion unavailable: {path.name}\n\nError: `{type(exc).__name__}: {exc}`\n"
            converter = "fallback-error"
            status = "failed"
            error = str(exc)
        target.write_text(text.strip() + "\n", encoding="utf-8")
        results.append(
            {
                "source_path": str(path),
                "relative_path": relative,
                "markdown_path": str(target),
                "status": status,
                "converter": converter,
                "error": error,
            }
        )
    return {"source": str(source_path), "output_dir": str(destination), "files": results}


def convert_one(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return path.read_text(encoding="utf-8", errors="replace"), "text"
    if suffix == ".csv":
        return csv_preview(path), "csv-preview"
    if suffix in {".json", ".xml", ".html", ".htm"}:
        return path.read_text(encoding="utf-8", errors="replace"), "text"
    try:
        from markitdown import MarkItDown
    except ImportError as exc:
        raise RuntimeError("MarkItDown is not installed for this file type") from exc
    result = MarkItDown(enable_plugins=False).convert(str(path))
    return result.text_content, "markitdown"


def csv_preview(path: Path, max_rows: int = 30) -> str:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = []
        for idx, row in enumerate(csv.reader(fh)):
            rows.append(row)
            if idx >= max_rows:
                break
    if not rows:
        return f"# CSV preview: {path.name}\n\nNo rows found.\n"
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    lines = [f"# CSV preview: {path.name}", ""]
    lines.append("| " + " | ".join(normalized[0]) + " |")
    lines.append("| " + " | ".join(["---"] * width) + " |")
    for row in normalized[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)

