import csv
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

import data_quality_engine as engine


class DataQualityEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.output = self.root / "output"
        self.output.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def write_csv(self, name, rows):
        path = self.root / name
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)
        return path

    def write_xlsx(self, name, rows, id_format=None):
        path = self.root / name
        wb = Workbook()
        ws = wb.active
        for row in rows:
            ws.append(row)
        if id_format:
            for cell in ws["A"]:
                cell.number_format = id_format
        wb.save(path)
        return path

    def test_header_csv_and_extra_columns_preserved(self):
        p = self.write_csv("headed.csv", [
            ["Customer ID", "Full Name", "Email Address", "Town", "Department"],
            ["001", "Alex Brown", "alex@example.com", "Port Louis", "Sales"],
        ])
        result = engine.process_file(p, output_dir=self.output)
        with (self.output / "cleaned_headed_csv.csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        self.assertEqual(rows[0], ["OriginalRow", "Customer ID", "Full Name", "Email Address", "Town", "Department"])
        self.assertEqual(rows[1][1], "001")
        self.assertEqual(rows[1][-1], "Sales")
        self.assertEqual(result["retained"], 1)

    def test_headerless_csv_requires_explicit_order_and_keeps_first_row(self):
        p = self.write_csv("bare.csv", [["301", "Alex Brown", "alex@example.com", "Port Louis"]])
        with self.assertRaises(ValueError):
            engine.read_input_file(p, has_header=False)
        result = engine.process_file(p, has_header=False,
            column_order=("CustomerID", "Name", "Email", "City"), output_dir=self.output)
        self.assertEqual(result["retained"], 1)

    def test_header_excel(self):
        p = self.write_xlsx("headed.xlsx", [
            ["CustomerID", "Name", "Email", "City", "Department"],
            ["002", "Jamie Lee", "jamie@example.com", "Curepipe", "HR"],
        ])
        result = engine.process_file(p, output_dir=self.output)
        self.assertEqual(result["retained"], 1)
        self.assertTrue(Path(result["excel_report"]).exists())

    def test_headerless_excel(self):
        p = self.write_xlsx("bare.xlsx", [
            ["303", "Taylor Smith", "taylor@example.com", "Mahebourg"],
        ])
        result = engine.process_file(p, has_header=False,
            column_order=("CustomerID", "Name", "Email", "City"), output_dir=self.output)
        self.assertEqual(result["retained"], 1)

    def test_excel_zero_mask_id_preserved(self):
        p = self.write_xlsx("zero.xlsx", [
            ["CustomerID", "Name", "Email", "City"],
            [7, "Sam Green", "sam@example.com", "Rose Hill"],
        ], id_format="000")
        result = engine.process_file(p, output_dir=self.output)
        with (self.output / "cleaned_zero_xlsx.csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        self.assertEqual(rows[1][1], "007")

    def test_duplicate_requires_all_key_fields(self):
        records = [
            {"original_row": 2, "data": {"name":"A", "email":"a@x.com", "city":"X"}, "raw":{}, "error":None},
            {"original_row": 3, "data": {"name":"A", "email":"a@x.com", "city":""}, "raw":{}, "error":None},
        ]
        _, duplicates = engine.inspect_records(records)
        self.assertEqual(duplicates, [])

    def test_exact_duplicate_detected(self):
        records = [
            {"original_row": 2, "data": {"customerid":"1","name":"A","email":"a@x.com","city":"X"}, "raw":{}, "error":None},
            {"original_row": 3, "data": {"customerid":"2","name":" a ","email":"A@X.COM","city":"x"}, "raw":{}, "error":None},
        ]
        _, duplicates = engine.inspect_records(records)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["matching_row"], 2)

    def test_malformed_csv_row_flagged_and_other_rows_retained(self):
        p = self.write_csv("malformed.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["1", "A", "a@x.com", "X"],
            ["2", "B", "b@x.com"],
        ])
        result = engine.process_file(p, output_dir=self.output)
        self.assertEqual(result["retained"], 1)
        self.assertEqual(result["issues"], 1)

    def test_original_input_not_modified(self):
        p = self.write_csv("untouched.csv", [
            ["CustomerID", "Name", "Email", "City"],
            ["001", "A", "a@x.com", "X"],
        ])
        before = p.read_bytes()
        engine.process_file(p, output_dir=self.output)
        self.assertEqual(p.read_bytes(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
