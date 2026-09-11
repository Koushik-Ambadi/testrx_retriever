import fs from "node:fs/promises";
import { Workbook } from "@oai/artifact-tool";

const inputPath = new URL("../output/datasets/golden/golden_dataset.csv", import.meta.url);
const previewPath = new URL("../tmp/golden_dataset_csv_preview.png", import.meta.url);
const csvText = await fs.readFile(inputPath, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Golden Dataset" });
const sheet = workbook.worksheets.getItem("Golden Dataset");
sheet.showGridLines = false;
sheet.freezePanes.freezeRows(1);
sheet.getRange("A1:Y133").format.font = { name: "Arial", size: 10 };
sheet.getRange("A1:Y1").format = {
  fill: "#1F4E78",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
  wrapText: true,
};
sheet.getRange("A2:Y133").format.verticalAlignment = "top";
sheet.getRange("A2:Y10").format.wrapText = true;
sheet.getRange("A:A").format.columnWidthPx = 70;
sheet.getRange("B:B").format.columnWidthPx = 260;
sheet.getRange("C:D").format.columnWidthPx = 95;
sheet.getRange("E:E").format.columnWidthPx = 340;
sheet.getRange("F:G").format.columnWidthPx = 110;
sheet.getRange("H:H").format.columnWidthPx = 300;
sheet.getRange("1:1").format.rowHeightPx = 42;
sheet.getRange("2:10").format.rowHeightPx = 62;
const inspection = await workbook.inspect({
  kind: "table",
  range: "Golden Dataset!A1:Y8",
  include: "values",
  tableMaxRows: 8,
  tableMaxCols: 25,
  maxChars: 8000,
});
console.log(inspection.ndjson);
const preview = await workbook.render({
  sheetName: "Golden Dataset",
  range: "A1:H10",
  scale: 1,
  format: "png",
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
console.log(JSON.stringify({ preview: previewPath.pathname, dataRows: csvText.trimEnd().split(/\r?\n/).length - 1 }));
