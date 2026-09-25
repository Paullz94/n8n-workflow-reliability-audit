import unittest

import qualify_audit


class QualificationTests(unittest.TestCase):
    def context(self):
        return {
            "scenario_name": "Orders",
            "business_goal": "Process each order reliably",
        }

    def test_secret_requires_resanitization(self):
        result = qualify_audit.qualify({
            "flow": [{
                "id": 1,
                "module": "http:ActionSendData",
                "mapper": {"headers": "Bearer abcdefghijklmnopqrstuvwxyz123456"},
            }]
        }, self.context())
        self.assertEqual(result["route"], "resanitize_required")

    def test_invalid_blueprint_is_rejected(self):
        result = qualify_audit.qualify({"name": "not a blueprint"}, self.context())
        self.assertEqual(result["route"], "invalid_input")

    def test_missing_context_does_not_sell_paid_audit(self):
        result = qualify_audit.qualify({
            "flow": [{"id": 1, "module": "crm:updateContact", "mapper": {}}]
        }, {})
        self.assertEqual(result["route"], "context_required")
        self.assertFalse(result["paid_candidate"])

    def test_high_value_write_risk_is_paid_candidate(self):
        result = qualify_audit.qualify({
            "flow": [{"id": 1, "module": "crm:updateContact", "mapper": {}}]
        }, self.context())
        self.assertEqual(result["route"], "paid_audit_candidate")
        self.assertTrue(result["paid_candidate"])

    def test_clean_read_only_flow_stays_free(self):
        result = qualify_audit.qualify({
            "flow": [{"id": 1, "module": "json:ParseJSON", "mapper": {}}]
        }, self.context())
        self.assertEqual(result["route"], "free_preflight_sufficient")
        self.assertFalse(result["paid_candidate"])

    def test_business_critical_context_can_justify_review(self):
        context = self.context()
        context["critical_side_effects"] = ["Trigger customer-facing approval decision"]
        result = qualify_audit.qualify({
            "flow": [{"id": 1, "module": "json:ParseJSON", "mapper": {}}]
        }, context)
        self.assertEqual(result["route"], "paid_audit_candidate")


if __name__ == "__main__":
    unittest.main()
