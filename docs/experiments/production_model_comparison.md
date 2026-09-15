# Production candidate model comparison

Date: 2026-09-13

## Decision summary

The production-grade semantic and reranking path is working end to end. On the
full 196-question diagnostic population, E5 plus the MiniLM cross-encoder has
the best aggregate MRR (0.872), while BGE plus the same reranker has nearly the
same MRR (0.869), slightly higher mean evidence coverage (0.986), and higher
Recall@3/5. Neither is frozen as the final retriever because these candidates
were inspected on the full benchmark rather than a held-out family split.

Hybrid reciprocal-rank fusion does not beat the best dense systems overall at
this chunk size. It remains useful for particular tables, figures, procedures,
and original-wording questions, so hybrid retrieval should remain a candidate
rather than becoming the default.

## Fixed evaluation contract

- Dataset: 132 original questions plus 64 controlled paraphrases.
- Chunking: current 300-token / 30-token-overlap diagnostic anchor.
- Candidate depth: 20; final metrics at K=1, 3, 5, and 10.
- First-stage systems: lexical hashing, pinned BGE small English v1.5, pinned E5
  small v2, and lexical+dense reciprocal-rank fusion for each dense encoder.
- Reranker: pinned MS MARCO MiniLM-L6 cross-encoder.
- Ground truth and evaluator: unchanged required/acceptable source lineage.

## Overall results

| System | R@1 | R@3 | R@5 | R@10 | MRR | Coverage@10 | Candidate R@20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| E5 + reranker | 0.760 | 0.913 | 0.949 | 0.980 | **0.872** | 0.983 | 0.980 |
| BGE + reranker | 0.755 | **0.918** | **0.959** | 0.980 | 0.869 | **0.986** | **0.990** |
| Lexical+E5 RRF + reranker | 0.760 | 0.913 | 0.944 | 0.959 | 0.868 | 0.967 | 0.969 |
| Lexical+BGE RRF + reranker | 0.755 | 0.903 | 0.949 | 0.980 | 0.868 | 0.982 | 0.985 |
| Lexical + reranker | 0.750 | 0.893 | 0.918 | 0.944 | 0.854 | 0.955 | 0.949 |
| BGE | 0.663 | 0.898 | 0.934 | 0.959 | 0.821 | 0.959 | 0.990 |
| E5 | 0.663 | 0.898 | 0.929 | 0.964 | 0.820 | 0.969 | 0.985 |
| Lexical+E5 RRF | 0.673 | 0.857 | 0.908 | 0.929 | 0.815 | 0.940 | 0.969 |
| Lexical+BGE RRF | 0.622 | 0.857 | 0.893 | 0.929 | 0.782 | 0.938 | 0.980 |
| Lexical | 0.520 | 0.714 | 0.786 | 0.852 | 0.667 | 0.871 | 0.949 |

## Where each system is strongest

MRR-first segment winners from the complete report are:

| Segment | Best measured system | Important result |
|---|---|---|
| Configuration | BGE + reranker | R@1 0.879, MRR 0.924 |
| Factual | BGE + reranker | R@1 0.897, MRR 0.938 |
| Troubleshooting | BGE + reranker | R@1/MRR 1.000 |
| Comparison | Lexical+BGE RRF + reranker | R@10 1.000, MRR 0.908 |
| Procedure | Lexical+E5 RRF + reranker | R@1 0.811, MRR 0.883 |
| Table | Lexical+E5 RRF without reranking | R@1 0.850, MRR 0.900 |
| Figure | Lexical+BGE RRF without reranking | R@1/MRR 0.833 |
| Multi-section | BGE without reranking | R@10 0.923, MRR 0.833 |
| Cross-reference | BGE without reranking | R@10 1.000; strict R@1 is 0 for multi-unit completion |
| Definition | BGE + reranker | R@1/MRR 0.889 |

The reranker is especially valuable for single-unit ranking, configuration,
factual, troubleshooting, and procedure questions. It can hurt cross-reference,
multi-hop, figure, and table behavior because a pairwise scorer ranks individual
chunks and does not optimize multi-chunk evidence assembly. Those categories
need an explicit diversity/evidence-assembly strategy, not simply more
reranking.

## Paraphrase and difficulty findings

- Original questions: lexical+BGE RRF plus reranker leads with MRR 0.933 and
  complete R@10.
- Light paraphrases: BGE without reranking leads with MRR 0.969.
- Moderate and conceptual paraphrases: E5 plus reranker leads with MRR 0.787 and
  0.704 respectively.
- Strong paraphrases: BGE without reranking leads with MRR 0.750, but R@10 is
  only 0.812, so this remains a material failure population.
- Hard questions: BGE without reranking leads with MRR 0.855. Medium questions
  favor lexical+BGE RRF plus reranking; easy questions favor E5 plus reranking.

## Dataset-column coverage

The machine-readable analysis profiles every top-level golden-set field. It
groups categorical and identity fields directly; explodes pages, section paths,
semantic/element IDs, required/acceptable/hard-negative sources, and evaluation
flags; derives counts from evidence/source lists; derives length buckets from
question and expected-answer text; and bins lexical-overlap/token diagnostics.
Free-text evidence, answers, notes, and questions remain in per-question results
for drill-down instead of creating meaningless one-question aggregate groups.

## Next controlled decision

Do not tune chunking from these same aggregate results. First create a
family-grouped development/held-out partition, add span-complete evidence and
fixed-index-fraction metrics, and rerun the current candidates unchanged. Then
vary chunking and retrieval/fusion strategy through the same configuration and
analysis code. A hybrid should be selected only if its held-out category gains
justify its extra retrieval cost.

Generated detail:

- `output/retrieval/pipeline_candidates/summary.json`
- `output/retrieval/pipeline_candidates/analysis/model_category_report.md`
- `output/retrieval/pipeline_candidates/analysis/model_category_analysis.json`
