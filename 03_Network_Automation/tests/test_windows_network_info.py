import json
import unittest
from unittest.mock import Mock, patch

from windows_diagnostics.network_info import (
    collect_network_info,
    format_network_info,
    parse_network_configuration,
)


class ParseNetworkConfigurationTests(unittest.TestCase):
    def test_parses_multiple_adapters(self):
        payload = [
            {
                "InterfaceAlias": "Ethernet",
                "InterfaceIndex": 7,
                "IPv4Address": ["192.168.1.20"],
                "DefaultGateway": ["192.168.1.1"],
                "DNSServers": ["192.168.1.1", "1.1.1.1"],
            },
            {
                "InterfaceAlias": "Wi-Fi",
                "InterfaceIndex": 12,
                "IPv4Address": "192.168.1.21",
                "DefaultGateway": None,
                "DNSServers": [],
            },
        ]
        result = parse_network_configuration(json.dumps(payload))

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["ipv4_addresses"], ["192.168.1.20"])
        self.assertEqual(result[0]["default_gateways"], ["192.168.1.1"])
        self.assertEqual(result[1]["ipv4_addresses"], ["192.168.1.21"])
        self.assertEqual(result[1]["default_gateways"], [])

    def test_empty_output_returns_empty_list(self):
        self.assertEqual(parse_network_configuration("  "), [])

    def test_single_adapter_object_is_normalized_to_list(self):
        payload = {
            "InterfaceAlias": "Ethernet",
            "InterfaceIndex": 3,
            "IPv4Address": "10.0.0.5",
            "DefaultGateway": "10.0.0.1",
            "DNSServers": "10.0.0.1",
        }
        result = parse_network_configuration(json.dumps(payload))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["dns_servers"], ["10.0.0.1"])


class CollectNetworkInfoTests(unittest.TestCase):
    @patch("windows_diagnostics.network_info.platform.system", return_value="Linux")
    def test_non_windows_is_reported_as_unsupported(self, _system):
        result = collect_network_info()
        self.assertEqual(result["status"], "UNSUPPORTED")
        self.assertEqual(result["adapters"], [])

    @patch("windows_diagnostics.network_info.subprocess.run")
    @patch("windows_diagnostics.network_info.platform.system", return_value="Windows")
    def test_collects_windows_network_configuration(self, _system, run):
        run.return_value = Mock(
            returncode=0,
            stdout=json.dumps({
                "InterfaceAlias": "Ethernet",
                "InterfaceIndex": 4,
                "IPv4Address": ["192.168.0.10"],
                "DefaultGateway": ["192.168.0.1"],
                "DNSServers": ["192.168.0.1"],
            }),
            stderr="",
        )
        result = collect_network_info()

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["adapters"][0]["interface_alias"], "Ethernet")
        self.assertEqual(result["adapters"][0]["ipv4_addresses"], ["192.168.0.10"])
        self.assertIn("powershell.exe", run.call_args.args[0][0])

    @patch("windows_diagnostics.network_info.subprocess.run")
    @patch("windows_diagnostics.network_info.platform.system", return_value="Windows")
    def test_powerShell_failure_is_returned_without_crashing(self, _system, run):
        run.return_value = Mock(returncode=1, stdout="", stderr="Access denied")
        result = collect_network_info()
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("Access denied", result["error"])

    @patch("windows_diagnostics.network_info.subprocess.run", side_effect=FileNotFoundError("missing"))
    @patch("windows_diagnostics.network_info.platform.system", return_value="Windows")
    def test_missing_powershell_is_handled(self, _system, _run):
        result = collect_network_info()
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("FileNotFoundError", result["error"])

    def test_formats_network_report(self):
        result = {
            "status": "SUCCESS",
            "adapters": [{
                "interface_alias": "Ethernet",
                "interface_index": 4,
                "ipv4_addresses": ["192.168.0.10"],
                "default_gateways": ["192.168.0.1"],
                "dns_servers": ["1.1.1.1"],
            }],
            "error": None,
        }
        report = format_network_info(result)
        self.assertIn("Ethernet", report)
        self.assertIn("192.168.0.1", report)
        self.assertIn("1.1.1.1", report)


if __name__ == "__main__":
    unittest.main()
