from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .analysis import analyze_run
from .config import ProjectPaths
from .conversion import convert_run
from .filesystem import write_json
from .ingestion import scan_source
from .load import load_run
from .memo import generate_memo
from .wiki import update_wiki


@dataclass(frozen=True)
class PipelineSummary:
    run_id: str
    source: str
    offline: bool
    files_discovered: int
    converted_files: int
    validation_status: str
    memo_path: str


def run_pipeline(source: Path, run_id: str, offline: bool = False, paths: ProjectPaths | None = None) -> PipelineSummary:
    paths = paths or ProjectPaths.discover()
    entries = scan_source(source, run_id, paths)
    conversions = convert_run(run_id, paths)
    load_run(run_id, offline=offline, paths=paths)
    analysis = analyze_run(run_id, offline=offline, paths=paths)
    update_wiki(run_id, paths)
    memo = generate_memo(run_id, paths)
    summary = PipelineSummary(
        run_id=run_id,
        source=str(source),
        offline=offline,
        files_discovered=len(entries),
        converted_files=len(conversions),
        validation_status=analysis.validation_status,
        memo_path=memo.memo_path,
    )
    write_json(paths.run_dir(run_id) / "pipeline_summary.json", asdict(summary))
    return summary

