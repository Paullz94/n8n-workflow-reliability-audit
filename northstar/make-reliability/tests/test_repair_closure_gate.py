import unittest

import repair_closure_gate
import resolution_contract


def connected_test(test_id,assertions):
    return {
        "test_id":test_id,
        "source":"connected_test_run",
        "provider":"make",
        "observed_by_pcflows":True,
        "passed":True,
        "assertions":assertions,
        "execution_ids":["exec_"+test_id],
    }


class RepairClosureGateTests(unittest.TestCase):
    def contract(self):
        return resolution_contract.build_resolution_contract(
            rule="retrying-write-idempotency-review",
            module_id=1,
            business_description="The same business event must create exactly one external effect.",
        )

    def blueprints(self):
        before={
            "flow":[{
                "id":1,
                "module":"crm:updateContact",
                "mapper":{},
                "onerror":[{"id":2,"module":"builtin:Break","mapper":{"retry":True}}],
            }]
        }
        after={
            "flow":[{
                "id":1,
                "module":"crm:updateContact",
                "mapper":{},
                "onerror":[{"id":2,"module":"builtin:Break","mapper":{"retry":False}}],
            }]
        }
        return before,after

    def production(self,tests):
        return {
            "status":"verified_in_production",
            "all_tests_passed":True,
            "tests":tests,
        }

    def test_case_closes_only_with_bound_connected_evidence(self):
        before,after=self.blueprints()
        test=connected_test("dup",{
            "duplicate_replay_executed":True,
            "same_business_key":True,
            "intended_side_effect_count_one":True,
        })
        r=repair_closure_gate.close_repair_case(
            original_blueprint=before,
            revised_blueprint=after,
            contracts=[self.contract()],
            production_verification=self.production([test]),
            evidence_bindings=[{
                "rule":"retrying-write-idempotency-review",
                "module_id":1,
                "test_id":"dup",
            }],
        )
        self.assertTrue(r["customer_complete"])
        self.assertEqual(r["case_status"],"closed_verified")

    def test_missing_evidence_binding_keeps_case_open(self):
        before,after=self.blueprints()
        r=repair_closure_gate.close_repair_case(
            original_blueprint=before,
            revised_blueprint=after,
            contracts=[self.contract()],
            production_verification=self.production([]),
            evidence_bindings=[],
        )
        self.assertFalse(r["customer_complete"])

    def test_static_signal_remaining_keeps_case_open(self):
        before,_=self.blueprints()
        test=connected_test("dup",{
            "duplicate_replay_executed":True,
            "intended_side_effect_count_one":True,
        })
        r=repair_closure_gate.close_repair_case(
            original_blueprint=before,
            revised_blueprint=before,
            contracts=[self.contract()],
            production_verification=self.production([test]),
            evidence_bindings=[{
                "rule":"retrying-write-idempotency-review",
                "module_id":1,
                "test_id":"dup",
            }],
        )
        self.assertFalse(r["customer_complete"])

    def test_new_static_finding_blocks_closure(self):
        before,after=self.blueprints()
        after["metadata"]={"scenario":{"dataloss":True}}
        test=connected_test("dup",{
            "duplicate_replay_executed":True,
            "same_business_key":True,
            "intended_side_effect_count_one":True,
        })
        r=repair_closure_gate.close_repair_case(
            original_blueprint=before,
            revised_blueprint=after,
            contracts=[self.contract()],
            production_verification=self.production([test]),
            evidence_bindings=[{
                "rule":"retrying-write-idempotency-review",
                "module_id":1,
                "test_id":"dup",
            }],
        )
        self.assertFalse(r["customer_complete"])
        self.assertFalse(r["no_new_static_findings"])

    def test_specialist_pack_requires_every_acceptance_test(self):
        before,after=self.blueprints()
        test=connected_test("dup",{
            "duplicate_replay_executed":True,
            "same_business_key":True,
            "intended_side_effect_count_one":True,
        })
        r=repair_closure_gate.close_repair_case(
            original_blueprint=before,
            revised_blueprint=after,
            contracts=[self.contract()],
            production_verification=self.production([test]),
            evidence_bindings=[{
                "rule":"retrying-write-idempotency-review",
                "module_id":1,
                "test_id":"dup",
            }],
            specialist_pack_id="lead_flow",
        )
        self.assertFalse(r["customer_complete"])
        self.assertFalse(r["specialist_pack"]["all_tests_independently_verified"])


if __name__=="__main__":
    unittest.main()
