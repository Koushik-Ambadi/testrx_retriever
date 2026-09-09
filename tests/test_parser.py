from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.inspection import collect_parsing_warnings, render_semantic_structure, walk_elements
from testrx_retriever.normalize import join_text, normalize_text
from testrx_retriever.parser import parse_manual, write_outputs
from testrx_retriever.validation import EXPECTED_SHA256, validate_document


class NormalizationTests(unittest.TestCase):
    def test_known_pdf_artifacts_are_conservatively_normalized(self) -> None:
        self.assertEqual(normalize_text("right\ufffeside"), "right-side")
        self.assertEqual(normalize_text("\uf0b7  Value"), "• Value")
        self.assertEqual(normalize_text("CANoe\t  mode"), "CANoe mode")

    def test_line_join_preserves_or_repairs_hyphens(self) -> None:
        self.assertEqual(join_text("configura-", "tion"), "configuration")
        self.assertEqual(join_text("Test Case", "parameter"), "Test Case parameter")


class ManualParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = parse_manual(ROOT / "source" / "TESTRX_User_Manual.pdf")
        cls.sections = {section.section_id: section for section in cls.document.sections}
        cls.elements = [
            element
            for section in cls.document.sections
            for element in walk_elements(section.elements)
        ]
        cls.tables = {element.data.get("printed_id"): element for element in cls.elements if element.type == "table"}

    def test_source_and_pages(self) -> None:
        self.assertEqual(self.document.source_sha256, EXPECTED_SHA256)
        self.assertEqual(len(self.document.pages), 61)
        self.assertEqual([page.page_number for page in self.document.pages], list(range(1, 62)))
        self.assertEqual(self.document.metadata["source_type"], "native_pdf")
        self.assertGreaterEqual(self.document.metadata["page_native_ratio"], 0.8)

    def test_complete_top_level_hierarchy(self) -> None:
        roots = {section.section_id for section in self.document.sections if section.parent_section_id is None}
        self.assertEqual(roots, {str(value) for value in range(1, 19)})
        self.assertEqual(self.sections["12.5.2"].parent_section_id, "12.5")
        self.assertEqual(self.sections["16.2.4.1"].ancestor_path[-2:], ["16.2.4 Map Labels", "16.2.4.1 Overview"])

    def test_known_cross_page_sections(self) -> None:
        self.assertEqual((self.sections["12.3"].page_start, self.sections["12.3"].page_end), (21, 22))
        self.assertEqual((self.sections["14.6"].page_start, self.sections["14.6"].page_end), (30, 31))
        self.assertEqual((self.sections["16.2.2"].page_start, self.sections["16.2.2"].page_end), (43, 46))

    def test_all_printed_tables_and_continuations(self) -> None:
        self.assertEqual(set(self.tables), {str(value) for value in range(1, 10)})
        self.assertEqual((self.tables["1"].page_start, self.tables["1"].page_end), (9, 10))
        self.assertEqual((self.tables["7"].page_start, self.tables["7"].page_end), (29, 30))
        for printed_id in ("6", "7", "8", "9"):
            self.assertTrue(self.tables[printed_id].data["resolved_rows"])

    def test_merged_table_context(self) -> None:
        self.assertTrue(all(row[0] == "Action" for row in self.tables["7"].data["resolved_rows"]))
        self.assertTrue(all(row[0] == "Entity Type" for row in self.tables["8"].data["resolved_rows"]))

    def test_real_procedure_remains_a_procedure(self) -> None:
        procedures = [element for element in self.sections["16.2.1"].elements if element.type == "procedure"]
        self.assertEqual(len(procedures), 1)
        items = procedures[0].data["items"]
        self.assertEqual(len(items), 5)
        self.assertTrue(items[0]["text"].startswith("Open the Configurator"))

    def test_interface_labels_become_owned_local_groups(self) -> None:
        groups = self.sections["16.2.2"].elements
        self.assertEqual(
            [group.data.get("label") for group in groups],
            ["CANoe", "Power Supply", "SDT", "FPGA", "VTE (Virtual Test Environment)"],
        )
        self.assertTrue(all(group.type == "local_group" and group.children for group in groups))
        for group in groups:
            descendants = list(walk_elements(group.children))
            self.assertIn("figure", {element.type for element in descendants})
            self.assertTrue(
                all(element.data.get("local_group_id") == group.id for element in descendants)
            )
        power = groups[1]
        self.assertEqual((power.page_start, power.page_end), (43, 44))
        self.assertIn("snp_28_p044", {element.id for element in walk_elements(power.children)})

    def test_generic_labelled_blocks_are_explicit(self) -> None:
        labels = {
            element.data.get("label")
            for element in walk_elements(self.sections["12.5.1"].elements)
            if element.type == "labelled_block"
        }
        self.assertTrue({"Validation Rules", "Invalid Example", "Valid Example"} <= labels)
        self.assertNotIn('label with the existing one?"', {
            element.data.get("label") for element in self.elements if element.type == "labelled_block"
        })

    def test_figures_preserve_duplicate_printed_id_without_duplicate_canonical_id(self) -> None:
        figures = [element for element in self.elements if element.type == "figure"]
        printed_threes = [element for element in figures if element.data["printed_id"] == "3"]
        self.assertEqual(len(printed_threes), 2)
        self.assertEqual(len({element.id for element in figures}), len(figures))

    def test_every_element_has_provenance(self) -> None:
        self.assertTrue(self.elements)
        self.assertTrue(all(element.sources for element in self.elements))
        self.assertTrue(all(source.source_ids for element in self.elements for source in element.sources))

    def test_toc_is_covered_by_body_hierarchy(self) -> None:
        report = validate_document(self.document)
        check = next(item for item in report["checks"] if item["id"] == "toc.heading_coverage")
        self.assertEqual(check["status"], "PASS")

    def test_all_semantic_body_lines_are_owned(self) -> None:
        report = validate_document(self.document)
        check = next(item for item in report["checks"] if item["id"] == "coverage.semantic_lines")
        self.assertEqual(check["evidence"]["count"], 0)

    def test_validation_has_no_failures(self) -> None:
        report = validate_document(self.document, collect_parsing_warnings(self.document))
        self.assertEqual(report["summary"]["failed"], 0, json.dumps(report, indent=2))
        self.assertEqual(report["overall_status"], "PASS_WITH_WARNINGS")

    def test_semantic_renderer_is_readable_and_excludes_geometry(self) -> None:
        rendered = render_semantic_structure(self.document)
        for expected in (
            "L1  14 Create Test Case",
            "L2  14.6 Identifier",
            "L4  16.2.4.1 Overview",
            "G1  CANoe",
            "[TABLE] Table 7",
            "[2 physical fragments -> 1 logical table]",
        ):
            self.assertIn(expected, rendered)
        for forbidden in ("bbox", "source_ids", "font_name"):
            self.assertNotIn(forbidden, rendered)

    def test_output_bundle_has_only_the_five_contract_artifacts(self) -> None:
        expected = {
            "document.json", "semantic_structure.md", "page_inventory.csv",
            "validation_report.json", "parsing_warnings.json",
        }
        with tempfile.TemporaryDirectory() as destination:
            write_outputs(self.document, destination)
            self.assertEqual({path.name for path in Path(destination).iterdir()}, expected)

    def test_serialization_is_stable(self) -> None:
        first = json.dumps(self.document.to_dict(), ensure_ascii=False, sort_keys=True)
        second = json.dumps(self.document.to_dict(), ensure_ascii=False, sort_keys=True)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
