import unittest

import stripe_checkout_adapter


class CheckoutAdapterTests(unittest.TestCase):
    def session(self,amount=14900):
        return {
            "id":"cs_live_real_customer",
            "livemode":True,
            "payment_status":"paid",
            "currency":"eur",
            "amount_total":amount,
            "metadata":{},
        }

    def test_package_from_payment_intent_metadata(self):
        r=stripe_checkout_adapter.normalize_checkout_session(
            self.session(),
            payment_intent={"metadata":{"pcflows_package":"data_integrity_audit"}},
            provider_verified=True,
        )
        self.assertEqual(r["package_id"],"data_integrity_audit")

    def test_package_from_price_metadata(self):
        r=stripe_checkout_adapter.normalize_checkout_session(
            self.session(7900),
            line_items=[{"price":{"metadata":{"pcflows_package":"focused_risk_check"}}}],
            provider_verified=True,
        )
        self.assertEqual(r["package_id"],"focused_risk_check")

    def test_conflicting_metadata_stops(self):
        with self.assertRaises(stripe_checkout_adapter.CheckoutAdapterError):
            stripe_checkout_adapter.normalize_checkout_session(
                self.session(),
                payment_intent={"metadata":{"pcflows_package":"data_integrity_audit"}},
                line_items=[{"price":{"metadata":{"pcflows_package":"focused_risk_check"}}}],
                provider_verified=True,
            )

    def test_untrusted_data_stops(self):
        with self.assertRaises(stripe_checkout_adapter.CheckoutAdapterError):
            stripe_checkout_adapter.normalize_checkout_session(
                self.session(),
                payment_intent={"metadata":{"pcflows_package":"data_integrity_audit"}},
                provider_verified=False,
            )

    def test_owner_payment_stops(self):
        s=self.session()
        s["metadata"]={"owner_or_test":"true","pcflows_package":"data_integrity_audit"}
        with self.assertRaises(stripe_checkout_adapter.CheckoutAdapterError):
            stripe_checkout_adapter.normalize_checkout_session(s,provider_verified=True)


if __name__=="__main__":
    unittest.main()
