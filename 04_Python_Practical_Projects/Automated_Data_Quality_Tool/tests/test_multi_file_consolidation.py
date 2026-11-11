import tempfile
import unittest
from difflib import SequenceMatcher
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
                consolidation.load_sources(
                    package, consolidation.load_source_config(
                        consolidation.DEFAULT_CONFIG_PATH
                    )
                )[0])
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
            record(4, "Mohamed Aly"),
            record(5, "Mohamed Ali"),
            record(6, "Mohammad Ali"),
            record(7, "Completely Different"),
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
                frozenset(("mohamed ali", "mohamed aly")),
            },
        )

    def test_possible_name_groups_match_exhaustive_reference(self):
        """Protect recall before introducing any candidate-blocking strategy."""
        names = [
            "Sarah Smith", "Sara Smith",
            "Mohamed Ali", "Mohamed Aly",
            "Mohammad Ali", "Muhammad Ali",
            "David Jones", "Dav id Jones",
            "Peter Jones", "Peter John",
            "Completely Different", "Another Unrelated Person",
        ]
        records = []
        for index, name in enumerate(names):
            records.append({
                "source_file": f"source_{index % 3}.xlsx",
                "worksheet": "Sheet1",
                "original_row": index + 2,
                "data": {
                    "customerid": f"REF-{index}",
                    "name": name,
                    "email": f"reference{index}@example.com",
                    "city": "Port Louis",
                    "phone": "",
                    "department": "",
                },
                "error": None,
            })

        keys = [(record["data"]["name"].strip().casefold(),
                 record["data"]["email"].strip().casefold())
                for record in records]
        parent = list(range(len(keys)))

        def find(index):
            while parent[index] != index:
                parent[index] = parent[parent[index]]
                index = parent[index]
            return index

        for left in range(len(keys)):
            for right in range(left + 1, len(keys)):
                left_name, left_email = keys[left]
                right_name, right_email = keys[right]
                if left_name == right_name or left_email == right_email:
                    continue
                if SequenceMatcher(None, left_name, right_name).ratio() >= 0.88:
                    root_left, root_right = find(left), find(right)
                    if root_left != root_right:
                        parent[root_right] = root_left

        expected_components = {}
        for index, key in enumerate(keys):
            expected_components.setdefault(find(index), set()).add(key)
        expected = {
            frozenset(component)
            for component in expected_components.values()
            if len({name for name, _ in component}) > 1
        }

        actual_groups = consolidation._possible_name_groups(records)
        actual = {
            frozenset(profiles)
            for _, profiles in actual_groups
        }
        self.assertEqual(actual, expected)

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


    def test_source_config_rejects_missing_required_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            config_path = Path(temp) / "config.json"
            config_path.write_text(
                '{"sources":[{"filename":"customers.csv",'
                '"column_mapping":{"name":"Name","email":"Email","city":"Town"}}]}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "customerid"):
                consolidation.load_source_config(config_path)

    def test_source_config_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            config_path = Path(temp) / "config.json"
            config_path.write_text(
                '{"sources":[{"filename":"../outside.csv",'
                '"column_mapping":{"customerid":"ID","name":"Name",'
                '"email":"Email","city":"Town"}}]}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "inside the package"):
                consolidation.load_source_config(config_path)

    def test_custom_csv_source_config_loads_without_changing_engine(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / "input"
            package.mkdir()
            (package / "regional.csv").write_text(
                "Account Ref,Resident,Contact,Location,Mobile,Unit\\n"
                "001,Alex Brown,alex@example.com,Port Louis,12345,Sales\\n",
                encoding="utf-8",
            )
            config_path = Path(temp) / "config.json"
            config_path.write_text(
                '{"sources":[{"filename":"regional.csv","has_header":true,'
                '"column_mapping":{"customerid":"Account Ref","name":"Resident",'
                '"email":"Contact","city":"Location","phone":"Mobile",'
                '"department":"Unit"}}]}',
                encoding="utf-8",
            )
            source_config = consolidation.load_source_config(config_path)
            records, summaries = consolidation.load_sources(package, source_config)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["data"]["customerid"], "001")
            self.assertEqual(records[0]["data"]["name"], "Alex Brown")
            self.assertEqual(summaries[0]["source_file"], "regional.csv")

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
