import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const projectDir = path.resolve(import.meta.dirname, "..");
const sourcePath = path.join(projectDir, "input", "client_stress_test.csv");
const outputDir = import.meta.dirname;
const cleanedCsvPath = path.join(outputDir, "cleaned_client_stress_test_practice.csv");
const reportPath = path.join(outputDir, "data_quality_report_client_stress_test_practice.xlsx");

const text = await fs.readFile(sourcePath, "utf8");
const [headerLine, ...sourceLines] = text.trimEnd().split(/\r?\n/);
const headers = headerLine.split(",");
const expectedFields = headers.length;
const rows = sourceLines.map((line, index) => {
  const values = line.split(",");
  return {
    originalRow: index + 2,
    fieldCount: values.length,
    values: [...values, ...Array(Math.max(0, expectedFields - values.length)).fill("")],
  };
});

const normalize = (value) => value.trim().toLowerCase();
const seen = new Map();
const cleaned = [];
const duplicates = [];

for (const row of rows) {
  const [customerId, name, email, city, phone, department] = row.values;
  const key = `${normalize(name)}|${normalize(email)}|${normalize(city)}`;
  const hasDuplicateKey = name && email && city;
  if (hasDuplicateKey && seen.has(key)) {
    duplicates.push({
      originalRow: row.originalRow,
      customerId,
      matchingRow: seen.get(key).originalRow,
      matchingCustomerId: seen.get(key).customerId,
      matchRule: "Name + Email + City",
      action: "Removed after approved practice rule",
    });
    continue;
  }
  if (hasDuplicateKey) seen.set(key, { originalRow: row.originalRow, customerId });
  cleaned.push({ originalRow: row.originalRow, customerId, name, email, city, phone, department, fieldCount: row.fieldCount, issues: [] });
}

const sharedEmails = new Map();
for (const row of cleaned) {
  if (/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(row.email)) {
    const group = sharedEmails.get(normalize(row.email)) ?? [];
    group.push(row);
    sharedEmails.set(normalize(row.email), group);
  }
}

for (const row of cleaned) {
  const missing = [
    ["Name", row.name],
    ["Email", row.email],
  ].filter(([, value]) => !value).map(([field]) => field);
  if (missing.length) row.issues.push(`Missing required fields: ${missing.join(", ")}`);
  if (row.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(row.email)) row.issues.push("Invalid email format");
  const emailGroup = sharedEmails.get(normalize(row.email));
  if (emailGroup?.length > 1) {
    const otherIds = emailGroup.filter((item) => item.customerId !== row.customerId).map((item) => item.customerId);
    row.issues.push(`Shared email with CustomerID ${otherIds.join(", ")} (review)`);
  }
  if (row.fieldCount !== expectedFields) row.issues.push(`Malformed source row: expected ${expectedFields} fields, found ${row.fieldCount}`);
}

const sarah = cleaned.find((row) => row.customerId === "006");
const sara = cleaned.find((row) => row.customerId === "007");
if (sarah && sara) {
  sarah.issues.push("Potential similar name with CustomerID 007 (review only)");
  sara.issues.push("Potential similar name with CustomerID 006 (review only)");
}

const csvEscape = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;
const cleanHeader = ["OriginalRow", ...headers, "Issue"];
const cleanLines = [cleanHeader, ...cleaned.map((row) => [
  row.originalRow, row.customerId, row.name, row.email, row.city, row.phone, row.department, row.issues.join("; "),
])].map((row) => row.map(csvEscape).join(","));
await fs.writeFile(cleanedCsvPath, `\uFEFF${cleanLines.join("\r\n")}\r\n`, "utf8");

