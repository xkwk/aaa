"""Source package profiling capability for agent evidence gathering."""

from __future__ import annotations

from pathlib import Path

from .common import iter_files, read_csv_rows, sha256_file


TABULAR_SUFFIXES = {".csv", ".xlsx", ".xls"}


def profile_source_package(source: str, sample_size: int = 5) -> dict:
    """Profile files and tabular structures without choosing an analysis path."""
    source_path = Path(source).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Source does not exist: {source_path}")
    files = [profile_file(path, source_path, sample_size) for path in iter_files(source_path)]
    return {"source": str(source_path), "files": files}


def profile_file(path: Path, source_root: Path, sample_size: int) -> dict:
    """Profile one file relative to the submitted source package."""
    relative = path.name if source_root.is_file() else path.relative_to(source_root).as_posix()
    base = {
        "path": str(path),
        "relative_path": relative,
        "suffix": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "kind": "tabular" if path.suffix.lower() in TABULAR_SUFFIXES else "document",
    }
    if path.suffix.lower() == ".csv":
        base.update(profile_csv(path, sample_size))
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        base.update(profile_excel(path, sample_size))
    return base


def profile_csv(path: Path, sample_size: int) -> dict:
    """Profile a CSV file using header names and sample values."""
    rows = read_csv_rows(path)
    return profile_rows(rows, sample_size)


def profile_excel(path: Path, sample_size: int) -> dict:
    """Profile workbook sheets when openpyxl is available."""
    try:
        import openpyxl
    except ImportError:
        return {"profile_status": "skipped", "reason": "openpyxl is not installed"}
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet_profiles = []
    for sheet in workbook.worksheets:
        values = list(sheet.iter_rows(values_only=True))
        if not values:
            sheet_profiles.append({"sheet": sheet.title, "row_count": 0, "columns": []})
            continue
        headers = [str(value or "").strip() for value in values[0]]
        rows = [
            {header: str(value or "").strip() for header, value in zip(headers, row) if header}
            for row in values[1:]
            if any(value is not None and str(value).strip() for value in row)
        ]
        profile = profile_rows(rows, sample_size)
        profile["sheet"] = sheet.title
        sheet_profiles.append(profile)
    return {"profile_status": "profiled", "sheets": sheet_profiles}


def profile_rows(rows: list[dict[str, str]], sample_size: int) -> dict:
    """Summarize row counts, columns, and representative values."""
    if not rows:
        return {"profile_status": "profiled", "row_count": 0, "columns": []}
    columns = []
    for name in rows[0].keys():
        values = [row.get(name, "") for row in rows if row.get(name, "") != ""]
        sample_values = []
        for value in values:
            if value not in sample_values:
                sample_values.append(value)
            if len(sample_values) >= sample_size:
                break
        columns.append({"name": name, "non_null_count": len(values), "sample_values": sample_values})
    return {"profile_status": "profiled", "row_count": len(rows), "columns": columns}
