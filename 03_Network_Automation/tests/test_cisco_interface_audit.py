import csv
import json
import tempfile
import unittest
from cisco_interface_audit.analyzer import build_audit, parse_interface_output, write_reports

SAMPLE = """Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0      192.168.1.1     YES manual up                    up
GigabitEthernet0/1      unassigned      YES unset  administratively down down
GigabitEthernet0/2      10.10.10.1      YES manual down                  down
Vlan10                  192.168.10.1   YES manual up                    down
"""

class CiscoInterfaceAuditTests(unittest.TestCase):
    def test_parses_all_interface_states(self):
        rows = parse_interface_output(SAMPLE)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["finding"], "OPERATIONAL")
        self.assertEqual(rows[1]["finding"], "ADMINISTRATIVELY_DOWN")
        self.assertEqual(rows[2]["finding"], "NOT_OPERATIONAL")
        self.assertEqual(rows[3]["status"], "up")
        self.assertEqual(rows[3]["protocol"], "down")

    def test_summary_counts_every_state(self):
        audit = build_audit(SAMPLE, "router1.txt")
        self.assertEqual(audit["summary"], {"interfaces_found": 4, "operational": 1, "administratively_down": 1, "not_operational": 2})

    def test_ignores_headers_and_unrecognized_lines(self):
        rows = parse_interface_output("Router#show ip interface brief\nInterface IP-Address OK? Method Status Protocol\nnoise\n")
        self.assertEqual(rows, [])

    def test_reports_are_created_and_csv_is_readable(self):
        audit = build_audit(SAMPLE)
        with tempfile.TemporaryDirectory() as folder:
            paths = write_reports(audit, folder)
            self.assertTrue(all(path.is_file() for path in paths))
            loaded = json.loads(paths[0].read_text(encoding="utf-8"))
            self.assertEqual(loaded["summary"]["interfaces_found"], 4)
            with paths[1].open(encoding="utf-8", newline="") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 4)

    def test_html_escapes_untrusted_source_text(self):
        audit = build_audit(SAMPLE, "<script>alert(1)</script>.txt")
        with tempfile.TemporaryDirectory() as folder:
            page = write_reports(audit, folder)[2].read_text(encoding="utf-8")
            self.assertNotIn("<script>alert(1)</script>", page)
            self.assertIn("&lt;script&gt;", page)

if __name__ == "__main__":
    unittest.main()
