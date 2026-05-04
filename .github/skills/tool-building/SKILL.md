---
name: tool-building
description: Use when the agent needs a new or improved Python/MCP capability.
---

# Tool Building Skill

The LLM decides what capability is needed. Python tools only execute bounded
actions.

1. Describe the missing capability and expected structured output.
2. Use `scaffold_python_tool` if a new module is needed.
3. Implement the smallest useful function.
4. Add or update focused tests.
5. Use `run_tests` and report failures clearly.

