import unittest
import resolution_contract


class ResolutionContractTests(unittest.TestCase):
    def test_runtime_contract_stays_open_after_static_change_only(self):
        c=resolution_contract.build_resolution_contract(
            rule="retrying-write-idempotency-review",
            module_id=4,
            business_description="The same order must never be created twice.",
        )
        r=resolution_contract.evaluate_resolution_contract(
            c,still_present_after=False,evidence=None
        )
        self.assertEqual(r["customer_status"],"open")
        self.assertFalse(resolution_contract.all_closed_verified([r]))

    def test_runtime_contract_closes_only_after_independent_pass(self):
        c=resolution_contract.build_resolution_contract(
            rule="retrying-write-idempotency-review",
            module_id=4,
            business_description="The same order must never be created twice.",
        )
        r=resolution_contract.evaluate_resolution_contract(
            c,
            still_present_after=False,
            evidence={
                "source":"connected_test_run",
                "assertions":{
                    "duplicate_replay_executed":True,
                    "intended_side_effect_count_one":True,
                }
            }
        )
        self.assertEqual(r["customer_status"],"closed_verified")
        self.assertTrue(resolution_contract.all_closed_verified([r]))

    def test_static_only_contract_can_close_from_clean_reexport(self):
        c=resolution_contract.build_resolution_contract(
            rule="possible-secret-in-blueprint",
            module_id=None,
            business_description="No secret-like literal may remain in the shareable export.",
        )
        r=resolution_contract.evaluate_resolution_contract(c,still_present_after=False)
        self.assertEqual(r["customer_status"],"closed_verified")

    def test_all_closed_requires_every_issue(self):
        a={"customer_status":"closed_verified"}
        b={"customer_status":"open"}
        self.assertFalse(resolution_contract.all_closed_verified([a,b]))


if __name__=="__main__":
    unittest.main()
