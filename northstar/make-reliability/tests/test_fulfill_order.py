import json
import pathlib
import tempfile
import unittest
import zipfile

import fulfill_order


class FulfillmentTests(unittest.TestCase):
    def test_rejects_non_stripe_order_reference(self):
        with self.assertRaises(fulfill_order.FulfillmentError):
            fulfill_order.validate_order_ref("order-123")

    def test_builds_bundle_without_raw_blueprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            bp = root / "blueprint.json"
            context = root / "context.json"
            out = root / "out"
            private_value = "PRIVATE-MAPPER-VALUE-7788"
            bp.write_text(json.dumps({
                "flow": [{"id": 1, "module": "crm:updateContact", "mapper": {"reference": private_value}}]
            }), encoding="utf-8")
            context.write_text(json.dumps({
                "scenario_name": "Orders",
                "business_goal": "Update each order once.",
                "critical_side_effects": ["Update CRM"],
                "duplicate_tolerance": "none",
                "ordering_required": False,
                "recovery_expectation": "Failures must be recoverable."
            }), encoding="utf-8")

            result = fulfill_order.build_delivery(
                blueprint_path=bp,
                context_path=context,
                order_ref="cs_live_demo_123",
                out_dir=out,
            )

            self.assertTrue((out / "pcflows-audit-delivery.zip").exists())
            self.assertTrue((out / "pcflows-ai-review-packet.json").exists())
            self.assertFalse((out / "blueprint.json").exists())
            manifest = json.loads((out / "pcflows-manifest.json").read_text())
            self.assertFalse(manifest["privacy"]["raw_blueprint_included"])
            self.assertTrue(manifest["privacy"]["case_isolation_enabled"])
            self.assertTrue(manifest["privacy"]["literal_customer_data_guard_enabled"])
            self.assertTrue(manifest["case_scope_id"].startswith("pcfcase_"))
            report = (out / "pcflows-data-integrity-audit.md").read_text()
            packet = (out / "pcflows-ai-review-packet.json").read_text()
            self.assertNotIn(private_value, report)
            self.assertNotIn(private_value, packet)
            with zipfile.ZipFile(result["zip"]) as z:
                self.assertNotIn("blueprint.json", z.namelist())
                self.assertNotIn("pcflows-ai-review-packet.json", z.namelist())

    def test_secret_finding_hard_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            bp = root / "blueprint.json"
            context = root / "context.json"
            bp.write_text(json.dumps({
                "flow": [{"id": 1, "module": "http:ActionSendData", "mapper": {
                    "headers": "Bearer abcdefghijklmnopqrstuvwxyz123456"
                }}]
            }), encoding="utf-8")
            context.write_text(json.dumps({
                "scenario_name": "Demo",
                "business_goal": "Demo goal"
            }), encoding="utf-8")
            with self.assertRaises(fulfill_order.FulfillmentError):
                fulfill_order.build_delivery(
                    blueprint_path=bp,
                    context_path=context,
                    order_ref="cs_live_demo_123",
                    out_dir=root / "out",
                )

    def test_personal_email_literal_hard_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            bp=root/"blueprint.json"
            context=root/"context.json"
            email="real.person"+"@"+"private-domain.be"
            bp.write_text(json.dumps({
                "flow":[{"id":1,"module":"crm:updateContact","mapper":{"email":email}}]
            }),encoding="utf-8")
            context.write_text(json.dumps({
                "scenario_name":"Demo",
                "business_goal":"Update CRM"
            }),encoding="utf-8")
            with self.assertRaises(fulfill_order.FulfillmentError):
                fulfill_order.build_delivery(
                    blueprint_path=bp,
                    context_path=context,
                    order_ref="cs_live_demo_123",
                    out_dir=root/"out",
                )

    def test_fulfillment_autoselects_lead_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            bp = root / "blueprint.json"
            context = root / "context.json"
            out = root / "out"
            bp.write_text(json.dumps({
                "flow": [{"id": 1, "module": "crm:createContact", "mapper": {}}]
            }), encoding="utf-8")
            context.write_text(json.dumps({
                "scenario_name": "Facebook leads to CRM",
                "business_goal": "Route every lead to one sales owner and stop follow-up after booking",
                "critical_side_effects": ["Create CRM lead exactly once"],
                "duplicate_tolerance": "none",
                "ordering_required": True,
                "recovery_expectation": "Failed lead remains visible."
            }), encoding="utf-8")

            result = fulfill_order.build_delivery(
                blueprint_path=bp,
                context_path=context,
                order_ref="cs_live_demo_pack",
                out_dir=out,
            )
            self.assertEqual(result["pack_selection"]["pack_id"], "lead_flow")
            self.assertTrue(result["case_scope_id"].startswith("pcfcase_"))
            report = (out / "pcflows-data-integrity-audit.md").read_text()
            self.assertIn("Lead Flow Reliability Audit", report)

    def test_claim_guard_is_applied_to_customer_report(self):
        self.assertIn("customer_claim_guard.assert_safe_report", __import__("inspect").getsource(fulfill_order.build_delivery))


if __name__ == "__main__":
    unittest.main()
