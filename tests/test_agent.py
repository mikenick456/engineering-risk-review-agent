import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from tools import review_application  # noqa: E402


class EngineeringRiskReviewTests(unittest.TestCase):
    def test_normal_application_matches_golden_case(self):
        result = review_application("EG-2026-0001")

        self.assertEqual(result["apply_no"], "EG-2026-0001")
        self.assertEqual(result["risk_level"], "low")
        self.assertFalse(result["blocked"])
        self.assertEqual(result["findings"], [])

    def test_high_risk_application_matches_golden_case(self):
        result = review_application("EG-2026-0002")

        self.assertEqual(result["risk_level"], "high")
        self.assertTrue(result["blocked"])
        self.assertIn("allocation_total_not_100", result["findings"])
        self.assertIn("overdue_receipt", result["findings"])

    def test_unknown_application_returns_not_found(self):
        result = review_application("EG-2099-9999")

        self.assertEqual(result["risk_level"], "high")
        self.assertTrue(result["blocked"])
        self.assertIn("application_not_found", result["findings"])


if __name__ == "__main__":
    unittest.main()
