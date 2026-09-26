import json
import pathlib
import unittest

import audit_make
import pack_selector
import vertical_packs


ROOT=pathlib.Path(__file__).resolve().parents[1]
EXAMPLES=ROOT/"examples"/"vertical"


class VerticalExamplesTests(unittest.TestCase):
    CASES={
        "lead_flow":("lead-flow-blueprint.json","lead-flow-context.json"),
        "invoice_payment":("invoice-payment-blueprint.json","invoice-payment-context.json"),
        "ai_guardrails":("ai-guardrails-blueprint.json","ai-guardrails-context.json"),
        "client_onboarding":("client-onboarding-blueprint.json","client-onboarding-context.json"),
    }

    def load(self,name):
        bp_name,ctx_name=self.CASES[name]
        bp=json.loads((EXAMPLES/bp_name).read_text(encoding="utf-8"))
        ctx=json.loads((EXAMPLES/ctx_name).read_text(encoding="utf-8"))
        return bp,ctx

    def test_each_example_selects_expected_pack(self):
        for pack_id in self.CASES:
            with self.subTest(pack_id=pack_id):
                _,ctx=self.load(pack_id)
                selected=pack_selector.select_pack(ctx)
                self.assertEqual(selected["pack_id"],pack_id)

    def test_each_example_produces_reliability_findings(self):
        for pack_id in self.CASES:
            with self.subTest(pack_id=pack_id):
                bp,_=self.load(pack_id)
                findings=audit_make.scan_blueprint(bp)
                self.assertGreater(len(findings),0)
                self.assertTrue(any(f.severity in {"high","medium"} for f in findings))

    def test_each_pack_has_four_business_acceptance_tests(self):
        for pack_id in self.CASES:
            with self.subTest(pack_id=pack_id):
                self.assertEqual(len(vertical_packs.get_pack(pack_id).acceptance_tests),4)


if __name__=="__main__":
    unittest.main()
