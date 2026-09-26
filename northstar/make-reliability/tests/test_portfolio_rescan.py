import unittest
import portfolio_rescan


class PortfolioRescanTests(unittest.TestCase):
    def pair(self,name):
        before={"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}]}
        after={"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Break","mapper":{}}]}]}
        return (name,before,after)

    def test_combines_three_pairs(self):
        r=portfolio_rescan.compare_portfolio([self.pair("A"),self.pair("B"),self.pair("C")])
        self.assertEqual(r["scenario_count"],3)
        self.assertGreaterEqual(r["totals"]["resolved"],3)

    def test_rejects_four_pairs(self):
        with self.assertRaises(portfolio_rescan.PortfolioRescanError):
            portfolio_rescan.compare_portfolio([self.pair("A"),self.pair("B"),self.pair("C"),self.pair("D")])

    def test_secret_stops_entire_portfolio(self):
        before={"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}]}
        after={"flow":[{"id":1,"module":"http:ActionSendData","mapper":{"headers":"Bearer abcdefghijklmnopqrstuvwxyz123456"}}]}
        with self.assertRaises(portfolio_rescan.PortfolioRescanError):
            portfolio_rescan.compare_portfolio([("Bad",before,after)])


if __name__=="__main__":
    unittest.main()
