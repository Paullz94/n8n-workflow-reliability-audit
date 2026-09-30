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

    def test_failure_recovery_requires_explicit_zero_duplicate_count(self):
        r=runtime_test_contract.assert_failure_recovery({
            "failure_injected":True,
            "failure_observable":True,
            "recovery_succeeded":True,
            "side_effect_count":1,
        })
        self.assertFalse(r["duplicate_side_effects_zero"])
        r2=runtime_test_contract.assert_failure_recovery({
            "failure_injected":True,
            "failure_observable":True,
            "recovery_succeeded":True,
            "duplicate_side_effect_count":0,
        })
        self.assertTrue(r2["duplicate_side_effects_zero"])

    def test_skip_visibility_contract(self):
        r=runtime_test_contract.assert_skip_visibility({
            "failure_injected":True,
            "missing_action_observable":True,
            "silent_success_prevented":True,
        })
        self.assertTrue(all(r.values()))

    def test_resume_fallback_contract(self):
        r=runtime_test_contract.assert_resume_fallback({
            "failure_injected":True,
            "fallback_distinguishable":True,
            "false_success_prevented":True,
        })
        self.assertTrue(all(r.values()))

    def test_concurrency_contract(self):
        r=runtime_test_contract.assert_concurrency({
            "concurrent_test_executed":True,
            "final_state_deterministic":True,
            "duplicate_side_effect_count":0,
        })
        self.assertTrue(all(r.values()))

    def test_failed_work_replay_contract(self):
        r=runtime_test_contract.assert_failed_work_replay({
            "failure_injected":True,
            "failed_work_locatable":True,
            "resume_or_replay_succeeded":True,
            "duplicate_side_effect_count":0,
        })
        self.assertTrue(all(r.values()))

    def test_data_loss_contract(self):
        r=runtime_test_contract.assert_data_loss_recovery({
            "failure_injected":True,
            "failed_work_recoverable":True,
            "unintended_data_loss_count":0,
        })
        self.assertTrue(all(r.values()))

    def test_privacy_safe_observability_contract(self):
        r=runtime_test_contract.assert_privacy_safe_observability({
            "failure_injected":True,
            "correlation_available":True,
            "affected_event_identifiable":True,
            "sensitive_payload_exposed":False,
        })
        self.assertTrue(all(r.values()))

    def test_customer_match_contract(self):
        r=runtime_test_contract.assert_customer_match({
            "expected_customer_id":"C-1",
            "matched_customer_id":"C-1",
        })
        self.assertTrue(all(r.values()))

    def test_ambiguous_ai_routes_to_review_without_write(self):
        r=runtime_test_contract.assert_ambiguous_review({
            "ambiguous_input":True,
            "routed_to_review":True,
            "write_performed":False,
        })
        self.assertTrue(all(r.values()))

    def test_concurrent_pair_requires_same_final_state_and_single_effect(self):
        a={"business_key":"L-1","final_state":"owner:A","side_effect_ids":["lead_1"]}
        b={"business_key":"L-1","final_state":"owner:A","side_effect_ids":["lead_1"]}
        r=runtime_test_contract.assert_concurrent_pair(a,b)
        self.assertTrue(r["final_state_deterministic"])
        self.assertTrue(r["duplicate_side_effects_zero"])

    def test_concurrent_pair_rejects_divergent_state(self):
        a={"business_key":"L-1","final_state":"owner:A","side_effect_ids":["lead_1"]}
        b={"business_key":"L-1","final_state":"owner:B","side_effect_ids":["lead_1"]}
        r=runtime_test_contract.assert_concurrent_pair(a,b)
        self.assertFalse(r["final_state_deterministic"])


if __name__=="__main__":
    unittest.main()
