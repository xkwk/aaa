from __future__ import annotations

from pathlib import Path

from .pipeline import run_pipeline
from .ingestion import scan_source
from .conversion import convert_run
from .load import load_run
from .analysis import analyze_run
from .wiki import update_wiki
from .memo import generate_memo


def main() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit("Install the mcp extra to run the optional MCP server: pip install -e '.[mcp]'") from exc

    mcp = FastMCP("actuarial-copilot-workbench")

    @mcp.tool()
    def act_run(source: str, run_id: str, offline: bool = False) -> dict:
        """Run the full valuation movement MVP pipeline."""
        return run_pipeline(Path(source), run_id, offline=offline).__dict__

    @mcp.tool()
    def act_ingest(source: str, run_id: str) -> dict:
        """Scan source files and create a manifest."""
        entries = scan_source(Path(source), run_id)
        return {"run_id": run_id, "files_discovered": len(entries)}

    @mcp.tool()
    def act_convert(run_id: str) -> dict:
        """Convert run source files to markdown previews."""
        results = convert_run(run_id)
        return {"run_id": run_id, "converted_files": len(results)}

    @mcp.tool()
    def act_load(run_id: str, offline: bool = False) -> dict:
        """Load valuation result and bridge files."""
        return load_run(run_id, offline=offline).__dict__

    @mcp.tool()
    def act_analyze(run_id: str, offline: bool = False) -> dict:
        """Run movement analysis and validation."""
        return analyze_run(run_id, offline=offline).__dict__

    @mcp.tool()
    def act_wiki(run_id: str) -> dict:
        """Update the markdown wiki."""
        return update_wiki(run_id).__dict__

    @mcp.tool()
    def act_memo(run_id: str) -> dict:
        """Generate a markdown memo."""
        return generate_memo(run_id).__dict__

    mcp.run()


if __name__ == "__main__":
    main()

