import unittest

import build_pack_report


class PackReportTests(unittest.TestCase):
    def base(self):
        return {
            "flow": [{"id": 1, "module": "crm:createContact", "mapper": {}}],
            "metadata": {"instant": True, "scenario": {"sequential": False, "dlq": False}},
        }

    def context(self):
        return {
            "scenario_name": "Demo",
            "business_goal": "Process each event reliably",
            "critical_side_effects": ["Update business system"],
            "duplicate_tolerance": "none",
            "ordering_required": True,
            "recovery_expectation": "Failures remain visible and replayable.",
        }

    def test_lead_report_contains_pack_acceptance_tests(self):
        report = build_pack_report.render_pack_report("lead_flow", "demo.json", self.base(), self.context())
        self.assertIn("Lead Flow Reliability Audit", report)
        self.assertIn("Duplicate lead/contact creation", report)
        self.assertIn("automated follow-up", report.lower())

    def test_invoice_report_contains_partial_payment(self):
        report = build_pack_report.render_pack_report("invoice_payment", "demo.json", self.base(), self.context())
        self.assertIn("Invoice & Payment Sync Audit", report)
        self.assertIn("Partial payment", report)

    def test_ai_report_contains_malformed_output(self):
        report = build_pack_report.render_pack_report("ai_guardrails", "demo.json", self.base(), self.context())
        self.assertIn("AI Workflow Guardrails Audit", report)
        self.assertIn("malformed", report.lower())
        self.assertIn("human", report.lower())

    def test_secret_blocks_pack_report(self):
        bp = {
            "flow": [{"id": 1, "module": "http:ActionSendData",
                      "mapper": {"headers": "Bearer abcdefghijklmnopqrstuvwxyz123456"}}]
        }
        with self.assertRaises(ValueError):
            build_pack_report.render_pack_report("lead_flow", "demo.json", bp, self.context())


if __name__ == "__main__":
    unittest.main()
