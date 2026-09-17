# Parsing subsystem

Status: subsystem reference  
Owner: parser  
Last reviewed: 2026-09-17  
Source of truth for: parser responsibilities, evidence model, and heuristic boundary

## Purpose

The parser preserves native PDF evidence and reconstructs conservative logical
structure without OCR or probabilistic interpretation. Logical cleanup never
destroys the page, line, bounding-box, font, or reading-order evidence needed to
trace an element to the source.

## Responsibilities

- `domain.py`: canonical physical/logical dataclasses and JSON serialization.
- `parser.py`: PDF orchestration, metadata, physical extraction, and outputs.
- `normalize.py`: conservative whitespace, control-character, and line joins.
- `structure.py`: headings, paragraphs, lists, procedures, local groups, and
  labelled-block reconstruction.
- `tables.py`: table fragments, merged context, captions, and continuation.
- `figures.py`: native captions and large image-region association.
- `inspection.py`: recursive walks, ambiguity records, and semantic rendering.
- `validation.py`: generic invariants and document-specific regressions.
- `cli.py`: parsing command only.

Several implementations remain in flat package modules while migration to
`parsing/` is characterized. Flat imports are compatibility boundaries, not a
second implementation.

## Physical and logical models

Physical pages retain dimensions, page type, ordered text lines, table
fragments, figure regions, and boilerplate. Lines retain original and normalized
text, bounding boxes, dominant font, size, and classification. Coordinates use
PDF points with top-left origin, matching pdfplumber's top/bottom convention.

The logical document contains numbered sections with identifiers, depth,
parents, ancestor paths, sequence, page ranges, heading sources, and ordered
typed elements. Elements carry source spans and may own children. `local_group`
represents a short numbered group inside a section; `labelled_block` preserves a
local label/body relation. Tables are first-class elements with physical
fragments and resolved rows. Figures preserve captions and regions but do not
interpret pixels.

## Heuristic boundary

- Heading recognition combines numeric shape, font/size, and left-edge geometry.
- Paragraph continuation uses vertical gap and next-page position evidence.
- Lists use known bullet markers with limited nesting.
- Procedures combine printed numbering, typography, and imperative evidence.
- Table continuation requires page adjacency, compatible position, owner, and
  column geometry; repeated continuation headers are removed.
- Figures associate the nearest qualifying large image above a same-page caption.
- Footer and table-of-contents rules contain manual-specific positions/pages.
- Ambiguous joins and associations produce warnings; no numeric confidence score
  is invented.

## Output contract

Parsing emits exactly `document.json`, `semantic_structure.md`,
`page_inventory.csv`, `validation_report.json`, and `parsing_warnings.json`.
Field-level contracts are defined in `../SCHEMA.md`; operations are defined in
`../workflows/runbook.md`.

## Excluded evidence

OCR, screenshot semantics, character-level table geometry, small/original image
objects, PDF tags/MCIDs, internal links, colors, matrices, and style flags are
outside the current canonical contract.
