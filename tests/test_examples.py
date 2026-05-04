from pathlib import Path
import unittest


class ExampleTests(unittest.TestCase):
    def test_examples_are_reference_material(self):
        root = Path(__file__).resolve().parents[1]

        valuation = root / "examples" / "valuation_movement" / "README.md"
        assumption = root / "examples" / "assumption_review" / "README.md"

        self.assertTrue(valuation.exists())
        self.assertTrue(assumption.exists())
        self.assertIn("Reference material only", valuation.read_text(encoding="utf-8"))
        self.assertIn("Reference material only", assumption.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

