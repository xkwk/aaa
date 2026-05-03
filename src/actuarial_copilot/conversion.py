from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import csv

from .config import ProjectPaths
from .filesystem import ensure_dir, safe_stem, write_csv
from .ingestion import ManifestEntry, load_manifest


CONVERSION_FIELDS = [
    "run_id",
    "file_id",
    "source_relative_path",
    "converted_path",
    "status",
    "converter",
    "notes",
]


@dataclass(frozen=True)
class ConversionResult:
    run_id: str
    file_id: str
    source_relative_path: str
    converted_path: str
    status: str
    converter: str
    notes: str = ""


def convert_run(run_id: str, paths: ProjectPaths | None = None) -> list[ConversionResult]:
    paths = paths or ProjectPaths.discover()
    entries = load_manifest(run_id, paths)
    output_dir = ensure_dir(paths.converted_run_dir(run_id))
    results = [convert_entry(entry, output_dir) for entry in entries]
    write_csv(paths.run_dir(run_id) / "conversion_manifest.csv", [asdict(r) for r in results], CONVERSION_FIELDS)
    return results


def convert_entry(entry: ManifestEntry, output_dir: Path) -> ConversionResult:
    source = Path(entry.absolute_path)
    out_path = output_dir / f"{safe_stem(entry.relative_path)}.md"
    try:
        text, converter = convert_file(source)
        status = "converted"
        notes = ""
    except Exception as exc:  # conversion failures should be visible but non-fatal
        text = conversion_stub(entry, f"{type(exc).__name__}: {exc}")
        converter = "stub"
        status = "conversion_failed"
        notes = str(exc)

    ensure_dir(out_path.parent)
    out_path.write_text(with_frontmatter(entry, text), encoding="utf-8")
    return ConversionResult(
        run_id=entry.run_id,
        file_id=entry.file_id,
        source_relative_path=entry.relative_path,
        converted_path=out_path.as_posix(),
        status=status,
        converter=converter,
        notes=notes,
    )


def convert_file(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return path.read_text(encoding="utf-8", errors="replace"), "text"
    if suffix == ".csv":
        return csv_preview(path), "csv-preview"
    if suffix in {".xlsx", ".xls"}:
        return xlsx_preview(path), "xlsx-preview"
    return markitdown_convert(path)


def markitdown_convert(path: Path) -> tuple[str, str]:
    try:
        from markitdown import MarkItDown
    except ImportError as exc:
        raise RuntimeError("MarkItDown is not installed; install the markitdown extra") from exc
    result = MarkItDown(enable_plugins=False).convert(str(path))
    return result.text_content, "markitdown"


def csv_preview(path: Path, max_rows: int = 30) -> str:
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        rows = []
        for idx, row in enumerate(reader):
            rows.append(row)
            if idx >= max_rows:
                break
    return rows_to_markdown(rows, f"CSV preview: {path.name}")


def xlsx_preview(path: Path, max_rows: int = 30) -> str:
    try:
        import openpyxl
    except ImportError as exc:
        raise RuntimeError("Install openpyxl or the markitdown extra to preview Excel files") from exc

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    parts = [f"# Excel preview: {path.name}"]
    for sheet in wb.worksheets:
        rows = []
        for idx, row in enumerate(sheet.iter_rows(values_only=True)):
            rows.append(["" if value is None else str(value) for value in row])
            if idx >= max_rows:
                break
        parts.append(rows_to_markdown(rows, f"Sheet: {sheet.title}"))
    return "\n\n".join(parts)


def rows_to_markdown(rows: list[list[str]], title: str) -> str:
    if not rows:
        return f"# {title}\n\nNo rows found.\n"
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    header = normalized[0]
    body = normalized[1:]
    lines = [f"# {title}", "", "| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * width) + " |"]
    for row in body:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines) + "\n"


def with_frontmatter(entry: ManifestEntry, text: str) -> str:
    return (
        "---\n"
        f"run_id: {entry.run_id}\n"
        f"file_id: {entry.file_id}\n"
        f"source_path: {entry.relative_path}\n"
        f"sha256: {entry.sha256}\n"
        f"role: {entry.role}\n"
        "---\n\n"
        f"{text.strip()}\n"
    )


def conversion_stub(entry: ManifestEntry, error: str) -> str:
    return (
        f"# Conversion unavailable: {entry.file_name}\n\n"
        f"- Source path: `{entry.relative_path}`\n"
        f"- Role: `{entry.role}`\n"
        f"- Error: `{error}`\n\n"
        "Install the relevant optional dependencies or inspect the source file manually.\n"
    )

