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
python -m testrx_retriever.baseline --config configs/retrieval_baseline.json
python -m testrx_retriever.experiments --config configs/retrieval_sweep.json
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
- `output/retrieval/experiments/`: shared compact run metrics,
  per-question diagnostics, human report, and checksums.

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
- `docs/retrieval_experiments.md`: controlled study design, measurements,
  explanations, limitations, and next experiments.

## Repository map

```text
testrx_retriever/
├── source/                    preserved, checksummed manual and manifest
├── configs/                   versioned baseline and experiment configurations
├── docs/                      intent, decisions, design, progress, operations
├── src/testrx_retriever/      parser, chunker, embedder, index, and evaluator
├── tests/                     parser, dataset, retrieval, and determinism tests
├── output/                    parsing, dataset, reference, and experiment layers
├── tmp/                       ignored render/verification intermediates
├── pyproject.toml             package metadata and dependency contract
└── README.md                  project entry point
```

## Current review state

The parser and 132-question golden dataset remain unchanged. The reproducible
baseline produces 22 chunks. The controlled study records 29 runs across four
smaller chunk sizes, seven hashing dimensions, and the unchanged control. The
results support a closed-domain lexical explanation and expose index-size and
lineage-density inflation; they do not establish semantic generalization.
