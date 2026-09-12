# Retrieval Analytics

## Purpose

Analytics are computed from normalized run and question records rather than from
new output directories. This keeps repeated investigations reusable without
duplicating chunks, embeddings, rankings, or one report per parameter point.

## Commands

From the project root:

```powershell
$env:PYTHONPATH = "src"
python -m testrx_retriever.analytics --group-by experiment_id,run_id
python -m testrx_retriever.analytics --group-by experiment_id,paraphrase_level
python -m testrx_retriever.analytics --group-by token_size,embedding_dimension
python -m testrx_retriever.analytics --group-by embedding_family,embedding_model,category
python -m testrx_retriever.analytics --group-by source_semantic_id --format json
```

Supported dimensions are experiment/run identity and role; chunking strategy,
token size, and overlap; embedding family, model, and dimension; retrieval and
reranking algorithms; difficulty, question type, paraphrase level, evaluation
category, semantic source ID, and source-question family. Multi-valued category
and source dimensions intentionally contribute a question to each applicable
group.

## Metric contract

- Recall@K is the fraction of questions whose complete required source set is
  retrieved by K.
- Precision@K is the mean fraction of returned chunks whose lineage intersects
  the acceptable source set.
- MRR uses the first chunk intersecting the required source set.
- Evidence coverage is the fraction of required source IDs retrieved at maximum
  K; the distribution reports zero, partial, and complete cases.
- Lexical overlap is unique case-folded query tokens found in concatenated
  required-source text divided by unique query tokens, using the same pinned
  regex tokenizer as chunking.

Required-evidence strings remain audit material. Metrics never use those strings
as a chunk-strategy-specific shortcut.

## Extending components

Every run records explicit component identity. New embedders should declare a
stable family such as `lexical`, `static`, `transformer`, or `attention`, plus
model/version/dimension. New retrieval and reranking implementations should use
stable algorithm names and serializable parameters. The runner must validate a
component before executing it; merely naming an unimplemented component is an
error.

The current implementation supports only token windows, the lexical hashing
embedder, exact cosine retrieval, and no reranking. The schema and grouping
contract are broader so later implementations remain comparable.
