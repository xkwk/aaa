from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from collections import defaultdict

from .config import ProjectPaths, SnowflakeSettings
from .filesystem import ensure_dir, read_csv, write_csv, write_json
from .snowflake import SnowflakeRepository
from .table_io import decimal_to_text, decimal_value


VALIDATION_FIELDS = ["run_id", "check_name", "status", "severity", "message", "details"]
MOVEMENT_FIELDS = ["run_id", "from_period", "to_period", "product", "portfolio", "measure", "driver", "amount"]
DASHBOARD_FIELDS = ["run_id", "from_period", "to_period", "product", "portfolio", "measure", "driver", "amount"]


@dataclass(frozen=True)
class ValidationResult:
    run_id: str
    check_name: str
    status: str
    severity: str
    message: str
    details: str = ""


@dataclass(frozen=True)
class AnalysisSummary:
    run_id: str
    from_period: str
    to_period: str
    total_result_delta: str
    total_bridge: str
    total_unreconciled: str
    validation_status: str
    validation_failures: int
    validation_warnings: int


def analyze_run(run_id: str, offline: bool = False, paths: ProjectPaths | None = None) -> AnalysisSummary:
    paths = paths or ProjectPaths.discover()
    loaded_dir = paths.run_dir(run_id) / "loaded"
    results_path = loaded_dir / "valuation_results.csv"
    bridge_path = loaded_dir / "valuation_bridge.csv"
    if not results_path.exists() or not bridge_path.exists():
        raise FileNotFoundError(f"Run {run_id} has not been loaded. Run act load first.")

    results = read_csv(results_path)
    bridge = read_csv(bridge_path)
    validations: list[ValidationResult] = []

    periods = sorted({(row["from_period"], row["to_period"]) for row in bridge})
    if len(periods) != 1:
        validations.append(
            ValidationResult(run_id, "single_bridge_period", "FAIL", "blocking", "Bridge must contain exactly one from/to period.", str(periods))
        )
        from_period, to_period = ("", "")
    else:
        from_period, to_period = periods[0]
        validations.append(
            ValidationResult(run_id, "single_bridge_period", "PASS", "info", f"Bridge period is {from_period} to {to_period}.")
        )

    validations.extend(validate_required_values(run_id, results, "valuation_results"))
    validations.extend(validate_required_values(run_id, bridge, "valuation_bridge"))
    validations.extend(validate_duplicate_rows(run_id, bridge))

    result_delta = valuation_delta(results, from_period, to_period)
    bridge_totals = bridge_by_dimension(bridge)
    reconciliation_rows, reconciliation_validations = reconcile_bridge(run_id, result_delta, bridge_totals)
    validations.extend(reconciliation_validations)

    movement_rows = [
        {
            "run_id": run_id,
            "from_period": row["from_period"],
            "to_period": row["to_period"],
            "product": row["product"],
            "portfolio": row["portfolio"],
            "measure": row["measure"],
            "driver": row["driver"],
            "amount": decimal_to_text(decimal_value(row["amount"])),
        }
        for row in bridge
    ]
    dashboard_rows = dashboard_summary(movement_rows)

    run_dir = ensure_dir(paths.run_dir(run_id))
    write_csv(run_dir / "movement_results.csv", movement_rows, MOVEMENT_FIELDS)
    write_csv(run_dir / "dashboard_summary.csv", dashboard_rows, DASHBOARD_FIELDS)
    write_csv(run_dir / "validation_results.csv", [asdict(v) for v in validations], VALIDATION_FIELDS)
    write_csv(run_dir / "reconciliation.csv", reconciliation_rows, ["run_id", "product", "portfolio", "measure", "result_delta", "bridge_total", "unreconciled"])

    failures = sum(1 for item in validations if item.status == "FAIL")
    warnings = sum(1 for item in validations if item.status == "WARN")
    total_result_delta = sum(result_delta.values(), Decimal("0"))
    total_bridge = sum(bridge_totals.values(), Decimal("0"))
    summary = AnalysisSummary(
        run_id=run_id,
        from_period=from_period,
        to_period=to_period,
        total_result_delta=decimal_to_text(total_result_delta),
        total_bridge=decimal_to_text(total_bridge),
        total_unreconciled=decimal_to_text(total_result_delta - total_bridge),
        validation_status="PASS" if failures == 0 else "FAIL",
        validation_failures=failures,
        validation_warnings=warnings,
    )
    write_json(run_dir / "analysis_summary.json", asdict(summary))

    if not offline:
        write_snowflake_outputs(run_id, movement_rows, dashboard_rows, validations)
    return summary


def validate_required_values(run_id: str, rows: list[dict[str, str]], label: str) -> list[ValidationResult]:
    failures = []
    for idx, row in enumerate(rows, start=1):
        missing = [key for key, value in row.items() if value == ""]
        if missing:
            failures.append(
                ValidationResult(run_id, f"{label}_required_values", "FAIL", "blocking", f"Row {idx} has missing required values.", ",".join(missing))
            )
    if failures:
        return failures
    return [ValidationResult(run_id, f"{label}_required_values", "PASS", "info", f"{label} required values are populated.")]


