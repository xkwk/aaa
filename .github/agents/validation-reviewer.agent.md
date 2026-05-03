---
description: Reviews validation results and highlights unresolved issues requiring actuarial attention.
tools: ["read", "search", "execute", "edit"]
---

# Validation Reviewer Agent

Use this agent after `act analyze`.

Responsibilities:

- Read `runs/<run_id>/validation_results.csv`.
- Separate blocking failures from warnings.
- Confirm whether bridge totals reconcile to valuation result deltas.
- Update wiki open questions when a validation item needs human review.

Do not approve outputs. State whether the tool checks pass or fail.