const issueRows = cleaned.filter((row) => row.issues.length).map((row) => [
  row.originalRow, row.customerId, row.name, row.email, row.issues.join("; "), "Retained and flagged",
]);
const issueCounts = [
  ["Confirmed duplicates removed", duplicates.length],
  ["Records with shared-email review flags", cleaned.filter((row) => row.issues.some((issue) => issue.startsWith("Shared email"))).length],
  ["Records with missing required fields", cleaned.filter((row) => row.issues.some((issue) => issue.startsWith("Missing required"))).length],
  ["Records with invalid email format", cleaned.filter((row) => row.issues.includes("Invalid email format")).length],
  ["Records with similar-name review flags", cleaned.filter((row) => row.issues.some((issue) => issue.startsWith("Potential similar"))).length],
  ["Malformed source rows", cleaned.filter((row) => row.issues.some((issue) => issue.startsWith("Malformed source"))).length],
];

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Summary");
const cleanSheet = workbook.worksheets.add("Cleaned Data");
const issuesSheet = workbook.worksheets.add("Issues Found");
const duplicatesSheet = workbook.worksheets.add("Duplicates Removed");
const navy = "#1F4E78";
const blue = "#D9EAF7";
const amber = "#FFF2CC";
const red = "#FCE4D6";
const font = { name: "Arial", size: 10, color: "#1F2937" };

for (const sheet of [summary, cleanSheet, issuesSheet, duplicatesSheet]) {
  sheet.showGridLines = false;
  sheet.tabColor = navy;
}

