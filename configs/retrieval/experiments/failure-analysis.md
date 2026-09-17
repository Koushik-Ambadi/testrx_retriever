# Retrieval Failure Analysis and Decision Report

Date: 2026-09-12

Status: frozen analysis record  
Owner: retrieval evaluation

## Executive decision

Retain 500/50/4,096 as the historical reference, but do not select it as a
production configuration from these scores. Use 300/30/8,192 as the second
diagnostic anchor for the next controlled model or scoring experiment. It has
fewer complete-evidence failures, exposes less of the index at K=10, and avoids
the severe collision regime without paying for the inconsistent 16,384 gain.

Before adding reranking, first audit the persistent evidence failures and add a
span-completeness or fixed-index-fraction view. When a learned embedding family
is introduced, compare it against both anchors on the original and paraphrase
populations, with Recall@1/MRR as primary semantic-sensitivity measures and
complete Recall@10 as an evidence-assembly measure.

## Evaluation populations

- Configuration matrix: 29 runs on the unchanged 132 original questions.
- Paraphrase reference: one fixed 500/50/4,096 run on 132 originals plus 64
  controlled paraphrases.
- A failure means the complete required source set is absent at K=10.
- Low Recall@1 or MRR with a K=10 pass is a ranking weakness, not a complete
  evidence miss.

## Which settings fail

### Embedding dimension

The fair 125-300-token comparison contains 528 question/runs at each dimension.
The 4,096 summary below excludes the separate 500-token control.

| Dimension | K=10 failures | Failure rate | Interpretation |
|---:|---:|---:|---|
| 128 | 144/528 | 27.3% | Severe collision regime |
| 256 | 124/528 | 23.5% | Severe collision regime |
| 512 | 85/528 | 16.1% | Still materially constrained |
| 1,024 | 76/528 | 14.4% | Improved but unstable |
| 4,096 | 53/528 | 10.0% | Practical baseline region |
| 8,192 | 42/528 | 8.0% | Best measured trade-off |
| 16,384 | 39/528 | 7.4% | Small aggregate gain over 8,192 |

Dimension is a genuine failure driver below 4,096. The difference between 8,192
and 16,384 is only three failures across 528 observations and is not consistent
for every chunk size. This does not justify 16,384 as the default.

### Chunk size at 4,096 dimensions

| Tokens/overlap | R@1 | MRR | K=10 failures | Failure rate |
|---|---:|---:|---:|---:|
| 125/13 | 0.530 | 0.701 | 16 | 12.1% |
| 200/20 | 0.561 | 0.703 | 14 | 10.6% |
| 250/25 | 0.591 | 0.713 | 12 | 9.1% |
| 300/30 | 0.606 | 0.724 | 11 | 8.3% |
| 500/50 | 0.667 | 0.780 | 10 | 7.6% |

Larger windows improve the lineage metric, but the effect is confounded by
broader source ownership and index exposure. The 500-token run returns 10 of 22
chunks (45.5%); the 300-token runs return 10 of 37 (27.0%). Therefore the
500-token advantage is not clean evidence of better semantic focus.

The useful non-reference candidate is 300/30/8,192: R@1 0.629, MRR 0.752,
R@10 0.939, eight failures (6.1%), and 27.0% index exposure. At 300/30/16,384,
MRR rises to 0.763 but failures increase to nine, so the larger dimension is not
uniformly better.

## Which original question types fail

Rates below pool the 29 settings; the denominator is question/run observations.

| Question type | Failures / observations | Failure rate | Number of questions |
|---|---:|---:|---:|
| Cross-reference | 26/58 | 44.8% | 2 |
| Figure | 23/58 | 39.7% | 2 |
| Definition | 41/145 | 28.3% | 5 |
| Troubleshooting | 46/290 | 15.9% | 10 |
| Configuration | 125/841 | 14.9% | 29 |
| Procedure | 104/725 | 14.3% | 25 |
| Factual | 118/841 | 14.0% | 29 |
| Table | 61/464 | 13.1% | 16 |
| Multi-section | 16/145 | 11.0% | 5 |
| Comparison | 13/261 | 5.0% | 9 |

Cross-reference, figure, and definition are the clearest failure-prone types,
but their question counts are small. The result is a prioritization signal, not
a stable type-level benchmark.

## Persistent original failures

