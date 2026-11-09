import csv
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import data_quality_engine as engine
import run_pipeline


class TestDataQualityEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.input = Path(self.temp_dir.name) / "input"
        self.output = Path(self.temp_dir.name) / "output"

        self.input.mkdir()
        self.output.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_csv(self, filename, rows):
        path = self.input / filename

        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        return path

    def test_duplicate_requires_all_key_fields(self):
        p = self.write_csv("duplicates.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["1", "Alex Brown", "alex@example.com", "Port Louis"],
            ["2", "Alex Brown", "alex@example.com", "Curepipe"],
        ])

        result = engine.process_file(p, output_dir=self.output)

        self.assertEqual(result["retained"], 2)
        self.assertEqual(result["duplicates_removed"], 0)

    def test_exact_duplicate_detected(self):
        p = self.write_csv("exact_duplicate.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["1", "Alex Brown", "alex@example.com", "Port Louis"],
            ["2", "Alex Brown", "alex@example.com", "Port Louis"],
        ])

        result = engine.process_file(p, output_dir=self.output)

        self.assertEqual(result["retained"], 1)
        self.assertEqual(result["duplicates_removed"], 1)

    def test_csv_customer_id_is_preserved_exactly(self):
        p = self.write_csv("customer_id_preservation.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["  001 ", "Alex Brown", "alex@example.com", "Port Louis"],
        ])

        engine.process_file(p, output_dir=self.output)

        output_file = self.output / "cleaned_customer_id_preservation_csv.csv"

        with output_file.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            rows = list(csv.DictReader(file))

        self.assertEqual(rows[0]["CustomerID"], "  001 ")


    def test_excel_text_customer_id_is_preserved_exactly(self):
        from openpyxl import Workbook, load_workbook

        p = self.input / "customer_id_preservation.xlsx"

        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["CustomerID", "Name", "Email", "City"])
        sheet.append(["  001 ", "Alex Brown", "alex@example.com", "Port Louis"])
        workbook.save(p)
        workbook.close()

        engine.process_file(p, output_dir=self.output)

        output_file = (
            self.output
            / "data_quality_report_customer_id_preservation_xlsx.xlsx"
        )

        output_workbook = load_workbook(output_file, data_only=False)
        output_sheet = output_workbook["Cleaned Data"]

        self.assertEqual(output_sheet["B2"].value, "  001 ")

        output_workbook.close()


    def test_excel_zero_mask_id_preserved(self):
        from openpyxl import Workbook, load_workbook

        p = self.input / "zero_id.xlsx"

        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["CustomerID", "Name", "Email", "City"])
        sheet.append([1, "Alex Brown", "alex@example.com", "Port Louis"])
        sheet["A2"].number_format = "000"
        workbook.save(p)

        result = engine.process_file(p, output_dir=self.output)

        output_file = self.output / "data_quality_report_zero_id_xlsx.xlsx"
        output_workbook = load_workbook(output_file, data_only=False)
        output_sheet = output_workbook["Cleaned Data"]

        self.assertEqual(result["retained"], 1)
        self.assertEqual(output_sheet["B2"].value, "001")

        output_workbook.close()

    def test_excel_name_email_and_other_fields_standardized(self):
        from openpyxl import Workbook, load_workbook

        p = self.input / "excel_standardization.xlsx"

        workbook = Workbook()
        sheet = workbook.active

        sheet.append([
            "CustomerID",
            "Name",
            "Email",
            "City",
            "Notes"
        ])

        sheet.append([
            1,
            "  alex brown ",
            " ALEX@EXAMPLE.COM ",
            " Port Louis ",
            " Keep This "
        ])

        sheet["A2"].number_format = "000"
        workbook.save(p)
        workbook.close()

        result = engine.process_file(p, output_dir=self.output)

        output_file = (
            self.output
            / "data_quality_report_excel_standardization_xlsx.xlsx"
        )

        output_workbook = load_workbook(output_file, data_only=False)
        output_sheet = output_workbook["Cleaned Data"]

        self.assertEqual(result["retained"], 1)

        # Column A: OriginalRow
        self.assertEqual(output_sheet["A2"].value, 2)

        # Column B: CustomerID
        self.assertEqual(output_sheet["B2"].value, "001")

        # Column C: Name
        self.assertEqual(output_sheet["C2"].value, "Alex Brown")

        # Column D: Email
        self.assertEqual(output_sheet["D2"].value, "alex@example.com")

        # Column E: City
        self.assertEqual(output_sheet["E2"].value, "Port Louis")

        # Column F: Notes
        self.assertEqual(output_sheet["F2"].value, "Keep This")

        output_workbook.close()

    def test_header_csv_and_extra_columns_preserved(self):
        p = self.write_csv("extra_columns.csv", [
            ["CustomerID", "Name", "Email", "City", "Notes"],
            ["1", "  alex brown ", "ALEX@EXAMPLE.COM", "Port Louis", "VIP"],
        ])

        engine.process_file(p, output_dir=self.output)

        output_file = self.output / "cleaned_extra_columns_csv.csv"

        with output_file.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            rows = list(csv.DictReader(file))

        self.assertIn("Notes", rows[0])
        self.assertEqual(rows[0]["Name"], "Alex Brown")
        self.assertEqual(rows[0]["Email"], "alex@example.com")
        self.assertEqual(rows[0]["Notes"], "VIP")

    def test_header_excel(self):
        from openpyxl import Workbook

        p = self.input / "header.xlsx"

        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["CustomerID", "Name", "Email", "City"])
        sheet.append([1, "Alex Brown", "alex@example.com", "Port Louis"])
        workbook.save(p)

        result = engine.process_file(p, output_dir=self.output)

        self.assertEqual(result["retained"], 1)

    def test_headerless_csv_requires_explicit_order_and_keeps_first_row(self):
        p = self.write_csv("headerless.csv", [
            ["001", "Alex Brown", "alex@example.com", "Port Louis"],
            ["002", "Sarah Smith", "sarah@example.com", "Curepipe"],
        ])

        result = engine.process_file(
            p,
            output_dir=self.output,
            has_header=False,
            column_order=("CustomerID", "Name", "Email", "City"),
        )

        self.assertEqual(result["retained"], 2)

    def test_headerless_excel(self):
        from openpyxl import Workbook

        p = self.input / "headerless.xlsx"

        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["001", "Alex Brown", "alex@example.com", "Port Louis"])
        sheet.append(["002", "Sarah Smith", "sarah@example.com", "Curepipe"])
        workbook.save(p)

        result = engine.process_file(
            p,
            output_dir=self.output,
            has_header=False,
            column_order=("CustomerID", "Name", "Email", "City"),
        )

        self.assertEqual(result["retained"], 2)

    def test_invalid_email_is_flagged(self):
        p = self.write_csv("invalid_email.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["1", "Alex Brown", "not-an-email", "Port Louis"],
        ])

        result = engine.process_file(p, output_dir=self.output)

        self.assertEqual(result["retained"], 1)
        self.assertEqual(result["issues"], 1)

    def test_malformed_csv_row_flagged_and_other_rows_retained(self):
        p = self.input / "malformed.csv"

        p.write_text(
            "CustomerID,Name,Email,City\n"
            "1,Alex Brown,alex@example.com,Port Louis\n"
            "2,Sarah Smith,sarah@example.com\n"
            "3,David Jones,david@example.com,Curepipe\n",
            encoding="utf-8-sig",
        )

        result = engine.process_file(p, output_dir=self.output)

        self.assertGreaterEqual(result["issues"], 1)
        self.assertGreaterEqual(result["retained"], 2)

    def test_original_input_not_modified(self):
        p = self.write_csv("original.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["1", "  alex brown ", "ALEX@EXAMPLE.COM", "Port Louis"],
        ])

        original_content = p.read_text(encoding="utf-8-sig")

        engine.process_file(p, output_dir=self.output)

        updated_content = p.read_text(encoding="utf-8-sig")

        self.assertEqual(original_content, updated_content)

    def test_valid_email_is_not_flagged(self):
        p = self.write_csv("valid_email.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["1", "Alex Brown", "alex.brown@example.com", "Port Louis"],
        ])

        result = engine.process_file(p, output_dir=self.output)

        self.assertEqual(result["retained"], 1)
        self.assertEqual(result["issues"], 0)

    def test_email_validation_edge_cases(self):
        cases = [
            # Valid email addresses
            ("standard", "alex@example.com", 0),
            ("subdomain", "alex.brown@example.co.uk", 0),
            ("plus_tag", "alex+tag@example.com", 0),

            # Invalid email addresses
            ("localhost", "alex@localhost", 1),
            ("missing_domain", "alex@", 1),
            ("missing_local", "@example.com", 1),
            ("space", "alex example@example.com", 1),
            ("consecutive_dots", "alex..brown@example.com", 1),
            ("leading_dot", ".alex@example.com", 1),
            ("trailing_dot", "alex.@example.com", 1),
            ("double_domain_dot", "alex@example..com", 1),
            ("domain_hyphen", "alex@-example.com", 1),
        ]

        for label, email, expected_issues in cases:
            with self.subTest(email=email):
                p = self.write_csv(f"email_{label}.csv", [
                    ["CustomerID", "Name", "Email", "City"],
                    ["1", "Alex Brown", email, "Port Louis"],
                ])

                result = engine.process_file(p, output_dir=self.output)

                self.assertEqual(result["retained"], 1)
                self.assertEqual(result["issues"], expected_issues)


    def test_malformed_csv_quoting_is_rejected(self):
        p = self.input / "broken_quotes.csv"

        p.write_text(
            'CustomerID,Name,Email,City\\n'
            '1,"Alex Brown,alex@example.com,Port Louis\\n',
            encoding="utf-8-sig"
        )

        with self.assertRaises(csv.Error):
            engine.process_file(p, output_dir=self.output)


    def test_batch_continues_after_failed_file(self):
        invalid_file = self.input / "a_invalid.csv"
        valid_file = self.write_csv("b_valid.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["001", "Alex Brown", "alex@example.com", "Port Louis"],
        ])

        invalid_file.write_text(
            'CustomerID,Name,Email,City\\n'
            '1,"Alex Brown,alex@example.com,Port Louis\\n',
            encoding="utf-8-sig"
        )

        with (
            patch.object(run_pipeline, "INPUT_DIR", self.input),
            patch.object(engine, "OUTPUT_DIR", self.output),
        ):

            summary = run_pipeline.main()

        self.assertEqual(summary["discovered"], 2)
        self.assertEqual(summary["completed"], 1)
        self.assertEqual(summary["failed"], 1)

        expected_output = self.output / "cleaned_b_valid_csv.csv"
        self.assertTrue(expected_output.is_file())


    def test_previous_outputs_are_restored_if_excel_install_fails(self):
        p = self.write_csv("rollback.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["1", "Alex Brown", "alex@example.com", "Port Louis"],
        ])

        cleaned_csv = self.output / "cleaned_rollback_csv.csv"
        report_xlsx = self.output / "data_quality_report_rollback_csv.xlsx"

        old_csv = "PREVIOUS CSV CONTENT"
        old_xlsx = "PREVIOUS EXCEL CONTENT"

        cleaned_csv.write_text(old_csv, encoding="utf-8")
        report_xlsx.write_text(old_xlsx, encoding="utf-8")

        original_replace = Path.replace

        def fail_excel_install(path, target):
            target_path = Path(target)

            is_temporary_excel = (
                path.name.startswith("data_quality_report_")
                and ".tmp.xlsx" in path.name
            )
            is_final_excel_target = (
                target_path.name == path.name.replace(".tmp.xlsx", ".xlsx")
            )

            if is_temporary_excel and is_final_excel_target:
                raise OSError("Simulated Excel installation failure")

            return original_replace(path, target)

        with patch.object(
            Path,
            "replace",
            autospec=True,
            side_effect=fail_excel_install
        ):
            with self.assertRaisesRegex(
                OSError,
                "Simulated Excel installation failure"
            ):
                engine.process_file(p, output_dir=self.output)

        self.assertEqual(
            cleaned_csv.read_text(encoding="utf-8"),
            old_csv
        )
        self.assertEqual(
            report_xlsx.read_text(encoding="utf-8"),
            old_xlsx
        )

        leftovers = [
            item.name for item in self.output.iterdir()
            if item.name.endswith(".bak") or ".tmp." in item.name
        ]
        self.assertEqual(leftovers, [])


    def test_excel_report_has_professional_formatting(self):
        from openpyxl import load_workbook

        p = self.write_csv("formatting.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["1", "Alex Brown", "not-an-email", "Port Louis"],
        ])

        engine.process_file(p, output_dir=self.output)

        report = self.output / "data_quality_report_formatting_csv.xlsx"
        workbook = load_workbook(report)
        summary = workbook["Summary"]
        cleaned = workbook["Cleaned Data"]
        issues = workbook["Issues Found"]

        self.assertEqual(summary["B7"].value, "PASS")
        self.assertEqual(summary["A1"].fill.fgColor.rgb[-6:], "17365D")
        self.assertEqual(cleaned.freeze_panes, "A2")
        self.assertTrue(cleaned["A1"].font.bold)
        self.assertTrue(cleaned["A2"].alignment.wrap_text)
        self.assertEqual(issues["D2"].value, "Review")
        self.assertEqual(issues["A2"].fill.fgColor.rgb[-6:], "FFF2CC")

        workbook.close()


if __name__ == "__main__":
    unittest.main()
