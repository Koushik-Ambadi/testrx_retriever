# TESTRX Chunk Size and Embedding Dimension Study

## Scope

The golden questions, parser output, tokenizer, hashing features, cosine index, and metric definitions are fixed. Only token-window size, approximately 10% overlap, and hashing dimension vary. The 500/50/4096 baseline is repeated as a control.

## Results

| Role | Chunk / overlap | Dim | Chunks | R@1 | R@3 | R@5 | R@10 | MRR | Random R@10 | Collision | Top-1 vs 16384 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sweep | 125 / 13 | 128 | 88 | 0.265 | 0.447 | 0.523 | 0.636 | 0.412 | 0.198 | 0.982 | 0.280 |
| sweep | 125 / 13 | 256 | 88 | 0.371 | 0.538 | 0.606 | 0.712 | 0.515 | 0.198 | 0.963 | 0.500 |
| sweep | 125 / 13 | 512 | 88 | 0.447 | 0.606 | 0.674 | 0.811 | 0.594 | 0.198 | 0.927 | 0.606 |
| sweep | 125 / 13 | 1024 | 88 | 0.508 | 0.659 | 0.795 | 0.841 | 0.660 | 0.198 | 0.854 | 0.712 |
| sweep | 125 / 13 | 4096 | 88 | 0.530 | 0.727 | 0.788 | 0.879 | 0.701 | 0.198 | 0.522 | 0.871 |
| sweep | 125 / 13 | 8192 | 88 | 0.553 | 0.735 | 0.811 | 0.909 | 0.721 | 0.198 | 0.332 | 0.955 |
| sweep | 125 / 13 | 16384 | 88 | 0.553 | 0.720 | 0.826 | 0.932 | 0.723 | 0.198 | 0.186 | 1.000 |
| sweep | 200 / 20 | 128 | 55 | 0.311 | 0.492 | 0.583 | 0.742 | 0.450 | 0.275 | 0.982 | 0.394 |
| sweep | 200 / 20 | 256 | 55 | 0.424 | 0.583 | 0.674 | 0.758 | 0.560 | 0.275 | 0.963 | 0.568 |
| sweep | 200 / 20 | 512 | 55 | 0.485 | 0.636 | 0.742 | 0.848 | 0.624 | 0.275 | 0.927 | 0.705 |
| sweep | 200 / 20 | 1024 | 55 | 0.545 | 0.720 | 0.773 | 0.848 | 0.683 | 0.275 | 0.854 | 0.795 |
| sweep | 200 / 20 | 4096 | 55 | 0.561 | 0.727 | 0.803 | 0.894 | 0.703 | 0.275 | 0.522 | 0.871 |
| sweep | 200 / 20 | 8192 | 55 | 0.583 | 0.765 | 0.848 | 0.917 | 0.726 | 0.275 | 0.332 | 0.939 |
| sweep | 200 / 20 | 16384 | 55 | 0.583 | 0.773 | 0.871 | 0.924 | 0.736 | 0.275 | 0.186 | 1.000 |
| sweep | 250 / 25 | 128 | 44 | 0.318 | 0.515 | 0.614 | 0.758 | 0.457 | 0.311 | 0.982 | 0.386 |
| sweep | 250 / 25 | 256 | 44 | 0.432 | 0.598 | 0.674 | 0.788 | 0.563 | 0.311 | 0.963 | 0.591 |
| sweep | 250 / 25 | 512 | 44 | 0.500 | 0.667 | 0.712 | 0.818 | 0.624 | 0.311 | 0.927 | 0.735 |
| sweep | 250 / 25 | 1024 | 44 | 0.530 | 0.727 | 0.765 | 0.856 | 0.665 | 0.311 | 0.854 | 0.765 |
| sweep | 250 / 25 | 4096 | 44 | 0.591 | 0.758 | 0.818 | 0.909 | 0.713 | 0.311 | 0.522 | 0.917 |
| sweep | 250 / 25 | 8192 | 44 | 0.606 | 0.788 | 0.833 | 0.917 | 0.733 | 0.311 | 0.332 | 0.962 |
| sweep | 250 / 25 | 16384 | 44 | 0.621 | 0.795 | 0.841 | 0.917 | 0.743 | 0.311 | 0.186 | 1.000 |
| sweep | 300 / 30 | 128 | 37 | 0.333 | 0.530 | 0.636 | 0.773 | 0.476 | 0.353 | 0.982 | 0.432 |
| sweep | 300 / 30 | 256 | 37 | 0.424 | 0.591 | 0.682 | 0.803 | 0.560 | 0.353 | 0.963 | 0.523 |
| sweep | 300 / 30 | 512 | 37 | 0.523 | 0.682 | 0.788 | 0.879 | 0.648 | 0.353 | 0.927 | 0.720 |
| sweep | 300 / 30 | 1024 | 37 | 0.561 | 0.720 | 0.811 | 0.879 | 0.681 | 0.353 | 0.854 | 0.811 |
| sweep | 300 / 30 | 4096 | 37 | 0.606 | 0.788 | 0.871 | 0.917 | 0.724 | 0.353 | 0.522 | 0.917 |
| sweep | 300 / 30 | 8192 | 37 | 0.629 | 0.818 | 0.879 | 0.939 | 0.752 | 0.353 | 0.332 | 0.939 |
| sweep | 300 / 30 | 16384 | 37 | 0.636 | 0.826 | 0.879 | 0.932 | 0.763 | 0.353 | 0.186 | 1.000 |
| control | 500 / 50 | 4096 | 22 | 0.667 | 0.811 | 0.879 | 0.924 | 0.780 | 0.529 | 0.522 | n/a |

## Observations

- At 4,096 dimensions, the strongest MRR among tested smaller windows is 0.724 at 300/30; its Recall@10 is 0.917.
- The 500-token control contains only 22 chunks, so K=10 searches 45.5% of the entire index. Its measured random-lineage Recall@10 is 0.529.
- Across the full dimension range, the MRR spread by chunk size is 125: 0.311, 200: 0.285, 250: 0.286, 300: 0.287. This is material: very small hashing spaces degrade ranking through collisions.
- Raising dimension from 4,096 to 16,384 changes MRR by 125: +0.022, 200: +0.033, 250: +0.030, 300: +0.039. These high-dimension deltas show whether the model has reached a practical collision plateau.
- `Random R@10` is a fixed-seed random-ranking lineage baseline. It exposes score inflation caused by a small index and chunks that each own many source IDs.
- `Collision` is the fraction of distinct corpus-and-query unigram/bigram features sharing an occupied hashing bucket. `Top-1 vs 16384` measures ranking stability against the 16,384-dimensional run at the same chunk size; the 4,096-dimensional control has no same-window reference and is marked `n/a`.
- The query/evidence lexical and lineage-density diagnostics are recorded in `summary.json`; per-question rank and relevant-versus-irrelevant score margins are in `question_diagnostics.jsonl`.

## Interpretation guardrails

These results characterize this manual and this frozen seed benchmark. They do not demonstrate semantic generalization. The embedder is lexical, the questions were written from the same source, and source-lineage recall gives a whole chunk credit when any recorded required ID is present.

## Reproduction

```powershell
python -m testrx_retriever.experiments --config configs/retrieval_sweep.json
```
