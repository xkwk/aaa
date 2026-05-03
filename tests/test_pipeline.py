from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuarial_copilot.config import ProjectPaths
from actuarial_copilot.pipeline import run_pipeline


class PipelineTests(unittest.TestCase):
    def test_full_pipeline_offline_generates_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "raw" / "sharepoint" / "sample"
            source.mkdir(parents=True)
            (source / "valuation_results.csv").write_text(
                "valuation_period,run_id,product,portfolio,cohort,measure,amount,currency\n"
                "2025Q4,r1,A,P,2020,BEL,100,AUD\n"
                "2026Q1,r1,A,P,2020,BEL,130,AUD\n",
                encoding="utf-8",
            )
            (source / "valuation_bridge.csv").write_text(
                "from_period,to_period,run_id,product,portfolio,measure,driver,amount\n"
                "2025Q4,2026Q1,r1,A,P,BEL,Expected unwind,10\n"
                "2025Q4,2026Q1,r1,A,P,BEL,Experience,20\n",
                encoding="utf-8",
            )
            (source / "note.md").write_text("# Note\n\nMasked support note.\n", encoding="utf-8")

            summary = run_pipeline(source, "r1", offline=True, paths=ProjectPaths(root))

            self.assertEqual(summary.validation_status, "PASS")
            self.assertTrue((root / "runs" / "r1" / "memo.md").exists())
            self.assertTrue((root / "wiki" / "sources" / "r1").exists())
            self.assertTrue((root / "converted" / "r1").exists())


if __name__ == "__main__":
    unittest.main()

