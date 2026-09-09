# TESTRX Retriever

Phase 1 converts the TESTRX User Manual PDF into a faithful, inspectable,
provenance-preserving canonical representation.

## Current boundary

Included:

- Native PDF extraction with page, bounding-box, font, and reading-order data.
- Conservative text normalization.
- Numbered section hierarchy reconstruction.
- Paragraph, list, procedure, local-group, labelled-block, table, and
  figure-reference elements.
- Merged-cell context and clear multi-page table continuation handling.
- Repeated boilerplate classification.
- Cross-page logical continuity.
- Canonical JSON, human semantic view, validation, warnings, and page inventory.

Explicitly excluded:

- OCR or screenshot interpretation.
- Chunking or token splitting.
- Embeddings, vector databases, retrieval, reranking, and generation.
- A service or API layer.

## Source

The preserved input is `source/TESTRX_User_Manual.pdf`. Its SHA-256 is recorded
in `source/README.md`. The original Downloads copy is not modified.

## Run

```powershell
python -m pip install -e .
python -m testrx_retriever source/TESTRX_User_Manual.pdf --output output
```

Run tests with the standard library:

```powershell
python -m unittest discover -s tests -v
```

## Outputs

- `output/document.json`: physical pages plus reconstructed logical sections.
- `output/semantic_structure.md`: readable hierarchy and semantic groups.
- `output/page_inventory.csv`: compact per-page inspection index.
- `output/validation_report.json`: named checks and measured coverage.
- `output/parsing_warnings.json`: inspectable ambiguity and continuation events.

Generated outputs are intentionally not the source of truth. The PDF is the
source of truth; `docs/decisions.md` records why the parser behaves as it does.

## Documentation map

- `docs/decisions.md`: accepted and superseded observations/decisions.
- `docs/plan.md`: scope, milestones, definition of done, and work sequence.
- `docs/architecture.md`: data flow, component responsibilities, schemas, and
  operating constraints.
- `docs/schema.md`: field-by-field meaning of physical and logical output.
- `docs/runbook.md`: repeatable operation, interpretation, and update procedure.
- `docs/review.md`: evidence-based audit and freeze blockers.
- `docs/progress.md`: chronological implementation and verification record.
- `docs/limitations.md`: known limitations and intentionally deferred work.

## Repository map

```text
testrx_retriever/
├── source/                    preserved, checksummed manual and manifest
├── docs/                      intent, decisions, design, progress, operations
├── src/testrx_retriever/      parser implementation
├── tests/                     source-specific and generic regression tests
├── output/                    five generated parsing artifacts
├── tmp/                       ignored render/verification intermediates
├── pyproject.toml             package metadata and dependency contract
└── README.md                  project entry point
```

## Current review state

Parsing implementation is complete. The five 16.2.2 interface groups now own
their text, lists, and figures. Validation has no failures. Chunking remains a
separate next phase and is not implemented here.