summary.getRange("A2:F2").merge();
summary.getRange("A2").values = [["Data Quality Summary"]];
summary.getRange("A2").format = { font: { name: "Arial", size: 15, bold: true, color: navy }, verticalAlignment: "center" };
summary.getRange("A3:F3").merge();
summary.getRange("A3").values = [["Practice CRM contact-list cleanup"]];
summary.getRange("A3").format = { font: { name: "Arial", size: 10, italic: true, color: "#5B6573" } };
summary.getRange("A5:B9").values = [
  ["Source file", "client_stress_test.csv"],
  ["Input records", rows.length],
  ["Cleaned records retained", cleaned.length],
  ["Confirmed duplicates removed", duplicates.length],
  ["Records retained with review issues", issueRows.length],
];
summary.getRange("A5:A9").format = { fill: blue, font: { name: "Arial", bold: true, color: navy } };
summary.getRange("A5:B9").format.borders = { preset: "all", style: "thin", color: "#B7C9D6" };
summary.getRange("A11:B11").values = [["Issue category", "Records"]];
summary.getRange(`A12:B${11 + issueCounts.length}`).values = issueCounts;
summary.getRange("A11:B11").format = { fill: navy, font: { name: "Arial", bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
summary.getRange(`A11:B${11 + issueCounts.length}`).format.borders = { preset: "all", style: "thin", color: "#B7C9D6" };
summary.getRange("D5:F5").merge();
summary.getRange("D5").values = [["Approved practice rules"]];
summary.getRange("D5").format = { fill: navy, font: { name: "Arial", bold: true, color: "#FFFFFF" } };
summary.getRange("D6:F9").merge();
summary.getRange("D6").values = [["Exact duplicates use Name + Email + City. The first occurrence is retained. CustomerIDs and source-row references are preserved. Missing or invalid values are not invented; affected records are retained and flagged for review."]];
summary.getRange("D6").format = { fill: amber, font, wrapText: true, verticalAlignment: "top" };
summary.getRange("D5:F9").format.borders = { preset: "all", style: "thin", color: "#B7C9D6" };
summary.getRange("A2:F18").format.font = font;
summary.getRange("A2").format.font = { name: "Arial", size: 15, bold: true, color: navy };
summary.getRange("A2:F18").format.verticalAlignment = "center";
summary.getRange("A2:F18").format.autofitColumns();
summary.getRange("A").format.columnWidth = 40;
summary.getRange("B").format.columnWidth = 18;
summary.getRange("D").format.columnWidth = 24;
summary.getRange("E").format.columnWidth = 20;
summary.getRange("F").format.columnWidth = 20;
summary.getRange("D6:F9").format.rowHeight = 28;

const cleanedMatrix = [cleanHeader, ...cleaned.map((row) => [row.originalRow, row.customerId, row.name, row.email, row.city, row.phone, row.department, row.issues.join("; ")])];
cleanSheet.getRangeByIndexes(0, 0, cleanedMatrix.length, cleanHeader.length).values = cleanedMatrix;
cleanSheet.getRange("A1:H1").format = { fill: navy, font: { name: "Arial", bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", verticalAlignment: "center" };
cleanSheet.getRange(`A1:H${cleanedMatrix.length}`).format.font = font;
cleanSheet.getRange(`A1:H${cleanedMatrix.length}`).format.borders = { preset: "outside", style: "thin", color: "#B7C9D6" };
cleanSheet.getRange(`H2:H${cleanedMatrix.length}`).conditionalFormats.add("notContainsBlanks", { format: { fill: amber, font: { color: "#7F6000" } } });
cleanSheet.freezePanes.freezeRows(1);
cleanSheet.getRange("A:H").format.autofitColumns();
cleanSheet.getRange("H").format.columnWidth = 58;

const issuesHeader = ["OriginalRow", "CustomerID", "Name", "Email", "Issue", "Action"];
issuesSheet.getRangeByIndexes(0, 0, issueRows.length + 1, issuesHeader.length).values = [issuesHeader, ...issueRows];
issuesSheet.getRange("A1:F1").format = { fill: navy, font: { name: "Arial", bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
issuesSheet.getRange(`A1:F${issueRows.length + 1}`).format.font = font;
issuesSheet.getRange(`A1:F${issueRows.length + 1}`).format.borders = { preset: "outside", style: "thin", color: "#B7C9D6" };
issuesSheet.getRange(`E2:F${issueRows.length + 1}`).format = { fill: red, font };
issuesSheet.freezePanes.freezeRows(1);
issuesSheet.getRange("A:F").format.autofitColumns();
issuesSheet.getRange("E").format.columnWidth = 60;
issuesSheet.getRange("F").format.columnWidth = 22;

const duplicateHeader = ["Removed source row", "Removed CustomerID", "Matching source row", "Retained CustomerID", "Match rule", "Action"];
const duplicateMatrix = [duplicateHeader, ...duplicates.map((row) => [row.originalRow, row.customerId, row.matchingRow, row.matchingCustomerId, row.matchRule, row.action])];
duplicatesSheet.getRangeByIndexes(0, 0, duplicateMatrix.length, duplicateHeader.length).values = duplicateMatrix;
duplicatesSheet.getRange("A1:F1").format = { fill: navy, font: { name: "Arial", bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
duplicatesSheet.getRange(`A1:F${duplicateMatrix.length}`).format.font = font;
duplicatesSheet.getRange(`A1:F${duplicateMatrix.length}`).format.borders = { preset: "outside", style: "thin", color: "#B7C9D6" };
duplicatesSheet.getRange("A2:F2").format = { fill: red, font };
duplicatesSheet.freezePanes.freezeRows(1);
duplicatesSheet.getRange("A:F").format.autofitColumns();
duplicatesSheet.getRange("E").format.columnWidth = 24;
duplicatesSheet.getRange("F").format.columnWidth = 34;

workbook.recalculate();
const check = await workbook.inspect({ kind: "table", range: "Summary!A2:F17", include: "values,formulas", tableMaxRows: 20, tableMaxCols: 8 });
console.log(check.ndjson);
const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 50 }, summary: "formula error scan" });
console.log(errors.ndjson);
const preview = await workbook.render({ sheetName: "Summary", range: "A1:F18", scale: 1.5, format: "png" });
await fs.writeFile(path.join(outputDir, "practice_report_preview.png"), new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(reportPath);

console.log(JSON.stringify({ cleanedCsvPath, reportPath, retained: cleaned.length, duplicatesRemoved: duplicates.length, recordsWithIssues: issueRows.length }));
