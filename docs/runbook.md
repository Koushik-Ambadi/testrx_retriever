# Parser Runbook

## Normal operation

From the project root:

```powershell
$env:PYTHONPATH = "src"
python -m testrx_retriever source/TESTRX_User_Manual.pdf --output output
python -m unittest discover -s tests -v
```

Expected current result:

- 61 pages.
- 89 sections.
- Counts are printed by the CLI; semantic groups are reported separately.
- 9 printed tables.
- 51 printed figure captions.
- 0 failed validation checks.
- Expected parsing warnings are review signals, including accepted table and
  cross-page joins and the page-10 vector/compound figure association.

## Review order

1. Read `output/validation_report.json`. Stop if any check is `FAIL`.
2. Read `output/parsing_warnings.json`; inspect every error and new warning type.
3. Scan `output/page_inventory.csv` for pages with unusual counts.
4. Read `output/semantic_structure.md` for hierarchy and group ownership.
5. Inspect `output/document.json` when exact provenance is needed.
6. Compare difficult cases to the PDF:
   - pages 9-10: Table 1 continuation;
   - pages 20-23: mixed-font section 12 hierarchy and cross-page lists;
   - pages 29-31: Tables 7/8 and Identifier continuation;
   - pages 42-47: table, procedures, screenshots, interface continuation;
   - pages 47-50: Map Labels level-four hierarchy;
   - pages 58-60: duplicate/late figure numbering and final section.

This order matters: automated invariants find omissions quickly, while visual
comparison verifies meaning and layout-derived relationships.

## Updating the manual

Do not overwrite the approved source silently.

1. Add the new PDF with a distinct stable filename.
2. Record filename, version, size, metadata, and SHA-256 in `source/README.md`.
3. Render representative pages and compare structure with the existing manual.
4. Add observations to `docs/decisions.md` before changing rules.
5. Run the parser into a separate output directory.
6. Review validation differences and add regression tests for real changes.
7. Promote the new source/output only after human approval.

## Investigating a failure

- Missing heading: inspect source line font, size, numeric depth, and x-position.
- Missing table value: inspect raw grid, physical table lines, and merged regions.
- Wrong table continuation: check page adjacency, bottom/top position, schema, and
  caption evidence; never join on page adjacency alone.
- Orphaned body line: find its physical line ID and inspect surrounding events.
- Missing figure region: determine whether the visual is vector artwork rather
  than a raster image; preserve the caption even without a region.
- Checksum failure: stop. The input is not the approved source.

## Why these controls exist

- Checksum prevents silent source replacement.
- Physical evidence makes normalization reversible and debuggable.
- TOC subset validation finds missing headings without treating an incomplete TOC
  as more authoritative than body content.
- Source-specific landmark tests catch regressions generic PDF rules cannot.
- Determinism makes diffs meaningful and later indexing reproducible.

## Phase boundary

Parsing and the chunking-independent golden seed are complete. The token baseline
is a separate module and command; do not add chunking behavior to the parser by
convenience.

## Golden dataset operation

From the project root:

```powershell
python scripts/build_golden_dataset.py
python -m unittest discover -s tests -v
node scripts/verify_golden_csv.mjs
```

The Node verification command uses the bundled Codex spreadsheet runtime. The
Python build and unit tests are the portable project contract.

Review in this order:

1. Confirm the builder reports 100-200 questions and no PDF lineage failures.
2. Read `golden_dataset_report.md` for type, difficulty, and retrieval flags.
3. Read `source_coverage_report.md`; gaps are allowed only when they do not
   support a distinct information need.
4. Review every item in `quality_control_report.md`, especially parser warnings
   and weaker independent PDF-text matches.
5. Run contract tests before changing IDs, schema, or question order.
6. For a source-PDF change, regenerate the parser outputs first, review their
   diff, then rebuild the benchmark as a separately reviewed change.

Do not silently renumber existing question IDs after the seed is used in an
experiment. Append a new wave or version the dataset when semantics change.

## Baseline retrieval operation

Build and evaluate from the project root:

```powershell
$env:PYTHONPATH = "src"
python -m testrx_retriever.baseline --config configs/retrieval_baseline.json
python -m unittest discover -s tests -v
```

Review in this order:

1. Confirm `run_config.json` contains the intended source hash, golden-set hash,
   tokenizer, chunk settings, embedding version, dimension, and K values.
2. Inspect `chunks/chunks.jsonl` for count, token sizes, overlap, ordering, and
   source lineage.
3. Confirm `index/chunk_ids.json` order matches the chunk order and embedding row
   count.
4. Read `evaluation/retrieval_metrics.json` and then the human report.
5. Inspect every failed question in `retrieval_results.jsonl` before proposing a
   later strategy.
6. Verify every checksum in `manifest.json` when artifacts are transferred.

The build has no timestamp and no random state. Repeating it with identical input,
configuration, Python, and NumPy must produce byte-identical artifacts. The
integration test enforces this for the complete bundle.

## Chunk-size and dimension experiment operation

Run the controlled sweep from the project root:

```powershell
$env:PYTHONPATH = "src"
python -m testrx_retriever.experiments --config configs/retrieval_sweep.json
python -m unittest discover -s tests -v
```

Review in this order:

1. Confirm `summary.json` source hashes and resolved configuration match the
   frozen canonical document and golden dataset.
2. Read `report.md`, comparing Recall@1 and MRR before interpreting Recall@10.
3. Compare every measured Recall@K with its random-lineage control.
4. Inspect chunk lineage density, query-word coverage, collision fraction, and
   top-1 stability in `summary.json`.
5. Use `question_diagnostics.jsonl` to inspect individual rank changes and
   relevant-versus-irrelevant score margins.
6. Verify `manifest.json` and rerun the full suite before accepting a change.

Do not compare fixed K across chunk sizes without noting the fraction of the
index returned. Do not interpret this lexical, same-document experiment as a
learned semantic embedding evaluation.

## Freeze gate

Verdict: **Parsing, golden dataset, and baseline retrieval gates passed.**

See `docs/review.md` for each phase's findings and resolution.
