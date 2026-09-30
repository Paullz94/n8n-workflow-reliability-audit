import unittest
import incident_containment


class IncidentContainmentTests(unittest.TestCase):
    def test_sensitive_data_is_contained_without_owner_dependency(self):
        r=incident_containment.decide_incident_action({
            "kind":"sensitive_data_detected_pre_delivery"
        })
        self.assertTrue(r["halt_case"])
        self.assertFalse(r["owner_escalation"])
        self.assertFalse(r["outbound_delivery_allowed"])

    def test_cross_case_mismatch_freezes_before_delivery(self):
        r=incident_containment.decide_incident_action({
            "kind":"cross_case_binding_mismatch"
        })
        self.assertEqual(r["action"],"freeze_affected_cases_and_investigate")
        self.assertTrue(r["quarantine_artifacts"])

    def test_confirmed_exposure_requires_owner_after_containment(self):
        r=incident_containment.decide_incident_action({
            "kind":"confirmed_cross_customer_exposure"
        })
        self.assertTrue(r["owner_escalation"])

    def test_unauthorized_write_is_blocked(self):
        r=incident_containment.decide_incident_action({
            "kind":"unauthorized_production_write_attempt"
        })
        self.assertTrue(r["halt_case"])
        self.assertEqual(r["action"],"block_write_and_preserve_audit_trail")

    def test_bad_ai_output_is_discarded_not_delivered(self):
        r=incident_containment.decide_incident_action({
            "kind":"ai_output_policy_violation"
        })
        self.assertFalse(r["outbound_delivery_allowed"])
        self.assertFalse(r["owner_escalation"])


if __name__=="__main__":
    unittest.main()
