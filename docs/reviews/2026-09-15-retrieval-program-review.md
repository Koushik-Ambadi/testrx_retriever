# TESTRX retrieval program: current evidence and next design

Date: 2026-09-15

Status: frozen program review; end-to-end retrieval was working and a production
retriever had not yet been selected at the review date.

This is a point-in-time planning review for the retrieval program. Current work
is owned by `docs/roadmap.md`; experiment details remain beside their
configurations. This document preserves the evidence-to-design reasoning at its
review date.

## 1. Executive decision

The project has proved the complete retrieval path and has two credible learned retriever candidates. The best measured configuration is E5 small v2 followed by the MiniLM cross-encoder, with MRR 0.872 and Recall@1 0.760 on all 196 questions. BGE small English v1.5 plus the same reranker is effectively tied: MRR 0.869, better Recall@3/5, mean evidence coverage, and candidate recall.

These results are strong enough to continue toward production, but not enough to freeze a production design. The present evaluation reused the full diagnostic set for comparison, used one token-window chunk policy, and fixed first-stage candidate depth at 20. It also has no independent generator-context selection parameter. On an index of only 37 chunks, candidate K=20 exposes 54% of the corpus, so high candidate recall is not by itself persuasive.

The next experiment should isolate the two deployment-depth variables on the current 300/30 chunks:

1. first-stage candidate K: how many chunks the encoder or fused retriever sends to the reranker;
2. final context K and token budget: how many reranked chunks are assembled for the generator.

Only after that should chunking strategies be compared. This order prevents a better K setting from being mistaken for a better chunker.

## 2. What exists now

```text
TESTRX PDF
  -> canonical document with source lineage
  -> configurable token-window chunker
  -> first-stage retrievers
       lexical hashing
       static corpus-fitted LSA
       contextual BGE / E5 bi-encoders
  -> optional reciprocal-rank fusion
  -> optional lexical or MiniLM cross-encoder reranker
  -> common grounded evaluator and category analysis
```

Model artifacts are separated by role under `model_store/encoders/`, `model_store/rerankers/`, and `model_store/generators/`. Runtime adapters mirror those roles under `src/testrx_retriever/retrieval/`. Generator storage is reserved; generation is outside the current runtime boundary.

The benchmark contains 196 questions: 132 preserved original questions and 64 controlled paraphrases across 16 source families. The paraphrases retain the same required source lineage, allowing lexical distance to change while ground truth stays fixed.

## 3. Experiment ledger and conclusions

| Experiment | Population and fixed contract | Variables | Main conclusion |
|---|---|---|---|
| Reference baseline | 132 originals; 500/50 chunks; exact cosine; K 1/3/5/10 | 4,096-dimensional signed word/bigram hashing | Good closed-domain result, but broad chunks and lexical alignment make it optimistic. |
| Chunk/dimension sweep | 132 originals; same document/evaluator | Chunk 125/13, 200/20, 250/25, 300/30; hash dimensions 128-16,384; 500/50 control | Larger chunks raise scores and random lineage coverage. Hash collisions matter sharply below 4,096. The experiment does not demonstrate semantic generalization. |
| Paraphrase-bias study | 132 originals + 64 controlled paraphrases; 500/50/4,096 | Original, light, moderate, strong, conceptual wording | Lexical performance falls materially as source wording disappears. The benchmark is now a useful semantic-distance diagnostic. |
| Runnable engineering baseline | 196 questions; 300/30; candidate K=20 | lexical hashing, LSA, RRF, lexical pairwise reranking | The complete component contract works. LSA and lexical reranking are wiring baselines, not production model choices. |
| Production candidate comparison | 196 questions; 300/30; exact cosine; candidate K=20; evaluation K 1/3/5/10 | lexical, BGE, E5, lexical+dense RRF; with/without MiniLM reranking | Learned dense models beat lexical overall. MiniLM strongly improves top-rank quality, but pairwise reranking can hurt multi-unit evidence assembly. RRF helps selected segments but not aggregate performance. |

### Chunk and hashing findings

