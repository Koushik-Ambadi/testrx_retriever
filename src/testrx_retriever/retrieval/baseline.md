# Baseline Chunking and Retrieval

Status: frozen reference characterization  
Owner: retrieval evaluation  
Created: 2026-09-11  
Last reviewed: 2026-09-17

## Purpose

This phase establishes the simplest reproducible retrieval reference for future
chunking, embedding, index, reranking, and context-assembly experiments. It is
deliberately not optimized.

## Pipeline

```text
output/parsing/document.json
  -> versioned regex tokenization
  -> fixed token windows
  -> local hashing embeddings
  -> exact cosine index
  -> unchanged golden questions
  -> lineage-based retrieval evaluation
```

The PDF remains the source of truth. The chunker consumes only the canonical
parsed document and never reparses the PDF.

## Baseline configuration

- Chunking strategy: `token_window`
- Chunk size: 500 tokens
- Chunk overlap: 50 tokens
- Tokenizer: `testrx_regex_tokenizer` version `1.0`
- Embedding model: `stable_hashing_word_bigram` version `1.0`
- Embedding dimension: 4,096
- Vector index: normalized NumPy matrix
- Similarity: exact cosine similarity
- Evaluation K values: 1, 3, 5, 10

The embedding model is a signed word-and-bigram feature hasher. It has no fitted
state and downloads no weights. This makes the first baseline portable and
deterministic, but it is lexical rather than a learned semantic model.

## Chunk construction

Sections and recursive elements are flattened in stable sequence order. Table
text contains its caption, columns, and resolved rows. Figure text contains only
the native caption. Parent local-group and labelled-block IDs propagate to child
segments so retrieval lineage preserves semantic ownership.

Token windows may cross paragraphs, elements, sections, semantic units, tables,
and pages. Every chunk records all contributing source IDs, section paths,
content types, and its page range. Chunk IDs hash the source checksum, tokenizer,
chunk configuration, index, and exact text.

## Retrieval evaluation

Golden records are matched through semantic-unit and source-element IDs, never
through strategy-specific chunk IDs.

- Recall@K is strict question-level recall. A question passes only when all
  required source units appear by K.
- Semantic-unit recall@K is mean required-unit coverage at K.
- Evidence coverage is the fraction of required units retrieved.
- MRR uses the first chunk containing any required source unit.
- Precision@K is the fraction of returned chunks whose lineage intersects the
  acceptable source set.

At K=10, failures are grouped only as no required evidence or incomplete
multi-unit evidence. No speculative root-cause label is assigned.

## Artifact layout

```text
output/retrieval/reference/
├── run_config.json
├── manifest.json
├── chunks/
│   └── chunks.jsonl
├── index/
│   ├── chunk_ids.json
│   └── embeddings.npy
└── evaluation/
    ├── retrieval_results.jsonl
    ├── retrieval_metrics.json
    ├── retrieval_analytics.json
    ├── retrieval_analytics.md
    └── retrieval_report.md
```

`retrieval_results.jsonl` intentionally stores the full top-10 chunks, scores,
metadata, and per-question evaluation so failures remain inspectable.

## Original-question reference

- Chunks: 22
- Questions: 132
- Recall@1: 0.667
- Recall@3: 0.811
- Recall@5: 0.879
- Recall@10: 0.924
- MRR: 0.780
- Mean evidence coverage@10: 0.933
- Complete at K=10: 122 of 132

These values define the comparison baseline. They are not a performance target.

## Expanded paraphrase-stress reference

The same fixed configuration now also records the complete 196-question view:

- Recall@1/3/5/10: 0.561/0.724/0.827/0.893
- Precision@1/3/5/10: 0.602/0.301/0.215/0.121
- MRR: 0.703
- Mean evidence coverage@10: 0.912
- Complete at K=10: 175 of 196

The original slice remains 0.780 MRR. Strong and conceptual paraphrase slices
fall to 0.379 and 0.418 MRR, supporting a material lexical-bias explanation.
