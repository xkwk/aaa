from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from .config import ProjectPaths
from .filesystem import ensure_dir, read_csv, read_json, write_json
from .ingestion import load_manifest


@dataclass(frozen=True)
class MemoSummary:
    run_id: str
    memo_path: str
    validation_status: str
    review_required: bool


def generate_memo(run_id: str, paths: ProjectPaths | None = None) -> MemoSummary:
    paths = paths or ProjectPaths.discover()
    run_dir = paths.run_dir(run_id)
    analysis_path = run_dir / "analysis_summary.json"
    if not analysis_path.exists():
        raise FileNotFoundError(f"Missing analysis summary for run {run_id}. Run act analyze first.")

    analysis = read_json(analysis_path)
    dashboard = read_csv(run_dir / "dashboard_summary.csv") if (run_dir / "dashboard_summary.csv").exists() else []
    validations = read_csv(run_dir / "validation_results.csv") if (run_dir / "validation_results.csv").exists() else []
    entries = load_manifest(run_id, paths)

    memo_path = run_dir / "memo.md"
    ensure_dir(memo_path.parent)
    memo_path.write_text(render_memo(run_id, analysis, dashboard, validations, entries), encoding="utf-8")

    summary = MemoSummary(
        run_id=run_id,
        memo_path=memo_path.as_posix(),
        validation_status=str(analysis.get("validation_status", "UNKNOWN")),
        review_required=True,
    )
    write_json(run_dir / "memo_summary.json", asdict(summary))
    return summary


def render_memo(run_id: str, analysis: dict, dashboard: list[dict[str, str]], validations: list[dict[str, str]], entries) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    failures = [row for row in validations if row.get("status") == "FAIL"]
    warnings = [row for row in validations if row.get("status") == "WARN"]
    source_lines = "\n".join(f"- `{entry.relative_path}` ({entry.role})" for entry in entries)
    dashboard_table = markdown_table(
        dashboard,
        ["product", "portfolio", "measure", "driver", "amount"],
        empty="No dashboard movement rows were generated.",
    )
    validation_table = markdown_table(
        validations,
        ["check_name", "status", "severity", "message"],
        empty="No validation results were generated.",
    )

    status_sentence = (
        "The deterministic validation checks passed."
        if analysis.get("validation_status") == "PASS"
        else "One or more deterministic validation checks failed and require review before use."
    )
    return f"""# Valuation Movement Memo Draft: {run_id}

Generated: {generated}

Review status: **Actuarial review required**  
Validation status: **{analysis.get("validation_status", "UNKNOWN")}**

## Executive Summary

This draft summarizes the valuation movement from `{analysis.get("from_period", "")}` to
`{analysis.get("to_period", "")}` using the provided movement bridge file. {status_sentence}

- Total valuation result delta: `{analysis.get("total_result_delta", "")}`
- Total bridge movement: `{analysis.get("total_bridge", "")}`
- Unreconciled movement: `{analysis.get("total_unreconciled", "")}`
- Validation failures: `{analysis.get("validation_failures", "")}`
- Validation warnings: `{analysis.get("validation_warnings", "")}`

## Movement Drivers

{dashboard_table}

## Validation

{validation_table}

## Source Files

{source_lines or "No source files recorded."}

## Review Notes

- This memo is generated from deterministic tools and wiki/source artifacts.
- It is not actuarial sign-off.
- Movement explanations must be reviewed against model owner commentary and committee requirements.
"""


def markdown_table(rows: list[dict[str, str]], columns: list[str], empty: str) -> str:
    if not rows:
        return empty
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)

