# Hierarchical chunking experiment

Date: 2026-09-15

Experiment ID: `hierarchical-chunking-v1`

Status: frozen experiment record; implementation and raw-data capture complete,
detailed comparison and chunk-policy selection intentionally deferred.  
Owner: retrieval experiments

## Objective and fixed contract

The experiment tests whether canonical section and semantic-element boundaries can preserve more self-contained procedural evidence than a flat token window. It reuses the existing retrieval and evaluation implementation without changing the 196-question golden set, source IDs, model revisions, exact cosine retrieval, RRF, MiniLM reranking, candidate K=20, or evaluation K={1,3,5,10}.

The fixed production-candidate systems are lexical hashing, BGE small English v1.5, E5 small v2, both lexical+dense RRF variants, and each system with/without the pinned MiniLM-L6 reranker. The unchanged token-window 300/30 configuration is the control.

## Implemented behavior

`hierarchical_pure` records and indexes every non-document canonical hierarchy node as its complete subtree. It imposes no maximum and intentionally contains overlapping parent/child candidates.

`hierarchical_max_tokens` begins at top-level sections. A subtree that fits is emitted. An oversized subtree descends to its canonical children. Emitted children receive concise hierarchy-label context and complete source lineage, not duplicated parent bodies. An oversized semantic leaf uses deterministic token splitting, retains its lineage, and records `fallback_split=true` with `split_reason=max_tokens_oversized_leaf`.

Chunk IDs derive from the document hash, tokenizer identity, strategy, configured maximum, canonical node, fallback part, and exact text. Repeated input/configuration produces identical chunk content and IDs. The legacy token-window serialization remains unchanged.

## Natural hierarchy measurements

The hierarchy contains 312 measured nodes including the document root and 311 non-document nodes. Level names are derived from canonical section levels and element types.

| Canonical level | Nodes | Min | Average | Median | P90 | P95 | P99 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| document | 1 | 9,762 | 9,762.00 | 9,762 | 9,762 | 9,762 | 9,762 | 9,762 |
| section level 1 | 18 | 29 | 542.33 | 368 | 2,129 | 2,263 | 2,263 | 2,263 |
| section level 2 | 42 | 27 | 199.26 | 129.5 | 431 | 480 | 1,224 | 1,224 |
| section level 3 | 23 | 35 | 154.61 | 119 | 310 | 377 | 633 | 633 |
| section level 4 | 6 | 38 | 89.83 | 83.5 | 166 | 166 | 166 | 166 |
| paragraph | 49 | 2 | 24.84 | 17 | 49 | 67 | 96 | 96 |
| list | 98 | 4 | 64.77 | 48 | 128 | 162 | 368 | 368 |
| figure | 51 | 5 | 6.37 | 6 | 8 | 9 | 11 | 11 |
| table | 9 | 54 | 147.22 | 127 | 426 | 426 | 426 | 426 |
| labelled block | 6 | 7 | 22.33 | 21 | 47 | 47 | 47 | 47 |
| procedure | 4 | 15 | 31.50 | 21.5 | 68 | 68 | 68 | 68 |
| local group | 5 | 22 | 39.40 | 36 | 56 | 56 | 56 | 56 |

Machine-readable per-node records and threshold counts for >256, >384, >512, >768, >1,024, >2,048, and >4,096 are stored under each hierarchy run's `hierarchy/` directory. Percentiles use the documented nearest-rank method.

## Maximum-token grid rationale

The preregistered bounded grid is 160, 256, 384, 512, 640, and 768 tokens.

- 160 is near list p95=162 and level-4 max=166, testing a granular semantic-leaf boundary.
- 256 is a conventional compact retrieval limit.
- 384 aligns with level-1 median=368 and level-3 p95=377.
- 512 covers nearly all level-2/3 subtrees and the largest natural table at 426.
- 640 specifically tests retaining the largest level-3 subtree at 633.
- 768 is the requested upper reference and tests broader structural context.

The grid was frozen after natural hierarchy measurement and before retrieval scores were inspected.

## Completed chunk inventory