| Question | Failed settings | Type/category | Required source |
|---|---:|---|---|
| Q080 | 29/29 | table, single unit | `table_7` |
| Q092 | 29/29 | procedure, multiple units | section 16 elements 001/002 |
| Q044 | 28/29 | configuration | section 12 element 001 |
| Q072 | 28/29 | factual | section 14 element 006 |
| Q123 | 27/29 | definition | section 17 element 001 |
| Q002 | 25/29 | factual, parent context, multiple units | section 2.1 elements 001/002 |
| Q005 | 23/29 | procedure | section 3.2 element 001 |
| Q023 | 23/29 | figure context | section 8 element 001 |
| Q131 | 19/29 | cross-reference, multi-hop | three sources across sections 16.2.2 and 11.1 |
| Q053 | 19/29 | configuration | section 12.3 element 002 |

Q080 and Q092 are configuration-independent failures and should be inspected
first. Their behavior is more consistent with representation/relevance-coverage
limitations than with a poor parameter choice. Q044, Q072, and Q123 are likely
lexical/model-sensitivity cases because only one or two configurations recover
them.

## Paraphrase failures under the fixed reference

| Level | R@1 | MRR | K=10 failures | Failure rate |
|---|---:|---:|---:|---:|
| Original | 0.667 | 0.780 | 10/132 | 7.6% |
| Light | 0.625 | 0.786 | 1/16 | 6.2% |
| Moderate | 0.438 | 0.598 | 4/16 | 25.0% |
| Strong | 0.125 | 0.379 | 2/16 | 12.5% |
| Conceptual | 0.188 | 0.418 | 4/16 | 25.0% |

Strong paraphrases are the most important ranking warning: 14 of 16 eventually
retrieve complete evidence, yet only 2 of 16 do so at rank 1. This is a lexical
ranking failure that high-K recall conceals.

The ten original failures in this fixed reference are Q001 and Q123
(definitions), Q002 and Q072 (factual), Q023 (figure), Q005 and Q092
(procedures), Q019 and Q080 (tables), and Q130 (cross-reference/multi-hop).
Q092 and Q130 have incomplete multi-unit evidence; the other eight retrieve none
of their required evidence by K=10.

The recurring derived failures are:

- Q130-P1 through Q130-P4: incomplete cross-reference/multi-hop evidence at K=10.
- Q099-P2 and Q071-P3/P4: procedure misses.
- Q017-P2: table miss.
- Q041-P2: troubleshooting miss.
- Q012-P4: comparison miss.
- Q001-P4: conceptual definition miss.

Category views reinforce the pattern: the one cross-reference/multi-hop family
fails complete evidence at every level; conceptual multiple-unit questions fail
3/8; moderate single-unit questions fail 3/8. Small cells must be reviewed by
question rather than treated as population estimates.

## Actionable decision sequence

1. Audit Q080 and Q092 against chunk text and lineage to distinguish annotation,
   chunk-span, and retrieval failures. Do not change the golden labels without
   PDF-backed review.
2. Add a span-complete evidence diagnostic and a fixed-index-fraction view. This
   tests whether broad chunks and K=10 coverage are overstating quality.
3. Keep 500/50/4,096 as the historical control; use 300/30/8,192 as the cleaner
   diagnostic anchor.
4. Run unigram/bigram and shuffled-query ablations to quantify how much signal
   comes from exact terms versus word order/co-occurrence.
5. Then add one learned embedding family under the same evaluation populations.
   Make paraphrase Recall@1/MRR and persistent-question recovery primary.
6. Add reranking only after retrieval candidates reliably contain the complete
   required evidence; reranking cannot recover absent evidence.

## Reproduction

```powershell
$env:PYTHONPATH = "src"
python -m testrx_retriever.analytics --where experiment_id=chunk-dimension-sweep-v1 --group-by token_size,embedding_dimension
python -m testrx_retriever.analytics --where experiment_id=chunk-dimension-sweep-v1 --group-by question_type
python -m testrx_retriever.analytics --where experiment_id=paraphrase-bias-baseline-v1 --group-by paraphrase_level,question_type
python -m testrx_retriever.analytics --where experiment_id=paraphrase-bias-baseline-v1 --group-by paraphrase_level,category
```

The underlying run and question records remain in the shared experiment store;
this report does not add a separate output directory or duplicate run artifacts.
