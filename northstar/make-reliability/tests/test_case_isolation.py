import pathlib
import tempfile
import unittest

import case_isolation


class CaseIsolationTests(unittest.TestCase):
    def test_order_ref_becomes_pseudonymous_case_id(self):
        case_id=case_isolation.case_scope_id("cs_live_customer_123")
        self.assertTrue(case_id.startswith("pcfcase_"))
        self.assertNotIn("customer",case_id)
        self.assertNotIn("cs_live",case_id)

    def test_different_orders_have_different_case_ids(self):
        self.assertNotEqual(
            case_isolation.case_scope_id("cs_live_a"),
            case_isolation.case_scope_id("cs_live_b"),
        )

    def test_cross_case_document_is_rejected(self):
        a=case_isolation.case_scope_id("cs_live_a")
        b=case_isolation.case_scope_id("cs_live_b")
        with self.assertRaises(case_isolation.CaseIsolationError):
            case_isolation.assert_document_bound_to_case({"case_scope_id":b},a)

    def test_safe_case_dir_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            case_id=case_isolation.case_scope_id("cs_live_a")
            path=case_isolation.safe_case_dir(root,case_id)
            self.assertEqual(path.parent,root.resolve())


if __name__=="__main__":
    unittest.main()
