import json
import pathlib
import tempfile
import unittest
import zipfile

import package_fulfillment


class PackageFulfillmentTests(unittest.TestCase):
    def order(self,package,amount):
        return {
            "provider_verified":True,
            "livemode":True,
            "session_id":"cs_live_customer_pkg",
            "payment_status":"paid",
            "currency":"eur",
            "amount_total":amount,
            "metadata":{"pcflows_package":package},
            "owner_or_test":False,
        }

    def write_pair(self,root,name="Demo",module="crm:updateContact"):
        bp=root/f"{name}-bp.json"
        ctx=root/f"{name}-ctx.json"
        bp.write_text(json.dumps({"flow":[{"id":1,"module":module,"mapper":{}}]}),encoding="utf-8")
        ctx.write_text(json.dumps({
            "scenario_name":name,
            "business_goal":"Process each event reliably",
            "critical_side_effects":["Update business system"],
            "duplicate_tolerance":"none",
            "ordering_required":False,
            "recovery_expectation":"Failures remain visible.",
        }),encoding="utf-8")
        return bp,ctx

    def test_focused_delivery_has_no_rescan_and_no_blueprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp); bp,ctx=self.write_pair(root); out=root/"out"
            r=package_fulfillment.build_focused_delivery(
                order=self.order("focused_risk_check",7900),
                blueprint_path=bp,context_path=ctx,focus="recovery",out_dir=out
            )
            with zipfile.ZipFile(r["zip"]) as z:
                names=set(z.namelist())
                self.assertNotIn(bp.name,names)
                self.assertIn("pcflows-focused-risk-check.md",names)
            manifest=json.loads((out/"pcflows-manifest.json").read_text())
            self.assertFalse(manifest["privacy"]["included_rescan"])

    def test_wrong_amount_cannot_unlock_portfolio(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp); bp,ctx=self.write_pair(root); out=root/"out"
            with self.assertRaises(Exception):
                package_fulfillment.build_portfolio_delivery(
                    order=self.order("portfolio_release_qa",14900),
                    scenarios=[("A",bp,ctx)],out_dir=out
                )

    def test_portfolio_delivery_excludes_internal_ai_packets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            bp1,ctx1=self.write_pair(root,"A")
            bp2,ctx2=self.write_pair(root,"B","json:ParseJSON")
            out=root/"out"
            r=package_fulfillment.build_portfolio_delivery(
                order=self.order("portfolio_release_qa",39900),
                scenarios=[("A",bp1,ctx1),("B",bp2,ctx2)],
                out_dir=out
            )
            self.assertEqual(r["scenario_count"],2)
            with zipfile.ZipFile(r["zip"]) as z:
                names=set(z.namelist())
                self.assertFalse(any("ai-review" in x for x in names))
                self.assertFalse(any(x.endswith("-bp.json") for x in names))
                self.assertIn("pcflows-portfolio-release-qa.md",names)

    def test_secret_in_one_portfolio_item_blocks_everything(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            bp1,ctx1=self.write_pair(root,"A")
            bp2,ctx2=self.write_pair(root,"B")
            bp2.write_text(json.dumps({"flow":[{"id":1,"module":"http:ActionSendData","mapper":{"headers":"Bearer abcdefghijklmnopqrstuvwxyz123456"}}]}),encoding="utf-8")
            out=root/"out"
            with self.assertRaises(package_fulfillment.PackageFulfillmentError):
                package_fulfillment.build_portfolio_delivery(
                    order=self.order("portfolio_release_qa",39900),
                    scenarios=[("A",bp1,ctx1),("B",bp2,ctx2)],out_dir=out
                )

    def test_data_integrity_routes_through_existing_fulfillment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp); bp,ctx=self.write_pair(root,"Orders"); out=root/"out"
            r=package_fulfillment.build_data_integrity_delivery(
                order=self.order("data_integrity_audit",14900),
                blueprint_path=bp,context_path=ctx,out_dir=out
            )
            self.assertEqual(r["package_id"],"data_integrity_audit")
            self.assertTrue(pathlib.Path(r["zip"]).exists())

    def test_focused_delivery_can_take_focus_from_safe_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp); bp,ctx=self.write_pair(root); out=root/"out"
            raw=json.loads(ctx.read_text())
            raw["requested_scope"]="focused"
            raw["requested_focus"]="recovery"
            ctx.write_text(json.dumps(raw),encoding="utf-8")
            r=package_fulfillment.build_focused_delivery(
                order=self.order("focused_risk_check",7900),
                blueprint_path=bp,context_path=ctx,focus=None,out_dir=out
            )
            self.assertEqual(r["focus"],"recovery")


if __name__=="__main__":
    unittest.main()
