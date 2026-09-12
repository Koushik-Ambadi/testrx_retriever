# TESTRX Retriever

The project converts the TESTRX User Manual PDF into a faithful canonical
representation, a source-grounded golden dataset, and a reproducible baseline
vector retriever.

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
- Deterministic 500-token chunks with 50-token overlap and source lineage.
- One local hashing embedder, exact cosine index, top-K retrieval, and golden-set
  evaluation.
- Controlled 125/200/250/300-token and 128-16,384-dimension retrieval study with
  random-lineage, collision, lexical, and ranking-stability diagnostics.
- Controlled four-level paraphrase extension and reusable analytics by run,
  configuration, category, source, and question family.

Explicitly excluded:

- OCR or screenshot interpretation.
- Alternative or semantic chunkers, embedding models, and retrievers.
- BM25, hybrid retrieval, reranking, query rewriting, and multi-query retrieval.
- Answer generation and LLM-based evaluation.
- A service or API layer.

## Source

The preserved input is `source/TESTRX_User_Manual.pdf`. Its SHA-256 is recorded
in `source/README.md`. The original Downloads copy is not modified.

## Run

```powershell
python -m pip install -e .
python -m testrx_retriever source/TESTRX_User_Manual.pdf --output output/parsing
python -m testrx_retriever.baseline --config configs/retrieval/reference.json
python -m testrx_retriever.experiments --config configs/retrieval/experiments/chunk_dimension_sweep.json
python -m testrx_retriever.experiments --config configs/retrieval/experiments/paraphrase_bias_baseline.json
python -m testrx_retriever.analytics --group-by experiment_id,paraphrase_level
```

Run tests with the standard library:

```powershell
python -m unittest discover -s tests -v
```

## Outputs

- `output/parsing/`: five reproducible parser artifacts.
- `output/datasets/golden/`: golden JSONL/CSV and dataset review reports.
- `output/retrieval/reference/`: the one full reference run, including chunks,
  embeddings, raw ranked results, configuration, report, and manifest.
- `output/retrieval/experiments/`: shared experiment catalog, run metrics,
  question-level analysis metadata, and checksums. It has no per-run folders.

Generate and validate the benchmark:

```powershell
python scripts/build_golden_dataset.py
python -m unittest discover -s tests -v
node scripts/verify_golden_csv.mjs
```

The Node command is an optional visual CSV check in the bundled Codex workspace
runtime. Dataset generation and contract tests use the declared Python project
dependencies.

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
- `docs/golden_dataset.md`: benchmark strategy, lifecycle, and evaluation use.
- `docs/baseline_retrieval.md`: baseline design, metrics, and artifact contract.
- `docs/analytics.md`: reusable dimensions, metric definitions, and commands.
- `docs/experiments/`: experiment-specific designs and findings; project-wide
  decisions and operating rules remain in the top-level documentation.

## Repository map

```text
testrx_retriever/
├── source/                    preserved, checksummed manual and manifest
├── configs/retrieval/         reference and reusable experiment configurations
├── docs/                      intent, decisions, design, progress, operations
├── src/testrx_retriever/      parser, chunker, embedder, index, and evaluator
├── tests/                     parser, dataset, retrieval, and determinism tests
├── output/                    parsing, dataset, reference, and experiment layers
├── tmp/                       ignored render/verification intermediates
├── pyproject.toml             package metadata and dependency contract
└── README.md                  project entry point
```

## Current review state

The 132-question legacy set remains unchanged and 64 controlled paraphrases are
appended in 16 families. The reproducible reference produces 22 chunks. The
shared store records 29 original-only chunk/dimension runs and one 196-question
paraphrase run. Strong/conceptual MRR degradation supports a material lexical
explanation; index-size and lineage-density inflation remain important, and the
results do not establish semantic generalization.
