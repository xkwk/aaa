# Wiki Schema

This schema tells the LLM how to maintain the wiki as a persistent,
compounding knowledge artifact. Raw sources are evidence. The wiki is the
agent-maintained synthesis layer.

## Core Rules

- Raw source files stay immutable.
- Wiki pages must be grounded in source material, tool results, or explicit user
  feedback.
- Uncertainty belongs in questions, not confident prose.
- The LLM agent maintains meaning; tools only read and write pages.
- Prefer updating existing pages over creating duplicates.
- When new evidence changes prior understanding, update the affected page and
  record the change in `log.md`.
- Claims should cite source pages, raw source paths, tool outputs, or user
  feedback.

## Page Areas

- `sources/`
- `concepts/`
- `methods/`
- `models/`
- `metrics/`
- `questions/`
- `decisions/`
- `lessons/`

## Page Frontmatter

Use concise YAML frontmatter when it helps indexing or review:

```yaml
---
type: source | concept | method | model | metric | question | decision | lesson
status: draft | reviewed | superseded
updated: YYYY-MM-DD
sources:
  - raw/path/or/wiki/page.md
tags: []
---
```

## Page Types

- `sources/`: one page per meaningful source or source package, with summary,
  key facts, limitations, and links to raw files.
- `concepts/`: durable ideas, products, regulations, entities, processes, and
  domain terms that may be reused across tasks.
- `methods/`: analytical approaches, formulas, validation logic, and known
  judgment points.
- `models/`: model inventories, model behavior, assumptions, ownership, and
  known caveats.
- `metrics/`: definitions, units, grain, reconciliation rules, and data quality
  notes.
- `questions/`: unresolved issues, contradictions, stale claims, and requested
  follow-ups.
- `decisions/`: explicit decisions from the user or reviewed project outcomes.
- `lessons/`: durable agent behavior corrections and feedback-derived lessons.

## Index Rules

`index.md` is the content map. Keep it current after every meaningful wiki
change. Each non-core page should have one catalog entry:

```md
- [[concepts/example]] - one-line summary. Sources: 2. Updated: YYYY-MM-DD.
```

Organize entries by page area. If a page is experimental or unresolved, mark it
as draft or question in the summary.

## Log Rules

`log.md` is chronological and append-only except for typo fixes. Use parseable
entries:

```md
## [YYYY-MM-DD] ingest | Short source name
## [YYYY-MM-DD] query | Short question
## [YYYY-MM-DD] lint | Scope
## [YYYY-MM-DD] update | Short change
```

Each entry should list touched pages and unresolved questions when relevant.

## Ingest Operation

When new source material arrives:

1. Read `schema.md`, `index.md`, and recent `log.md` entries.
2. Profile or convert sources only as needed for evidence.
3. Create or update `sources/` pages with raw source links and limitations.
4. Update affected concept, method, model, metric, decision, or question pages.
5. Flag contradictions or unclear evidence in `questions/`.
6. Update `index.md`.
7. Append a parseable `log.md` entry.

## Query Operation

When answering from the wiki:

1. Read `index.md` first, then search/read relevant pages.
2. Answer with citations to wiki pages and source pages.
3. If the answer creates durable synthesis, file it back into the wiki.
4. Append a `log.md` entry when the query changes the wiki.

## Lint Operation

Periodically review wiki health:

- pages missing from `index.md`
- orphan pages with no obvious inbound link
- concepts mentioned repeatedly but lacking pages
- contradictions between pages
- claims that newer sources supersede
- source pages without limitations
- questions that are stale, answered, or missing owners
