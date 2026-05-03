from __future__ import annotations

from pathlib import Path
import csv
from decimal import Decimal, InvalidOperation
from typing import Iterable


def normalize_header(value: object) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def read_table(path: Path) -> list[dict[str, str]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            return [{normalize_header(k): str(v or "").strip() for k, v in row.items()} for row in reader]
    if suffix in {".xlsx", ".xls"}:
        return read_xlsx(path)
    raise ValueError(f"Unsupported tabular file type: {path.suffix}")


def read_xlsx(path: Path) -> list[dict[str, str]]:
    try:
        import openpyxl
    except ImportError as exc:
        raise RuntimeError("Install openpyxl or the markitdown extra to read Excel files") from exc

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows: list[dict[str, str]] = []
    for sheet in wb.worksheets:
        iterator = sheet.iter_rows(values_only=True)
        try:
            headers = [normalize_header(value) for value in next(iterator)]
        except StopIteration:
            continue
        for values in iterator:
            if not any(value is not None and str(value).strip() for value in values):
                continue
            rows.append({header: str(value or "").strip() for header, value in zip(headers, values) if header})
    return rows


def decimal_value(value: object) -> Decimal:
    text = str(value or "0").strip().replace(",", "")
    if text == "":
        text = "0"
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid decimal value: {value!r}") from exc


def decimal_to_text(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(value.quantize(Decimal("1")))
    return format(value.normalize(), "f")


def require_columns(rows: Iterable[dict[str, str]], required: set[str], label: str) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError(f"{label} contains no rows")
    available = set(rows[0].keys())
    missing = sorted(required - available)
    if missing:
        raise ValueError(f"{label} missing required columns: {', '.join(missing)}")

