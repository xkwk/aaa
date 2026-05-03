from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuarial_copilot.config import ProjectPaths
from actuarial_copilot.ingestion import scan_source


class IngestionTests(unittest.TestCase):
    def test_scan_source_detects_roles_and_writes_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "raw" / "sharepoint" / "run"
            source.mkdir(parents=True)
            (source / "valuation_results.csv").write_text("valuation_period,run_id,product,portfolio,cohort,measure,amount,currency\n", encoding="utf-8")
            (source / "valuation_bridge.csv").write_text("from_period,to_period,run_id,product,portfolio,measure,driver,amount\n", encoding="utf-8")

            entries = scan_source(source, "r1", ProjectPaths(root))

            self.assertEqual({entry.role for entry in entries}, {"valuation_results", "valuation_bridge"})
            self.assertTrue((root / "runs" / "r1" / "manifest.csv").exists())
            self.assertTrue((root / "runs" / "r1" / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()

