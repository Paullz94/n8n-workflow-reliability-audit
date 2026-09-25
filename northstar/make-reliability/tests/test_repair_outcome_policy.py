import unittest
import repair_outcome_policy


class RepairOutcomePolicyTests(unittest.TestCase):
    def test_success_requires_every_issue_verified(self):
        r=repair_outcome_policy.decide_repair_outcome({
            "accepted_as_verified_repair":True,
            "all_issues_closed_verified":True,
        })
        self.assertEqual(r["outcome"],"verified_success")
        self.assertTrue(r["customer_complete"])
        self.assertFalse(r["refund_required"])

    def test_unfixed_at_bounded_deadline_requires_refund(self):
        r=repair_outcome_policy.decide_repair_outcome({
            "accepted_as_verified_repair":True,
            "all_issues_closed_verified":False,
            "delivery_window_exhausted":True,
        })
        self.assertEqual(r["outcome"],"verified_fix_not_achieved")
        self.assertTrue(r["refund_required"])
        self.assertFalse(r["customer_complete"])

    def test_open_case_never_claims_complete(self):
        r=repair_outcome_policy.decide_repair_outcome({
            "accepted_as_verified_repair":True,
            "all_issues_closed_verified":False,
        })
        self.assertEqual(r["outcome"],"repair_in_progress")
        self.assertFalse(r["customer_complete"])

    def test_rollback_failure_is_critical_and_refundable(self):
        r=repair_outcome_policy.decide_repair_outcome({
            "accepted_as_verified_repair":True,
            "critical_rollback_failure":True,
        })
        self.assertEqual(r["outcome"],"critical_incident_escalation")
        self.assertTrue(r["refund_required"])

    def test_customer_revoked_access_does_not_falsely_complete(self):
        r=repair_outcome_policy.decide_repair_outcome({
            "accepted_as_verified_repair":True,
            "customer_access_revoked":True,
        })
        self.assertEqual(r["outcome"],"blocked_by_customer_access")
        self.assertFalse(r["customer_complete"])


if __name__=="__main__":
    unittest.main()
