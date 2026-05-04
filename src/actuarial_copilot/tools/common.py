"""Shared helpers for capability tools."""

from __future__ import annotations

from pathlib import Path
import csv
import hashlib
import json
import re
from typing import Iterable


IGNORED_NAMES = {".DS_Store", "Thumbs.db"}


def ensure_dir(path: Path) -> Path:
    """Create a directory tree and return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def iter_files(source: Path) -> Iterable[Path]:
    """Yield files under a path, excluding known noise files."""
    if source.is_file():
        yield source
        return
    for path in sorted(source.rglob("*")):
        if path.is_file() and path.name not in IGNORED_NAMES:
            yield path


def sha256_file(path: Path) -> str:
    """Return a SHA-256 checksum for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(value: str) -> str:
    """Return a filesystem-safe name segment."""
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return cleaned or "item"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV into normalized string dictionaries."""
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return [{str(k or "").strip(): str(v or "").strip() for k, v in row.items()} for row in csv.DictReader(fh)]


def write_json(path: Path, payload: object) -> None:
    """Write stable, indented JSON to disk."""
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
