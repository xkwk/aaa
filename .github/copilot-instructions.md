# Copilot Operating Instructions

This workspace is a Copilot-operated valuation movement workbench. The user only
talks to GitHub Copilot in VS Code. Do not introduce another conversational UI.

## Hard boundaries

- Use the internal `act` CLI or MCP tools for workflow execution.
- Do not perform complex actuarial calculation directly in chat. Instead, build Python tools for it.
- Do not write secrets into files. Read Snowflake credentials from environment variables or ignored local config.
- Treat `raw/sharepoint/` as a synced SharePoint/local source folder.`
- Treat raw files as immutable. Generated artifacts belong under `converted/`, `runs/`, and `wiki/`.
- Exclude or mask any PII data when ingesting raw files.

## Standard workflow

When asked to run valuation movement for a run:

1. Use the Document Intake agent/skill to scan raw files and update the manifest.
2. Use MarkItDown conversion tooling for supporting document previews.
3. Use the Snowflake Loader agent/skill to load valuation result and bridge files.
4. Use the Valuation Analyst agent/skill to reconcile bridge movement.
5. Use the Wiki Curator agent/skill to update the Karpathy-style markdown wiki.
6. Use the Dashboard Engineer agent/skill to update Streamlit/Snowflake artifacts.
7. Use the Memo Writer agent/skill to draft `runs/<run_id>/memo.md`.

For local smoke testing without Snowflake, pass `--offline`. For intended MVP
operation, omit `--offline` and use Snowflake credentials.

