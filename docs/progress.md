# Progress Log

## 2026-09-03 - Phase 1 started

DONE
- Read the supplied project instruction and prior inspection report.
- Confirmed the workspace was empty and not yet a Git repository.
- Copied the source PDF into the project without modifying the original.
- Verified source and project-copy SHA-256 hashes match.
- Confirmed 61 pages, A4, native text, no encryption/forms/JavaScript.
- Rendered representative pages for visual inspection.
- Tested native table discovery on pages 9, 10, 29, 30, and 42.

OBSERVED
- Numbered headings have consistent typography and up to four numeric levels.
- Procedure numbering is visually distinct from section headings.
- Tables use merged cells; Table 7 continues from page 29 to page 30.
- Figure captions are native text and screenshots are separate image objects.
- Page number, certification marks, and legal text form repeated footer noise.
- Page boundaries split semantic units and therefore cannot terminate sections.

DECIDED
- Use `pdfplumber` as the single primary extraction dependency.
- Keep physical and logical representations together.
- Preserve boilerplate as classified evidence but exclude it from semantic elements.
- Use native captions/regions for figures; no OCR.
- Use standard-library `unittest` so development does not require pytest.

CHANGED
- Added the project source, package skeleton documentation, and output location.

NEXT
- Implement models and extraction modules.
- Generate the first canonical output.
- Validate and visually spot-check difficult cases.

## 2026-09-03 - First-pass audit and corrections

DONE
- Generated and inspected the first canonical artifact.
- Checked all root sections, section 12, tables 1/7/8, figure IDs, cross-page
  elements, classifications, and source-line ownership.

OBSERVED
- Sections 4 and 12 contain valid headings using regular Calibri instead of the
  more common Calibri Light.
- Pdfplumber omitted visible merged value `Action` from Table 7's raw cell grid.
- The manual prints `Snp.3` twice on pages 10 and 11.
- The body contains six valid `16.2.4.x` headings absent from the printed TOC.

DECIDED
- Expand heading evidence without accepting ordinary numbered procedures.
- Recover missing first-column merged text from its native geometric region.
- Page-qualify canonical figure IDs and preserve printed IDs separately.
- Validate TOC identifiers as a subset of body identifiers.

CHANGED
- Corrected the complete section 1-18 hierarchy.
- Corrected Table 7 merged context across pages 29-30.
- Added stronger landmark, uniqueness, TOC, and coverage checks.

NEXT
- Run final compile, regression, determinism, and artifact inspection.

## 2026-09-03 - Phase 1 implementation complete

DONE
- Compiled all source and test modules.
- Passed 13 regression tests.
- Generated `canonical.json`, `validation.json`, and `page_inventory.csv` twice.
- Confirmed byte-identical SHA-256 hashes across independent runs.
- Confirmed all 683 eligible body lines belong to logical elements.
- Confirmed 25 validation checks: 24 pass, 1 documented source warning, 0 fail.

OBSERVED
- Final model contains 61 pages, 89 sections, and 217 semantic elements:
  50 paragraphs, 98 lists, 9 procedures, 9 tables, and 51 figures.
- The only warning is the duplicate printed `Snp.3` identifier.

DECIDED
- Phase 1 is technically complete and awaits human acceptance.
- No chunking or retrieval work will start without a separate Phase 2 agreement.

CHANGED
- Added schema documentation, operating runbook, and final outputs.

NEXT
- Human review of representative canonical sections/tables.
- After acceptance, plan chunking experiments as a new phase.

## 2026-09-03 - Implementation review

DONE
- Inspected code, outputs, tests, validation, PDF tags, hardcoding.
- Viewed pages 20-23, 27-31, 42-45, 47-50.
- Added `docs/review.md`.
- Documentation changed. Parser code unchanged.

FOUND
- Core hierarchy/provenance/tables strong.
- PDF tags and 83 internal links ignored.
- 16.2.2 interface labels mis-typed as procedures.
- Interface-to-figure relation implicit.
- Continuation/TOC/footer rules tightly tuned.

VERDICT
- Minor parser corrections needed first.
- Do not freeze. Do not chunk.

NEXT
- Agree P0/P1 from `docs/review.md`.

## 2026-09-04 - Parsing corrections complete

DONE
- Added generic local numbered groups and conservative labelled blocks.
- Nested interface descriptions, lists, and figures under CANoe, Power Supply,
  SDT, FPGA, and VTE.
- Preserved the real five-step procedure in 16.2.1.
- Strengthened table continuation using owner, geometry, and repeated headers.
- Added native/non-native input detection without OCR.
- Added readable semantic structure and structured parsing warnings.
- Changed generated output to the agreed five-file contract.
- Expanded regression tests for hierarchy, cross-page content, semantic groups,
  tables, renderer output, provenance, validation, and artifact names.

DECIDED
- Parsing is complete enough to close this phase.
- Warnings describe review-worthy joins/associations; they are not hidden.
- No chunking or retrieval logic belongs in the parser.

NEXT
- Agree the chunking contract, test cases, token policy, and evaluation method.
- Implement chunking only after that agreement.

## 2026-09-09 - Golden evaluation seed complete

DONE
- Initialized the repository with a Phase 1 baseline commit and created the
  `feature/golden-evaluation-dataset` branch.
- Reviewed all 61 PDF pages plus the canonical hierarchy, tables, procedures,
  figures, warnings, and validation output.
- Added a deterministic builder for JSONL, CSV, statistics, coverage, and QC.
- Created 132 source-grounded questions with required and acceptable retrieval
  sets, exact metadata lineage, hard negatives, and analysis flags.
- Added contract tests for size, IDs, categories, source resolution, retrieval
  consistency, and JSONL/CSV row parity.
- Imported and rendered the CSV through the spreadsheet runtime.

DECIDED
- Keep the PDF authoritative and the parsed model as supporting evidence.
- Freeze the initial benchmark independently of future chunking policy.
- Preserve manual-review candidates and parser warnings in the QC report.
- Add failure-driven questions as a new reviewed wave, not silent edits.

NEXT
- Define chunk objects, token accounting, overlap, and parent-context policy.
- Run fixed-dataset Recall@K, MRR, and nDCG comparisons across chunkers.
