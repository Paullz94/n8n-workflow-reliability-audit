import unittest
import repair_case


class RepairCaseTests(unittest.TestCase):
    def test_case_stays_open_if_one_issue_is_open(self):
        r=repair_case.evaluate_case([
            {"rule":"a","customer_status":"closed_verified"},
            {"rule":"b","customer_status":"open"},
        ])
        self.assertEqual(r["case_status"],"open")
        self.assertFalse(r["can_tell_customer_complete"])

    def test_case_closes_only_when_all_are_verified(self):
        r=repair_case.evaluate_case([
            {"rule":"a","customer_status":"closed_verified"},
            {"rule":"b","customer_status":"closed_verified"},
        ])
        self.assertEqual(r["case_status"],"closed_verified")
        self.assertTrue(r["can_tell_customer_complete"])


if __name__=="__main__":
    unittest.main()
