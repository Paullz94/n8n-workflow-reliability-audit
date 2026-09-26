import unittest

import autonomous_lifecycle


class AutonomousLifecycleTests(unittest.TestCase):
    def test_high_fit_allowed_lead_is_autonomous(self):
        d = autonomous_lifecycle.decide({
            "state":"lead_discovered",
            "channel_allowed":True,
            "offer_fit":True,
        })
        self.assertTrue(d.autonomous)
        self.assertEqual(d.next_state, "outreach_sent")

    def test_research_only_channel_does_not_outreach(self):
        d = autonomous_lifecycle.decide({
            "state":"lead_discovered",
            "channel_allowed":False,
            "offer_fit":True,
        })
        self.assertTrue(d.autonomous)
        self.assertEqual(d.action, "archive_research_only")

    def test_verified_external_payment_enters_fulfillment(self):
        d = autonomous_lifecycle.decide({
            "state":"payment_detected",
            "provider_verified":True,
            "owner_or_test":False,
        })
        self.assertTrue(d.autonomous)
        self.assertEqual(d.next_state, "awaiting_files")

    def test_secret_hard_stops_autonomously(self):
        d = autonomous_lifecycle.decide({
            "state":"files_received",
            "secret_like":True,
            "scope_fit":True,
        })
        self.assertTrue(d.autonomous)
        self.assertEqual(d.action, "stop_and_request_resanitization")

    def test_personal_data_hard_stops_autonomously(self):
        d = autonomous_lifecycle.decide({
            "state":"files_received",
            "personal_data_like":True,
            "scope_fit":True,
        })
        self.assertEqual(d.next_state,"awaiting_safe_input")

    def test_cross_case_mismatch_freezes_case(self):
        d = autonomous_lifecycle.decide({
            "state":"files_received",
            "cross_case_mismatch":True,
            "scope_fit":True,
        })
        self.assertEqual(d.next_state,"privacy_hold")

    def test_verified_repair_cannot_start_before_public_gate(self):
        d = autonomous_lifecycle.decide({
            "state":"verified_repair_requested",
            "verified_repair_public_enabled":False,
            "repair_eligible":True,
        })
        self.assertEqual(d.next_state,"audit_or_diagnostic")

    def test_unrealistic_repair_never_opens_contract(self):
        d = autonomous_lifecycle.decide({
            "state":"verified_repair_requested",
            "verified_repair_public_enabled":True,
            "repair_eligible":False,
        })
        self.assertEqual(d.next_state,"audit_or_diagnostic")

    def test_policy_refund_is_autonomous(self):
        d = autonomous_lifecycle.decide({
            "state":"refund_requested",
            "refund_reason":"duplicate_charge",
        })
        self.assertTrue(d.autonomous)
        self.assertEqual(d.next_state, "refunded")

    def test_ambiguous_refund_requires_exception_review(self):
        d = autonomous_lifecycle.decide({
            "state":"refund_requested",
            "refund_reason":"customer_dislikes_recommendations",
        })
        self.assertFalse(d.autonomous)

    def test_owner_only_prerequisites_remain_owner_only(self):
        for gate in autonomous_lifecycle.OWNER_ONLY_GATES:
            with self.subTest(gate=gate):
                d=autonomous_lifecycle.decide({"state":"blocked","blocked_by":gate})
                self.assertFalse(d.autonomous)


if __name__ == "__main__":
    unittest.main()
