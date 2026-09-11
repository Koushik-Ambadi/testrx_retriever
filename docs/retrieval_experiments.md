# Retrieval Experiment: Chunk Size and Hashing Dimension

## Question

Why does the deliberately basic signed word-and-bigram hashing retriever score
well on the TESTRX golden set, and how much of the result changes with chunk
size, index size, source-lineage density, and hashing dimension?

This experiment does not optimize a production retriever. It tests plausible
explanations for the baseline result while holding the PDF-derived canonical
document, 132 golden questions, tokenizer, features, exact cosine ranking, and
metric definitions fixed.

## Design

The controlled matrix contains four token-window sizes with approximately 10%
overlap. Integer overlap is rounded half up.

| Chunk size | Overlap | Chunk count |
|---:|---:|---:|
| 125 | 13 | 88 |
| 200 | 20 | 55 |
| 250 | 25 | 44 |
| 300 | 30 | 37 |

Each window is evaluated at 128, 256, 512, 1,024, 4,096, 8,192, and 16,384
hashing dimensions. The original 500-token, 50-overlap, 4,096-dimensional run
is repeated as a control, giving 29 total runs.

The following diagnostics are recorded in addition to the unchanged retrieval
metrics:

- fixed-seed random-ranking lineage Recall@K over 1,000 trials;
- fraction of the index returned at maximum K;
- mean source elements and semantic units owned by a chunk;
- mean fraction of chunks considered relevant to a question;
- best query-word coverage in an evidence-bearing chunk;
- distinct hashing features, occupied dimensions, and collision fraction;
- top-1 agreement with the 16,384-dimensional run at the same chunk size;
- per-question first relevant rank and relevant-versus-irrelevant score margin;
- recall slices by difficulty and question type.

Random-ranking recall uses source lineage and the same strict all-required-unit
definition as the real evaluation. It is not a generic IR random baseline; it is
specifically a diagnostic for this corpus, chunking policy, and metric.

## Main measurements

At 4,096 dimensions:

| Chunk / overlap | Chunks | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR | Random R@10 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 125 / 13 | 88 | 0.530 | 0.727 | 0.788 | 0.879 | 0.701 | 0.198 |
| 200 / 20 | 55 | 0.561 | 0.727 | 0.803 | 0.894 | 0.703 | 0.275 |
| 250 / 25 | 44 | 0.591 | 0.758 | 0.818 | 0.909 | 0.713 | 0.311 |
| 300 / 30 | 37 | 0.606 | 0.788 | 0.871 | 0.917 | 0.724 | 0.353 |
| 500 / 50 control | 22 | 0.667 | 0.811 | 0.879 | 0.924 | 0.780 | 0.529 |

At 16,384 dimensions, the 125/13, 200/20, 250/25, and 300/30 windows reach MRR
0.723, 0.736, 0.743, and 0.763 respectively. Raising dimension from 4,096 to
16,384 adds only 0.022-0.039 MRR, while raising it from 128 to 16,384 adds
0.285-0.311 MRR. The feature collision diagnostic falls from 0.982 at 128
dimensions to 0.522 at 4,096 and 0.186 at 16,384.

## Findings

### F1 - The high score is partly real lexical signal

The actual 4,096-dimensional Recall@10 exceeds random-lineage Recall@10 by
0.681, 0.619, 0.598, and 0.563 for chunk sizes 125 through 300. Recall@1 is
0.530-0.606 even though only about 2.5%-4.2% of chunks are relevant to an
average question. The hashing model is therefore doing useful ranking; the
result is not explained by random exposure alone.

The likely signal is lexical alignment. Mean best query-word coverage in a
relevant chunk rises from 0.627 at 125 tokens to 0.714 for the 500-token control.
The golden questions were authored from the same manual and preserve its product
names, configuration terms, UI labels, and procedure vocabulary. A word/bigram
model is well suited to that closed-domain condition even though it has no
semantic representation.

### F2 - Large chunks and K=10 materially inflate apparent coverage

The 500-token control has only 22 chunks, so top 10 returns 45.5% of the entire
index. Its random-lineage Recall@10 is already 0.529. A control chunk owns 12.18
source elements and 12.23 semantic units on average, compared with 3.76 and 3.78
for 125-token chunks. Because evaluation credits lineage presence anywhere in a
chunk, larger windows make both random and ranked evidence coverage easier.

This explains why Recall@10 remains very high as chunk size grows. MRR and
Recall@1 are more informative than Recall@10 for this small corpus, though they
still benefit from broader chunks and lexical overlap.

### F3 - Hashing dimension matters until collisions become tolerable

Dimensions of 128-1,024 are not a fair neutral compression of this feature set.
They produce collision fractions from 0.982 to 0.854 and sharply reduce ranking
quality and top-1 stability. Performance continues to improve from 4,096 to
16,384, but much more slowly. For this corpus, 4,096 is near a practical plateau,
not proof that dimension is irrelevant.

### F4 - The experiment does not establish semantic generalization

The evaluation uses one short manual, source-derived answerable questions, and
lineage-based relevance. It contains no paraphrase-stress split, unseen manual,
unanswerable questions, adversarial lexical distractors, or span-completeness
metric. High scores here mean strong closed-domain lexical retrieval under this
evaluation contract. They should not be described as semantic understanding.

## Next discriminating experiments

1. Add a reviewed paraphrase-only evaluation view that replaces distinctive
   source wording without changing required source IDs.
2. Report span-complete evidence containment alongside lineage presence.
3. Compare fixed retrieval fractions (for example top 5% and top 10% of the
   index), not only fixed K, across chunk counts.
4. Add shuffled-query, stopword-only, unigram-only, and bigram-only ablations.
5. Compare BM25 and a learned embedding model on the unchanged questions.
6. Evaluate an unseen document before making any generalization claim.

These are follow-up studies. The current golden set and recorded artifacts must
remain unchanged so the present result stays reproducible.

## Artifacts and reproduction

Configuration: `configs/retrieval_sweep.json`

Artifacts:

```text
output/retrieval_experiments/chunk_dimension_sweep/
├── summary.json
├── question_diagnostics.jsonl
├── report.md
└── manifest.json
```

Run from the project root after installing the package:

```powershell
python -m testrx_retriever.experiments --config configs/retrieval_sweep.json
python -m unittest discover -s tests -v
```

The runner has no timestamps. Random ranking uses a pinned seed, and the
manifest was byte-identical across two complete regenerations on 2026-09-11.
