import unittest

import focused_risk_check


class FocusedRiskCheckTests(unittest.TestCase):
    def context(self):
        return {"scenario_name":"Demo","business_goal":"Process reliably"}

    def test_duplicate_focus_filters_other_findings(self):
        bp={"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}]}
        report=focused_risk_check.render_focused_report("duplicates","demo.json",bp,self.context())
        self.assertIn("Duplicate effects / idempotency",report)
        self.assertNotIn("write-without-error-handler",report)

    def test_recovery_focus_includes_missing_handler(self):
        bp={"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}]}
        report=focused_risk_check.render_focused_report("recovery","demo.json",bp,self.context())
        self.assertIn("write-without-error-handler",report)

    def test_secret_stops(self):
        bp={"flow":[{"id":1,"module":"http:ActionSendData","mapper":{"headers":"Bearer abcdefghijklmnopqrstuvwxyz123456"}}]}
        with self.assertRaises(ValueError):
            focused_risk_check.render_focused_report("recovery","demo.json",bp,self.context())


if __name__=="__main__":
    unittest.main()
