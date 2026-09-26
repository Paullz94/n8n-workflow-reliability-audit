import unittest

import reconcile_stripe_snapshot


class ReconcileStripeSnapshotTests(unittest.TestCase):
    def payment_event(self):
        return {
            "type": "payment_intent.succeeded",
            "data": {"object": {
                "id": "pi_external_1",
                "object": "payment_intent",
                "amount_received": 14900,
                "currency": "eur",
                "livemode": True,
                "metadata": {},
                "status": "succeeded",
            }},
        }

    def test_requires_trusted_provider_snapshot(self):
        with self.assertRaises(reconcile_stripe_snapshot.ReconcileError):
            reconcile_stripe_snapshot.reconcile([], [self.payment_event()], provider_verified=False)

    def test_adds_real_final_payment_once(self):
        merged, summary = reconcile_stripe_snapshot.reconcile(
            [], [self.payment_event()], provider_verified=True
        )
        self.assertEqual(len(merged), 1)
        self.assertEqual(summary["added_event_ids"], ["pi_external_1"])
        self.assertEqual(summary["totals"]["verified_gross_revenue"], 149.0)

        merged2, summary2 = reconcile_stripe_snapshot.reconcile(
            merged, [self.payment_event()], provider_verified=True
        )
        self.assertEqual(len(merged2), 1)
        self.assertEqual(summary2["added_event_ids"], [])
        self.assertEqual(summary2["unchanged_event_ids"], ["pi_external_1"])

    def test_pending_refund_is_not_journaled(self):
        snapshot = [
            self.payment_event(),
            {
                "type": "refund.created",
                "data": {"object": {
                    "id": "re_pending_1",
                    "object": "refund",
                    "amount": 4900,
                    "currency": "eur",
                    "payment_intent": "pi_external_1",
                    "status": "pending",
                }},
            },
        ]
        merged, summary = reconcile_stripe_snapshot.reconcile(
            [], snapshot, provider_verified=True
        )
        self.assertEqual([event["id"] for event in merged], ["pi_external_1"])
        self.assertEqual(summary["ignored_nonfinal_count"], 1)

    def test_completed_refund_disqualifies_target_payment(self):
        snapshot = [
            self.payment_event(),
            {
                "type": "refund.updated",
                "data": {"object": {
                    "id": "re_success_1",
                    "object": "refund",
                    "amount": 4900,
                    "currency": "eur",
                    "payment_intent": "pi_external_1",
                    "status": "succeeded",
                }},
            },
        ]
        merged, summary = reconcile_stripe_snapshot.reconcile(
            [], snapshot, provider_verified=True
        )
        self.assertEqual(len(merged), 2)
        self.assertEqual(summary["totals"]["verified_gross_revenue"], 0.0)
        self.assertEqual(summary["totals"]["refunds"], 49.0)

    def test_conflicting_existing_event_hard_stops(self):
        existing = [{
            "id": "pi_external_1",
            "kind": "payment",
            "currency": "EUR",
            "amount_eur": 99.0,
            "status": "succeeded",
            "provider_verified": True,
            "customer_class": "external",
            "test": False,
            "provider": "stripe",
        }]
        with self.assertRaises(reconcile_stripe_snapshot.ReconcileError):
            reconcile_stripe_snapshot.reconcile(
                existing, [self.payment_event()], provider_verified=True
            )


if __name__ == "__main__":
    unittest.main()
