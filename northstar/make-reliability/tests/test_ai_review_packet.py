import unittest

import ai_review_packet


class AIReviewPacketTests(unittest.TestCase):
    def test_packet_excludes_mapper_payload_values(self):
        private_value = "PRIVATE-MAPPER-VALUE-999"
        bp = {
            "flow": [{
                "id": 1,
                "module": "crm:updateContact",
                "mapper": {"private_reference": private_value},
            }]
        }
        packet = ai_review_packet.make_packet(
            bp,
            {"scenario_name": "Orders", "business_goal": "Update CRM reliably"},
        )
        rendered = __import__("json").dumps(packet)
        self.assertNotIn(private_value, rendered)
        self.assertIn("write-without-error-handler", rendered)

    def test_context_is_allowlisted(self):
        packet = ai_review_packet.make_packet(
            {"flow": [{"id": 1, "module": "crm:updateContact", "mapper": {}}]},
            {
                "scenario_name": "Orders",
                "business_goal": "Update CRM",
                "api_key": "should-never-appear",
            },
        )
        self.assertNotIn("api_key", packet["context"])

    def test_secret_finding_blocks_packet(self):
        bp = {
            "flow": [{
                "id": 1,
                "module": "http:ActionSendData",
                "mapper": {"headers": "Bearer abcdefghijklmnopqrstuvwxyz123456"},
            }]
        }
        with self.assertRaises(ai_review_packet.PacketError):
            ai_review_packet.make_packet(
                bp,
                {"scenario_name": "Demo", "business_goal": "Demo"},
            )

    def test_official_reference_is_carried_into_packet(self):
        bp = {
            "flow": [{
                "id": 1,
                "module": "crm:updateContact",
                "mapper": {},
                "onerror": [{"id": 2, "module": "builtin:Ignore", "mapper": {}}],
            }]
        }
        packet = ai_review_packet.make_packet(
            bp,
            {"scenario_name": "Demo", "business_goal": "Update CRM"},
        )
        hit = next(x for x in packet["findings"] if x["rule"] == "write-skip-handler-data-loss-review")
        self.assertEqual(hit["official_reference"], "https://help.make.com/skip-error-handler")

    def test_personal_email_literal_blocks_packet(self):
        bp={"flow":[{"id":1,"module":"crm:updateContact","mapper":{"email":"person@private-domain.be"}}]}
        with self.assertRaises(ai_review_packet.PacketError):
            ai_review_packet.make_packet(
                bp,
                {"scenario_name":"Demo","business_goal":"Update CRM"},
            )

    def test_case_scope_id_is_carried_without_order_reference(self):
        import case_isolation
        case_id=case_isolation.case_scope_id("cs_live_customer_123")
        packet=ai_review_packet.make_packet(
            {"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}]},
            {"scenario_name":"Demo","business_goal":"Parse safely"},
            case_scope_id=case_id,
        )
        self.assertEqual(packet["case_scope_id"],case_id)
        self.assertNotIn("cs_live_customer_123",__import__("json").dumps(packet))


if __name__ == "__main__":
    unittest.main()
