import unittest
import customer_claim_guard


class CustomerClaimGuardTests(unittest.TestCase):
    def test_blocks_absolute_fix_claim(self):
        with self.assertRaises(customer_claim_guard.ClaimGuardError):
            customer_claim_guard.assert_safe_report("This issue is fixed.")

    def test_blocks_production_ready_claim(self):
        with self.assertRaises(customer_claim_guard.ClaimGuardError):
            customer_claim_guard.assert_safe_report("The scenario is production-ready and safe.")

    def test_allows_conservative_static_language(self):
        customer_claim_guard.assert_safe_report(
            "The revised blueprint no longer matches this static rule. Runtime verification is still required."
        )

    def test_allows_scope_limitation(self):
        customer_claim_guard.assert_safe_report(
            "Static analysis cannot prove the absence of defects."
        )

    def test_allows_explicit_negative_fix_statement(self):
        customer_claim_guard.assert_safe_report(
            "PCFlows cannot say the issue is fixed until runtime verification passes."
        )

    def test_allows_not_production_ready_statement(self):
        customer_claim_guard.assert_safe_report(
            "This static review does not prove the scenario is production-ready."
        )


if __name__=="__main__":
    unittest.main()
