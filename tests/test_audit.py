import json
import unittest
from pathlib import Path

from audit import audit_workflow, failure_threshold_met, render_markdown


ROOT = Path(__file__).resolve().parents[1]


class PublicPortfolioTests(unittest.TestCase):
    def load(self, name: str):
        return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))

    def rule_ids(self, workflow):
        return {item["rule_id"] for item in audit_workflow(workflow)["findings"]}

    def test_seeded_secret_is_reported_but_never_rendered(self):
        result = audit_workflow(self.load("unsafe_order_intake.json"))
        self.assertIn("SEC-003", {item["rule_id"] for item in result["findings"]})
        self.assertNotIn("DEMO_ONLY_NOT_A_REAL_SECRET", render_markdown(result))

    def test_hardened_counterpart_has_no_critical_or_high_findings(self):
        result = audit_workflow(self.load("hardened_order_intake.json"))
        self.assertEqual(result["summary"]["critical"], 0)
        self.assertEqual(result["summary"]["high"], 0)
        self.assertEqual(result["analysis"]["unguarded_side_effect_nodes"], [])

    def test_scheduled_sync_flags_recovery_and_idempotency(self):
        result = audit_workflow(self.load("unsafe_scheduled_sync.json"))
        rules = {item["rule_id"] for item in result["findings"]}
        self.assertTrue({"RECOVERY-001", "RECOVERY-002", "RECOVERY-003", "RECOVERY-004", "DATA-001"}.issubset(rules))
        self.assertEqual(result["analysis"]["unguarded_side_effect_nodes"], ["Append CRM Rows"])

    def test_duplicate_names_are_rejected(self):
        result = audit_workflow(self.load("unsafe_duplicate_nodes.json"))
        self.assertIn("STRUCT-002", {item["rule_id"] for item in result["findings"]})

    def test_missing_workflow_and_node_ids_are_rejected(self):
        result = audit_workflow({
            "name": "No IDs",
            "active": False,
            "nodes": [{"name": "Manual Trigger", "type": "n8n-nodes-base.manualTrigger", "parameters": {}}],
            "connections": {},
        })
        rules = {item["rule_id"] for item in result["findings"]}
        self.assertTrue({"STRUCT-004", "STRUCT-005"}.issubset(rules))

    def test_runtime_smoke_fixture_has_no_static_release_blocker(self):
        result = audit_workflow(self.load("runtime_smoke.json"))
        self.assertEqual(result["summary"]["critical"], 0)
        self.assertEqual(result["summary"]["high"], 0)

    def test_http_get_is_not_treated_as_side_effect(self):
        workflow = {
            "name": "Read Only HTTP",
            "id": "wf-read-only",
            "active": True,
            "versionId": "v1",
            "nodes": [
                {
                    "id": "trigger",
                    "name": "Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "parameters": {},
                },
                {
                    "id": "fetch",
                    "name": "Fetch Records",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {"method": "GET", "url": "https://example.invalid", "options": {"timeout": 1000}},
                    "retryOnFail": True,
                },
            ],
            "connections": {
                "Schedule Trigger": {"main": [[{"node": "Fetch Records", "type": "main", "index": 0}]]}
            },
            "settings": {"errorWorkflow": "err"},
        }
        result = audit_workflow(workflow)
        self.assertNotIn("DATA-001", {item["rule_id"] for item in result["findings"]})
        self.assertEqual(result["analysis"]["side_effect_nodes"], [])

    def test_guard_on_other_branch_does_not_mask_unguarded_write(self):
        workflow = {
            "name": "Split Guard",
            "id": "wf-split-guard",
            "active": True,
            "versionId": "v1",
            "nodes": [
                {
                    "id": "trigger",
                    "name": "Authenticated Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "parameters": {"authentication": "headerAuth"},
                },
                {
                    "id": "guard",
                    "name": "Check Duplicate Event",
                    "type": "n8n-nodes-base.noOp",
                    "parameters": {},
                },
                {
                    "id": "write",
                    "name": "Create Order",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {"method": "POST", "url": "https://example.invalid", "options": {"timeout": 1000}},
                },
            ],
            "connections": {
                "Authenticated Webhook": {
                    "main": [[
                        {"node": "Check Duplicate Event", "type": "main", "index": 0},
                        {"node": "Create Order", "type": "main", "index": 0},
                    ]]
                }
            },
            "settings": {"errorWorkflow": "err"},
        }
        result = audit_workflow(workflow)
        self.assertIn("DATA-001", {item["rule_id"] for item in result["findings"]})
        self.assertEqual(result["analysis"]["unguarded_side_effect_nodes"], ["Create Order"])

    def test_retrying_write_without_guard_gets_specific_finding(self):
        workflow = {
            "name": "Retrying Write",
            "id": "wf-retrying-write",
            "active": True,
            "versionId": "v1",
            "nodes": [
                {
                    "id": "trigger",
                    "name": "Manual Trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "parameters": {},
                },
                {
                    "id": "write",
                    "name": "Create Order",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {"method": "POST", "url": "https://example.invalid", "options": {"timeout": 1000}},
                    "retryOnFail": True,
                },
            ],
            "connections": {
                "Manual Trigger": {"main": [[{"node": "Create Order", "type": "main", "index": 0}]]}
            },
            "settings": {"errorWorkflow": "err"},
        }
        rules = self.rule_ids(workflow)
        self.assertIn("DATA-001", rules)
        self.assertIn("DATA-002", rules)

    def test_guard_before_retrying_write_suppresses_duplicate_findings(self):
        workflow = {
            "name": "Guarded Retry",
            "id": "wf-guarded-retry",
            "active": True,
            "versionId": "v1",
            "nodes": [
                {
                    "id": "trigger",
                    "name": "Manual Trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "parameters": {},
                },
                {
                    "id": "guard",
                    "name": "Check Duplicate Event",
                    "type": "n8n-nodes-base.redis",
                    "parameters": {"operation": "get"},
                },
                {
                    "id": "write",
                    "name": "Create Order",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {"method": "POST", "url": "https://example.invalid", "options": {"timeout": 1000}},
                    "retryOnFail": True,
                },
            ],
            "connections": {
                "Manual Trigger": {"main": [[{"node": "Check Duplicate Event", "type": "main", "index": 0}]]},
                "Check Duplicate Event": {"main": [[{"node": "Create Order", "type": "main", "index": 0}]]},
            },
            "settings": {"errorWorkflow": "err"},
        }
        result = audit_workflow(workflow)
        rules = {item["rule_id"] for item in result["findings"]}
        self.assertNotIn("DATA-001", rules)
        self.assertNotIn("DATA-002", rules)
        self.assertEqual(result["analysis"]["unguarded_side_effect_nodes"], [])

    def test_broken_connection_references_are_explicit(self):
        workflow = {
            "name": "Broken Graph",
            "id": "wf-broken-graph",
            "active": False,
            "versionId": "v1",
            "nodes": [
                {
                    "id": "only",
                    "name": "Only Node",
                    "type": "n8n-nodes-base.noOp",
                    "parameters": {},
                }
            ],
            "connections": {
                "Ghost Source": {"main": [[{"node": "Only Node", "type": "main", "index": 0}]]},
                "Only Node": {"main": [[{"node": "Ghost Target", "type": "main", "index": 0}]]},
            },
            "settings": {},
        }
        rules = self.rule_ids(workflow)
        self.assertIn("GRAPH-002", rules)
        self.assertIn("GRAPH-003", rules)

    def test_failure_threshold_respects_severity_order(self):
        result = {
            "findings": [
                {"severity": "high"},
                {"severity": "low"},
            ]
        }
        self.assertFalse(failure_threshold_met(result, "none"))
        self.assertFalse(failure_threshold_met(result, "critical"))
        self.assertTrue(failure_threshold_met(result, "high"))
        self.assertTrue(failure_threshold_met(result, "medium"))
        self.assertTrue(failure_threshold_met(result, "low"))


if __name__ == "__main__":
    unittest.main()