| Chunk/overlap | Chunks | R@1 | R@3 | R@5 | R@10 | MRR | Random lineage R@10 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 125/13 | 88 | 0.530 | 0.727 | 0.788 | 0.879 | 0.701 | 0.198 |
| 200/20 | 55 | 0.561 | 0.727 | 0.803 | 0.894 | 0.703 | 0.275 |
| 250/25 | 44 | 0.591 | 0.758 | 0.818 | 0.909 | 0.713 | 0.311 |
| 300/30 | 37 | 0.606 | 0.788 | 0.871 | 0.917 | 0.724 | 0.353 |
| 500/50 control | 22 | 0.667 | 0.811 | 0.879 | 0.924 | 0.780 | 0.529 |

These are the 4,096-dimensional lexical runs. At 16,384 dimensions, MRR for the four diagnostic chunk sizes was 0.723, 0.736, 0.743, and 0.763. Pooled failure fell from 27.3% at 128 dimensions to 10.0% at 4,096, 8.0% at 8,192, and 7.4% at 16,384. The 300/30/8,192 lexical configuration was chosen as a diagnostic engineering anchor, not as proof of optimal chunking.

### Lexical paraphrase findings

| Wording | N | R@1 | R@3 | R@5 | R@10 | MRR | Coverage@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original | 132 | 0.667 | 0.811 | 0.879 | 0.924 | 0.780 | 0.933 |
| Light | 16 | 0.625 | 0.750 | 0.938 | 0.938 | 0.786 | 0.979 |
| Moderate | 16 | 0.438 | 0.562 | 0.688 | 0.750 | 0.598 | 0.792 |
| Strong | 16 | 0.125 | 0.438 | 0.688 | 0.875 | 0.379 | 0.917 |
| Conceptual | 16 | 0.188 | 0.438 | 0.562 | 0.750 | 0.418 | 0.792 |

This established the main phenomenon: the original hashing score depends materially on shared vocabulary and does not represent robust semantic retrieval.

## 4. Models used

| Role | Generic system ID | Pinned model/algorithm | Revision or version | Important current settings | Status |
|---|---|---|---|---|---|
| Lexical encoder | `lexical_hashing` | signed word and word-bigram feature hashing | 1.0 | dimension 8,192 in candidate flow; normalized vectors | required control and possible hybrid input |
| Static semantic encoder | `semantic_lsa` | corpus-fitted truncated SVD over 4,096-dimensional hashing features | local implementation | latent dimension 128 | engineering baseline only |
| Contextual bi-encoder | `dense_bge_small_en_v15` | BAAI/bge-small-en-v1.5 | `5c38ec7c...267a` | 384 dimensions; batch 32; normalized embeddings; no prefix | production candidate |
| Contextual bi-encoder | `dense_e5_small_v2` | intfloat/e5-small-v2 | `ffb93f3b...7c52` | 384 dimensions; batch 32; `query: ` and `passage: ` prefixes; normalized embeddings | production candidate |
| Baseline reranker | `pairwise_lexical` | deterministic lexical pair scorer | local implementation | no learned weights | engineering control only |
| Cross-encoder reranker | `reranker_minilm_l6` | cross-encoder/ms-marco-MiniLM-L6-v2 | `233902d2...bee0a` | batch 32; query/chunk pair scoring | production candidate |

Weights are installed locally and pinned; they are intentionally ignored by Git. The current adapters use model-defined tokenization, pooling, truncation, and maximum sequence length. Those effective values must be exported into resolved run metadata and explicitly controllable before production so a library upgrade cannot silently change the experiment.

## 5. Current candidate results

