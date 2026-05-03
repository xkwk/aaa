from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from actuarial_copilot.analysis import analyze_run
from actuarial_copilot.config import ProjectPaths
from actuarial_copilot.filesystem import ensure_dir, write_csv


class AnalysisTests(unittest.TestCase):
    def test_analyze_reconciled_bridge_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            loaded = ensure_dir(root / "runs" / "r1" / "loaded")
            write_csv(
                loaded / "valuation_results.csv",
                [
                    {"valuation_period": "2025Q4", "run_id": "r1", "product": "A", "portfolio": "P", "cohort": "2020", "measure": "BEL", "amount": "100", "currency": "AUD"},
                    {"valuation_period": "2026Q1", "run_id": "r1", "product": "A", "portfolio": "P", "cohort": "2020", "measure": "BEL", "amount": "130", "currency": "AUD"},
                ],
                ["valuation_period", "run_id", "product", "portfolio", "cohort", "measure", "amount", "currency"],
            )
            write_csv(
                loaded / "valuation_bridge.csv",
                [
                    {"from_period": "2025Q4", "to_period": "2026Q1", "run_id": "r1", "product": "A", "portfolio": "P", "measure": "BEL", "driver": "Expected unwind", "amount": "10"},
                    {"from_period": "2025Q4", "to_period": "2026Q1", "run_id": "r1", "product": "A", "portfolio": "P", "measure": "BEL", "driver": "Experience", "amount": "20"},
                ],
                ["from_period", "to_period", "run_id", "product", "portfolio", "measure", "driver", "amount"],
            )

            summary = analyze_run("r1", offline=True, paths=ProjectPaths(root))

            self.assertEqual(summary.validation_status, "PASS")
            self.assertEqual(summary.total_unreconciled, "0")

    def test_analyze_unreconciled_bridge_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            loaded = ensure_dir(root / "runs" / "r1" / "loaded")
            write_csv(
                loaded / "valuation_results.csv",
                [
                    {"valuation_period": "2025Q4", "run_id": "r1", "product": "A", "portfolio": "P", "cohort": "2020", "measure": "BEL", "amount": "100", "currency": "AUD"},
                    {"valuation_period": "2026Q1", "run_id": "r1", "product": "A", "portfolio": "P", "cohort": "2020", "measure": "BEL", "amount": "130", "currency": "AUD"},
                ],
                ["valuation_period", "run_id", "product", "portfolio", "cohort", "measure", "amount", "currency"],
            )
            write_csv(
                loaded / "valuation_bridge.csv",
                [
                    {"from_period": "2025Q4", "to_period": "2026Q1", "run_id": "r1", "product": "A", "portfolio": "P", "measure": "BEL", "driver": "Expected unwind", "amount": "10"},
                ],
                ["from_period", "to_period", "run_id", "product", "portfolio", "measure", "driver", "amount"],
            )

            summary = analyze_run("r1", offline=True, paths=ProjectPaths(root))

            self.assertEqual(summary.validation_status, "FAIL")
            self.assertEqual(summary.total_unreconciled, "20")


if __name__ == "__main__":
    unittest.main()

