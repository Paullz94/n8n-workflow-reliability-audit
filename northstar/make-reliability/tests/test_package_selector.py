import unittest
import package_selector


class PackageSelectorTests(unittest.TestCase):
    def test_free_when_preflight_sufficient(self):
        r=package_selector.recommend_package(qualification_route="free_preflight_sufficient")
        self.assertEqual(r["package_id"],"preflight_free")

    def test_focused_when_one_explicit_focus(self):
        r=package_selector.recommend_package(requested_scope="focused",requested_focus="duplicates")
        self.assertEqual(r["package_id"],"focused_risk_check")
        self.assertEqual(r["price_eur"],79)

    def test_full_is_default_for_one_scenario(self):
        r=package_selector.recommend_package()
        self.assertEqual(r["package_id"],"data_integrity_audit")

    def test_portfolio_for_multiple(self):
        r=package_selector.recommend_package(scenario_count=3)
        self.assertEqual(r["package_id"],"portfolio_release_qa")

    def test_more_than_three_is_out_of_catalog(self):
        r=package_selector.recommend_package(scenario_count=4)
        self.assertEqual(r["route"],"out_of_catalog")


if __name__=="__main__":
    unittest.main()
