import unittest

import pack_selector


class PackSelectorTests(unittest.TestCase):
    def test_selects_lead_flow(self):
        r=pack_selector.select_pack({
            "scenario_name":"Facebook leads to CRM",
            "business_goal":"Route every lead to one sales owner and stop follow-up after booking",
        })
        self.assertEqual(r["pack_id"], "lead_flow")

    def test_selects_invoice_payment(self):
        r=pack_selector.select_pack({
            "scenario_name":"Stripe QuickBooks sync",
            "business_goal":"Keep invoice balance and payment state correct",
        })
        self.assertEqual(r["pack_id"], "invoice_payment")

    def test_selects_ai_guardrails(self):
        r=pack_selector.select_pack({
            "scenario_name":"OpenAI document classification",
            "business_goal":"Require human approval before AI output updates CRM",
        })
        self.assertEqual(r["pack_id"], "ai_guardrails")

    def test_selects_client_onboarding(self):
        r=pack_selector.select_pack({
            "scenario_name":"New customer onboarding",
            "business_goal":"Create project setup and welcome resources exactly once before kickoff",
        })
        self.assertEqual(r["pack_id"], "client_onboarding")

    def test_unknown_context_stays_generic(self):
        r=pack_selector.select_pack({
            "scenario_name":"Daily operations",
            "business_goal":"Move business records reliably",
        })
        self.assertIsNone(r["pack_id"])
        self.assertEqual(r["route"], "generic_data_integrity")

    def test_tie_does_not_guess(self):
        r=pack_selector.select_pack({
            "scenario_name":"AI invoice classifier",
            "business_goal":"AI extracts invoice data for payment",
        })
        self.assertEqual(r["route"], "generic_data_integrity")


if __name__ == "__main__":
    unittest.main()
