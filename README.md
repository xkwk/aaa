# VS Code Copilot Valuation Movement Workbench

This MVP is built so GitHub Copilot in VS Code is the only user-facing control
surface. Users ask Copilot to run a valuation movement workflow; Copilot uses
workspace agents, skills, and deterministic Python tools to do the work.

## MVP workflow

```text
raw/sharepoint/<run folder>
  -> act ingest
  -> act convert
  -> act load
  -> act analyze
  -> wiki updates
  -> act memo
  -> Streamlit in Snowflake dashboard tables
```

The LLM coordinates and drafts. Python and Snowflake perform calculations and
data handling.

## First Copilot prompt

Open this workspace in VS Code and ask Copilot:

```text
Run valuation movement for sample_2026q1 from raw/sharepoint/sample_2026q1.
Use the project skills and internal act CLI. Do not calculate movement amounts in chat.
```

For local smoke tests without Snowflake credentials, Copilot can run:

```bash
PYTHONPATH=src python -m actuarial_copilot.cli run --source raw/sharepoint/sample_2026q1 --run-id sample_2026q1 --offline
```

For the intended Snowflake-backed path, configure the environment variables in
`.env.example` and omit `--offline`.

The default Snowflake login mode is browser SSO:

```bash
export ACT_SNOWFLAKE_AUTHENTICATOR=externalbrowser
export ACT_SNOWFLAKE_ACCOUNT=<company-account>
export ACT_SNOWFLAKE_USER=<your-email>
export ACT_SNOWFLAKE_ROLE=<role>
export ACT_SNOWFLAKE_WAREHOUSE=<warehouse>
```

When Copilot runs the Snowflake-backed path, the Snowflake Python connector will
open the browser login flow. Password auth is only used if
`ACT_SNOWFLAKE_AUTHENTICATOR=snowflake`.

## Required input files

`valuation_results.csv` or `.xlsx`:

```text
valuation_period, run_id, product, portfolio, cohort, measure, amount, currency
```

`valuation_bridge.csv` or `.xlsx`:

```text
from_period, to_period, run_id, product, portfolio, measure, driver, amount
```

Optional supporting documents can be PDF, DOCX, PPTX, XLSX, Markdown, TXT, CSV,
JSON, or HTML. MarkItDown is used when installed; built-in previews are used for
plain text, Markdown, CSV, and simple XLSX files when available.

## Repository map

- `.github/copilot-instructions.md` - always-on Copilot operating rules.
- `.github/agents/` - VS Code Copilot custom agents.
- `.github/skills/` - reusable workflow playbooks.
- `src/actuarial_copilot/` - deterministic tooling Copilot calls.
- `wiki/` - Karpathy-style LLM-maintained markdown wiki seed.
- `raw/sharepoint/` - synced SharePoint/local input folder.
- `converted/` - generated markdown previews.
- `runs/` - run manifests, validation results, memo drafts, and local caches.
- `sql/` - Snowflake bootstrap DDL.
- `streamlit/` - Streamlit in Snowflake app artifact.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
act run --source raw/sharepoint/sample_2026q1 --run-id sample_2026q1 --offline
python -m unittest discover -s tests
```

Install optional integrations as needed:

```bash
python -m pip install -e ".[markitdown,snowflake,mcp,streamlit]"
```
