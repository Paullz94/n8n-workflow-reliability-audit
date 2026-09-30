import unittest
import package_consistency


class PackageConsistencyTests(unittest.TestCase):
    def catalog(self):
        return {
            "packages":[
                {"id":"preflight_free","price_eur":0},
                {"id":"focused_risk_check","price_eur":79},
                {"id":"data_integrity_audit","price_eur":149},
                {"id":"portfolio_release_qa","price_eur":399},
            ]
        }

    def test_valid_catalog(self):
        r=package_consistency.validate_catalog(self.catalog())
        self.assertEqual(r["package_count"],4)

    def test_price_drift_fails(self):
        c=self.catalog()
        c["packages"][1]["price_eur"]=89
        with self.assertRaises(package_consistency.PackageConsistencyError):
            package_consistency.validate_catalog(c)

    def test_missing_paid_package_fails(self):
        c=self.catalog()
        c["packages"]=[x for x in c["packages"] if x["id"]!="portfolio_release_qa"]
        with self.assertRaises(package_consistency.PackageConsistencyError):
            package_consistency.validate_catalog(c)

    def test_free_must_remain_zero(self):
        c=self.catalog()
        c["packages"][0]["price_eur"]=1
        with self.assertRaises(package_consistency.PackageConsistencyError):
            package_consistency.validate_catalog(c)


if __name__=="__main__":
    unittest.main()