| System | R@1 | R@3 | R@5 | R@10 | MRR | Coverage@10 | Candidate R@20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| E5 + MiniLM | **0.760** | 0.913 | 0.949 | **0.980** | **0.872** | 0.983 | 0.985 |
| BGE + MiniLM | 0.755 | **0.918** | **0.959** | **0.980** | 0.869 | **0.986** | **0.990** |
| Lexical+E5 RRF + MiniLM | **0.760** | 0.908 | 0.939 | 0.959 | 0.868 | 0.967 | 0.969 |
| Lexical+BGE RRF + MiniLM | 0.755 | 0.903 | 0.949 | **0.980** | 0.868 | 0.982 | 0.985 |
| Lexical + MiniLM | 0.750 | 0.888 | 0.918 | 0.944 | 0.854 | 0.955 | 0.949 |
| BGE | 0.663 | 0.898 | 0.934 | 0.959 | 0.821 | 0.959 | **0.990** |
| E5 | 0.663 | 0.898 | 0.929 | 0.964 | 0.820 | 0.969 | 0.985 |
| Lexical+E5 RRF | 0.673 | 0.862 | 0.908 | 0.929 | 0.815 | 0.940 | 0.969 |
| Lexical+BGE RRF | 0.622 | 0.862 | 0.893 | 0.929 | 0.782 | 0.938 | 0.985 |
| Lexical | 0.520 | 0.714 | 0.786 | 0.852 | 0.667 | 0.871 | 0.949 |

The candidate-recall column is measured before reranking. A reranker cannot recover evidence absent from that candidate set. Its job is to improve ordering within the set.

### Category and population winners

| Segment | Best observed behavior | Design implication |
|---|---|---|
| Configuration, factual, definition, troubleshooting | BGE + MiniLM | pairwise reranking is strong for single-unit evidence |
| Procedure | lexical+E5 RRF + MiniLM | exact product terms and semantic matching can be complementary |
| Table | lexical+E5 RRF without MiniLM | preserve structured/table evidence and avoid blindly reranking isolated chunks |
| Figure | lexical+BGE RRF without MiniLM | figure references benefit from lexical anchors and context |
| Comparison | lexical+BGE RRF + MiniLM | hybrid remains a viable routed candidate |
| Multi-section and cross-reference | BGE without MiniLM | pairwise relevance is not the same as assembling a complete evidence set |
| Original wording | lexical+BGE RRF + MiniLM, MRR 0.933 | lexical cues remain useful |
| Light paraphrase | BGE without MiniLM, MRR 0.969 | dense first-stage ranking is already strong |
| Moderate paraphrase | E5 + MiniLM, MRR 0.787 | E5 handles reduced lexical overlap best in this slice |
| Strong paraphrase | BGE without MiniLM, MRR 0.750 and R@10 0.812 | still a material weakness |
| Conceptual paraphrase | E5 + MiniLM, MRR 0.704 | best measured option, but not yet strong enough to stop testing |
| Hard questions | BGE without MiniLM, MRR 0.855 | reranking is not universally beneficial |

Cross-reference questions that require multiple source units can have strict Recall@1 equal to zero by construction. MRR can still credit the first required unit. Therefore strict complete-set recall, first-hit MRR, and evidence coverage must be read together.

## 6. The three different K values

| Parameter | Meaning | Current value | What it controls |
|---|---|---:|---|
| Candidate K | chunks emitted by each first-stage retriever for fusion/reranking | 20 | recall ceiling, reranking cost, latency |
| Evaluation K | cutoffs at which offline metrics are reported | 1, 3, 5, 10 | measurement only; R@1 evaluates the first result after ranking |
| Context/output K | chunks selected after reranking for the generator | not independently implemented | evidence completeness, redundancy, prompt tokens, generation quality |

If candidate K is 1, a reranker has nothing to reorder. In the current run candidate K is 20, MiniLM scores those candidates, and R@1 asks whether its first output satisfies the evaluation rule. The current code materializes reranked results up to the largest evaluation K; that is not yet a proper, independent generator-context policy.

Raw context K is also incomplete without a context token budget. Three large chunks and three small chunks have different cost. Production selection should optimize both final chunk count and total assembled tokens.

## 7. Complete retriever control surface

The following parameters can affect the result. Items marked **current** are already configurable or recorded. Items marked **next** must be added or made explicit before final selection.

### Corpus and benchmark

- **current:** source document checksum, canonical parser output, golden dataset path and checksum;
- **current:** question family, original source question, paraphrase level, difficulty, question type, evidence shape, required sources, acceptable sources, hard negatives, pages, sections, semantic units, element IDs, expected answer, evaluation flags, and lexical diagnostics;
- **next:** family-grouped development/held-out assignment, unseen-document evaluation, unanswerable questions, and adversarial lexical distractors;
- **next:** explicit policies for acceptable evidence, partial evidence, and multi-unit completion.

