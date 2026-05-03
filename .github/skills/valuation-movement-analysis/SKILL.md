---
name: valuation-movement-analysis
description: Use when reconciling valuation movement bridge files to prior/current valuation results.
---

# Valuation Movement Analysis Skill

Use this workflow after load.

1. Run `act analyze --run-id <run_id>`.
2. Read `runs/<run_id>/analysis_summary.json`.
3. Read `runs/<run_id>/validation_results.csv`.
4. If validation fails, report the failed checks and affected dimensions.
5. If validation passes, hand off to dashboard and memo skills.

Do not infer movement drivers from snapshots. V1 drivers come from the provided
bridge file.

