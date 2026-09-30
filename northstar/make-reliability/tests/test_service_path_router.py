import unittest

import service_path_router


class ServicePathRouterTests(unittest.TestCase):
    def base(self,**overrides):
        data=dict(
            rule="retrying-write-idempotency-review",
            safe_to_analyze=True,
            authorized_to_review=True,
            root_cause_known=True,
            safe_test_environment=False,
            pcflows_can_observe_runtime=False,
            external_side_effect_observable=False,
            acceptance_criteria_defined=True,
            customer_wants_done_for_you_fix=True,
        )
        data.update(overrides)
        return data

    def test_unverifiable_fix_is_not_customer_rejection(self):
        r=service_path_router.route_case(**self.base())
        self.assertFalse(r["declined"])
        self.assertEqual(r["route"],"guided_remediation_then_verify")

    def test_unknown_root_cause_routes_to_audit(self):
        r=service_path_router.route_case(**self.base(root_cause_known=False))
        self.assertFalse(r["declined"])
        self.assertEqual(r["route"],"audit_then_decide")

    def test_verified_repair_when_all_proof_gates_exist(self):
        r=service_path_router.route_case(**self.base(
            safe_test_environment=True,
            pcflows_can_observe_runtime=True,
            external_side_effect_observable=True,
        ))
        self.assertEqual(r["route"],"verified_repair_candidate")

    def test_secret_or_unsafe_input_requests_resanitization_not_rejection(self):
        r=service_path_router.route_case(**self.base(safe_to_analyze=False))
        self.assertFalse(r["declined"])
        self.assertEqual(r["route"],"resanitize_or_scope_correction")

    def test_missing_authorization_is_a_prerequisite_not_rejection(self):
        r=service_path_router.route_case(**self.base(authorized_to_review=False))
        self.assertFalse(r["declined"])
        self.assertEqual(r["route"],"authorization_required")


if __name__=="__main__":
    unittest.main()