### Chunking

- **current:** strategy=`token_window`, chunk size, overlap, tokenizer/version, deterministic source lineage;
- **next:** semantic/section boundary preservation, minimum/maximum size, title/header injection, procedure-step grouping, table representation, figure-caption association, parent-child construction, parent return policy, neighboring-chunk expansion, and cross-reference expansion;
- **next:** duplicate text/lineage handling and span-complete evidence containment;
- derived controls to always report: chunk count, token distribution, evidence-bearing chunk density, source units per chunk, and fraction of index returned.

### First-stage encoders

- **current:** encoder ID, algorithm, artifact path, pinned revision, lexical/hash dimension, LSA latent dimension, E5 query/document prefixes, batch size, device, and normalized embeddings;
- **next:** explicit tokenizer revision, maximum input length, truncation side, pooling strategy, precision/dtype, and query/document instruction templates;
- model hyperparameters are inference parameters unless a later fine-tuning experiment is explicitly introduced.

### Index and candidate retrieval

- **current:** exact cosine similarity, deterministic score and chunk-index tie breaking, candidate K;
- **next:** candidate K grid and candidate fraction of index, score threshold, metadata filters, per-parent cap, candidate deduplication policy, and latency/memory measurement;
- later scaling option: ANN index type and its search parameters, evaluated against exact-search recall before adoption.

### Fusion and diversity

- **current:** reciprocal-rank fusion, equal source contribution, rank constant 60, per-source candidate K;
- **next:** RRF constant grid, source weights, dense/lexical candidate allocation, score normalization alternative, union cap, and duplicate handling;
- **next:** maximal marginal relevance or explicit evidence diversity, per-section/source caps, and multi-unit coverage selection.

### Reranking

- **current:** reranker ID/revision, candidate K, batch size, optional device, pairwise query-chunk scoring, deterministic tie break;
- **next:** maximum pair length, truncation policy, score calibration/threshold, final output K, category routing, and evidence-diverse selection after relevance scoring;
- always compare against the same first-stage order so reranker gain or harm is visible.

### Context assembly for generation

- **next:** output K, total context token budget, per-chunk or per-parent limits, redundant-overlap removal, source ordering, parent/neighbor expansion, required metadata, and citations;
- **next:** selection objective balancing relevance, evidence completeness, diversity, and token cost;
- generator evaluation should record whether failure came from retrieval, context assembly, or answer generation.

### Evaluation and operations

- **current:** Recall@1/3/5/10, Precision@K, MRR, complete required-source recall, acceptable-source handling, evidence coverage, category/difficulty/paraphrase analysis, and random-lineage controls;
- **next:** candidate recall at every candidate K, fixed-index-fraction recall, span-complete recall, context recall at output K/token budget, duplicate-source rate, context utilization, p50/p95 latency, throughput, peak memory, index size, cold/warm load time, and deterministic repeatability;
- report macro and micro summaries and include sample counts/confidence intervals for small categories.

## 8. Threats to validity

- The corpus is one short manual. Results do not establish cross-document generalization.
- The 196 questions were all visible during candidate comparison. Model selection on them can overfit analysis choices even without weight training.
- The 64 paraphrases cover only 16 families, so per-category counts can be small.
- Required-source lineage can credit a large chunk even when the precise answer span is incomplete or hard for a generator to use.
- Fixed K is misleading across different chunk counts. Candidate K=20 on 37 chunks is 54% index exposure; K=10 on the 22-chunk control is 45.5%.
- Pairwise rerankers score chunks independently and do not optimize a complementary multi-chunk set.
- Latency, memory, concurrency, and generator answer quality have not been measured.
- Transformer maximum lengths, pooling, and truncation currently inherit model/runtime defaults rather than an explicit experiment contract.

## 9. Recommended target design

