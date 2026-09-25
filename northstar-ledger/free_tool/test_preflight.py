import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("preflight", HERE / "preflight.py")
preflight = importlib.util.module_from_spec(SPEC)
sys.modules["preflight"] = preflight
SPEC.loader.exec_module(preflight)


class PreflightLiteTests(unittest.TestCase):
    def test_secret_is_detected_and_redacted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            secret = "sk-proj-EXAMPLEONLYABCDEFGHIJKLMNOPQRSTUV"
            (root / "app.py").write_text(f'KEY="{secret}"\n', encoding="utf-8")
            findings, count = preflight.scan(root)
            self.assertEqual(count, 1)
            hit = next(f for f in findings if f.rule == "SECRET-OPENAI")
            self.assertNotIn(secret, hit.evidence)

    def test_stripe_without_signature_check_is_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "payments.ts").write_text('import Stripe from "stripe";\n', encoding="utf-8")
            findings, _ = preflight.scan(root)
            self.assertIn("STRIPE-WEBHOOK-VERIFY", {f.rule for f in findings})

    def test_ci_directory_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "test.yml").write_text("name: test\n", encoding="utf-8")
            (root / "test_app.py").write_text("assert True\n", encoding="utf-8")
            findings, _ = preflight.scan(root)
            ids = {f.rule for f in findings}
            self.assertNotIn("CI-MISSING", ids)
            self.assertNotIn("TESTS-MISSING", ids)

    def test_firebase_open_rule_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "firestore.rules").write_text("allow read, write: if true;\n", encoding="utf-8")
            findings, _ = preflight.scan(root)
            self.assertIn("FIREBASE-OPEN", {f.rule for f in findings})

    def test_json_serialization_shape(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "app.py").write_text("print('ok')\n", encoding="utf-8")
            findings, count = preflight.scan(root)
            payload = {"version": preflight.VERSION, "files_scanned": count, "findings": [preflight.asdict(f) for f in findings]}
            encoded = json.dumps(payload)
            self.assertIn('"version": "0.1.0"', encoded)


if __name__ == "__main__":
    unittest.main()
