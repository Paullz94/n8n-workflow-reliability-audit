import unittest

import verified_repair_intake


class VerifiedRepairIntakeTests(unittest.TestCase):
    def request(self):
        return {
            "requested_outcome":"fix_duplicate_issue",
            "requires_third_party_vendor_change":False,
            "requires_destructive_real_data_test":False,
            "safe_test_environment":True,
            "reproducible_or_observable":True,
            "acceptance_criteria_defined":True,
            "accepted_root_cause_count":1,
            "customer_authorized_target":True,
            "pcflows_can_observe_runtime":True,
            "external_side_effect_observable":True,
        }

    def test_realistic_runtime_issue_can_be_candidate(self):
        r=verified_repair_intake.qualify(
            rule="retrying-write-idempotency-review",
            request=self.request(),
        )
        self.assertTrue(r["verified_repair_eligible"])

    def test_unrealistic_absolute_request_never_reaches_technical_acceptance(self):
        req=self.request()
        req["requested_outcome"]="guarantee_no_future_bugs"
        r=verified_repair_intake.qualify(
            rule="retrying-write-idempotency-review",
            request=req,
        )
        self.assertFalse(r["verified_repair_eligible"])
        self.assertIsNone(r["fix_eligibility"])

    def test_unobservable_external_side_effect_downgrades_to_diagnostic(self):
        req=self.request()
        req["external_side_effect_observable"]=False
        r=verified_repair_intake.qualify(
            rule="retrying-write-idempotency-review",
            request=req,
        )
        self.assertFalse(r["verified_repair_eligible"])
        self.assertEqual(r["route"],"audit_or_diagnostic_only")


if __name__=="__main__":
    unittest.main()
