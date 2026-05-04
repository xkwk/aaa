from pathlib import Path
import importlib.util
import os
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuarial_copilot.tools.snowflake import inspect_snowflake, propose_snowflake_objects


class SnowflakeMcpDocsTests(unittest.TestCase):
    def setUp(self):
        self.original_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_snowflake_externalbrowser_default(self):
        os.environ["ACT_SNOWFLAKE_ACCOUNT"] = "acct"
        os.environ["ACT_SNOWFLAKE_USER"] = "user@example.com"
        os.environ.pop("ACT_SNOWFLAKE_AUTHENTICATOR", None)
        os.environ.pop("ACT_SNOWFLAKE_PASSWORD", None)

        result = inspect_snowflake()

        self.assertEqual(result["authenticator"], "externalbrowser")
        self.assertTrue(result["is_configured"])
        self.assertEqual(result["password"], "")

    def test_propose_snowflake_objects_is_draft_only(self):
        result = propose_snowflake_objects("capital analysis", {"files": [{"kind": "tabular"}]})

        self.assertEqual(result["objects"]["raw"], "RAW.CAPITAL_ANALYSIS_SOURCE")
        self.assertIn("draft", " ".join(result["notes"]).lower())

    def test_mcp_tool_list_is_available_without_mcp_dependency(self):
        server_path = Path(__file__).resolve().parents[1] / "mcp" / "server.py"
        spec = importlib.util.spec_from_file_location("actuarial_mcp_server", server_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        self.assertIn("profile_source_package", module.TOOL_NAMES)
        self.assertIn("record_feedback", module.TOOL_NAMES)

    def test_public_docs_do_not_center_cli_or_fixed_flows(self):
        root = Path(__file__).resolve().parents[1]
        public_files = [root / "README.md", root / ".github" / "copilot-instructions.md"]
        text = "\n".join(path.read_text(encoding="utf-8") for path in public_files)

        self.assertNotIn("act decide", text)
        self.assertNotIn("run-extension", text)
        self.assertNotIn("workflow", text.lower())


if __name__ == "__main__":
    unittest.main()
