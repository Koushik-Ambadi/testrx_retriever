# Retrieval Analytics

## Paraphrase-level summary

| Level | N | Lexical overlap | R@1 | R@3 | R@5 | R@10 | MRR | Coverage | P@1 | P@3 | P@5 | P@10 | Zero | Partial | Complete |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| level_1_light | 16 | 0.493 | 0.625 | 0.750 | 0.938 | 0.938 | 0.786 | 0.979 | 0.688 | 0.312 | 0.263 | 0.138 | 0.000 | 0.062 | 0.938 |
| level_2_moderate | 16 | 0.277 | 0.438 | 0.562 | 0.688 | 0.750 | 0.598 | 0.792 | 0.500 | 0.250 | 0.175 | 0.113 | 0.188 | 0.062 | 0.750 |
| level_3_strong | 16 | 0.295 | 0.125 | 0.438 | 0.688 | 0.875 | 0.379 | 0.917 | 0.125 | 0.229 | 0.200 | 0.138 | 0.062 | 0.062 | 0.875 |
| level_4_conceptual | 16 | 0.246 | 0.188 | 0.438 | 0.562 | 0.750 | 0.418 | 0.792 | 0.250 | 0.188 | 0.175 | 0.106 | 0.188 | 0.062 | 0.750 |
| original | 132 | 0.527 | 0.667 | 0.811 | 0.879 | 0.924 | 0.780 | 0.933 | 0.705 | 0.328 | 0.221 | 0.120 | 0.061 | 0.015 | 0.924 |

## Primary diagnostic

- Paired family questions: 80
- Pearson correlation, lexical overlap versus reciprocal rank: 0.349878

## Additional slices

Machine-readable analytics include difficulty × paraphrase level, question type × paraphrase level, category × paraphrase level, source semantic ID, and source-question family × paraphrase level.

Precision treats a retrieved chunk as relevant when its semantic-unit or source-element lineage intersects the question's acceptable source set. Recall, evidence coverage, and MRR continue to use the required source set. Required-evidence text is retained for audit but is not used as a strategy-specific text-match shortcut.
