import unittest

import compare_rescan


class ReScanCompareTests(unittest.TestCase):
    def test_resolved_finding_is_reported(self):
        before = {"flow": [{"id": 1, "module": "crm:updateContact", "mapper": {}}]}
        after = {"flow": [{
            "id": 1,
            "module": "crm:updateContact",
            "mapper": {},
            "onerror": [{"id": 2, "module": "builtin:Break", "mapper": {}}],
        }]}
        result = compare_rescan.compare(before, after)
        rules = {x["rule"] for x in result["resolved"]}
        self.assertIn("write-without-error-handler", rules)

    def test_new_finding_is_reported(self):
        before = {"flow": [{"id": 1, "module": "json:ParseJSON", "mapper": {}}]}
        after = {"flow": [{"id": 1, "module": "crm:updateContact", "mapper": {}}]}
        result = compare_rescan.compare(before, after)
        rules = {x["rule"] for x in result["new"]}
        self.assertIn("write-without-error-handler", rules)

    def test_remaining_finding_is_reported(self):
        before = {"flow": [{"id": 1, "module": "crm:updateContact", "mapper": {}}]}
        after = {"flow": [{"id": 1, "module": "crm:updateContact", "mapper": {"x": "changed"}}]}
        result = compare_rescan.compare(before, after)
        rules = {x["rule"] for x in result["remaining"]}
        self.assertIn("write-without-error-handler", rules)

    def test_secret_in_either_version_hard_stops(self):
        before = {"flow": [{"id": 1, "module": "json:ParseJSON", "mapper": {}}]}
        after = {"flow": [{
            "id": 1,
            "module": "http:ActionSendData",
            "mapper": {"headers": "Bearer abcdefghijklmnopqrstuvwxyz123456"},
        }]}
        with self.assertRaises(compare_rescan.CompareError):
            compare_rescan.compare(before, after)

    def test_markdown_explains_static_limit(self):
        result = compare_rescan.compare(
            {"flow": [{"id": 1, "module": "crm:updateContact", "mapper": {}}]},
            {"flow": [{
                "id": 1,
                "module": "crm:updateContact",
                "mapper": {},
                "onerror": [{"id": 2, "module": "builtin:Break", "mapper": {}}],
            }]},
        )
        md = compare_rescan.render_markdown(result)
        self.assertIn("does not prove", md)

    def test_module_reorder_does_not_create_false_new_and_resolved(self):
        before = {"flow": [
            {"id": 10, "module": "crm:updateContact", "mapper": {}},
        ]}
        after = {"flow": [
            {"id": 99, "module": "json:ParseJSON", "mapper": {}},
            {"id": 10, "module": "crm:updateContact", "mapper": {}},
        ]}
        result = compare_rescan.compare(before, after)
        rules_remaining = {x["rule"] for x in result["remaining"]}
        self.assertIn("write-without-error-handler", rules_remaining)
        self.assertEqual(
            [x for x in result["new"] if x["rule"] == "write-without-error-handler"],
            [],
        )


if __name__ == "__main__":
    unittest.main()
