import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import audit_make


class AuditMakeTests(unittest.TestCase):
    def test_invalid_blueprint(self):
        findings = audit_make.scan_blueprint({"name": "x"})
        self.assertEqual(findings[0].rule, "invalid-blueprint")

    def test_write_without_handler_is_high(self):
        bp = {"flow": [{"id": 1, "module": "google-sheets:createRow", "mapper": {}}]}
        rules = {(f.rule, f.severity) for f in audit_make.scan_blueprint(bp)}
        self.assertIn(("write-without-error-handler", "high"), rules)

    def test_http_post_gets_idempotency_review(self):
        bp = {"flow": [{"id": 1, "module": "http:ActionSendData", "mapper": {"method": "POST"}}]}
        rules = {f.rule for f in audit_make.scan_blueprint(bp)}
        self.assertIn("http-write-idempotency-review", rules)
        self.assertIn("write-without-error-handler", rules)

    def test_secret_is_never_echoed(self):
        secret = "Bearer abcdefghijklmnopqrstuvwxyz123456"
        bp = {"flow": [{"id": 1, "module": "http:ActionSendData", "mapper": {"headers": secret}}]}
        findings = audit_make.scan_blueprint(bp)
        hit = next(f for f in findings if f.rule == "possible-secret-in-blueprint")
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", hit.message)

    def test_nested_route_is_scanned(self):
        bp = {
            "flow": [{
                "id": 1,
                "module": "builtin:BasicRouter",
                "routes": [{"flow": [{"id": 2, "module": "crm:updateContact", "mapper": {}}]}],
            }]
        }
        hits = [f for f in audit_make.scan_blueprint(bp) if f.rule == "write-without-error-handler"]
        self.assertEqual(len(hits), 1)
        self.assertIn("routes[0].flow", hits[0].path)

    def test_onerror_suppresses_missing_handler_finding(self):
        bp = {"flow": [{
            "id": 1,
            "module": "crm:updateContact",
            "mapper": {},
            "onerror": [{"id": 2, "module": "util:SetVariable2", "mapper": {}}],
        }]}
        rules = {f.rule for f in audit_make.scan_blueprint(bp)}
        self.assertNotIn("write-without-error-handler", rules)

    def test_designer_warning_is_surfaced(self):
        bp = {"flow": [{
            "id": 1,
            "module": "json:ParseJSON",
            "metadata": {"designer": {"messages": [{"severity": "warning", "message": "Transformer should not be last"}]}}
        }]}
        rules = {f.rule for f in audit_make.scan_blueprint(bp)}
        self.assertIn("exported-designer-message", rules)

    def test_api_blueprint_wrapper_is_supported(self):
        bp = {"blueprint": {"flow": [{"id": 1, "module": "crm:updateContact", "mapper": {}}]}}
        rules = {f.rule for f in audit_make.scan_blueprint(bp)}
        self.assertIn("write-without-error-handler", rules)

    def test_string_blueprint_wrapper_is_supported(self):
        bp = {"blueprint": '{"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}]}'}
        rules = {f.rule for f in audit_make.scan_blueprint(bp)}
        self.assertIn("write-without-error-handler", rules)

    def test_retrying_write_is_reviewed(self):
        bp = {"flow": [{
            "id": 1, "module": "crm:updateContact", "mapper": {},
            "onerror": [{"id": 2, "module": "builtin:Break", "mapper": {"retry": True, "count": "3"}}]
        }]}
        rules = {f.rule for f in audit_make.scan_blueprint(bp)}
        self.assertIn("retrying-write-idempotency-review", rules)
        self.assertNotIn("write-without-error-handler", rules)

    def test_scenario_safety_settings_are_reviewed(self):
        bp = {
            "flow": [{"id": 1, "module": "crm:updateContact", "mapper": {}}],
            "metadata": {
                "instant": True,
                "scenario": {"sequential": False, "dlq": False, "dataloss": True, "confidential": True},
            },
        }
        by_rule = {f.rule: f.severity for f in audit_make.scan_blueprint(bp)}
        self.assertEqual(by_rule["concurrency-review"], "medium")
        self.assertEqual(by_rule["incomplete-executions-disabled-review"], "medium")
        self.assertEqual(by_rule["data-loss-enabled"], "high")
        self.assertEqual(by_rule["confidential-observability-review"], "low")

    def test_skip_handler_on_write_is_high_risk(self):
        bp = {"flow": [{
            "id": 1, "module": "crm:updateContact", "mapper": {},
            "onerror": [{"id": 2, "module": "builtin:Ignore", "mapper": {}}]
        }]}
        by_rule = {f.rule: f.severity for f in audit_make.scan_blueprint(bp)}
        self.assertEqual(by_rule["write-skip-handler-data-loss-review"], "high")

    def test_resume_handler_on_write_is_high_risk(self):
        bp = {"flow": [{
            "id": 1, "module": "crm:updateContact", "mapper": {},
            "onerror": [{"id": 2, "module": "builtin:Resume", "mapper": {"output": "fallback"}}]
        }]}
        by_rule = {f.rule: f.severity for f in audit_make.scan_blueprint(bp)}
        self.assertEqual(by_rule["write-resume-handler-silent-success-review"], "high")

    def test_commit_handler_on_write_is_partial_state_review(self):
        bp = {"flow": [{
            "id": 1, "module": "crm:updateContact", "mapper": {},
            "onerror": [{"id": 2, "module": "builtin:Commit", "mapper": {}}]
        }]}
        by_rule = {f.rule: f.severity for f in audit_make.scan_blueprint(bp)}
        self.assertEqual(by_rule["write-commit-partial-state-review"], "medium")

    def test_rollback_with_autocommit_is_reviewed(self):
        bp = {
            "flow": [{
                "id": 1, "module": "crm:updateContact", "mapper": {},
                "onerror": [{"id": 2, "module": "builtin:Rollback", "mapper": {}}]
            }],
            "metadata": {"scenario": {"autoCommit": True, "dlq": True}},
        }
        rules = {f.rule for f in audit_make.scan_blueprint(bp)}
        self.assertIn("auto-commit-recovery-review", rules)
        self.assertIn("rollback-limited-by-autocommit-review", rules)

    def test_make_webhook_url_is_treated_as_secret_like(self):
        webhook = "https://hook.eu1.make.com/abcdefghijklmnopqrstuvwxyz123456"
        bp = {"flow": [{"id": 1, "module": "http:ActionSendData", "mapper": {"url": webhook}}]}
        findings = audit_make.scan_blueprint(bp)
        hit = next(f for f in findings if f.rule == "possible-secret-in-blueprint")
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", hit.message)


if __name__ == "__main__":
    unittest.main()
