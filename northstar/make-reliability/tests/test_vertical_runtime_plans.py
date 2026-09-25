import unittest

import vertical_packs
import vertical_runtime_plans


class VerticalRuntimePlansTests(unittest.TestCase):
    def test_every_specialist_pack_has_exact_runtime_plan(self):
        self.assertEqual(set(vertical_runtime_plans.PLANS),set(vertical_packs.PACKS))
        for pack_id in vertical_packs.PACKS:
            plan=vertical_runtime_plans.get_runtime_plan(pack_id)
            expected={x["id"] for x in vertical_packs.get_pack(pack_id).acceptance_tests}
            actual={x["test_id"] for x in plan}
            self.assertEqual(actual,expected)

    def test_all_production_tests_are_explicitly_safe(self):
        for pack_id in vertical_packs.PACKS:
            for test in vertical_runtime_plans.get_runtime_plan(pack_id):
                self.assertIs(test["production_safe"],True)

    def test_every_input_is_synthetic_labeled(self):
        for pack_id in vertical_packs.PACKS:
            for test in vertical_runtime_plans.get_runtime_plan(pack_id):
                value=str(test["input"].get("pcflows_case",""))
                self.assertTrue(value.startswith("SYN-"))

    def test_lead_race_uses_real_concurrent_pair(self):
        plan=vertical_runtime_plans.get_runtime_plan("lead_flow")
        race=next(x for x in plan if x["test_id"]=="lead_route_race")
        self.assertEqual(race["evaluator"],"concurrent_pair")

    def test_invoice_partial_payment_is_explicit(self):
        plan=vertical_runtime_plans.get_runtime_plan("invoice_payment")
        partial=next(x for x in plan if x["test_id"]=="payment_partial")
        self.assertEqual(partial["input"]["invoice_total"],2000)
        self.assertEqual(partial["input"]["paid_amount"],500)


if __name__=="__main__":
    unittest.main()
