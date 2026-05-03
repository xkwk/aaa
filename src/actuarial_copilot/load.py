from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .config import ProjectPaths, SnowflakeSettings
from .filesystem import ensure_dir, read_csv, write_csv, write_json
from .ingestion import ManifestEntry, load_manifest, MANIFEST_FIELDS
from .snowflake import SnowflakeRepository, bootstrap_sql
from .table_io import decimal_value, decimal_to_text, read_table, require_columns


VALUATION_RESULT_COLUMNS = [
    "valuation_period",
    "run_id",
    "product",
    "portfolio",
    "cohort",
    "measure",
    "amount",
    "currency",
]
BRIDGE_COLUMNS = [
    "from_period",
    "to_period",
    "run_id",
    "product",
    "portfolio",
    "measure",
    "driver",
    "amount",
]


@dataclass(frozen=True)
class LoadSummary:
    run_id: str
    mode: str
    valuation_results_rows: int
    valuation_bridge_rows: int
    manifest_rows: int
    snowflake_database: str
    status: str
    message: str


def load_run(run_id: str, offline: bool = False, paths: ProjectPaths | None = None) -> LoadSummary:
    paths = paths or ProjectPaths.discover()
    entries = load_manifest(run_id, paths)
    result_file = find_single_role(entries, "valuation_results")
    bridge_file = find_single_role(entries, "valuation_bridge")

    results = normalize_rows(read_table(Path(result_file.absolute_path)), VALUATION_RESULT_COLUMNS, run_id, "valuation results")
    bridge = normalize_rows(read_table(Path(bridge_file.absolute_path)), BRIDGE_COLUMNS, run_id, "valuation bridge")

    loaded_dir = ensure_dir(paths.run_dir(run_id) / "loaded")
    write_csv(loaded_dir / "valuation_results.csv", results, VALUATION_RESULT_COLUMNS)
    write_csv(loaded_dir / "valuation_bridge.csv", bridge, BRIDGE_COLUMNS)

    settings = SnowflakeSettings.from_env()
    mode = "offline"
    message = "Loaded local run cache only."

    if not offline:
        repo = SnowflakeRepository(settings)
        repo.bootstrap()
        repo.replace_rows(
            settings.schema_raw,
            "FILE_MANIFEST",
            run_id,
            ["RUN_ID", "FILE_ID", "RELATIVE_PATH", "FILE_NAME", "ROLE", "SHA256", "SIZE_BYTES", "MODIFIED_AT_UTC"],
            [
                (
                    e.run_id,
                    e.file_id,
                    e.relative_path,
                    e.file_name,
                    e.role,
                    e.sha256,
                    e.size_bytes,
                    e.modified_at_utc,
                )
                for e in entries
            ],
        )
        repo.replace_rows(
            settings.schema_raw,
            "VALUATION_RESULTS",
            run_id,
            ["VALUATION_PERIOD", "RUN_ID", "PRODUCT", "PORTFOLIO", "COHORT", "MEASURE", "AMOUNT", "CURRENCY"],
            [
                (
                    row["valuation_period"],
                    row["run_id"],
                    row["product"],
                    row["portfolio"],
                    row["cohort"],
                    row["measure"],
                    row["amount"],
                    row["currency"],
                )
                for row in results
            ],
        )
        repo.replace_rows(
            settings.schema_raw,
            "VALUATION_BRIDGE",
            run_id,
            ["FROM_PERIOD", "TO_PERIOD", "RUN_ID", "PRODUCT", "PORTFOLIO", "MEASURE", "DRIVER", "AMOUNT"],
            [
                (
                    row["from_period"],
                    row["to_period"],
                    row["run_id"],
                    row["product"],
                    row["portfolio"],
                    row["measure"],
                    row["driver"],
                    row["amount"],
                )
                for row in bridge
            ],
        )
        mode = "snowflake"
        message = "Loaded Snowflake raw tables and local run cache."

    sql_path = paths.run_dir(run_id) / "snowflake_bootstrap.sql"
    sql_path.write_text(bootstrap_sql(settings) + "\n", encoding="utf-8")

    summary = LoadSummary(
        run_id=run_id,
        mode=mode,
        valuation_results_rows=len(results),
        valuation_bridge_rows=len(bridge),
        manifest_rows=len(entries),
        snowflake_database=settings.database,
        status="loaded",
        message=message,
    )
    write_json(paths.run_dir(run_id) / "load_summary.json", asdict(summary))
    return summary


def find_single_role(entries: list[ManifestEntry], role: str) -> ManifestEntry:
    matches = [entry for entry in entries if entry.role == role]
    if not matches:
        raise ValueError(f"Manifest has no file with role {role}")
    if len(matches) > 1:
        names = ", ".join(entry.relative_path for entry in matches)
        raise ValueError(f"Manifest has multiple files with role {role}: {names}")
    return matches[0]


def normalize_rows(rows: list[dict[str, str]], columns: list[str], run_id: str, label: str) -> list[dict[str, str]]:
    require_columns(rows, set(columns), label)
    normalized: list[dict[str, str]] = []
    for row in rows:
        if row.get("run_id") and row["run_id"] != run_id:
            continue
        item = {column: str(row.get(column, "")).strip() for column in columns}
        item["run_id"] = run_id
        item["amount"] = decimal_to_text(decimal_value(item["amount"]))
        normalized.append(item)
    if not normalized:
        raise ValueError(f"{label} has no rows for run_id {run_id}")
    return normalized

