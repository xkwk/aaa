from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import ProjectPaths
from .filesystem import ensure_dir, iter_files, relative_posix, sha256_file, write_csv, write_json


MANIFEST_FIELDS = [
    "run_id",
    "file_id",
    "relative_path",
    "absolute_path",
    "file_name",
    "suffix",
    "size_bytes",
    "sha256",
    "modified_at_utc",
    "role",
    "status",
    "notes",
]

DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".pptx", ".md", ".txt", ".html", ".htm", ".json"}
TABLE_EXTENSIONS = {".csv", ".xlsx", ".xls"}


@dataclass(frozen=True)
class ManifestEntry:
    run_id: str
    file_id: str
    relative_path: str
    absolute_path: str
    file_name: str
    suffix: str
    size_bytes: int
    sha256: str
    modified_at_utc: str
    role: str
    status: str = "discovered"
    notes: str = ""


def detect_role(path: Path) -> str:
    name = path.name.lower().replace(" ", "_")
    suffix = path.suffix.lower()
    if suffix in TABLE_EXTENSIONS and "bridge" in name:
        return "valuation_bridge"
    if suffix in TABLE_EXTENSIONS and "movement" in name:
        return "valuation_bridge"
    if suffix in TABLE_EXTENSIONS and "valuation" in name and ("result" in name or "snapshot" in name):
        return "valuation_results"
    if suffix in TABLE_EXTENSIONS:
        return "data_file"
    if suffix in DOCUMENT_EXTENSIONS:
        return "supporting_document"
    return "other"


def scan_source(source: Path, run_id: str, paths: ProjectPaths | None = None) -> list[ManifestEntry]:
    source = source.resolve()
    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"Source folder does not exist: {source}")

    paths = paths or ProjectPaths.discover()
    run_dir = ensure_dir(paths.run_dir(run_id))
    entries: list[ManifestEntry] = []

    for file_path in iter_files(source):
        digest = sha256_file(file_path)
        stat = file_path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        entries.append(
            ManifestEntry(
                run_id=run_id,
                file_id=digest[:16],
                relative_path=relative_posix(file_path, source),
                absolute_path=str(file_path),
                file_name=file_path.name,
                suffix=file_path.suffix.lower(),
                size_bytes=stat.st_size,
                sha256=digest,
                modified_at_utc=modified,
                role=detect_role(file_path),
            )
        )

    rows = [asdict(entry) for entry in entries]
    write_csv(run_dir / "manifest.csv", rows, MANIFEST_FIELDS)
    write_json(run_dir / "manifest.json", rows)
    return entries


def load_manifest(run_id: str, paths: ProjectPaths | None = None) -> list[ManifestEntry]:
    paths = paths or ProjectPaths.discover()
    manifest = paths.run_dir(run_id) / "manifest.json"
    if not manifest.exists():
        raise FileNotFoundError(f"Missing manifest for run {run_id}: {manifest}")
    import json

    with manifest.open("r", encoding="utf-8") as fh:
        rows = json.load(fh)
    return [ManifestEntry(**row) for row in rows]

