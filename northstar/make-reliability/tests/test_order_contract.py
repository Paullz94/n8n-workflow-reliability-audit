import unittest
import order_contract


class OrderContractTests(unittest.TestCase):
    def base(self, package="data_integrity_audit", amount=14900):
        return {
            "provider_verified": True,
            "livemode": True,
            "session_id": "cs_live_customer_123",
            "payment_status": "paid",
            "currency": "eur",
            "amount_total": amount,
            "metadata": {"pcflows_package": package},
            "owner_or_test": False,
        }

    def test_valid_full_audit(self):
        r=order_contract.validate_paid_order(self.base())
        self.assertEqual(r["package_id"],"data_integrity_audit")

    def test_focused_amount(self):
        r=order_contract.validate_paid_order(self.base("focused_risk_check",7900))
        self.assertEqual(r["amount_total"],7900)

    def test_portfolio_amount(self):
        r=order_contract.validate_paid_order(self.base("portfolio_release_qa",39900))
        self.assertEqual(r["package_id"],"portfolio_release_qa")

    def test_rejects_amount_mismatch(self):
        with self.assertRaises(order_contract.OrderContractError):
            order_contract.validate_paid_order(self.base("focused_risk_check",14900))

    def test_rejects_unverified(self):
        x=self.base(); x["provider_verified"]=False
        with self.assertRaises(order_contract.OrderContractError):
            order_contract.validate_paid_order(x)

    def test_rejects_test_owner(self):
        x=self.base(); x["owner_or_test"]=True
        with self.assertRaises(order_contract.OrderContractError):
            order_contract.validate_paid_order(x)

    def test_rejects_unpaid(self):
        x=self.base(); x["payment_status"]="unpaid"
        with self.assertRaises(order_contract.OrderContractError):
            order_contract.validate_paid_order(x)


if __name__=="__main__":
    unittest.main()
