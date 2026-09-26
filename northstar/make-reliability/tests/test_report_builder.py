import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import audit_make
import report_builder


class ReportBuilderTests(unittest.TestCase):
    def test_context_is_allowlisted_and_bounded(self):
        raw = {
            "scenario_name": "Orders",
            "business_goal": "x" * 900,
            "api_key": "do-not-copy",
            "critical_side_effects": ["Create invoice", "Send email"],
            "ordering_required": True,
        }
        clean = report_builder.sanitize_context(raw)
        self.assertNotIn("api_key", clean)
        self.assertEqual(len(clean["business_goal"]), 500)
        self.assertTrue(clean["ordering_required"])

    def test_retry_is_prevent_with_action_and_verification(self):
        bp = {"flow": [{
            "id": 1,
            "module": "crm:updateContact",
            "mapper": {},
            "onerror": [{"id": 2, "module": "builtin:Break", "mapper": {"retry": True}}],
        }]}
        findings = audit_make.scan_blueprint(bp)
        report = report_builder.render_report("demo.json", findings, {"duplicate_tolerance": "none"})
        self.assertIn("retrying-write-idempotency-review", report.lower())
        self.assertIn("idempotency", report.lower())
        self.assertIn("Verification", report)

    def test_report_does_not_echo_mapper_values(self):
        secret_business_value = "CUSTOMER-PRIVATE-REF-778899"
        bp = {"flow": [{
            "id": 1,
            "module": "crm:updateContact",
            "mapper": {"reference": secret_business_value},
        }]}
        findings = audit_make.scan_blueprint(bp)
        report = report_builder.render_report("demo.json", findings, {})
        self.assertNotIn(secret_business_value, report)

    def test_ordering_context_increases_concurrency_priority(self):
        f = audit_make.Finding("concurrency-review", "medium", "review")
        without = report_builder.priority_score(f, {})
        with_ordering = report_builder.priority_score(f, {"ordering_required": True})
        self.assertGreater(with_ordering, without)

    def test_pillars_are_present(self):
        bp = {
            "flow": [{"id": 1, "module": "crm:updateContact", "mapper": {}}],
            "metadata": {"scenario": {"sequential": False, "dlq": False, "confidential": True}},
        }
        findings = audit_make.scan_blueprint(bp)
        report = report_builder.render_report("demo.json", findings, {})
        self.assertIn("PREVENT", report)
        self.assertIn("DETECT", report)
        self.assertIn("RECOVER", report)

    def test_official_make_reference_is_included_when_available(self):
        finding = audit_make.Finding(
            "write-skip-handler-data-loss-review",
            "high",
            "Skip handler review",
            1,
            "crm:updateContact",
            "flow[0]",
        )
        report = report_builder.render_report("demo.json", [finding], {"scenario_name": "Demo"})
        self.assertIn("https://help.make.com/skip-error-handler", report)


if __name__ == "__main__":
    unittest.main()