```text
canonical elements
  -> structure-aware leaf chunks + optional parent/table representations
  -> one selected dense bi-encoder
  -> optional lexical branch only where held-out evidence supports it
  -> candidate union/deduplication
  -> MiniLM reranking of candidate K
  -> relevance + diversity/evidence-set selector
  -> parent/neighbor expansion within a token budget
  -> generator-ready chunks with stable source citations
```

E5+MiniLM and BGE+MiniLM should both remain in the next controlled round. The aggregate difference is too small to justify discarding either. Hybrid retrieval should not be the default unless it wins held-out metrics or critical categories by enough to justify its extra index, latency, and operational complexity.

## 10. Staged experimental plan

### Stage A: repair the validation contract

Create a deterministic family-grouped development/held-out split. Every original question and all its paraphrases must remain in the same partition. Freeze held-out data for final comparisons. Add span-complete and fixed-index-fraction metrics before optimizing.

Deliverables: split manifest, leakage tests, unchanged full diagnostic view, dev report, held-out report.

### Stage B: tune candidate K on current chunks

Hold 300/30 chunking fixed. Run BGE, E5, lexical, and only the two already-defined RRF hybrids at candidate K `{5, 10, 15, 20, 30}`. Because 30/37 is an unusually large fraction, also compare fixed fractions `{10%, 20%, 30%, 50%}` with deterministic rounding.

Measure pre-rerank complete recall, evidence coverage, span-complete recall, index exposure, latency, and reranker pair count. Eliminate depths that are dominated: higher cost with no material recall gain.

### Stage C: tune reranked context selection

For surviving first-stage configurations, sweep final output K `{1, 3, 5, 8, 10}` and context token budgets `{1,024, 2,048, 4,096}`. Compare plain top-K with a diversity-aware selector and parent/neighbor expansion. Output K must never exceed candidate K.

Measure post-rerank complete recall, precision, MRR, evidence coverage, duplicate-source rate, token cost, and eventually grounded generator answer quality. K=1 is a valid output only for single-unit questions; it cannot be a universal policy for multi-unit evidence.

### Stage D: compare chunking strategies

Use the same surviving model and K-selection procedure for each chunker:

- token windows: 200/20, 300/30, and 500/50 control;
- section/semantic boundary chunks with controlled maximum length;
- hierarchical parent-child retrieval: retrieve compact children, return the relevant parent or bounded parent excerpt;
- table-aware chunks preserving caption, headers, row context, and continuation lineage;
- optional procedure-aware step grouping and cross-reference expansion.

Do not compare chunkers only at the same raw K. Report fixed token budget and fixed index fraction as well.

### Stage E: final retrieval decision

Run the untouched held-out split once for the shortlisted systems. Select one dense model or a justified hybrid and freeze its chunking, candidate retrieval, reranking, context assembly, model revisions, and thresholds. Repeat deterministically and measure operational performance.

### Stage F: generator integration

Expose the frozen retrieval/context-assembly flow behind one stable wrapper or endpoint. Evaluate grounded answer correctness, citation support, abstention, and context utilization. If generation fails, diagnose whether the necessary evidence was absent, badly assembled, or ignored before changing retrieval.

After retrieval and generation contracts are stable, proceed to persistent storage, service deployment, UI, user/session state, telemetry, and feedback collection.

## 11. Decision gates

The following are provisional gates to be finalized before the held-out run:

- Candidate gate: choose the smallest candidate K that reaches at least 98% complete candidate recall on development data, or is within one percentage point of the best achievable value if 98% is not reached.
- Reranker gate: require a material MRR/Recall@1 gain without more than a one-point absolute regression in high-K complete recall or critical-category evidence coverage.
- Context gate: choose the smallest output K/token budget that reaches the evidence-coverage target for both single- and multi-unit questions. Do not average away cross-reference, table, procedure, or strong/conceptual failures.
- Hybrid gate: require a held-out gain that justifies two retrieval branches and their added latency/operations. Category routing is allowed only with enough labeled support and a deterministic routing rule.
- Chunking gate: require improvement under fixed token budget or fixed index exposure, not only raw fixed-K recall.
- Production gate: deterministic held-out quality, span-complete evidence, latency/memory targets, versioned artifacts, failure handling, and a stable endpoint contract must all pass.

