import unittest

import support_router


class SupportRouterTests(unittest.TestCase):
    def test_price(self):
        r=support_router.route_message("Price?", "How much does the audit cost?")
        self.assertEqual(r.intent, "price")
        self.assertTrue(r.autonomous)

    def test_privacy(self):
        r=support_router.route_message("Blueprint", "Can I send my API key with it?")
        self.assertEqual(r.intent, "privacy")
        self.assertIn("do not send", support_router.render_reply(r).lower())

    def test_implementation_boundary(self):
        r=support_router.route_message("Can you fix it?", "Can you implement all changes for me?")
        self.assertEqual(r.intent, "implementation")
        self.assertIn("not", support_router.render_reply(r).lower())

    def test_certification_boundary(self):
        r=support_router.route_message("SOC 2", "Can you certify this workflow?")
        self.assertEqual(r.intent, "security_certification")

    def test_unknown_asks_one_bounded_clarification(self):
        r=support_router.route_message("Hello", "I have a question")
        self.assertEqual(r.intent, "unknown")
        self.assertTrue(r.autonomous)


if __name__ == "__main__":
    unittest.main()
