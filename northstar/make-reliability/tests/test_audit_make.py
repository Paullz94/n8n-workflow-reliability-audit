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


if __name__ == "__main__":
    unittest.main()
