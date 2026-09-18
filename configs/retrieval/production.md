# Frozen retrieval configuration

Date: 2026-09-17  
Status: accepted application default  
Owner: retrieval architecture  
Configuration: [`production.json`](production.json)  
Reproducible evaluation: [`../pipelines/production_evaluation.json`](../pipelines/production_evaluation.json)

## Decision

The default query-to-chunks path is:

```text
canonical document
  -> hierarchy-aware chunks, maximum 384 regex tokens
  -> BAAI/bge-small-en-v1.5 exact cosine retrieval
  -> 10 candidates
  -> cross-encoder/ms-marco-MiniLM-L-6-v2 reranking
  -> 5 returned chunks
```

The model revisions are pinned in the JSON configuration. `candidate_k=10` and
`top_k=5` are defaults, not constants: both may be overridden per application
call, subject to `candidate_k >= top_k`.

## Evidence considered

The decision used all eight chunk variants, all ten candidate systems, and all
196 golden questions from `output/retrieval/pipeline_hierarchy_chunking/`. The
comparison included strict complete-evidence Recall@K, semantic-unit coverage,
MRR, precision, question/category slices, paraphrase strength, difficulty,
chunk count and size, returned context tokens, index exposure, build/query
latency, and failure inspection.

The 300/30 token-window control remains slightly stronger at deep K, but it
returns much more text. Pure hierarchy has the highest raw MRR by 0.002 but is
rejected because it creates 311 overlapping chunks and permits 2,263-token
chunks. Bounded hierarchy at 384 tokens is the best quality/context/operational
frontier.

| Configuration | R@1 | R@3 | R@5 | R@10 | MRR | Mean K=5 tokens |
|---|---:|---:|---:|---:|---:|---:|
| Hierarchy 384, BGE + MiniLM, candidate K=10 | **0.760** | **0.918** | 0.949 | 0.980 | **0.883** | **715** |
| Hierarchy 384, BGE + MiniLM, candidate K=20 | 0.755 | 0.913 | 0.923 | 0.964 | 0.875 | 707 |
| Token window 300/30, BGE + MiniLM, candidate K=20 | 0.755 | 0.918 | **0.959** | 0.980 | 0.869 | 1,499 |
| Token window 300/30, E5 + MiniLM, candidate K=20 | **0.760** | 0.913 | 0.949 | 0.980 | 0.872 | 1,499 |
| Pure hierarchy, BGE + MiniLM, candidate K=20 | 0.699 | 0.883 | 0.929 | 0.954 | 0.877 | 1,201 |

The selected index has 95 chunks averaging 109.6 tokens. At the default final
K=5, returned context is 715 tokens on average, 696.5 at the median, 1,018 at
p90, and 1,262 at maximum. K=3 averages 432 tokens but loses six additional
complete questions; K=10 averages 1,288 tokens and recovers six. K=5 is the
knee: 186/196 questions are complete while avoiding the extra 573 average
tokens required by K=10.

## Candidate-depth tuning

Candidate K was varied after fixing hierarchy-384 and BGE+MiniLM. Expanding the
pool made the pairwise reranker displace useful multi-chunk evidence.

| Candidate K | R@1 | R@3 | R@5 | R@10 | MRR | Coverage@10 |
|---:|---:|---:|---:|---:|---:|---:|
| **10** | **0.760** | **0.918** | **0.949** | **0.980** | **0.883** | **0.986** |
| 12 | 0.760 | 0.913 | 0.939 | 0.974 | 0.882 | 0.984 |
| 15 | 0.760 | 0.913 | 0.934 | 0.974 | 0.880 | 0.983 |
| 20 | 0.755 | 0.913 | 0.923 | 0.964 | 0.875 | 0.977 |
| 30 | 0.755 | 0.913 | 0.923 | 0.954 | 0.873 | 0.965 |

The first-stage BGE pool at K=10 contains complete evidence for 192/196
questions (strict recall 0.980, mean evidence coverage 0.986). This establishes
that the reranker is not hiding a weak candidate generator.

## Question behavior

With the frozen configuration, Recall@5 is 1.000 for configuration,
cross-reference, definition, factual, figure, table, and troubleshooting
questions; 0.960 for comparisons; 0.846 for multi-section; and 0.811 for
procedures. Single-unit Recall@5 is 0.993, while multi-unit Recall@5 is 0.850.

The reranker is clearly beneficial for single-unit, configuration, definition,
factual, procedure, table, and troubleshooting ranking. Raw BGE remains better
by MRR for cross-reference, multi-hop, parent-context, and multi-section slices.
This is a known pairwise-reranking limitation; the single generalized default is
retained, while future context assembly should add diversity rather than route
queries through an unvalidated classifier.

Original questions achieve R@5 0.977. Light/moderate/strong/conceptual
paraphrases achieve 0.938/0.938/0.938/0.750. Easy/medium/hard questions achieve
0.986/0.987/0.822. The remaining failures concentrate in multi-unit procedures,
multi-section conceptual paraphrases, and parent-context evidence.

A post-experiment family-grouped robustness view kept every original and its
paraphrases together. A deterministic, question-type/difficulty-stratified
quarter (42/132 families; 58/196 questions) gave the selected system R@1/3/5 of
0.862/0.966/0.966 and MRR 0.932. The token-window controls retained perfect
R@5 on that slice but still used about twice the context. Because this split was
defined after raw experiment capture, it is supporting sensitivity evidence,
not a prospective held-out claim.

## Latency and operating boundary

Measured timings exclude startup, chunking, and index construction. On the two
fixed hard sentinels, reducing candidate K from 20 to 10 changed end-to-end
retrieval from 1,287 to 661 ms and from 1,858 to 1,162 ms on the recorded CPU
environment. A fresh application startup (both local models plus a 95-chunk
index) measured 19.8 seconds. The wrapper is therefore a long-lived in-process
object; rebuilding it for every query is not an intended use.

These are diagnostic local measurements, not an SLA. Hardware, framework, and
warm-up effects require a dedicated deployment benchmark before serving traffic.

## Fresh-question manual smoke test

On 2026-09-17, six new compositional questions were authored after reading and
visually checking PDF pages 8, 9-10, 32, 48, and 50. None copied golden question
text. The production wrapper was called once per question, every returned chunk
was split into atomic statements, and each statement was manually classified as
unrelated, topical, or directly answer-bearing, with separate answer-support
scoring.

- Five questions had a clean complete answer in rank 1.
- The sixth was complete by rank 2, but `Options > User Preferences > Future
  Scope` was split across two adjacent fallback chunks.
- No question was incomplete at Top-5.
- The 306 statements comprised 21 direct, 82 topical, and 203 unrelated
  statements for these particular questions.
- Mean accumulated context was 223 tokens at rank 1, 364 at rank 2, 489 at rank
  3, and 740 at rank 5.

This small hand-authored set does not justify lowering the broad default from
Top-5: the 196-question benchmark shows a strict completeness gain from K=3 to
K=5. It does show that downstream context assembly should prune or compress
low-value chunks, and that table-aware fallback splitting should preserve rows
instead of cutting them at a raw token boundary.

## Residual risks

- The benchmark covers one manual and no unanswerable or adversarial queries.
- The same diagnostic corpus informed selection; a family-grouped robustness
  check did not expose a reversal, but it is not a prospective external test.
- Lineage recall does not prove answer-span completeness or generator quality.
- Pairwise reranking does not explicitly optimize evidence diversity.
- Oversized table fallback can split a semantic row across adjacent chunks.
- Exact in-memory cosine retrieval is appropriate for 95 chunks, not proof of
  large-corpus scalability.
