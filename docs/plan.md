# TESTRX Retriever Phase 1 Plan

## Intent

Turn one known 61-page TESTRX manual into a canonical document that retains
meaning, hierarchy, tables, figures, and traceable source locations. The output
must be suitable for later chunking experiments without embedding any chunking
policy in the parser.

## Work sequence

1. Preserve source PDF and checksum.
2. Profile PDF metadata, rendering, text, fonts, ordering, tables, images,
   repeated regions, and cross-page cases.
3. Record observations before fixing extraction rules.
4. Implement physical extraction.
5. Classify boilerplate, headings, captions, tables, paragraphs, and lists.
6. Normalize conservatively.
7. Reconstruct logical hierarchy and cross-page elements.
8. Reconstruct merged and clearly continued tables.
9. Associate figure captions/regions without OCR.
10. Emit canonical and inspection artifacts.
11. Validate representative difficult cases and whole-document invariants.
12. Stop. Review canonical output before beginning chunking as a new phase.

## Milestones

### M1 - Evidence and project skeleton

- Source checksum matches original.
- Representative pages visually inspected.
- Tool choice recorded.
- Minimal package and living documentation exist.

### M2 - Physical extraction

- All 61 pages represented.
- Text lines retain page, bounding box, order, font, and source text.
- Tables and large image regions are separately discoverable.
- Boilerplate is marked, not silently erased.

### M3 - Logical reconstruction

- Numbered heading tree is valid.
- Body text becomes paragraphs/lists/procedures.
- Section content can span pages.
- Figures retain caption, page, section, and region.
- Tables retain columns, rows, merged context, source fragments, and captions.

### M4 - Validation and stop

- Coverage, ordering, hierarchy, tables, figures, boilerplate, and provenance
  checks have explicit pass/fail results.
- Known limitations are written down.
- Canonical output is manually spot-checked against difficult pages.
- No Phase 2 retrieval work exists in the repository.

## Definition of done

Parsing is done only when the CLI completes deterministically, all 61 pages
have physical representations, meaningful content has logical ownership,
known multi-page tables are reconstructed, source provenance remains usable,
and validation reports failures specifically enough to investigate.

## Parsing close gate - 2026-09-04

Status: implemented and verified.

- Local interface groups and recursive ownership added.
- Labelled blocks added conservatively.
- Table continuation evidence strengthened.
- Native-source detection and explicit warning artifact added.
- Five-artifact output contract and semantic renderer added.
- Chunking remains untouched.

## Out of scope

OCR, screenshot semantics, chunk sizing, overlap, embeddings, vector stores,
retrieval, reranking, prompts, LLM calls, APIs, and deployment.

## Phase 2A - Golden evaluation dataset

Status: implemented and verified on 2026-09-09.

1. Review the PDF and canonical hierarchy before question generation.
2. Define answer-bearing semantic units independently of headings and chunks.
3. Create realistic questions across factual, procedural, configuration, table,
   comparison, troubleshooting, figure-context, multi-section, and
   cross-reference needs.
4. Record required, acceptable, supporting, and hard-negative source units.
5. Resolve every metadata ID and verify its page evidence against the PDF.
6. Export JSONL, CSV, statistics, coverage, and QC artifacts.
7. Keep the seed set fixed during initial chunking comparisons.
8. Add a separately versioned targeted wave only after retrieval failure analysis.

At the Phase 2A close, chunking, embeddings, and retrieval were the next
implementation phase. Phase 2B below records their baseline implementation.

## Phase 2B - Baseline chunking and retrieval

Status: implemented and verified on 2026-09-11.

1. Freeze the existing golden dataset and consume the canonical document.
2. Flatten source content deterministically while retaining recursive lineage.
3. Build 500-token windows with 50-token overlap using a pinned tokenizer.
4. Encode chunks and unchanged queries with one local deterministic embedder.
5. Build an exact cosine index and return ranked chunks, scores, and metadata.
6. Evaluate strict Recall@1/3/5/10, semantic-unit coverage, and MRR.
7. Persist run configuration, chunks, index, raw results, metrics, report, and
   checksum manifest.
8. Verify the entire output bundle is byte-identical across repeated builds.

Explicitly deferred: semantic and structure-aware chunking, learned embedding
models, BM25, hybrid retrieval, reranking, query rewriting, answer generation,
and LLM judging.

## Phase 2C - Chunk-size and hashing-dimension investigation

Status: implemented and verified on 2026-09-11.

1. Keep the canonical document, golden set, tokenizer, embedder features, exact
   cosine index, and evaluation definitions fixed.
2. Compare 125, 200, 250, and 300-token windows at approximately 10% overlap.
3. Sweep hashing dimensions from 128 through 16,384 and repeat the baseline
   configuration as a control.
4. Measure random-ranking lineage recall, index fraction, lineage density,
   lexical coverage, collisions, top-1 stability, and per-question margins.
5. Persist a compact deterministic artifact bundle and checksum manifest.
6. Record explanations and threats to validity without changing the benchmark.

The next phase should discriminate lexical memorability from semantic retrieval
using paraphrase stress, span-complete relevance, fixed index fractions, and
feature ablations before adding more complex models.

## Phase 2D - Reusable experiment and artifact architecture

Status: implemented and verified on 2026-09-12.

1. Group parser, dataset, full reference, and compact experiment outputs by
   stable pipeline layer.
2. Group reference and experiment configurations under `configs/retrieval/`.
3. Express chunker, embedder, retriever, reranker, control, evaluation, input,
   and retention settings in a versioned experiment contract.
4. Use content-derived run IDs and shared upsert stores instead of directories
   per experiment or configuration.
5. Retain compact question-level failure facts for later dataset slicing.
6. Keep large chunks, vectors, and raw rankings only for designated references.
7. Preserve experiment-specific findings under `docs/experiments/` and update
   project-level decisions, progress, runbook, schema, review, and limitations.

## Phase 2E - Controlled paraphrase and reusable analytics

Status: implemented and verified on 2026-09-12.

1. Append controlled paraphrases without changing the 132-question legacy set.
2. Store deterministic family/level metadata and tokenizer-aligned lexical
   diagnostics per question.
3. Add precision and zero/partial/complete evidence distributions without
   changing strict recall, coverage, or MRR semantics.
4. Re-run the fixed 500/50/4096 reference on all 196 questions.
5. Keep the earlier chunk/dimension experiment filtered to original questions.
6. Provide reusable shared-store analytics across run, component, dataset,
   category, and semantic-source dimensions.
7. Record measured exceptions, findings, limitations, and reproduction commands.
