# Research synthesis

Status: living
Owner: retrieval research
Created: 2026-09-29
Last reviewed: 2026-09-29
Update trigger: a completed study materially changes cross-study understanding, project direction, or a binding decision
Source of truth for: concise, cross-study conclusions and how evidence changed the project direction
Does not own: exhaustive metrics, fixed protocols, binding decisions, or the dated implementation chronology

This is the project-level bridge between experiment evidence and project
direction. Study records own their protocols and interpretation; the normalized
store owns detailed run/question metrics; [decisions](decisions.md) own binding
choices; [progress](progress.md) records what was implemented and verified; and
the [roadmap](roadmap.md) owns remaining work.

## Evidence-to-direction history

### Why did a simple word/bigram hash baseline look strong?

The original benchmark used questions grounded in the same manual indexed by the
retriever. The first controlled sweep showed that performance reflected several
effects together: genuine in-domain term matching, broad source lineage in large
chunks, a small index where fixed K exposed a large fraction of all chunks, and
hash collisions at low dimensions. The sweep therefore did not establish
semantic understanding. See the [chunk and dimension study](../studies/retrieval/chunk-dimension-sweep/results.md),
[failure analysis](../studies/retrieval/failure-analysis.md), and decisions
[O027](decisions.md#o027---the-first-embedder-has-no-external-model),
[O030-O032](decisions.md#o030---chunk-comparisons-hold-the-benchmark-and-evaluator-fixed),
and [O040](decisions.md#o040---keep-two-anchors-for-the-next-retrieval-investigation).

### What changed to test the lexical-overlap explanation?

The project preserved the 132 original grounded questions and appended 64
controlled paraphrases across 16 source families. The paraphrases changed
wording while retaining source support, allowing lexical distance to be probed
without changing the answer evidence. Tokenizer-aligned overlap diagnostics were
added. This supported lexical overlap as a material contributor to the baseline
score, while also showing that broad chunks and index exposure influenced high-K
recall. The finding was not that lexical overlap explains everything, nor that
the system generalizes semantically. See the [paraphrase study](../studies/retrieval/paraphrase-bias-baseline/results.md),
the [golden dataset record](../output/datasets/golden/README.md), and decisions
[O036-O037](decisions.md#o036---paraphrases-extend-rather-than-replace-the-golden-set).

Six later compositional questions were used in a separate manual retrieval smoke
test; they were not silently added to the scored golden benchmark. Their
statement-level evidence inspection is summarized in the
[frozen retrieval evaluation](../configs/retrieval/production.md).

### What did the broader model and chunking comparisons change?

The project next compared lexical, static-semantic, and pinned dense retrieval
families on a shared population, then evaluated chunk structure, reranking,
evidence completeness, context size, and latency together. Dense encoders
materially improved ranking over the lexical control, but fusion did not improve
aggregate quality consistently, and reranking could weaken multi-unit evidence
assembly. Larger candidate pools were not automatically better. Hierarchy-aware
chunks bounded at 384 tokens with BGE retrieval, MiniLM reranking, candidate
K=10, and final K=5 became the configurable application default because that
combination balanced completeness, returned context, and operational behavior.
Detailed comparisons remain in the [candidate report](../configs/pipelines/candidate-model-comparison.md),
[hierarchy study](../configs/pipelines/hierarchical-chunking-experiment.md),
[frozen production evaluation](../configs/retrieval/production.md), and decision
[O047](decisions.md#o047---freeze-the-bounded-hierarchy-bge-reranking-path).

## Current interpretation and next direction

- The benchmark is useful for closed-domain retrieval comparisons, but is not a
  prospective, unseen-document or unanswerable-query evaluation.
- Lexical matching remains a useful control and sometimes a useful hybrid
  signal; it is not a claim of semantic generalization.
- Aggregate retrieval scores must be read with complete-evidence behavior,
  question-family slices, context size, and operating cost.
- The current retrieval contract is frozen. The next gate is diversity-aware
  context assembly and generator-facing evidence completeness, not another
  unconstrained tuning sweep.

See the current [roadmap](roadmap.md) for gate status and the owning study and
decision records for detailed evidence. When new experiments change this
interpretation, update this synthesis and link the run evidence, study record,
decision, and progress entry rather than copying their detailed metrics here.
