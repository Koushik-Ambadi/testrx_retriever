# Project workflow runbook

Status: workflow operations reference  
Owner: project operations  
Last reviewed: 2026-09-17

## Normal operation

From the project root:

```powershell
$env:PYTHONPATH = "src"
python -m testrx_retriever source/TESTRX_User_Manual.pdf --output output/parsing
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

1. Read `output/parsing/validation_report.json`. Stop if any check is `FAIL`.
2. Read `output/parsing/parsing_warnings.json`; inspect every error and new warning type.
3. Scan `output/parsing/page_inventory.csv` for pages with unusual counts.
4. Read `output/parsing/semantic_structure.md` for hierarchy and group ownership.
5. Inspect `output/parsing/document.json` when exact provenance is needed.
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
python -m testrx_retriever.workflows.reference_run --config configs/retrieval/reference.json
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
python -m testrx_retriever.experiments --config experiments/retrieval/chunk-dimension-sweep/experiment.json
python -m unittest discover -s tests -v
```

Review in this order:

1. Confirm the matching record in `experiments.jsonl` contains the intended
   source hashes, resolved configuration, retention policy, and observations.
2. Filter `runs.jsonl` by `experiment_id`, then compare Recall@1 and MRR before
   interpreting Recall@10.
3. Compare every measured Recall@K with its random-lineage control.
4. Inspect chunk lineage density, query-word coverage, collision fraction, and
   top-1 stability in the run records.
5. Join `question_metrics.jsonl` to runs by `run_id`; slice failures by
   difficulty, question type, category, page, section path, or semantic ID.
6. Verify `manifest.json` and rerun the full suite before accepting a change.

Do not compare fixed K across chunk sizes without noting the fraction of the
index returned. Do not interpret this lexical, same-document experiment as a
learned semantic embedding evaluation.

For a new experiment, copy an existing configuration under
`experiments/retrieval/<study-name>/`, assign a new stable `experiment_id`, and edit
the component grid. Supported component implementations are validated before a
run. The shared store upserts by `experiment_id`; rerunning does not duplicate
records. Retention defaults must remain compact. Full artifacts belong only in
the explicitly configured reference pipeline.

## Freeze gate

Verdict: **Parsing, golden dataset, and baseline retrieval gates passed.**

See `docs/reviews/2026-09-12-project-review-history.md` for the historical phase
findings and resolutions.

## Paraphrase-bias and reusable analytics operation

```powershell
$env:PYTHONPATH = "src"
python scripts/build_golden_dataset.py
python -m testrx_retriever.workflows.reference_run --config configs/retrieval/reference.json
python -m testrx_retriever.experiments --config experiments/retrieval/paraphrase-bias-baseline/experiment.json
python -m testrx_retriever.evaluation.analysis --group-by experiment_id,paraphrase_level
python -m testrx_retriever.evaluation.analysis --group-by token_size,embedding_family,embedding_dimension
python -m unittest discover -s tests -v
```

The older chunk/dimension configuration explicitly filters `original` questions
so extending the dataset cannot silently change its evaluation population. The
paraphrase configuration includes all five levels. Review the full reference
analytics for paired families and detailed slices; use the CLI for arbitrary
cross-run views without writing new files. See
`src/testrx_retriever/evaluation/analytics.md` for all dimensions and metric
definitions.

## Production candidate comparison

```powershell
python -m pip install -e ".[transformers]"
python scripts/install_model_candidates.py
python -m testrx_retriever.workflows.model_comparison --config configs/pipelines/candidates.json
python -m unittest discover -s tests -v
```

Model downloads are explicit. Verify registry identity and local artifact paths
before running. Review candidate recall before reranked metrics; reranking must
not hide missing evidence at the candidate stage.

## Hierarchical chunking experiment

```powershell
python -m testrx_retriever.workflows.hierarchy_experiment --config configs/pipelines/hierarchical_chunking_experiment.json
python -m unittest discover -s tests -v
```

Treat `output/retrieval/pipeline_hierarchy_chunking/` as reproducible ignored
run output. Compare fixed-K metrics together with index exposure, evidence
completeness, emitted chunk counts, fallback splits, and the documented latency
boundary. Do not select a production policy from aggregate MRR alone.

## Frozen retrieval application

Install the optional local-model runtime and model artifacts, then query the
frozen default:

```powershell
python -m pip install -e ".[transformers]"
python scripts/install_model_candidates.py
testrx-retrieve "How do I create a project?"
testrx-retrieve "How do I create a project?" --candidate-k 15 --top-k 10
```

The runtime source of truth is `configs/retrieval/production.json`. Defaults are
hierarchy max 384, pinned BGE, pinned MiniLM, candidate K=10, and final K=5.
`candidate_k` must be at least `top_k`. The CLI is a diagnostic convenience and
loads models on each invocation; application integrations should construct one
`RetrievalApplication` and reuse it.

Reproduce the frozen quality metrics with:

```powershell
python -m testrx_retriever.workflows.model_comparison --config configs/pipelines/production_evaluation.json
```

Review `configs/retrieval/production.md` before changing chunking, model
revisions, or defaults. Such a change reopens the retrieval gate and requires
the same complete-evidence, context-token, failure, and latency views.

Run the fixed fresh-question statement audit with:

```powershell
python scripts/manual_retrieval_smoke.py
python scripts/score_manual_retrieval_smoke.py
```

The first command loads the production wrapper once, retrieves six questions,
and splits every chunk into atomic review statements. The second applies the
documented human rubric and writes the complete per-statement JSON and Markdown
report under `output/retrieval/pipeline_manual_smoke/`. Review score rules when
questions change; they intentionally encode human judgments for this fixed set.
