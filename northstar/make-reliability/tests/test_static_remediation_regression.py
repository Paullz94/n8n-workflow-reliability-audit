import unittest

import audit_make


def rules(bp):
    return {f.rule for f in audit_make.scan_blueprint(bp)}


class StaticRemediationRegressionTests(unittest.TestCase):
    def assert_clears(self, rule, before, after):
        self.assertIn(rule, rules(before), f"{rule} was not detected in before fixture")
        self.assertNotIn(rule, rules(after), f"{rule} did not clear in after fixture")

    def test_invalid_blueprint(self):
        self.assert_clears(
            "invalid-blueprint",
            {"name":"bad"},
            {"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}]},
        )

    def test_empty_flow(self):
        self.assert_clears(
            "empty-flow",
            {"flow":[]},
            {"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}]},
        )

    def test_missing_error_handler(self):
        self.assert_clears(
            "write-without-error-handler",
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}]},
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Break","mapper":{}}]}]},
        )

    def test_retrying_write(self):
        self.assert_clears(
            "retrying-write-idempotency-review",
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Break","mapper":{"retry":True}}]}]},
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Break","mapper":{"retry":False}}]}]},
        )

    def test_ignore_handler(self):
        self.assert_clears(
            "write-skip-handler-data-loss-review",
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Ignore","mapper":{}}]}]},
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Break","mapper":{}}]}]},
        )

    def test_resume_handler(self):
        self.assert_clears(
            "write-resume-handler-silent-success-review",
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Resume","mapper":{}}]}]},
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Break","mapper":{}}]}]},
        )

    def test_commit_handler(self):
        self.assert_clears(
            "write-commit-partial-state-review",
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Commit","mapper":{}}]}]},
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Break","mapper":{}}]}]},
        )

    def test_http_write_review(self):
        self.assert_clears(
            "http-write-idempotency-review",
            {"flow":[{"id":1,"module":"http:ActionSendData","mapper":{"method":"POST"}}]},
            {"flow":[{"id":1,"module":"http:ActionSendData","mapper":{"method":"GET"}}]},
        )

    def test_filtered_write(self):
        self.assert_clears(
            "filtered-write-silent-skip-review",
            {"flow":[{"id":1,"module":"crm:updateContact","filter":{"name":"gate"},"mapper":{}}]},
            {"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}]},
        )

    def test_designer_message(self):
        self.assert_clears(
            "exported-designer-message",
            {"flow":[{"id":1,"module":"json:ParseJSON","metadata":{"designer":{"messages":[{"severity":"warning","message":"demo"}]}}}]},
            {"flow":[{"id":1,"module":"json:ParseJSON","metadata":{"designer":{"messages":[]}}}]},
        )

    def test_concurrency(self):
        before={"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}],"metadata":{"instant":True,"scenario":{"sequential":False}}}
        after={"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}],"metadata":{"instant":True,"scenario":{"sequential":True}}}
        self.assert_clears("concurrency-review",before,after)

    def test_auto_commit(self):
        before={"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}],"metadata":{"scenario":{"autoCommit":True}}}
        after={"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}],"metadata":{"scenario":{"autoCommit":False}}}
        self.assert_clears("auto-commit-recovery-review",before,after)

    def test_rollback_autocommit(self):
        before={
            "flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Rollback","mapper":{}}]}],
            "metadata":{"scenario":{"autoCommit":True}}
        }
        after={
            "flow":[{"id":1,"module":"crm:updateContact","mapper":{},"onerror":[{"id":2,"module":"builtin:Rollback","mapper":{}}]}],
            "metadata":{"scenario":{"autoCommit":False}}
        }
        self.assert_clears("rollback-limited-by-autocommit-review",before,after)

    def test_incomplete_executions(self):
        before={"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}],"metadata":{"scenario":{"dlq":False}}}
        after={"flow":[{"id":1,"module":"crm:updateContact","mapper":{}}],"metadata":{"scenario":{"dlq":True}}}
        self.assert_clears("incomplete-executions-disabled-review",before,after)

    def test_data_loss(self):
        before={"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}],"metadata":{"scenario":{"dataloss":True}}}
        after={"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}],"metadata":{"scenario":{"dataloss":False}}}
        self.assert_clears("data-loss-enabled",before,after)

    def test_confidential_observability(self):
        before={"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}],"metadata":{"scenario":{"confidential":True}}}
        after={"flow":[{"id":1,"module":"json:ParseJSON","mapper":{}}],"metadata":{"scenario":{"confidential":False}}}
        self.assert_clears("confidential-observability-review",before,after)

    def test_secret(self):
        before={"flow":[{"id":1,"module":"http:ActionSendData","mapper":{"headers":"Bearer abcdefghijklmnopqrstuvwxyz123456"}}]}
        after={"flow":[{"id":1,"module":"http:ActionSendData","mapper":{"headers":"[REDACTED]"}}]}
        self.assert_clears("possible-secret-in-blueprint",before,after)


if __name__=="__main__":
    unittest.main()
