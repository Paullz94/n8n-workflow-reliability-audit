import unittest
import remediation_proof_report


class RemediationProofReportTests(unittest.TestCase):
    def before_after(self):
        before={"flow":[{"id":1,"module":"crm:updateContact","mapper":{} }]}
        after={"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Break","mapper":{}}]}]}
        return before,after

    def test_static_clear_is_not_verified_fixed(self):
        before,after=self.before_after()
        r=remediation_proof_report.build_proof(before,after,[])
        hit=next(x for x in r["statuses"] if x["rule"]=="write-without-error-handler")
        self.assertFalse(hit["status"]["verified_fixed"])
        self.assertEqual(hit["status"]["status"],"statically_cleared_runtime_pending")

    def test_connected_evidence_can_verify(self):
        before,after=self.before_after()
        evidence=[{
            "rule":"write-without-error-handler",
            "module_id":1,
            "source":"connected_test_run",
            "assertions":{
                "failure_injected":True,
                "failure_observable":True,
                "recovery_path_succeeds":True,
                "duplicate_side_effects_zero":True,
            }
        }]
        r=remediation_proof_report.build_proof(before,after,evidence)
        hit=next(x for x in r["statuses"] if x["rule"]=="write-without-error-handler")
        self.assertTrue(hit["status"]["verified_fixed"])

    def test_customer_evidence_is_supporting_not_independent(self):
        before,after=self.before_after()
        evidence=[{
            "rule":"write-without-error-handler",
            "module_id":1,
            "source":"customer_test_record",
            "assertions":{
                "failure_injected":True,
                "failure_observable":True,
                "recovery_path_succeeds":True,
                "duplicate_side_effects_zero":True,
            }
        }]
        r=remediation_proof_report.build_proof(before,after,evidence)
        hit=next(x for x in r["statuses"] if x["rule"]=="write-without-error-handler")
        self.assertFalse(hit["status"]["verified_fixed"])
        self.assertEqual(hit["status"]["status"],"evidence_supported_pending_independent_verification")


if __name__=="__main__":
    unittest.main()
