---
name: document-conversion
description: Use when ingesting raw SharePoint/local files and creating markdown previews with MarkItDown or built-in fallback converters.
---

# Document Conversion Skill

Use this workflow when the user asks Copilot to ingest documents or start a run.

1. Identify the source folder under `raw/sharepoint/`.
2. Run `act ingest --source <folder> --run-id <run_id>`.
3. Run `act convert --run-id <run_id>`.
4. Inspect `runs/<run_id>/manifest.csv` and `runs/<run_id>/conversion_manifest.csv`.
5. Hand off to `wiki-curation` after conversion succeeds.

Never paste converted document content into chat unless the user asks for a
specific excerpt.

