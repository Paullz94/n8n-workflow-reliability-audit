import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ledger_engine


class LedgerEngineTests(unittest.TestCase):
    def test_owner_test_pending_are_never_target_revenue(self):
        events = [
            {"id": "p1", "kind": "payment", "amount_eur": 149, "status": "succeeded", "provider_verified": True, "customer_class": "owner"},
            {"id": "p2", "kind": "payment", "amount_eur": 149, "status": "succeeded", "provider_verified": True, "customer_class": "external", "test": True},
            {"id": "p3", "kind": "payment", "amount_eur": 149, "status": "pending", "provider_verified": True, "customer_class": "external"},
            {"id": "p4", "kind": "payment", "amount_eur": 149, "status": "succeeded", "provider_verified": False, "customer_class": "external"},
        ]
        totals = ledger_engine.calculate(events)
        self.assertEqual(totals.verified_gross_revenue, 0.0)
        self.assertEqual(totals.eligible_payment_count, 0)

    def test_real_external_verified_payment_counts(self):
        totals = ledger_engine.calculate([
            {"id": "p1", "kind": "payment", "amount_eur": 149, "status": "succeeded", "provider_verified": True, "customer_class": "external"}
        ])
        self.assertEqual(totals.verified_gross_revenue, 149.0)
        self.assertEqual(totals.target_remaining, 851.0)
        self.assertEqual(totals.net_revenue, 149.0)

    def test_any_refund_disqualifies_whole_payment_from_target(self):
        events = [
            {"id": "p1", "kind": "payment", "amount_eur": 149, "status": "succeeded", "provider_verified": True, "customer_class": "external"},
            {"id": "r1", "kind": "refund", "payment_id": "p1", "amount_eur": 49, "status": "succeeded"},
        ]
        totals = ledger_engine.calculate(events)
        self.assertEqual(totals.verified_gross_revenue, 0.0)
        self.assertEqual(totals.provider_collected_external_gross, 149.0)
        self.assertEqual(totals.refunds, 49.0)
        self.assertEqual(totals.net_revenue, 100.0)

    def test_reinvestment_and_operating_result_are_separate(self):
        events = [
            {"id": "p1", "kind": "payment", "amount_eur": 149, "status": "settled", "provider_verified": True, "customer_class": "external"},
            {"id": "e1", "kind": "expense", "amount_eur": 20, "status": "paid", "funded_by": "business_revenue"},
            {"id": "e2", "kind": "expense", "amount_eur": 10, "status": "paid", "funded_by": "owner_capital"},
            {"id": "o1", "kind": "owner_capital", "amount_eur": 10, "status": "confirmed", "approved_by_paul": True},
        ]
        totals = ledger_engine.calculate(events)
        self.assertEqual(totals.revenue_reinvested, 20.0)
        self.assertEqual(totals.expenses, 30.0)
        self.assertEqual(totals.business_generated_cash, 129.0)
        self.assertEqual(totals.net_operating_result, 119.0)
        self.assertEqual(totals.owner_capital_injected, 10.0)
        self.assertEqual(totals.owner_reserve_uninjected, 490.0)

    def test_owner_capital_requires_explicit_approval(self):
        with self.assertRaises(ledger_engine.LedgerError):
            ledger_engine.calculate([
                {"id": "o1", "kind": "owner_capital", "amount_eur": 50, "status": "confirmed", "approved_by_paul": False}
            ])

    def test_duplicate_event_id_rejected(self):
        with self.assertRaises(ledger_engine.LedgerError):
            ledger_engine.calculate([
                {"id": "p1", "kind": "payment", "amount_eur": 49, "status": "succeeded", "provider_verified": True, "customer_class": "external"},
                {"id": "p1", "kind": "payment", "amount_eur": 49, "status": "succeeded", "provider_verified": True, "customer_class": "external"},
            ])

    def test_target_reached_only_with_unrefunded_verified_external_payments(self):
        events = []
        for i in range(7):
            events.append({"id": f"p{i}", "kind": "payment", "amount_eur": 149, "status": "succeeded", "provider_verified": True, "customer_class": "external"})
        totals = ledger_engine.calculate(events)
        self.assertEqual(totals.verified_gross_revenue, 1043.0)
        self.assertTrue(totals.target_reached)
        self.assertEqual(totals.target_remaining, 0.0)


if __name__ == "__main__":
    unittest.main()
