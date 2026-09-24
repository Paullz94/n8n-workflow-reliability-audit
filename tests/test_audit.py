import json
import unittest
from pathlib import Path

from audit import audit_workflow, render_markdown


ROOT = Path(__file__).resolve().parents[1]


class PublicPortfolioTests(unittest.TestCase):
    def load(self, name: str):
        return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))

    def test_seeded_secret_is_reported_but_never_rendered(self):
        result = audit_workflow(self.load("unsafe_order_intake.json"))
        self.assertIn("SEC-003", {item["rule_id"] for item in result["findings"]})
        self.assertNotIn("DEMO_ONLY_NOT_A_REAL_SECRET", render_markdown(result))

    def test_hardened_counterpart_has_no_critical_or_high_findings(self):
        result = audit_workflow(self.load("hardened_order_intake.json"))
        self.assertEqual(result["summary"]["critical"], 0)
        self.assertEqual(result["summary"]["high"], 0)

    def test_scheduled_sync_flags_recovery_and_idempotency(self):
        result = audit_workflow(self.load("unsafe_scheduled_sync.json"))
        rules = {item["rule_id"] for item in result["findings"]}
        self.assertTrue({"RECOVERY-001", "RECOVERY-002", "RECOVERY-003", "DATA-001"}.issubset(rules))

    def test_duplicate_names_are_rejected(self):
        result = audit_workflow(self.load("unsafe_duplicate_nodes.json"))
        self.assertIn("STRUCT-002", {item["rule_id"] for item in result["findings"]})


if __name__ == "__main__":
    unittest.main()
