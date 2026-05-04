from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuarial_copilot.tools.feedback import record_feedback
from actuarial_copilot.tools.scaffold import scaffold_python_tool
from actuarial_copilot.tools.wiki import read_wiki, search_wiki, write_wiki_page


class WikiFeedbackScaffoldTests(unittest.TestCase):
    def test_wiki_read_write_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"

            write_result = write_wiki_page("concepts/mortality.md", "Mortality assumption note.", wiki_dir=str(wiki))
            read_result = read_wiki("concepts/mortality.md", wiki_dir=str(wiki))
            search_result = search_wiki("assumption", wiki_dir=str(wiki))

            self.assertTrue(Path(write_result["path"]).exists())
            self.assertIn("Mortality", read_result["content"])
            self.assertEqual(len(search_result["matches"]), 1)

    def test_scaffold_python_tool_creates_draft_tool_and_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = scaffold_python_tool(
                "capital ratio helper",
                "Calculate reviewed capital ratios after the agent defines the method.",
                tools_dir=str(root / "src" / "actuarial_copilot" / "tools"),
                tests_dir=str(root / "tests"),
            )

            self.assertTrue(Path(result["tool"]).exists())
            self.assertTrue(Path(result["test"]).exists())
            self.assertEqual(result["status"], "draft_scaffolded")

    def test_record_feedback_writes_lesson(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = record_feedback("Prefer source profiling before dashboard design.", topic="dashboard", feedback_dir=str(Path(tmp) / "feedback"))

            self.assertTrue(Path(result["path"]).exists())
            self.assertTrue(Path(result["lessons"]).exists())


if __name__ == "__main__":
    unittest.main()

