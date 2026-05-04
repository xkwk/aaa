from __future__ import annotations

from actuarial_copilot.tools.convert import convert_documents
from actuarial_copilot.tools.feedback import record_feedback
from actuarial_copilot.tools.profile import profile_source_package
from actuarial_copilot.tools.scaffold import scaffold_python_tool
from actuarial_copilot.tools.snowflake import inspect_snowflake, propose_snowflake_objects
from actuarial_copilot.tools.tests import run_tests
from actuarial_copilot.tools.wiki import read_wiki, search_wiki, write_wiki_page


TOOL_NAMES = [
    "convert_documents",
    "profile_source_package",
    "read_wiki",
    "write_wiki_page",
    "search_wiki",
    "inspect_snowflake",
    "propose_snowflake_objects",
    "scaffold_python_tool",
    "run_tests",
    "record_feedback",
]


def register_tools(mcp) -> None:
    mcp.tool()(convert_documents)
    mcp.tool()(profile_source_package)
    mcp.tool()(read_wiki)
    mcp.tool()(write_wiki_page)
    mcp.tool()(search_wiki)
    mcp.tool()(inspect_snowflake)
    mcp.tool()(propose_snowflake_objects)
    mcp.tool()(scaffold_python_tool)
    mcp.tool()(run_tests)
    mcp.tool()(record_feedback)


def build_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install the mcp extra to run the MCP server") from exc
    server = FastMCP("actuarial-agent-workbench")
    register_tools(server)
    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()

