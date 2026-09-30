import unittest

import production_deploy_runner
import sandbox_repair_runner


class FakeProductionClient:
    def __init__(self,responses,rollback_fails=False):
        self.responses=list(responses)
        self.original={"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}]}
        self.current=self.original
        self.rollback_calls=0
        self.rollback_fails=rollback_fails

    def update_production_blueprint(self,scenario_id,revised):
        self.current=revised
        return {
            "scenario_id":scenario_id,
            "repair_case_id":"case_1",
            "customer_authorization_id":"auth_1",
            "original_blueprint":self.original,
            "original_sha256":"orig",
        }

    def get_blueprint(self,scenario_id):
        return self.current

    def run_scenario(self,scenario_id,*,data=None,responsive=True):
        if not self.responses:
            raise RuntimeError("no response")
        return self.responses.pop(0)

    def rollback_production_blueprint(self,scenario_id,original):
        self.rollback_calls+=1
        if self.rollback_fails:
            raise RuntimeError("rollback failed")
        self.current=original


class ProductionDeployRunnerTests(unittest.TestCase):
    def revised(self):
        return {"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}]}

    def cert(self):
        bp=self.revised()
        return {
            "status":"verified_in_sandbox",
            "all_tests_passed":True,
            "requested_revised_sha256":production_deploy_runner._sha(bp),
        }

    def test_requires_exact_sandbox_verified_revision(self):
        cert=self.cert()
        with self.assertRaises(production_deploy_runner.ProductionDeployError):
            production_deploy_runner.validate_sandbox_certificate(
                {"flow":[{"id":2,"module":"json:ParseJSON","mapper":{}}]},
                cert,
            )

    def test_rejects_non_production_safe_test(self):
        with self.assertRaises(production_deploy_runner.ProductionDeployError):
            production_deploy_runner.validate_production_test_plan([
                {"test_id":"x","evaluator":"failure_recovery","production_safe":False}
            ])

    def test_successful_deploy_passes_postdeploy_acceptance(self):
        client=FakeProductionClient([
            {"executionId":"e1","output":{
                "invoice_total":2000,
                "paid_amount":500,
                "marked_fully_paid":False,
            }}
        ])
        result=production_deploy_runner.deploy_verified_repair(
            client=client,
            production_scenario_id=444,
            revised_blueprint=self.revised(),
            sandbox_verification=self.cert(),
            production_test_plan=[{
                "test_id":"partial",
                "evaluator":"partial_payment",
                "input":{"case":"synthetic-partial"},
                "production_safe":True,
            }],
        )
        self.assertEqual(result["status"],"verified_in_production")
        self.assertTrue(result["all_tests_passed"])
        self.assertEqual(client.rollback_calls,0)

    def test_failed_postdeploy_test_restores_original(self):
        client=FakeProductionClient([
            {"executionId":"e1","output":{
                "invoice_total":2000,
                "paid_amount":500,
                "marked_fully_paid":True,
            }}
        ])
        with self.assertRaises(production_deploy_runner.ProductionDeployError) as ctx:
            production_deploy_runner.deploy_verified_repair(
                client=client,
                production_scenario_id=444,
                revised_blueprint=self.revised(),
                sandbox_verification=self.cert(),
                production_test_plan=[{
                    "test_id":"partial",
                    "evaluator":"partial_payment",
                    "input":{},
                    "production_safe":True,
                }],
            )
        self.assertIn("original production blueprint was restored",str(ctx.exception))
        self.assertEqual(client.current,client.original)

    def test_rollback_failure_is_exposed(self):
        client=FakeProductionClient([
            {"executionId":"e1","output":{
                "invoice_total":2000,
                "paid_amount":500,
                "marked_fully_paid":True,
            }}
        ],rollback_fails=True)
        with self.assertRaises(production_deploy_runner.ProductionDeployError) as ctx:
            production_deploy_runner.deploy_verified_repair(
                client=client,
                production_scenario_id=444,
                revised_blueprint=self.revised(),
                sandbox_verification=self.cert(),
                production_test_plan=[{
                    "test_id":"partial",
                    "evaluator":"partial_payment",
                    "input":{},
                    "production_safe":True,
                }],
            )
        self.assertIn("production rollback also failed",str(ctx.exception))


if __name__=="__main__":
    unittest.main()
