# Model store

Model artifacts are separated by runtime role so retrieval, reranking, and
generation can be versioned independently.

- `encoders/`: document/query encoders used for first-stage retrieval.
- `rerankers/`: query-document scorers used only for reranking candidates.
- `generators/`: future answer-generation models; not part of retrieval.

Each model directory contains a small versioned manifest. Large weights and
download caches belong in its ignored `artifacts/` directory and must not be
committed. Pipeline configurations refer to a local artifact path or pinned
external model revision; model downloads are never performed implicitly by the
built-in baseline configuration.
