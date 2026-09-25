import unittest

import audit_make
import fix_verification


class FixVerificationTests(unittest.TestCase):
    def test_registry_covers_every_known_rule(self):
        self.assertEqual(set(fix_verification.RULE_VERIFICATION_SPECS), set(audit_make.KNOWN_RULES))

    def test_runtime_rule_is_not_fixed_when_only_static_signal_disappears(self):
        r=fix_verification.resolution_status(
            rule="retrying-write-idempotency-review",
            still_present_after=False,
            evidence=None,
        )
        self.assertFalse(r["verified_fixed"])
        self.assertEqual(r["status"],"statically_cleared_runtime_pending")

    def test_customer_supplied_runtime_evidence_is_not_independent_verified_fix(self):
        r=fix_verification.resolution_status(
            rule="retrying-write-idempotency-review",
            still_present_after=False,
            evidence={
                "source":"customer_test_record",
                "assertions":{
                    "duplicate_replay_executed":True,
                    "intended_side_effect_count_one":True,
                }
            },
        )
        self.assertFalse(r["verified_fixed"])
        self.assertEqual(r["status"],"evidence_supported_pending_independent_verification")

    def test_connected_runtime_test_can_verify_fix(self):
        r=fix_verification.resolution_status(
            rule="retrying-write-idempotency-review",
            still_present_after=False,
            evidence={
                "source":"connected_test_run",
                "provider":"make",
                "observed_by_pcflows":True,
                "execution_ids":["exec_1"],
                "assertions":{
                    "duplicate_replay_executed":True,
                    "intended_side_effect_count_one":True,
                }
            },
        )
        self.assertTrue(r["verified_fixed"])
        self.assertEqual(r["status"],"verified_fixed")

    def test_incomplete_runtime_evidence_cannot_verify(self):
        r=fix_verification.resolution_status(
            rule="concurrency-review",
            still_present_after=False,
            evidence={
                "source":"connected_test_run",
                "assertions":{"concurrent_test_executed":True}
            },
        )
        self.assertFalse(r["verified_fixed"])
        self.assertIn("final_state_deterministic",r["evidence"]["missing"])

    def test_static_secret_fix_can_be_verified_statically(self):
        r=fix_verification.resolution_status(
            rule="possible-secret-in-blueprint",
            still_present_after=False,
        )
        self.assertTrue(r["verified_fixed"])
        self.assertEqual(r["status"],"verified_static_fix")

    def test_remaining_signal_never_called_fixed(self):
        r=fix_verification.resolution_status(
            rule="write-without-error-handler",
            still_present_after=True,
            evidence={
                "source":"connected_test_run",
                "provider":"make",
                "observed_by_pcflows":True,
                "execution_ids":["exec_2"],
                "assertions":{
                    "failure_injected":True,
                    "failure_observable":True,
                    "recovery_path_succeeds":True,
                    "duplicate_side_effects_zero":True,
                }
            },
            trusted_connected_evidence=True,
        )
        self.assertFalse(r["verified_fixed"])
        self.assertEqual(r["status"],"verified_mitigated_not_statically_cleared")

    def test_spoofed_connected_source_cannot_self_certify(self):
        r=fix_verification.resolution_status(
            rule="retrying-write-idempotency-review",
            still_present_after=False,
            evidence={
                "source":"connected_test_run",
                "provider":"make",
                "observed_by_pcflows":True,
                "execution_ids":["fake"],
                "assertions":{
                    "duplicate_replay_executed":True,
                    "intended_side_effect_count_one":True,
                },
            },
            trusted_connected_evidence=False,
        )
        self.assertFalse(r["verified_fixed"])
        self.assertEqual(r["status"],"statically_cleared_runtime_pending")


if __name__=="__main__":
    unittest.main()