| Variant | Chunks | Min | Average | Median | P90 | P95 | Observed max | Fallback fragments |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| token window 300/30 | 37 | 42 | 293.03 | 300 | 300 | 300 | 300 | 0 |
| pure hierarchy | 311 | 8 | 114.06 | 57 | 213 | 403 | 2,263 | 0 |
| hierarchy max 160 | 154 | 8 | 73.01 | 59.5 | 153 | 160 | 160 | 18 |
| hierarchy max 256 | 111 | 8 | 95.51 | 93 | 188 | 222 | 256 | 4 |
| hierarchy max 384 | 95 | 8 | 109.60 | 101 | 220 | 282 | 384 | 2 |
| hierarchy max 512 | 79 | 8 | 129.63 | 106 | 282 | 403 | 485 | 0 |
| hierarchy max 640 | 68 | 8 | 149.85 | 113.5 | 403 | 480 | 619 | 0 |
| hierarchy max 768 | 55 | 8 | 182.51 | 132 | 480 | 619 | 646 | 0 |

Pure hierarchy includes chunks longer than common transformer input limits and is a diagnostic control, not a deployable default. Bounded configurations respect their configured maximum after parent-context injection. Fallback splitting disappears at 512 and above.

## Raw results and latency contract

The ordinary-run root is `output/retrieval/pipeline_hierarchy_chunking/` and remains ignored by Git under the established artifact policy. It contains all eight completed variants plus `experiment_manifest.json`.

Each variant contains:

```text
run_config.json
summary.json
chunks/chunks.jsonl
chunks/statistics.json
hierarchy/nodes.jsonl              hierarchy variants only
hierarchy/statistics.json          hierarchy variants only
hierarchy/summary.md               hierarchy variants only
systems/<system>/results.jsonl     196 raw ranked/evaluated question rows
systems/<system>/metrics.json
systems/<timed-system>/query_latency.jsonl
analysis/model_category_analysis.json
analysis/model_category_report.md
```

Validation found 10 system directories and exactly 196 result rows per system for every variant. Each variant has seven timing files: five first-stage systems with all 196 questions, plus BGE+MiniLM and E5+MiniLM with the two fixed sentinels Q092 and Q130-P4.

Every latency row stores the question and benchmark dimensions, requested candidate K, requested top K, returned counts, chunk IDs, scores, `candidate_retrieval_ns`, `reranking_ns`, and `total_retrieval_cycle_ns`. Timings use `time.perf_counter_ns`, include query encoding, exact ranking, candidate selection, and reranking where enabled, and exclude chunking, index construction, and model loading. Cross-encoder pair-cache state is snapshotted, cleared for the cold-pair sentinel, then restored so latency capture cannot perturb or multiply evaluator work.

Q092 is an original hard procedure requiring two source units. Q130-P4 is a conceptual hard cross-reference requiring three source units. These timings are diagnostic sentinels, not a production latency distribution. A later dedicated benchmark can configure a larger explicit or deterministic stratified sample after chunking is shortlisted.

## Run log and observations

- Implemented hierarchy traversal and pure diagnostics before choosing bounded limits.
- Measured natural hierarchy sizes, then froze the six-limit grid.
- Initial all-query online reranker timing exposed multi-hour CPU cost. The final contract retains all first-stage timings and two explicit end-to-end sentinels for the two leading production paths while keeping full quality evaluation for all systems.
- Separated timing cache state from shared evaluator cache state after detecting redundant rescoring during trial runs.
- Completed and validated all eight variants; no partial-run summary was accepted.
- No graph is generated in this capture phase because the requested output is raw evidence. Plots and cross-variant derived analytics belong to the later comparison pass.

## Decision boundary and next analysis

No strongest configuration or production chunk policy is selected in this run. Detailed comparison is deliberately deferred at the user's request. The stored data supports later analysis of all overall/category/paraphrase/multi-unit metrics, candidate recall, number of chunks needed for complete evidence, index size, fallback behavior, and raw latency.

The later analysis should compare fixed-K results alongside index exposure and retrieved evidence completeness, inspect failures rather than selecting on aggregate MRR alone, and treat pure hierarchy's long overlapping chunks as a diagnostic control. Only after that analysis should one bounded hierarchy configuration be shortlisted for candidate-K tuning or generator-context evaluation.

## Reproduction

```powershell
python -m pip install -e ".[transformers]"
python scripts/install_model_candidates.py
python -m testrx_retriever.workflows.hierarchy_experiment --config configs/pipelines/hierarchical_chunking_experiment.json
python -m unittest discover -s tests -v
```

## Resolution (2026-09-17)

The deferred comparison is complete. Hierarchy max 384 was selected as the
bounded quality/context frontier, paired with BGE and MiniLM. Candidate K=10
and final K=5 were tuned separately. The binding decision, full trade-off table,
question slices, latency boundary, and residual risks are recorded in
`configs/retrieval/production.md`; this file remains the frozen preregistered
experiment record.
