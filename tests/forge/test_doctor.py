"""Behavior tests for the standalone Forge doctor."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "forge_doctor.py"
spec = importlib.util.spec_from_file_location("forge_doctor", SCRIPT)
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class ForgeDoctorTests(unittest.TestCase):
    def test_unauthorized_network_is_not_retryable(self):
        r = doctor.classify_error("HTTP 403: Network for IP is not authorized")
        self.assertEqual(r, {"code": "unauthorized_network", "retryable": False})

    def test_error_classifier_does_not_echo_secrets(self):
        secret = "super-secret-api-token"
        self.assertNotIn(secret, str(doctor.classify_error("DNS error " + secret)))

    def test_diagnoses_common_errors(self):
        self.assertEqual(doctor.classify_error("getaddrinfo failed")["code"], "dns_failure")
        self.assertEqual(doctor.classify_error("HTTP 429")["code"], "rate_limited")
        self.assertEqual(doctor.classify_error("request timed out")["code"], "timeout")

    def test_inspection_is_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            profile = Path(td) / "not-created"
            report = doctor.inspect(profile, min_free_mb=0)
            self.assertFalse(profile.exists())
            self.assertEqual(report["status"], "healthy")
            self.assertFalse(report["runtime"]["profile_exists"])
            self.assertFalse(report["recovery"]["automatic_restart"])

    def test_threshold_causes_critical_status(self):
        with tempfile.TemporaryDirectory() as td:
            report = doctor.inspect(Path(td), min_free_mb=10**15)
            self.assertEqual(report["status"], "critical")

    def test_negative_threshold_rejected(self):
        with self.assertRaises(ValueError):
            doctor.inspect(Path("."), min_free_mb=-1)


if __name__ == "__main__":
    unittest.main()
