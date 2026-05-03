# Wiki Schema

This wiki follows the LLM Wiki pattern:

- Raw sources are immutable and live outside the wiki.
- Generated wiki pages are markdown files owned by the LLM workflow.
- `index.md` is the content catalog.
- `log.md` is the chronological operation record.
- Every source-derived page must cite the run id and source path.

## Page types

- `sources/` - source summaries and converted file references.
- `products/` - product and portfolio context.
- `assumptions/` - actuarial and economic assumption notes.
- `models/` - model and process notes.
- `metrics/` - valuation measures and movement drivers.
- `questions/` - open questions requiring human review.

## Rules

- Do not overwrite raw source meaning with unsupported interpretation.
- Mark uncertain statements as open questions.
- Prefer links to generated artifacts under `runs/<run_id>/`.
- Append to `log.md` for each ingest, analysis, lint, and memo operation.

