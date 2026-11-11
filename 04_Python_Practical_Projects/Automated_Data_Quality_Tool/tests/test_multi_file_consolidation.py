import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

import multi_file_consolidation as consolidation


class TestGroupedMultiFileConsolidation(unittest.TestCase):
    def test_case_study_outputs_and_grouped_report(self):
        package = Path(__file__).resolve().parents[3] / "Client_Case_01_Package"
        if not package.exists():
            self.skipTest("Case study input package not available.")

        with tempfile.TemporaryDirectory() as temp:
            result = consolidation.run_consolidation(package, temp)

            self.assertEqual(result["source_files"], 2)
            self.assertEqual(result["input_records"], 26)
            self.assertEqual(result["retained_records"], 26)
            self.assertEqual(result["records_removed"], 0)
            self.assertGreater(result["review_groups"], 0)
            self.assertEqual(
                result["review_groups"],
                result["exact_match_groups"]
                + result["possible_name_groups"]
                + result["shared_email_groups"],
            )

            _, review_rows = consolidation.compare_records(
                consolidation.load_sources(package)[0])
            possible = next(row for row in review_rows
                            if row["MatchType"] == "Possible name match")
            shared = next(row for row in review_rows
                          if row["MatchType"] == "Shared-email conflict")
            self.assertEqual(possible["RecordCount"], 4)
            self.assertEqual(possible["ProfileCount"], 2)
            self.assertIn("Sarah Smith (2 source records", possible["Profiles"])
            self.assertIn("Sara Smith (2 source records", possible["Profiles"])
            self.assertIn("95.24%", possible["Details"])
            self.assertEqual(shared["RecordCount"], 4)
            self.assertEqual(shared["ProfileCount"], 2)
            self.assertIn("Peter Jones (3 source records", shared["Profiles"])
            self.assertIn("Another Person (1 source records", shared["Profiles"])

            for key in ("cleaned_csv", "issues_csv", "duplicates_csv", "report_xlsx"):
                self.assertTrue(Path(result[key]).is_file())

            wb = load_workbook(result["report_xlsx"], read_only=True)
            self.assertEqual(wb["Consolidated Data"].max_row, 27)
            self.assertEqual(
                wb["Duplicate Review"].max_row, result["review_groups"] + 1)
            self.assertIn("Unique records appearing in review groups",
                          [wb["Summary"].cell(row, 1).value
                           for row in range(1, wb["Summary"].max_row + 1)])
            wb.close()

    def test_related_name_pairs_are_grouped_into_one_review_group(self):
        def record(source, row, name, email):
            return {
                "source_file": source, "worksheet": "Sheet1",
                "original_row": row,
                "data": {
                    "customerid": f"{source}-{row}", "name": name,
                    "email": email, "city": "Port Louis",
                    "phone": "", "department": "",
                },
                "error": None,
            }

        records = [
            record("A.xlsx", 2, "Sarah Smith", "sarah.a@example.com"),
            record("A.xlsx", 3, "Sara Smith", "sara.a@example.com"),
            record("B.xlsx", 2, "Sarah Smith", "sarah.b@example.com"),
            record("B.xlsx", 3, "Sara Smith", "sara.b@example.com"),
        ]
        _, groups = consolidation.compare_records(records)
        possible = [g for g in groups if g["MatchType"] == "Possible name match"]

        self.assertEqual(len(possible), 1)
        self.assertEqual(possible[0]["RecordCount"], 4)
        self.assertEqual(possible[0]["ProfileCount"], 2)
        self.assertIn("Sarah Smith (2 source records", possible[0]["Profiles"])
        self.assertIn("Sara Smith (2 source records", possible[0]["Profiles"])
        self.assertEqual(possible[0]["CustomerIDs"].count(" | ") + 1, 4)

    def test_possible_name_matching_keeps_distinct_similar_pairs_separate(self):
        def record(index, name):
            return {
                "source_file": f"{index}.xlsx", "worksheet": "Sheet1",
                "original_row": 2,
                "data": {
                    "customerid": f"ID-{index}", "name": name,
                    "email": f"person{index}@example.com", "city": "Port Louis",
                    "phone": "", "department": "",
                },
                "error": None,
            }

        records = [
            record(1, "Sarah Smith"),
            record(2, "Sara Smith"),
            record(3, "Mohamed Ali"),
            record(4, "Mohammad Ali"),
            record(5, "Completely Different"),
        ]
        groups = consolidation._possible_name_groups(records)
        actual = {
            frozenset(name for name, _ in profiles)
            for _, profiles in groups
        }
        self.assertEqual(
            actual,
            {
                frozenset(("sarah smith", "sara smith")),
                frozenset(("mohamed ali", "mohammad ali")),
            },
        )

    def test_exact_group_reports_phone_and_department_conflicts(self):
        def record(source, customer_id, phone, department):
            return {
                "source_file": source, "worksheet": "Sheet1",
                "original_row": 2,
                "data": {
                    "customerid": customer_id, "name": "Alex Brown",
                    "email": "alex@example.com", "city": "Port Louis",
                    "phone": phone, "department": department,
                },
                "error": None,
            }

        records = [
            record("A.xlsx", "A1", "111", "Sales"),
            record("B.xlsx", "B1", "222", "Support"),
        ]
        _, groups = consolidation.compare_records(records)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["ConflictingFields"], "phone, department")

    def test_overlapping_source_row_numbers_do_not_cause_false_match(self):
        def record(source, customer_id, name, email, city):
            return {
                "source_file": source, "worksheet": "Sheet1",
                "original_row": 2,
                "data": {
                    "customerid": customer_id, "name": name,
                    "email": email, "city": city,
                    "phone": "", "department": "",
                },
                "error": None,
            }

        records = [
            record("A.xlsx", "A1", "Alex Brown", "alex@example.com", "Port Louis"),
            record("B.xlsx", "B1", "Jamie Brown", "jamie@example.com", "Curepipe"),
        ]
        _, groups = consolidation.compare_records(records)
        self.assertEqual(groups, [])


if __name__ == "__main__":
    unittest.main()
