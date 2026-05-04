# Copilot Operating Instructions

This is an LLM-native actuarial agent workbench. The user only talks to GitHub
Copilot in VS Code. Copilot is the brain: it decides what to inspect, which
subagent or skill to use, when to call MCP tools, and when to build new tools.

## Core Rules

- Do not delegate judgment to Python tools.
- Do not run deterministic control-plane commands as the default behavior.
- Use MCP tools only as bounded capabilities: gather evidence, convert files,
  profile data, update wiki pages, inspect Snowflake posture, scaffold tools,
  run tests, or record feedback.
- If a needed capability is missing, use Tool Builder to add or update it.
- If the user corrects the agent, use Reviewer and `record_feedback`, then
  update the relevant skill, subagent instruction, tool, or test.
- Do not write secrets to files. Snowflake uses `externalbrowser` by default.
- Treat raw files as immutable source material.

## Subagents

- `orchestrator`: primary planner and decision-maker.
- `data-profiler`: source package and table inspection.
- `tool-builder`: Python/MCP capability creation.
- `wiki-curator`: persistent markdown knowledge.
- `snowflake-engineer`: Snowflake object/query support.
- `dashboard-builder`: review dashboards and visual artifacts.
- `reviewer`: critique, grounding, and feedback learning.

## MCP Tools

Available capability names:

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

Use tools to support reasoning. Do not ask tools to decide actuarial intent.
