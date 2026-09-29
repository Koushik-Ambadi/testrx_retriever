# Controlled Paraphrase Bias Study

Status: frozen experiment record  
Owner: retrieval experiments  
Recorded: 2026-09-12

## Question

Why does a basic, unfitted word/bigram hashing embedder score well on the TESTRX
golden set? The study tests whether direct source vocabulary and a small,
lineage-dense index explain a material part of the result.

## Design

- Preserve all 132 original questions and their complete grounded records.
- Select 16 source-question families spanning difficulty, question type,
  single/multiple evidence, tables, procedures, parent context, and cross
  references.
- Append four handcrafted levels per family: light, moderate, strong, and
  conceptual. Only ID, text, paraphrase metadata, and measured lexical
  diagnostics may differ from the source question.
- Keep the reference pipeline fixed at 500 tokens, 50 overlap,
  `stable_hashing_word_bigram` 1.0, 4,096 dimensions, exact cosine, and no
  reranking.
- Evaluate all 196 questions at K=1, 3, 5, and 10.

The paraphrase specification is versioned in
`configs/datasets/golden_paraphrases.json`. Deterministic derived IDs use
`<source>-P1` through `<source>-P4`. The builder guards the pre-extension set
with a canonical legacy hash.

## Results

| Level | N | Mean overlap | R@1 | R@3 | R@5 | R@10 | MRR | Coverage@10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Original | 132 | 0.527 | 0.667 | 0.811 | 0.879 | 0.924 | 0.780 | 0.933 |
| Light | 16 | 0.493 | 0.625 | 0.750 | 0.938 | 0.938 | 0.786 | 0.979 |
| Moderate | 16 | 0.277 | 0.438 | 0.562 | 0.688 | 0.750 | 0.598 | 0.792 |
| Strong | 16 | 0.295 | 0.125 | 0.438 | 0.688 | 0.875 | 0.379 | 0.917 |
| Conceptual | 16 | 0.246 | 0.188 | 0.438 | 0.562 | 0.750 | 0.418 | 0.792 |

Across all 196 questions, Recall@1/3/5/10 is 0.561/0.724/0.827/0.893,
MRR is 0.703, and mean evidence coverage@10 is 0.912. On the 80 paired family
questions, lexical overlap and reciprocal rank have Pearson correlation 0.350.

## Interpretation

The large top-rank decline from original/light wording to strong/conceptual
wording is direct evidence that lexical alignment contributes substantially to
the original score. It is not the whole explanation: correlation is positive
but modest, light paraphrases remain strong, and some low-overlap questions are
still retrieved. Broad 500-token chunks, source-lineage density, and returning
10 of only 22 chunks continue to lift high-K recall.

The paraphrase ladder is controlled but small. Mean lexical overlap increases
from moderate (0.277) to strong (0.295), so abstraction level is not a perfectly
monotonic numeric treatment. Q048-P4 exceeds its conceptual-level overlap review
threshold. Both facts are retained in QC rather than edited after seeing scores.

Low-count category slices are diagnostic, not estimates of population quality.
Notable failure concentrations include moderate/conceptual procedures and
multiple-unit strong/conceptual questions. Family Q130 has high first-hit ranks
but fails complete evidence at K=10 across its derived variants, illustrating
why MRR and complete-set recall must be read together.

## Conclusion and next evidence

The hypothesis is supported: the original baseline materially benefits from
same-document lexical wording. The experiment does not show that hashing is a
strong general semantic model. Before introducing a learned embedder, useful
isolating tests are unigram/bigram ablation, shuffled or keyword-only queries,
fixed-index-fraction evaluation, and span-complete evidence scoring. Those are
future experiments, not changes to this run.
