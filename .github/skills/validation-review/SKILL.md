---
name: validation-review
description: Use when reviewing validation outputs and deciding whether the run is ready for actuarial review.
---

# Validation Review Skill

Use this workflow after `act analyze`.

1. Inspect `runs/<run_id>/validation_results.csv`.
2. Treat `FAIL` rows as blocking for memo finalization.
3. Treat `WARN` rows as review items.
4. Update wiki open questions with unresolved issues if needed.
5. Do not approve the run; state the tool status and what needs review.

