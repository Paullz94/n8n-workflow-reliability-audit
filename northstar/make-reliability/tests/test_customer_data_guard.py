import unittest
import customer_data_guard


class CustomerDataGuardTests(unittest.TestCase):
    def test_real_email_is_blocked_without_echoing_value(self):
        payload={"customer":"real.person@private-domain.be"}
        findings=customer_data_guard.inspect_sensitive_literals(payload)
        self.assertEqual(findings,[{"path":"customer","kind":"email_literal"}])
        with self.assertRaises(customer_data_guard.SensitiveDataError) as ctx:
            customer_data_guard.assert_no_sensitive_literals(payload,"context")
        self.assertNotIn("real.person@private-domain.be",str(ctx.exception))

    def test_synthetic_example_email_allowed(self):
        self.assertEqual(
            customer_data_guard.inspect_sensitive_literals({"email":"qa@example.com"}),
            []
        )

    def test_mapping_expression_allowed(self):
        self.assertEqual(
            customer_data_guard.inspect_sensitive_literals({"email":"{{1.email}}"}),
            []
        )

    def test_e164_phone_is_blocked(self):
        findings=customer_data_guard.inspect_sensitive_literals({"phone":"+32470123456"})
        self.assertEqual(findings[0]["kind"],"phone_literal")

    def test_iban_is_blocked(self):
        findings=customer_data_guard.inspect_sensitive_literals({"iban":"BE68539007547034"})
        self.assertEqual(findings[0]["kind"],"iban_literal")

    def test_valid_luhn_card_is_blocked(self):
        findings=customer_data_guard.inspect_sensitive_literals({"card":"4242 4242 4242 4242"})
        self.assertEqual(findings[0]["kind"],"payment_card_literal")

    def test_jwt_is_blocked(self):
        token="eyJabcdefghijk.abcdefghijk.abcdefghijk"
        findings=customer_data_guard.inspect_sensitive_literals({"token":token})
        self.assertEqual(findings[0]["kind"],"jwt_literal")

    def test_diagnostic_never_returns_raw_value(self):
        payload={"nested":{"email":"person@private-domain.be"}}
        result=customer_data_guard.inspect_sensitive_literals(payload)
        self.assertNotIn("value",result[0])
        self.assertEqual(result[0]["path"],"nested.email")


if __name__=="__main__":
    unittest.main()
