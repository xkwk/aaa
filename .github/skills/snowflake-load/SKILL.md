---
name: snowflake-load
description: Use when loading valuation result and bridge files into Snowflake dev schemas.
---

# Snowflake Load Skill

Use this workflow after document intake has created a manifest.

1. Confirm the manifest has one valuation result file and one bridge file.
2. Run `act load --run-id <run_id>` for normal MVP operation.
3. If Snowflake credentials are unavailable and the user is doing a smoke test,
   run `act load --run-id <run_id> --offline`.
4. Review `runs/<run_id>/load_summary.json`.
5. Hand off to `valuation-movement-analysis`.

Do not write SQL ad hoc in chat unless fixing the internal tool.

