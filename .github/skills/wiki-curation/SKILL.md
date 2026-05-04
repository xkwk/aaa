---
name: wiki-curation
description: Use when ingesting source material into the persistent wiki, answering from wiki memory, filing durable synthesis, or linting wiki health.
---

# Wiki Curation Skill

Use the wiki as durable agent memory. The LLM owns synthesis and maintenance;
Python tools only read, write, search, convert, or profile evidence.

## Always

1. Read `wiki/schema.md` and `wiki/index.md` before structural edits.
2. Use `read_wiki` and `search_wiki` before adding duplicate content.
3. Keep raw source files immutable.
4. Ground claims in source pages, raw paths, tool results, or user feedback.
5. Mark uncertainty as questions, not confident prose.

## Ingest

1. Use `profile_source_package` or `convert_documents` only when evidence is
   needed.
2. Create or update `sources/` pages with summary, key facts, limitations, and
   raw source links.
3. Update affected concept, method, model, metric, decision, or question pages.
4. Note contradictions, gaps, and stale claims in `questions/`.
5. Update `wiki/index.md` with one-line catalog entries.
6. Append a parseable `wiki/log.md` entry.

## Query

1. Read `wiki/index.md`, then search/read relevant pages.
2. Answer from wiki evidence and cite the pages used.
3. If the answer creates durable synthesis, write or update a wiki page.
4. Log wiki-changing queries.

## Lint

Check for missing index entries, orphan pages, repeated concepts without pages,
contradictions, stale claims, source pages without limitations, and unresolved
questions that need follow-up.
