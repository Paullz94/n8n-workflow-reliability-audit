import unittest

import pack_acceptance_verification


class PackAcceptanceVerificationTests(unittest.TestCase):
    def evidence(self,pack,source="connected_test_run",passed=True):
        return [
            {"test_id":tid,"source":source,"passed":passed}
            for tid in pack_acceptance_verification.required_test_ids(pack)
        ]

    def test_connected_evidence_verifies_entire_pack(self):
        r=pack_acceptance_verification.verify_pack_acceptance(
            "lead_flow",
            self.evidence("lead_flow"),
        )
        self.assertTrue(r["all_tests_independently_verified"])
        self.assertEqual(r["customer_status"],"verified_fixed")

    def test_customer_evidence_supports_but_does_not_independently_verify(self):
        r=pack_acceptance_verification.verify_pack_acceptance(
            "invoice_payment",
            self.evidence("invoice_payment","customer_test_record"),
        )
        self.assertTrue(r["all_tests_passed"])
        self.assertFalse(r["all_tests_independently_verified"])
        self.assertEqual(r["customer_status"],"evidence_supported")

    def test_one_missing_test_keeps_pack_open(self):
        evidence=self.evidence("ai_guardrails")
        evidence.pop()
        r=pack_acceptance_verification.verify_pack_acceptance("ai_guardrails",evidence)
        self.assertEqual(r["customer_status"],"open")

    def test_one_failed_test_keeps_pack_open(self):
        evidence=self.evidence("client_onboarding")
        evidence[0]["passed"]=False
        r=pack_acceptance_verification.verify_pack_acceptance("client_onboarding",evidence)
        self.assertEqual(r["customer_status"],"open")


if __name__=="__main__":
    unittest.main()
