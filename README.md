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
- One runnable 300/30 baseline flow comparing lexical hashing, corpus-fitted LSA
  bi-encoding, reciprocal-rank fusion, and deterministic pairwise reranking.
- Separate model stores and lazy adapters for attention-based bi-encoders and
  cross-encoders; LLMs remain outside the retrieval runtime.
- A pinned production-candidate comparison covering BGE, E5, MiniLM reranking,
  lexical controls, and reciprocal-rank fusion over all 196 questions.
- Controlled 125/200/250/300-token and 128-16,384-dimension retrieval study with
  random-lineage, collision, lexical, and ranking-stability diagnostics.
- Controlled four-level paraphrase extension and reusable analytics by run,
  configuration, category, source, and question family.
- A frozen hierarchy-384 / BGE / MiniLM retrieval default with candidate K=10,
  final K=5, and a configurable query-to-chunks application wrapper.

Explicitly excluded:

- OCR or screenshot interpretation.
- BM25, committed model weights, query rewriting, and multi-query retrieval.
- Answer generation and LLM-based evaluation.
- A service or API layer.

## Source

The preserved input is `source/TESTRX_User_Manual.pdf`. Its SHA-256 is recorded
in `source/README.md`. The original Downloads copy is not modified.

## Run

```powershell
python -m pip install -e .
testrx-parse source/TESTRX_User_Manual.pdf --output output/parsing
testrx-baseline --config configs/retrieval/reference.json
testrx-experiments --config configs/retrieval/experiments/chunk_dimension_sweep.json
testrx-experiments --config configs/retrieval/experiments/paraphrase_bias_baseline.json
testrx-analyze --group-by experiment_id,paraphrase_level
testrx-pipeline --config configs/pipelines/baseline.json
testrx-hierarchy-experiment --config configs/pipelines/hierarchical_chunking_experiment.json
testrx-retrieve "How do I create a TESTRX project?"
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
- `output/retrieval/pipeline_baseline/`: complete lexical/static-semantic,
  hybrid-fusion, and pairwise-reranking baseline flow with per-system metrics.

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

Project-level documentation is indexed in [`docs/README.md`](docs/README.md).
Subsystem contracts and experiment records live beside the code, configuration,
or durable dataset they describe. Generated reports remain under `output/` and
are not hand-maintained.

## Repository map

```text
testrx_retriever/
├── source/                    preserved, checksummed manual and manifest
├── configs/                   reference, pipeline, and experiment configurations
├── docs/                      project governance, progress, and dated reviews
├── src/testrx_retriever/      parsing, retrieval, evaluation, and workflows
├── model_store/               encoder, reranker, and generator artifacts
├── tests/                     parser, dataset, retrieval, and determinism tests
├── skills/                    reusable, cross-project engineering workflows
├── output/                    parsing, dataset, reference, and experiment layers
├── tmp/                       ignored render/verification intermediates
├── pyproject.toml             package metadata and dependency contract
└── README.md                  project entry point
```

## Current review state

The grounded benchmark, controlled retrieval studies, and production retriever
freeze are complete. The next gate is diversity-aware context assembly and
generator-facing evidence completeness.
