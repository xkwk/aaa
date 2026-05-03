from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import sys

from .analysis import analyze_run
from .config import ProjectPaths
from .conversion import convert_run
from .ingestion import scan_source
from .load import load_run
from .memo import generate_memo
from .pipeline import run_pipeline
from .wiki import update_wiki


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = ProjectPaths.discover()
    try:
        result = dispatch(args, paths)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if result is not None:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="act", description="Copilot-operated actuarial valuation movement CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="Scan a source folder and create a run manifest")
    ingest.add_argument("--source", required=True)
    ingest.add_argument("--run-id", required=True)

    convert = sub.add_parser("convert", help="Convert run source files to markdown previews")
    convert.add_argument("--run-id", required=True)

    load = sub.add_parser("load", help="Load valuation result and bridge files")
    load.add_argument("--run-id", required=True)
    load.add_argument("--offline", action="store_true", help="Write local cache only; do not connect to Snowflake")

    analyze = sub.add_parser("analyze", help="Run movement bridge validation and analysis")
    analyze.add_argument("--run-id", required=True)
    analyze.add_argument("--offline", action="store_true", help="Do not write Snowflake output tables")

    wiki = sub.add_parser("wiki", help="Update the markdown wiki for a run")
    wiki.add_argument("--run-id", required=True)

    memo = sub.add_parser("memo", help="Generate a markdown valuation movement memo")
    memo.add_argument("--run-id", required=True)

    run = sub.add_parser("run", help="Run the full MVP pipeline")
    run.add_argument("--source", required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument("--offline", action="store_true", help="Write local cache only; do not connect to Snowflake")
    return parser


def dispatch(args: argparse.Namespace, paths: ProjectPaths) -> dict | list[dict] | None:
    offline = bool(getattr(args, "offline", False) or os.getenv("ACT_OFFLINE") == "1")
    if args.command == "ingest":
        entries = scan_source(Path(args.source), args.run_id, paths)
        return {"run_id": args.run_id, "files_discovered": len(entries)}
    if args.command == "convert":
        results = convert_run(args.run_id, paths)
        return {"run_id": args.run_id, "converted_files": len(results)}
    if args.command == "load":
        return load_run(args.run_id, offline=offline, paths=paths).__dict__
    if args.command == "analyze":
        return analyze_run(args.run_id, offline=offline, paths=paths).__dict__
    if args.command == "wiki":
        return update_wiki(args.run_id, paths).__dict__
    if args.command == "memo":
        return generate_memo(args.run_id, paths).__dict__
    if args.command == "run":
        return run_pipeline(Path(args.source), args.run_id, offline=offline, paths=paths).__dict__
    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