These thresholds are decision policy, not findings. They should be adjusted based on the risk of missing evidence and the eventual generator/context limit.

## 12. Action items

| Priority | Action | Output |
|---:|---|---|
| P0 | Add family-grouped dev/held-out split and leakage validation | versioned split manifest and tests |
| P0 | Separate candidate K, evaluation K, output K, and context token budget in configuration and artifacts | schema update with validation |
| P0 | Add candidate-depth/fixed-fraction sweep and dominance analysis | reusable K experiment report |
| P0 | Add span-complete and context-budget evaluation | trustworthy evidence metric |
| P1 | Add relevance-plus-diversity context selector | multi-unit evidence assembly baseline |
| P1 | Implement semantic/section, hierarchical parent-child, and table-aware chunkers behind the same interface | reusable chunk strategy matrix |
| P1 | Record effective transformer tokenizer, max length, truncation, pooling, dtype, device, and timings | reproducible resolved manifests |
| P1 | Run the staged model/K/chunk matrix on development data and generate category reports from every golden-set column | shortlist with failure drill-down |
| P2 | Run one frozen held-out comparison and operational benchmark | retriever decision record |
| P2 | Add retrieval/context wrapper or endpoint and generator evaluation | generator-ready interface |
| P3 | Add storage, UI, sessions, telemetry, and feedback lifecycle | product layer |

## 13. Fallbacks

- If E5 is unstable or too slow, use BGE; it is nearly tied and has slightly better candidate recall and coverage in the current run. The reverse fallback also applies.
- If MiniLM harms multi-hop or cross-reference coverage, retain its relevance scores but use diversity-aware set selection, route those evidence shapes around reranking, or return expanded parent context. Do not simply increase output K without measuring token cost.
- If hybrid fusion has no held-out advantage, deploy one dense index. If it wins only stable, sufficiently populated categories, consider deterministic category routing.
- If semantic chunks lose recall, use parent-child retrieval: index small evidence-focused children and return bounded structural parents. Preserve the token-window control in every comparison.
- If tables remain weak, create table-native representations with caption/header/row context rather than globally increasing chunk size.
- If latency is excessive, first reduce dominated candidate depths, cache document embeddings, batch reranker pairs, and use one dense branch. Then evaluate ONNX/quantization or ANN against the exact-search reference.
- If the held-out set is too small for a stable choice, add reviewed unseen families, unanswerable questions, adversarial distractors, and another manual before freezing production.
- If generator quality is poor despite complete retrieval coverage, improve context assembly and prompting before changing the retriever.

## 14. Stop conditions and immediate next run

Do not move to production merely because aggregate R@10 is near 0.98. Stop retriever experimentation and freeze a version only when the held-out, category, evidence-completeness, context-budget, and operational gates are satisfied and remaining failures have an accepted fallback.

The immediate next implementation is the configuration/evaluator separation of candidate K and output/context K, followed by the Stage B candidate-depth sweep on unchanged 300/30 chunks. That is the cleanest experiment because it answers the current open question without mixing model, chunking, and context effects.

## 15. Reproducibility map

- Pipeline configurations: `configs/pipelines/baseline.json`, `configs/pipelines/candidates.json`
- Chunk/dimension experiment: `configs/retrieval/experiments/chunk_dimension_sweep.json`
- Paraphrase experiment: `configs/retrieval/experiments/paraphrase_bias_baseline.json`
- Durable candidate summary: `configs/pipelines/candidate-model-comparison.md`
- Generated complete category report: `output/retrieval/pipeline_candidates/analysis/model_category_report.md`
- Generated machine-readable analysis: `output/retrieval/pipeline_candidates/analysis/model_category_analysis.json`
- Retrieval pipeline operation: `src/testrx_retriever/workflows/retrieval-pipeline.md`
- Artifact/model retention policy: `docs/artifact-policy.md`

All future model, chunking, fusion, reranking, and context-selection implementations should emit the same question-level schema so the existing reusable category analyzer can compare them without custom analysis code.
