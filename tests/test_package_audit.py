import json
import tempfile
import unittest
from pathlib import Path

from package_audit import create_delivery_pack


ROOT = Path(__file__).resolve().parents[1]


class DeliveryPackTests(unittest.TestCase):
    def test_pack_contains_expected_files_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"
            manifest = create_delivery_pack(
                ROOT / "examples" / "unsafe_order_intake.json",
                output,
                "cs_test_example",
            )

            self.assertEqual(manifest["order_reference"], "cs_test_example")
            self.assertTrue((output / "01-audit-report.md").exists())
            self.assertTrue((output / "02-audit-report.json").exists())
            self.assertTrue((output / "03-client-summary.md").exists())
            self.assertTrue((output / "04-synthetic-verification-plan.md").exists())
            self.assertTrue((output / "MANIFEST.json").exists())
            self.assertIn("01-audit-report.md", manifest["files"])

    def test_pack_redacts_fixture_secret_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "delivery"
            create_delivery_pack(ROOT / "examples" / "unsafe_order_intake.json", output)

            combined = "\n".join(
                p.read_text(encoding="utf-8")
                for p in output.iterdir()
                if p.is_file()
            )
            self.assertNotIn("DEMO_ONLY_NOT_A_REAL_SECRET", combined)
            self.assertIn("value redacted", combined)

    def test_non_object_export_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "bad.json"
            src.write_text(json.dumps([]), encoding="utf-8")
            with self.assertRaises(ValueError):
                create_delivery_pack(src, Path(tmp) / "delivery")


if __name__ == "__main__":
    unittest.main()
