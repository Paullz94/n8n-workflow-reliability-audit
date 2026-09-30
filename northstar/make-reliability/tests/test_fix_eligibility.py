import unittest

import fix_eligibility


class FixEligibilityTests(unittest.TestCase):
    def test_runtime_issue_rejected_without_observable_sandbox(self):
        r=fix_eligibility.assess_fix_eligibility(
            rule="retrying-write-idempotency-review",
            safe_test_environment=True,
            pcflows_can_observe_runtime=False,
            external_side_effect_observable=True,
            acceptance_criteria_defined=True,
        )
        self.assertFalse(r["eligible_for_verified_repair"])
        self.assertIn("pcflows_can_observe_runtime",r["missing"])

    def test_runtime_issue_eligible_when_all_proof_prerequisites_exist(self):
        r=fix_eligibility.assess_fix_eligibility(
            rule="retrying-write-idempotency-review",
            safe_test_environment=True,
            pcflows_can_observe_runtime=True,
            external_side_effect_observable=True,
            acceptance_criteria_defined=True,
        )
        self.assertTrue(r["eligible_for_verified_repair"])

    def test_static_secret_cleanup_can_be_verified_without_runtime(self):
        r=fix_eligibility.assess_fix_eligibility(
            rule="possible-secret-in-blueprint",
            safe_test_environment=False,
            pcflows_can_observe_runtime=False,
            external_side_effect_observable=False,
            acceptance_criteria_defined=False,
        )
        self.assertTrue(r["eligible_for_verified_repair"])


if __name__=="__main__":
    unittest.main()
