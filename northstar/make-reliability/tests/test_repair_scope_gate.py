import unittest
import repair_scope_gate


class RepairScopeGateTests(unittest.TestCase):
    def base(self):
        return {
            "requested_outcome":"fix_duplicate_invoice_issue",
            "requires_third_party_vendor_change":False,
            "requires_destructive_real_data_test":False,
            "safe_test_environment":True,
            "reproducible_or_observable":True,
            "acceptance_criteria_defined":True,
            "accepted_root_cause_count":1,
            "customer_authorized_target":True,
        }

    def test_bounded_observable_issue_is_candidate(self):
        r=repair_scope_gate.qualify_repair_request(self.base())
        self.assertTrue(r["verified_repair_eligible"])

    def test_absolute_no_future_bugs_is_declined(self):
        x=self.base(); x["requested_outcome"]="guarantee_no_future_bugs"
        r=repair_scope_gate.qualify_repair_request(x)
        self.assertFalse(r["verified_repair_eligible"])
        self.assertEqual(r["route"],"decline_absolute_promise")

    def test_third_party_vendor_bug_is_diagnosis_only(self):
        x=self.base(); x["requires_third_party_vendor_change"]=True
        r=repair_scope_gate.qualify_repair_request(x)
        self.assertEqual(r["route"],"diagnosis_only_external_dependency")

    def test_no_safe_test_environment_blocks_verified_repair(self):
        x=self.base(); x["safe_test_environment"]=False
        r=repair_scope_gate.qualify_repair_request(x)
        self.assertEqual(r["route"],"audit_or_prepare_test_environment")

    def test_unobservable_symptom_routes_to_diagnostic_first(self):
        x=self.base(); x["reproducible_or_observable"]=False
        r=repair_scope_gate.qualify_repair_request(x)
        self.assertEqual(r["route"],"diagnostic_first")

    def test_multiple_root_causes_must_be_split(self):
        x=self.base(); x["accepted_root_cause_count"]=3
        r=repair_scope_gate.qualify_repair_request(x)
        self.assertEqual(r["route"],"split_or_requalify_scope")


if __name__=="__main__":
    unittest.main()
