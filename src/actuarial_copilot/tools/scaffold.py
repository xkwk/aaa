from __future__ import annotations

from pathlib import Path
import re

from .common import ensure_dir


def scaffold_python_tool(name: str, purpose: str, tools_dir: str = "src/actuarial_copilot/tools", tests_dir: str = "tests") -> dict:
    """Create a draft Python capability tool and focused test scaffold."""
    identifier = tool_identifier(name)
    tool_path = Path(tools_dir).resolve() / f"{identifier}.py"
    test_path = Path(tests_dir).resolve() / f"test_tool_{identifier}.py"
    ensure_dir(tool_path.parent)
    ensure_dir(test_path.parent)
    if not tool_path.exists():
        tool_path.write_text(tool_template(identifier, purpose), encoding="utf-8")
    if not test_path.exists():
        test_path.write_text(test_template(identifier), encoding="utf-8")
    return {"tool": str(tool_path), "test": str(test_path), "status": "draft_scaffolded"}


def tool_identifier(value: str) -> str:
    identifier = re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_").lower()
    if not identifier:
        identifier = "new_tool"
    if identifier[0].isdigit():
        identifier = f"tool_{identifier}"
    return identifier


def tool_template(identifier: str, purpose: str) -> str:
    return f'''"""Draft capability tool: {identifier}.

Purpose: {purpose}

The LLM agent decides when this tool is useful. This module should only perform
bounded execution and return structured evidence/results.
"""


def run(**kwargs) -> dict:
    return {{
        "tool": "{identifier}",
        "status": "draft",
        "inputs": kwargs,
        "message": "Implement bounded capability logic here.",
    }}
'''


def test_template(identifier: str) -> str:
    return f'''from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuarial_copilot.tools.{identifier} import run


class {''.join(part.title() for part in identifier.split('_'))}ToolTests(unittest.TestCase):
    def test_draft_tool_returns_structured_result(self):
        result = run(sample=True)

        self.assertEqual(result["tool"], "{identifier}")
        self.assertIn("status", result)


if __name__ == "__main__":
    unittest.main()
'''

