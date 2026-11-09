
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

import network_diagnostic_report as report
import interface_parser
import multi_device_automation as multi

class NetworkProjectTests(unittest.TestCase):

    def test_interface_parser_sample(self):
        raw = (BASE / "raw_output.txt").read_text(encoding="utf-8")
        found = interface_parser.parse_interfaces(raw)
        names = {item["interface"] for item in found}
        self.assertEqual(names, {"GigabitEthernet0/0", "Loopback0"})

    def test_offline_report(self):
        result = report.build_report(offline=True)
        self.assertEqual(result["mode"], "offline_demo")
        self.assertEqual(result["summary"]["checks_total"], 1)
        self.assertEqual(result["summary"]["checks_failed"], 0)

    def test_report_files_created(self):
        result = report.build_report(offline=True)
        with tempfile.TemporaryDirectory() as folder:
            original = report.OUTPUT
            try:
                report.OUTPUT = Path(folder)
                paths = report.write_reports(result)
                for path in paths:
                    self.assertTrue(path.is_file())
                loaded = json.loads(paths[0].read_text())
                self.assertEqual(loaded["mode"], "offline_demo")
            finally:
                report.OUTPUT = original

    def test_dns_failure_is_reported(self):
        with patch.object(report.socket, "getaddrinfo",
                          side_effect=OSError("test failure")):
            result = report.dns_check("invalid.example")
        self.assertEqual(result["status"], "FAILED")

    def test_devices_configuration_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "devices.json"
            path.write_text(json.dumps([
                {"host": "192.0.2.10", "device_type": "cisco_ios"}
            ]))
            original = multi.DEVICES_FILE
            try:
                multi.DEVICES_FILE = path
                devices = multi.load_devices()
                self.assertEqual(len(devices), 1)
            finally:
                multi.DEVICES_FILE = original

    def test_missing_device_configuration(self):
        original = multi.DEVICES_FILE
        try:
            multi.DEVICES_FILE = Path("/tmp/nonexistent_network_devices.json")
            with self.assertRaises(FileNotFoundError):
                multi.load_devices()
        finally:
            multi.DEVICES_FILE = original

    def test_multi_device_connection_uses_mock(self):
        device = {"host": "192.0.2.10", "device_type": "cisco_ios"}
        mock_connection = MagicMock()
        mock_connection.send_command.return_value = "sample output"

        with patch.dict("os.environ", {
            "NETWORK_USERNAME": "test_user",
            "NETWORK_PASSWORD": "test_password"
        }):
            with patch.object(multi, "ConnectHandler",
                              return_value=mock_connection) as connect:
                multi.connect_to_device(device)

        connect.assert_called_once()
        mock_connection.send_command.assert_called_once()
        mock_connection.disconnect.assert_called_once()

    def test_missing_credentials_prevent_connection(self):
        device = {"host": "192.0.2.10", "device_type": "cisco_ios"}
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(multi, "ConnectHandler") as connect:
                multi.connect_to_device(device)
        connect.assert_not_called()

if __name__ == "__main__":
    unittest.main()
