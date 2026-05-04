from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuarial_copilot.tools.convert import convert_documents
from actuarial_copilot.tools.profile import profile_source_package


class ConvertProfileTests(unittest.TestCase):
    def test_convert_documents_creates_markdown_previews(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            (source / "note.md").write_text("# Note\n\nText.", encoding="utf-8")
            (source / "data.csv").write_text("period,amount\n2026Q1,10\n", encoding="utf-8")

            result = convert_documents(str(source), output_dir=str(root / "converted"))

            self.assertEqual(len(result["files"]), 2)
            for item in result["files"]:
                self.assertTrue(Path(item["markdown_path"]).exists())

    def test_profile_source_package_profiles_csv_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            source.mkdir()
            (source / "capital.csv").write_text(
                "period,scenario,capital_required\n2026Q1,Base,100\n",
                encoding="utf-8",
            )

            result = profile_source_package(str(source))

            self.assertEqual(len(result["files"]), 1)
            self.assertEqual(result["files"][0]["kind"], "tabular")
            column_names = {column["name"] for column in result["files"][0]["columns"]}
            self.assertIn("capital_required", column_names)


if __name__ == "__main__":
    unittest.main()