def validate_duplicate_rows(run_id: str, rows: list[dict[str, str]]) -> list[ValidationResult]:
    seen: set[tuple[tuple[str, str], ...]] = set()
    duplicates = 0
    for row in rows:
        key = tuple(sorted(row.items()))
        if key in seen:
            duplicates += 1
        seen.add(key)
    if duplicates:
        return [ValidationResult(run_id, "duplicate_bridge_rows", "WARN", "review", f"Bridge has {duplicates} exact duplicate row(s).")]
    return [ValidationResult(run_id, "duplicate_bridge_rows", "PASS", "info", "No exact duplicate bridge rows found.")]


def valuation_delta(rows: list[dict[str, str]], from_period: str, to_period: str) -> dict[tuple[str, str, str], Decimal]:
    grouped: dict[tuple[str, str, str, str], Decimal] = defaultdict(lambda: Decimal("0"))
    for row in rows:
        period = row["valuation_period"]
        if period not in {from_period, to_period}:
            continue
        key = (period, row["product"], row["portfolio"], row["measure"])
        grouped[key] += decimal_value(row["amount"])

    deltas: dict[tuple[str, str, str], Decimal] = defaultdict(lambda: Decimal("0"))
    dimensions = {(product, portfolio, measure) for _, product, portfolio, measure in grouped}
    for product, portfolio, measure in dimensions:
        current = grouped[(to_period, product, portfolio, measure)]
        prior = grouped[(from_period, product, portfolio, measure)]
        deltas[(product, portfolio, measure)] = current - prior
    return dict(deltas)


def bridge_by_dimension(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], Decimal]:
    grouped: dict[tuple[str, str, str], Decimal] = defaultdict(lambda: Decimal("0"))
    for row in rows:
        grouped[(row["product"], row["portfolio"], row["measure"])] += decimal_value(row["amount"])
    return dict(grouped)


def reconcile_bridge(
    run_id: str,
    result_delta: dict[tuple[str, str, str], Decimal],
    bridge_totals: dict[tuple[str, str, str], Decimal],
    tolerance: Decimal = Decimal("0.01"),
) -> tuple[list[dict[str, str]], list[ValidationResult]]:
    rows = []
    failures = []
    for key in sorted(set(result_delta) | set(bridge_totals)):
        delta = result_delta.get(key, Decimal("0"))
        bridge = bridge_totals.get(key, Decimal("0"))
        unreconciled = delta - bridge
        product, portfolio, measure = key
        rows.append(
            {
                "run_id": run_id,
                "product": product,
                "portfolio": portfolio,
                "measure": measure,
                "result_delta": decimal_to_text(delta),
                "bridge_total": decimal_to_text(bridge),
                "unreconciled": decimal_to_text(unreconciled),
            }
        )
        if abs(unreconciled) > tolerance:
            failures.append(f"{product}/{portfolio}/{measure}: {decimal_to_text(unreconciled)}")

    if failures:
        return rows, [
            ValidationResult(
                run_id,
                "bridge_reconciliation",
                "FAIL",
                "blocking",
                "Bridge totals do not reconcile to valuation result deltas.",
                "; ".join(failures),
            )
        ]
    return rows, [ValidationResult(run_id, "bridge_reconciliation", "PASS", "info", "Bridge totals reconcile to valuation result deltas.")]


def dashboard_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str, str, str, str, str], Decimal] = defaultdict(lambda: Decimal("0"))
    for row in rows:
        key = (
            row["run_id"],
            row["from_period"],
            row["to_period"],
            row["product"],
            row["portfolio"],
            row["measure"],
            row["driver"],
        )
        grouped[key] += decimal_value(row["amount"])
    return [
        {
            "run_id": key[0],
            "from_period": key[1],
            "to_period": key[2],
            "product": key[3],
            "portfolio": key[4],
            "measure": key[5],
            "driver": key[6],
            "amount": decimal_to_text(value),
        }
        for key, value in sorted(grouped.items())
    ]


def write_snowflake_outputs(
    run_id: str,
    movement_rows: list[dict[str, str]],
    dashboard_rows: list[dict[str, str]],
    validations: list[ValidationResult],
) -> None:
    settings = SnowflakeSettings.from_env()
    repo = SnowflakeRepository(settings)
    repo.bootstrap()
    repo.replace_rows(
        settings.schema_curated,
        "MOVEMENT_RESULTS",
        run_id,
        ["RUN_ID", "FROM_PERIOD", "TO_PERIOD", "PRODUCT", "PORTFOLIO", "MEASURE", "DRIVER", "AMOUNT"],
        [
            (
                row["run_id"],
                row["from_period"],
                row["to_period"],
                row["product"],
                row["portfolio"],
                row["measure"],
                row["driver"],
                row["amount"],
            )
            for row in movement_rows
        ],
    )
    repo.replace_rows(
        settings.schema_runs,
        "VALIDATION_RESULTS",
        run_id,
        ["RUN_ID", "CHECK_NAME", "STATUS", "SEVERITY", "MESSAGE", "DETAILS"],
        [(v.run_id, v.check_name, v.status, v.severity, v.message, v.details) for v in validations],
    )
    repo.replace_rows(
        settings.schema_app,
        "DASHBOARD_SUMMARY",
        run_id,
        ["RUN_ID", "FROM_PERIOD", "TO_PERIOD", "PRODUCT", "PORTFOLIO", "MEASURE", "DRIVER", "AMOUNT"],
        [
            (
                row["run_id"],
                row["from_period"],
                row["to_period"],
                row["product"],
                row["portfolio"],
                row["measure"],
                row["driver"],
                row["amount"],
            )
            for row in dashboard_rows
        ],
    )

