import unittest

import refund_policy


class RefundPolicyTests(unittest.TestCase):
    def test_duplicate_charge_auto_refunds(self):
        d=refund_policy.decide_refund(
            reason_code="duplicate_charge",
            payment_succeeded=True,
            already_refunded=False,
            substantive_delivery_started=True,
            custom_report_delivered=True,
        )
        self.assertTrue(d.autonomous)
        self.assertEqual(d.action, "refund")
        self.assertEqual(d.amount_mode, "full")

    def test_out_of_scope_before_work_auto_refunds(self):
        d=refund_policy.decide_refund(
            reason_code="out_of_scope_before_delivery",
            payment_succeeded=True,
            already_refunded=False,
            substantive_delivery_started=False,
            custom_report_delivered=False,
        )
        self.assertTrue(d.autonomous)
        self.assertEqual(d.action, "refund")

    def test_changed_mind_after_delivery_does_not_auto_refund(self):
        d=refund_policy.decide_refund(
            reason_code="customer_changed_mind_after_custom_report",
            payment_succeeded=True,
            already_refunded=False,
            substantive_delivery_started=True,
            custom_report_delivered=True,
        )
        self.assertFalse(d.autonomous)

    def test_no_successful_payment_needs_no_refund(self):
        d=refund_policy.decide_refund(
            reason_code="duplicate_charge",
            payment_succeeded=False,
            already_refunded=False,
            substantive_delivery_started=False,
            custom_report_delivered=False,
        )
        self.assertTrue(d.autonomous)
        self.assertEqual(d.action, "no_refund_needed")


if __name__ == "__main__":
    unittest.main()
