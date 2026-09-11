# Canonical Output Schema

## Purpose

`output/parsing/document.json` contains two linked views of the same manual:

- `pages`: physical evidence as extracted from the PDF.
- `sections`: logical content reconstructed for later structure-aware use.

Keeping both makes normalization and reconstruction auditable.

## Document fields

- `schema_version`: shape/version of this JSON contract.
- `parser_version`: code version that produced the artifact.
- `document_id`: stable project identifier.
- `title`: known document title.
- `source_file`: preserved input filename.
- `source_sha256`: exact source identity.
- `metadata`: PDF metadata plus controlled ingestion facts.
- `pages`: ordered physical pages.
- `sections`: ordered flat section list linked through parent IDs.

## Physical page

- `page_number`: one-based PDF page number.
- `width`, `height`: PDF points.
- `page_type`: `cover`, `toc`, or `body`.
- `lines`: native ordered text lines.
- `table_fragments`: per-page ruled table geometry and raw cells.
- `figure_regions`: large native image regions; small repeated logos excluded.

## Physical line

- `id`: stable page/order identifier.
- `text`: source extraction preserved without semantic rewriting.
- `normalized_text`: conservative artifact/whitespace normalization.
- `bbox`: `x0`, `top`, `x1`, `bottom` in PDF points, top-left convention.
- `font_name`, `font_size`: evidence used for classification.
- `classification`: `body`, `heading`, `table_text`, `table_caption`,
  `figure_caption`, `boilerplate`, `toc`, or `cover`.

Classification does not delete source evidence. For example, a footer remains in
`pages` but never becomes a logical searchable element.

## Section

- `section_id`: printed numeric identifier such as `16.2.4.1`.
- `title`: heading text without the identifier.
- `level`: count of numeric path components.
- `parent_section_id`: nearest numeric parent or null for top level.
- `ancestor_path`: full human-readable path including this section.
- `sequence`: document heading order.
- `page_start`, `page_end`: range including direct content and descendants.
- `heading_source`: source page, bounding box, and physical line ID.
- `elements`: direct content only; child content remains in child sections.

## Element

- `id`: unique deterministic identifier.
- `type`: `paragraph`, `list`, `procedure`, `local_group`, `labelled_block`,
  `table`, or `figure`.
- `sequence`: global semantic event order.
- `text`: readable text/caption; table detail lives under `data`.
- `page_start`, `page_end`: physical provenance range.
- `sources`: one or more page/bounding-box/source-ID links.
- `data`: type-specific structured information.
- `children`: recursively owned elements; empty for leaf elements.

## Semantic groups

- `local_group`: numbered local grouping such as `1. CANoe`; keeps label, printed
  order/marker, kind, sources, page range, and child content.
- `labelled_block`: short heading-like label such as `Validation Rules`, `Invalid
  Example`, `Parameter Warning`, or `Note`; owns following local content.
- Descendants of a local group carry `data.local_group_id`.

## Lists and procedures

`data.items` preserves item text, nesting level, marker, and its own source spans.
`ordered` distinguishes procedures from unordered lists. Wrapped items and clear
cross-page continuations become one logical item with multiple source spans.

## Tables

- `printed_id`, `caption`: source label.
- `columns`: normalized semantic column headings.
- `rows`: logical rows before merged-context propagation.
- `resolved_rows`: retrieval-ready rows with inherited parent cells filled.
- `raw_rows`: inspectable cells tied to physical fragment and row number.
- `fragment_ids`: one or more physical fragments.

The raw and resolved forms intentionally coexist. The resolved form is convenient;
the raw form shows exactly what transformation produced it.

## Figures

- Canonical ID includes printed ID and page because the source repeats `Snp.3`.
- `printed_id` and `caption` preserve source labeling.
- `region_id` and `region_bbox` link to a large native image when available.
- `semantically_interpreted` is always false in Phase 1.

## Validation output

`output/parsing/validation_report.json` contains an overall status, aggregate counts, and named
checks with `PASS`, `WARN`, or `FAIL`. A warning records a known source anomaly or
accepted limitation. A failure means parsing is not acceptable for the approved
source and must be investigated before later phases.

`output/parsing/parsing_warnings.json` separately records ambiguity type, severity,
message, section, element, and pages. `output/parsing/semantic_structure.md` is a human
inspection view. It intentionally omits geometry and source IDs.

## Missing fields

- Child section list. Derive from parent IDs.
- Explicit page-break object. Derive from source pages.
- Numeric confidence score.
- Per-cell boxes and merge spans.
- Per-element extraction method.
- PDF tag/MCID/color/link/annotation data.
- Original image bytes.

Parsing schema is ready for the chunking design review. Chunk objects are not yet
part of this contract.

## Golden evaluation schema

`output/datasets/golden/golden_dataset.jsonl` is a separate derived contract. Each
line contains:

- question identity, text, type, and difficulty;
- expected answer, kept separate from evidence requirements;
- source document, pages, section paths, semantic-unit IDs, and element IDs;
- primary, required, and acceptable retrieval source sets;
- required and supporting evidence;
- naturally confusing hard-negative element IDs;
- answerability and retrieval-analysis flags;
- notes for exceptional semantic or parsing cases.

The flat CSV uses the same fields. Lists are serialized with `|`; multiple
section paths and evidence strings use ` || `. Boolean flags remain explicit.
No chunk IDs exist because the benchmark precedes chunk-policy selection.

## Baseline chunk schema

`output/retrieval/reference/chunks/chunks.jsonl` contains one record per token
window:

- deterministic `chunk_id`, zero-based `chunk_index`, and `document_id`;
- exact chunk `text`, `token_count`, `token_start`, and exclusive `token_end`;
- inclusive `page_start` and `page_end`;
- first `section_path` plus all contributing `section_paths`;
- contributing `semantic_unit_ids` and `source_element_ids`;
- contributing `content_types`.

Recursive child elements include their semantic ancestor IDs. Source element IDs
identify the elements whose text directly contributed to the chunk.

## Baseline retrieval schema

`evaluation/retrieval_results.jsonl` records the unchanged question, required
semantic units, ranked chunks with scores and complete metadata, retrieved IDs,
and the per-question evaluation. Coverage and completion are keyed by K.

`evaluation/retrieval_metrics.json` contains dataset size, strict Recall@K,
semantic-unit recall@K, MRR, mean evidence coverage at the maximum K, pass/fail
counts, and simple failure categories.

`run_config.json` records source and golden-set hashes, resolved configuration,
runtime versions, and chunk count. `manifest.json` records SHA-256 for every other
baseline artifact.
