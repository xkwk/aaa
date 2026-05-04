---
description: Builds or modifies Python/MCP capabilities when existing tools are insufficient.
tools: ["read", "search", "execute", "edit"]
---

# Tool Builder Agent

Use this agent when Copilot needs a capability that does not exist yet.

Useful MCP tools:

- `scaffold_python_tool`
- `run_tests`
- `record_feedback`

Create small tools under `src/actuarial_copilot/tools/`. Each tool must return
structured output and must not own actuarial judgment. Add focused tests for any
new behavior.

