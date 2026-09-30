import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ledger_engine
import stripe_adapter


class StripeAdapterTests(unittest.TestCase):
    def payment(self, *, livemode=True, verified=True):
        raw = {
            "type": "payment_intent.succeeded",
            "data": {"object": {
                "id": "pi_demo",
                "object": "payment_intent",
                "amount": 14900,
                "amount_received": 14900,
                "currency": "eur",
                "livemode": livemode,
                "metadata": {},
                "status": "succeeded",
                "receipt_email": "private@example.com",
            }},
        }
        return stripe_adapter.normalize_item(raw, provider_verified=verified)

    def test_live_verified_payment_normalizes_to_eur(self):
        event = self.payment()
        self.assertEqual(event["amount_eur"], 149.0)
        self.assertTrue(event["provider_verified"])
        self.assertFalse(event["test"])
        self.assertNotIn("receipt_email", event)

    def test_testmode_payment_is_excluded_by_ledger(self):
        event = self.payment(livemode=False)
        totals = ledger_engine.calculate([event])
        self.assertEqual(totals.verified_gross_revenue, 0.0)

    def test_unverified_source_is_excluded_by_ledger(self):
        event = self.payment(verified=False)
        totals = ledger_engine.calculate([event])
        self.assertEqual(totals.verified_gross_revenue, 0.0)

    def test_owner_metadata_excludes_payment(self):
        raw = {
            "id": "pi_owner", "object": "payment_intent", "amount_received": 14900,
            "currency": "eur", "livemode": True, "status": "succeeded",
            "metadata": {"northstar_owner": "true"},
        }
        event = stripe_adapter.normalize_item(raw, provider_verified=True)
        self.assertEqual(event["customer_class"], "owner")
        self.assertEqual(ledger_engine.calculate([event]).verified_gross_revenue, 0.0)

    def test_successful_refund_maps_to_payment_intent(self):
        raw = {
            "type": "refund.updated",
            "data": {"object": {
                "id": "re_demo", "object": "refund", "amount": 4900,
                "currency": "eur", "payment_intent": "pi_demo", "status": "succeeded"
            }},
        }
        event = stripe_adapter.normalize_item(raw, provider_verified=True)
        self.assertEqual(event["kind"], "refund")
        self.assertEqual(event["payment_id"], "pi_demo")
        self.assertEqual(event["amount_eur"], 49.0)

    def test_duplicate_refund_lifecycle_events_collapse_by_object_id(self):
        created = {"type": "refund.created", "data": {"object": {
            "id": "re_demo", "object": "refund", "amount": 4900,
            "currency": "eur", "payment_intent": "pi_demo", "status": "pending"
        }}}
        updated = {"type": "refund.updated", "data": {"object": {
            "id": "re_demo", "object": "refund", "amount": 4900,
            "currency": "eur", "payment_intent": "pi_demo", "status": "succeeded"
        }}}
        events = stripe_adapter.normalize_many([created, updated], provider_verified=True)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["status"], "succeeded")

    def test_non_eur_is_rejected(self):
        raw = {"id": "pi_usd", "object": "payment_intent", "amount_received": 1000, "currency": "usd", "livemode": True, "status": "succeeded"}
        with self.assertRaises(stripe_adapter.StripeAdapterError):
            stripe_adapter.normalize_item(raw, provider_verified=True)


if __name__ == "__main__":
    unittest.main()
