import unittest
from unittest.mock import patch

from windows_diagnostics.system_info import (
    collect_system_info,
    format_system_info,
    identify_windows,
)


class IdentifyWindowsTests(unittest.TestCase):
    def test_identifies_windows_11_by_build(self):
        result = identify_windows("Windows", "10", "10.0.22631")
        self.assertEqual(result["name"], "Windows 11")
        self.assertTrue(result["supported"])

    def test_identifies_windows_10_by_build(self):
        result = identify_windows("Windows", "10", "10.0.19045")
        self.assertEqual(result["name"], "Windows 10")
        self.assertTrue(result["supported"])

    def test_does_not_claim_linux_is_supported(self):
        result = identify_windows("Linux", "6.8", "6.8.0")
        self.assertFalse(result["supported"])
        self.assertIn("Linux", result["name"])

    def test_unknown_windows_build_is_not_guessed(self):
        result = identify_windows("Windows", "10", "unknown")
        self.assertFalse(result["supported"])
        self.assertIn("build not identified", result["name"])


class CollectSystemInfoTests(unittest.TestCase):
    @patch("windows_diagnostics.system_info.shutil.which")
    @patch("windows_diagnostics.system_info.platform.python_version", return_value="3.12.0")
    @patch("windows_diagnostics.system_info.platform.machine", return_value="AMD64")
    @patch("windows_diagnostics.system_info.platform.version", return_value="10.0.22631")
    @patch("windows_diagnostics.system_info.platform.release", return_value="10")
    @patch("windows_diagnostics.system_info.platform.system", return_value="Windows")
    def test_collects_details_and_command_availability(
        self, _system, _release, _version, _machine, _python, which
    ):
        which.side_effect = lambda command: f"C:/Windows/System32/{command}.exe"
        result = collect_system_info()

        self.assertEqual(result["windows"]["name"], "Windows 11")
        self.assertTrue(result["windows"]["supported"])
        self.assertTrue(all(result["commands"].values()))

    @patch("windows_diagnostics.system_info.shutil.which", return_value=None)
    @patch("windows_diagnostics.system_info.platform.python_version", return_value="3.12.0")
    @patch("windows_diagnostics.system_info.platform.machine", return_value="AMD64")
    @patch("windows_diagnostics.system_info.platform.version", return_value="10.0.19045")
    @patch("windows_diagnostics.system_info.platform.release", return_value="10")
    @patch("windows_diagnostics.system_info.platform.system", return_value="Windows")
    def test_reports_missing_commands(
        self, _system, _release, _version, _machine, _python, _which
    ):
        result = collect_system_info()
        self.assertFalse(any(result["commands"].values()))

    def test_formats_system_report(self):
        info = {
            "operating_system": "Windows",
            "windows": {
                "name": "Windows 11",
                "supported": True,
                "build": 22631,
                "reason": None,
            },
            "windows_release": "10",
            "windows_version": "10.0.22631",
            "architecture": "AMD64",
            "python_version": "3.12.0",
            "commands": {
                "ipconfig": True,
                "ping": True,
                "nslookup": False,
                "tracert": True,
            },
        }
        report = format_system_info(info)
        self.assertIn("Detected version: Windows 11", report)
        self.assertIn("nslookup: Not found", report)


if __name__ == "__main__":
    unittest.main()
