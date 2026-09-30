import unittest

import audit_make
import vertical_packs


class VerticalPackTests(unittest.TestCase):
    def findings(self):
        return audit_make.scan_blueprint({
            "flow": [
                {"id": 1, "module": "crm:createContact", "mapper": {}},
                {"id": 2, "module": "http:ActionSendData", "mapper": {"method": "POST"}},
            ],
            "metadata": {"instant": True, "scenario": {"sequential": False, "dlq": False}},
        })

    def test_all_priority_packs_exist(self):
        self.assertEqual(
            set(vertical_packs.PACKS),
            {"lead_flow", "invoice_payment", "ai_guardrails", "client_onboarding"},
        )

    def test_lead_pack_contains_duplicate_and_handoff_tests(self):
        plan = vertical_packs.build_pack_plan("lead_flow", self.findings(), {"scenario_name":"Lead intake"})
        ids = {x["id"] for x in plan["acceptance_tests"]}
        self.assertIn("lead_duplicate_replay", ids)
        self.assertIn("lead_followup_stop", ids)

    def test_invoice_pack_contains_partial_payment_test(self):
        plan = vertical_packs.build_pack_plan("invoice_payment", self.findings(), {"scenario_name":"Billing"})
        ids = {x["id"] for x in plan["acceptance_tests"]}
        self.assertIn("payment_partial", ids)
        self.assertIn("customer_match_collision", ids)

    def test_ai_pack_requires_malformed_output_and_handoff_tests(self):
        plan = vertical_packs.build_pack_plan("ai_guardrails", self.findings(), {"scenario_name":"AI triage"})
        ids = {x["id"] for x in plan["acceptance_tests"]}
        self.assertIn("ai_malformed_output", ids)
        self.assertIn("ai_human_handoff", ids)

    def test_onboarding_pack_contains_partial_and_handoff_tests(self):
        plan = vertical_packs.build_pack_plan("client_onboarding", self.findings(), {"scenario_name":"Client onboarding"})
        ids = {x["id"] for x in plan["acceptance_tests"]}
        self.assertIn("onboarding_partial_failure", ids)
        self.assertIn("onboarding_handoff", ids)

    def test_unknown_pack_rejected(self):
        with self.assertRaises(ValueError):
            vertical_packs.get_pack("anything")


if __name__ == "__main__":
    unittest.main()
