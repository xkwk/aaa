# LLM-Native Actuarial Agent Workbench

This repo is an AI agent project for actuarial teams. The user talks only to
GitHub Copilot in VS Code. Copilot is the brain: it plans, judges, delegates to
subagents, uses skills, and calls MCP tools only when useful.

Python does not direct actuarial tasks. Python provides bounded
capabilities.

```text
User -> Copilot Orchestrator
  -> subagents + skills
  -> MCP tools when useful
  -> wiki / feedback / examples as memory and reference
```

## Structure

```text
.github/
  agents/   # Copilot subagent instructions
  skills/   # reusable agent playbooks

mcp/
  server.py # MCP tool server

src/actuarial_copilot/tools/
  convert.py
  profile.py
  wiki.py
  snowflake.py
  scaffold.py
  tests.py
  feedback.py

wiki/            # persistent markdown knowledge
agent_feedback/  # lessons from user feedback
examples/        # reference material only
```

## MCP Tools

The MCP server exposes capabilities, not decisions:

- `convert_documents`
- `profile_source_package`
- `read_wiki`
- `write_wiki_page`
- `search_wiki`
- `inspect_snowflake`
- `propose_snowflake_objects`
- `scaffold_python_tool`
- `run_tests`
- `record_feedback`

Run the MCP server after installing the optional dependency:

```bash
python -m pip install -e ".[mcp]"
PYTHONPATH=src python mcp/server.py
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
PYTHONPATH=src python -m unittest discover -s tests
```

Optional integrations:

```bash
python -m pip install -e ".[markitdown,snowflake,mcp]"
```

Snowflake browser login is the default:

```bash
export ACT_SNOWFLAKE_AUTHENTICATOR=externalbrowser
export ACT_SNOWFLAKE_ACCOUNT=<company-account>
export ACT_SNOWFLAKE_USER=<your-email>
```

## Design Rule

The LLM decides. Tools assist.

If Copilot needs a capability that does not exist, it should use Tool Builder to
create or update a small Python/MCP tool, add tests, and update skills or
subagent instructions from feedback.
