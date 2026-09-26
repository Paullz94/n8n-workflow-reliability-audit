import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class SiteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.privacy = (ROOT / "privacy.html").read_text(encoding="utf-8")
        cls.engine = (ROOT / "BUSINESS_ENGINE.md").read_text(encoding="utf-8")

    def test_local_scanner_contract_is_present(self):
        self.assertIn('id="file"', self.index)
        self.assertIn('id="scanBtn"', self.index)
        self.assertIn("processed locally", self.index)
        self.assertIn("JSON.parse", self.index)
        self.assertIn("URL.createObjectURL", self.index)

    def test_prelaunch_does_not_expose_paid_checkout(self):
        self.assertIn("Pre-launch gate", self.index)
        self.assertNotIn("buy.stripe.com", self.index)
        self.assertNotIn("checkout.stripe.com", self.index)

    def test_offer_prices_match_engine(self):
        self.assertIn("€249", self.index)
        self.assertIn("€890", self.index)
        self.assertIn("EUR 249", self.engine)
        self.assertIn("EUR 890", self.engine)

    def test_privacy_discloses_local_processing_and_stripe_state(self):
        self.assertIn("parsed locally", self.privacy)
        self.assertIn("not yet enabled", self.privacy)

    def test_zero_owner_capital_rule_is_documented(self):
        self.assertIn("Owner capital budget: EUR 0", self.engine)
        self.assertIn("already actually earned and settled", self.engine)


if __name__ == "__main__":
    unittest.main()
