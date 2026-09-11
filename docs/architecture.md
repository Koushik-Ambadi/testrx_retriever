# TESTRX Retriever Architecture

## Data flow

```text
source PDF
  -> physical extraction
  -> typed page evidence
  -> conservative normalization/classification
  -> logical reconstruction
  -> canonical document
  -> document + semantic inspection + validation + warnings + inventory
  -> chunking-independent golden evaluation dataset
  -> baseline token windows
  -> deterministic hashing embeddings
  -> exact cosine index
  -> golden retrieval evaluation
```

The physical and logical views coexist. Logical cleanup never destroys the
evidence needed to trace an element back to a source page and bounding box.

## Responsibilities

- `models.py`: small dataclasses and JSON serialization.
- `parser.py`: orchestration, PDF metadata, physical page extraction, output.
- `normalize.py`: safe whitespace, control-character, and line-join rules.
- `structure.py`: heading hierarchy, paragraph/list/procedure reconstruction.
- `tables.py`: table fragments, merged-cell context, captioning, continuation.
- `figures.py`: native figure captions and large image-region association.
- `validation.py`: measurable invariants and document-specific regression checks.
- `inspection.py`: recursive element walk, warning collection, readable renderer.
- `cli.py`: one parsing command; no service layer.
- `baseline_config.py`: validated, versioned baseline configuration.
- `tokenization.py`: pinned token boundary definition.
- `chunking.py`: source-order flattening and fixed token windows.
- `embedding.py`: deterministic local word/bigram feature hashing.
- `vector_index.py`: exact in-memory cosine index and ranked results.
- `evaluation.py`: lineage metrics and report rendering.
- `baseline.py`: baseline build/evaluation orchestration and artifact writing.

## Physical model

Each page retains dimensions, page type, ordered text lines, table fragments,
figure regions, and boilerplate lines. A text line retains its original text,
normalized text, bounding box, dominant font, size, and classification.

Coordinates use PDF points with origin at the top-left, matching pdfplumber's
`top`/`bottom` coordinate convention.

## Logical model

The document contains numbered sections. Each section records its identifier,
title, numeric depth, parent, ancestor path, sequence, page range, heading
source, and ordered typed elements. Elements carry one or more source spans.

Tables are first-class logical elements. They keep normalized rectangular rows,
forward-filled merged context, captions, and physical fragment provenance.
Figures are references only: identifier, caption, region, page, and owning
section. Screenshot pixels are deliberately not interpreted.

Elements may own `children`. `local_group` represents a numbered semantic group
inside a formal section. `labelled_block` represents a short local label and its
body. Formal numbered sections remain the only section tree.

## Determinism

- No network calls, OCR engines, LLMs, or probabilistic classifiers.
- Stable page and reading-order traversal.
- Stable identifiers derived from page/order or printed section/table/figure IDs.
- JSON keys and list ordering are deterministic.

## Failure philosophy

Uncertain source content is preserved and surfaced as a warning. The parser
does not silently invent structure. Document-specific assertions supplement
generic invariants because this project targets one source manual in Phase 1.

## Actual heuristic boundaries

- Heading: number regex plus font/size/x gate.
- Paragraph: vertical gap or next-page top threshold.
- List: known bullet markers. Limited nesting.
- Procedure: `N. text` plus non-Light font.
- Table continuation: adjacent page + bottom/top position + same heading owner +
  compatible column geometry. Repeated continuation headers are removed.
- Figure: nearest large image above same-page caption.
- Footer: bottom coordinate or two exact strings.
- TOC: fixed pages 2-4.
- Confidence: no numeric score. Ambiguous joins and associations are warnings.

## Phase state

Parsing corrections, a source-grounded seed dataset, and the first baseline
retriever are implemented and verified. Advanced chunking and retrieval remain
separate future phases.

## Baseline component boundaries

The baseline follows one-way dependencies:

```text
BaselineConfig -> TokenChunker -> StableHashingEmbedder
               -> ExactVectorIndex -> Evaluator -> Artifacts
```

The chunker accepts a canonical document dictionary. The index accepts chunks
and owns the single configured embedder. The evaluator depends only on a small
`retrieve(query, top_k)` protocol and source-lineage metadata. These boundaries
allow later replacements without implementing alternatives prematurely.

The persisted index is a deterministic `.npy` matrix plus ordered chunk IDs. The
full chunk records are stored once under `chunks/`; the IDs map vector rows back
to those records.

## Experiment layer

`experiments.py` orchestrates controlled parameter sweeps above the existing
chunker, embedder, index, and evaluator. It does not change their contracts.
Chunks are built once per window and reused across dimensions. The runner adds
random-lineage, lexical-coverage, lineage-density, collision, ranking-stability,
slice, and per-question margin diagnostics.

Experiment configurations declare input identity, retention, evaluation,
chunker variants, embedder variants, retrievers, rerankers, and controls. The
runner expands their Cartesian product and assigns a content-derived `run_id`.
Unsupported component implementations fail validation before computation.

All experiments upsert into one normalized store: experiment records, run
records, and question-level metrics. Question records retain difficulty, type,
analysis categories, source pages, section paths, semantic IDs, coverage,
failure category, rank, and score margin. They omit chunk text, vectors, and raw
ranked payloads. The full reference run remains the only persisted bundle with
those large intermediates.

## Golden dataset layer

The benchmark is a derived evaluation layer, not part of the parser contract.
Each question links an expected answer to required and acceptable semantic-unit
sets, exact element IDs, section paths, pages, hard negatives, and retrieval
requirements. The original PDF remains authoritative; parsed metadata supplies
stable lineage and structure.

`scripts/build_golden_dataset.py` resolves every referenced ID against the
canonical document and independently checks the associated page text against the
PDF. JSONL is the machine contract. CSV is a flat review view. Reports summarize
distribution, coverage, and quality-control exceptions.

## Not carried forward

- PDF tags/MCIDs, internal links, colors, matrices, style flags.
- Character-level and exact table-cell geometry.
- Small/original image objects.
- Numeric confidence scores.
