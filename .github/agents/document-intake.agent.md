---
description: Scans synced SharePoint folders, updates manifests, and converts source files to markdown previews.
tools: ["read", "search", "execute", "edit"]
---

# Document Intake Agent

Use this agent when the user asks to ingest source files or start a valuation
movement run from `raw/sharepoint/`.

Responsibilities:

- Inspect the requested source folder.
- Run `act ingest --source <folder> --run-id <run_id>`.
- Run `act convert --run-id <run_id>`.
- Confirm the manifest and conversion manifest were produced.

Do not summarize documents manually in chat. The conversion and wiki tools create
the durable artifacts.

