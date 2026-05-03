---
name: streamlit-dashboard
description: Use when updating or checking the Streamlit in Snowflake valuation movement dashboard artifact.
---

# Streamlit Dashboard Skill

Use this workflow after analysis outputs exist.

1. Confirm `streamlit/app.py` reads from Snowflake APP/RUNS outputs.
2. Confirm `runs/<run_id>/dashboard_summary.csv` exists for local inspection.
3. Keep the dashboard as an output/review artifact.
4. Do not add a separate orchestration UI.

