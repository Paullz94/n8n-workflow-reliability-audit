import unittest

import portfolio_qa


class PortfolioQATests(unittest.TestCase):
    def scenario(self,name,module):
        return (
            name,
            {"flow":[{"id":1,"module":module,"mapper":{}}]},
            {"scenario_name":name,"business_goal":"Process reliably"},
        )

    def test_supports_three(self):
        r=portfolio_qa.build_portfolio([
            self.scenario("A","crm:updateContact"),
            self.scenario("B","crm:updateContact"),
            self.scenario("C","json:ParseJSON"),
        ])
        self.assertEqual(r["scenario_count"],3)
        self.assertIn("write-without-error-handler",r["recurring_rules"])

    def test_rejects_more_than_three(self):
        with self.assertRaises(portfolio_qa.PortfolioError):
            portfolio_qa.build_portfolio([
                self.scenario("A","json:ParseJSON"),
                self.scenario("B","json:ParseJSON"),
                self.scenario("C","json:ParseJSON"),
                self.scenario("D","json:ParseJSON"),
            ])

    def test_secret_in_any_scenario_stops_entire_portfolio(self):
        bad=(
            "Bad",
            {"flow":[{"id":1,"module":"http:ActionSendData","mapper":{"headers":"Bearer abcdefghijklmnopqrstuvwxyz123456"}}]},
            {"scenario_name":"Bad","business_goal":"Demo"},
        )
        with self.assertRaises(portfolio_qa.PortfolioError):
            portfolio_qa.build_portfolio([bad])


if __name__=="__main__":
    unittest.main()
