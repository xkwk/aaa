---
name: wiki-curation
description: Use when maintaining the Karpathy-style markdown wiki from converted source files and run outputs.
---

# Wiki Curation Skill

Use this workflow after conversion or analysis.

1. Run `act wiki --run-id <run_id>`.
2. Check `wiki/index.md` has the run source summaries.
3. Check `wiki/log.md` has an append-only entry.
4. Add open questions only when the source or validation output supports them.

Keep raw files immutable. The wiki is a generated synthesis layer.

