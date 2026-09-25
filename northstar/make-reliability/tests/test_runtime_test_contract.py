import unittest
import runtime_test_contract


class RuntimeTestContractTests(unittest.TestCase):
    def test_duplicate_replay_requires_same_business_key_and_one_effect(self):
        first={"business_key":"ORDER-1","side_effect_ids":["inv_123"],"side_effect_count":1}
        second={"business_key":"ORDER-1","side_effect_ids":["inv_123"],"side_effect_count":1}
        r=runtime_test_contract.assert_duplicate_replay(first,second)
        self.assertTrue(r["intended_side_effect_count_one"])

    def test_duplicate_replay_fails_for_two_effect_ids(self):
        first={"business_key":"ORDER-1","side_effect_ids":["inv_123"],"side_effect_count":1}
        second={"business_key":"ORDER-1","side_effect_ids":["inv_456"],"side_effect_count":2}
        r=runtime_test_contract.assert_duplicate_replay(first,second)
        self.assertFalse(r["intended_side_effect_count_one"])

    def test_partial_payment_must_not_mark_fully_paid(self):
        r=runtime_test_contract.assert_partial_payment({
            "invoice_total":2000,
            "paid_amount":500,
            "marked_fully_paid":False,
        })
        self.assertTrue(r["partial_payment_tested"])
        self.assertTrue(r["not_marked_fully_paid"])

    def test_ai_invalid_output_requires_no_write(self):
        r=runtime_test_contract.assert_invalid_ai_output({
            "invalid_input_rejected":True,
            "write_performed":False,
        })
        self.assertTrue(r["invalid_input_rejected"])
        self.assertTrue(r["unsafe_write_prevented"])

    def test_onboarding_requires_no_missing_resources(self):
        r=runtime_test_contract.assert_required_onboarding_resources({
            "required_resources":["crm","project","folder"],
            "missing_required_resources":[],
        })
        self.assertTrue(r["missing_required_resources_zero"])

    def test_unknown_sensitive_fields_are_dropped(self):
        r=runtime_test_contract.sanitize_result({
            "business_key":"A",
            "customer_email":"secret@example.com",
            "api_key":"secret",
        })
        self.assertNotIn("customer_email",r)
        self.assertNotIn("api_key",r)


if __name__=="__main__":
    unittest.main()
