import unittest

import sandbox_repair_runner


class FakeClient:
    def __init__(self,responses,rollback_fails=False):
        self.responses=list(responses)
        self.original={"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}]}
        self.current=self.original
        self.rollback_calls=0
        self.update_calls=0
        self.rollback_fails=rollback_fails

    def update_sandbox_blueprint(self,scenario_id,revised):
        self.update_calls+=1
        self.current=revised
        return {
            "scenario_id":scenario_id,
            "original_blueprint":self.original,
            "original_sha256":"abc",
        }

    def get_blueprint(self,scenario_id):
        return self.current

    def run_scenario(self,scenario_id,*,data=None,responsive=True):
        if not self.responses:
            raise RuntimeError("no fake response")
        return self.responses.pop(0)

    def rollback_sandbox_blueprint(self,scenario_id,original):
        self.rollback_calls+=1
        if self.rollback_fails:
            raise RuntimeError("rollback boom")
        self.current=original


class SandboxRepairRunnerTests(unittest.TestCase):
    def revised(self):
        return {"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}]}

    def test_duplicate_replay_passes_and_keeps_sandbox_revision(self):
        client=FakeClient([
            {"executionId":"e1","output":{"business_key":"O-1","side_effect_ids":["inv_1"],"side_effect_count":1}},
            {"executionId":"e2","output":{"business_key":"O-1","side_effect_ids":["inv_1"],"side_effect_count":1}},
        ])
        result=sandbox_repair_runner.run_sandbox_repair(
            client=client,
            scenario_id=123,
            revised_blueprint=self.revised(),
            test_plan=[{"test_id":"dup","evaluator":"duplicate_replay","input":{"order_id":"SYN-1"}}],
        )
        self.assertEqual(result["status"],"verified_in_sandbox")
        self.assertTrue(result["all_tests_passed"])
        self.assertEqual(client.rollback_calls,0)

    def test_failed_assertion_rolls_back(self):
        client=FakeClient([
            {"executionId":"e1","output":{"invoice_total":2000,"paid_amount":500,"marked_fully_paid":True}},
        ])
        with self.assertRaises(sandbox_repair_runner.SandboxRepairError) as ctx:
            sandbox_repair_runner.run_sandbox_repair(
                client=client,
                scenario_id=123,
                revised_blueprint=self.revised(),
                test_plan=[{"test_id":"partial","evaluator":"partial_payment","input":{"case":"partial"}}],
            )
        self.assertIn("original sandbox blueprint was restored",str(ctx.exception))
        self.assertEqual(client.rollback_calls,1)
        self.assertEqual(client.current,client.original)

    def test_runtime_exception_rolls_back(self):
        class Broken(FakeClient):
            def run_scenario(self,*args,**kwargs):
                raise RuntimeError("Make run failed")
        client=Broken([])
        with self.assertRaises(sandbox_repair_runner.SandboxRepairError):
            sandbox_repair_runner.run_sandbox_repair(
                client=client,
                scenario_id=123,
                revised_blueprint=self.revised(),
                test_plan=[{"test_id":"fail","evaluator":"failure_recovery","input":{}}],
            )
        self.assertEqual(client.rollback_calls,1)

    def test_rollback_failure_is_never_hidden(self):
        client=FakeClient([
            {"executionId":"e1","output":{"invoice_total":2000,"paid_amount":500,"marked_fully_paid":True}},
        ],rollback_fails=True)
        with self.assertRaises(sandbox_repair_runner.SandboxRepairError) as ctx:
            sandbox_repair_runner.run_sandbox_repair(
                client=client,
                scenario_id=123,
                revised_blueprint=self.revised(),
                test_plan=[{"test_id":"partial","evaluator":"partial_payment","input":{}}],
            )
        self.assertIn("rollback also failed",str(ctx.exception))

    def test_secret_like_synthetic_input_is_rejected_before_run(self):
        client=FakeClient([])
        with self.assertRaises(sandbox_repair_runner.SandboxRepairError):
            sandbox_repair_runner.run_sandbox_repair(
                client=client,
                scenario_id=123,
                revised_blueprint=self.revised(),
                test_plan=[{
                    "test_id":"bad",
                    "evaluator":"failure_recovery",
                    "input":{"authorization":"Bearer abcdefghijklmnopqrstuvwxyz123456"},
                }],
            )

    def test_requires_structured_proof_output(self):
        client=FakeClient([{"executionId":"e1","status":"1"}])
        with self.assertRaises(sandbox_repair_runner.SandboxRepairError):
            sandbox_repair_runner.run_sandbox_repair(
                client=client,
                scenario_id=123,
                revised_blueprint=self.revised(),
                test_plan=[{"test_id":"bad","evaluator":"failure_recovery","input":{}}],
            )
        self.assertEqual(client.rollback_calls,1)


if __name__=="__main__":
    unittest.main()
