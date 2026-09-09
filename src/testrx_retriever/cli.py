"""Command line entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .parser import parse_manual, write_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse the TESTRX User Manual into canonical JSON.")
    parser.add_argument("pdf", type=Path, help="Path to the preserved source PDF")
    parser.add_argument("--output", type=Path, default=Path("output"), help="Output directory")
    arguments = parser.parse_args()

    document = parse_manual(arguments.pdf)
    report, warnings = write_outputs(document, arguments.output)
    counts = report["summary"]
    print("Parsing complete\n")
    print(f"Pages: {counts['pages']}")
    print(f"Sections: {counts['sections']}")
    print(f"Semantic groups: {counts.get('semantic_groups', 0)}")
    print(f"Elements: {counts['elements']}")
    print(f"Tables: {counts['element_types'].get('table', 0)}")
    print(f"Figures: {counts['element_types'].get('figure', 0)}")
    print(f"Warnings: {warnings['summary']['warnings']}")
    print("\nOutput:")
    for name in (
        "document.json", "semantic_structure.md", "page_inventory.csv",
        "validation_report.json", "parsing_warnings.json",
    ):
        print(arguments.output / name)
    return 1 if report["overall_status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
