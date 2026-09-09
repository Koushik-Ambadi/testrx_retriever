# Known Limitations and Deferred Work

## Accepted Phase 1 limitations

- Screenshot pixels are not OCRed or visually interpreted. Captions and source
  regions are preserved for future selective processing.
- One caption on page 10 is associated with vector/compound page content rather
  than a qualifying raster region; its caption and provenance remain preserved.
- PDF logical tags are not trusted as the hierarchy; numbered headings and
  typography are reconstructed deterministically.
- Table reconstruction is based on ruled-line geometry and explicit continuity
  evidence. Ambiguous borderless tables remain physical evidence with warnings.
- Text normalization is intentionally conservative and can preserve awkward
  source punctuation rather than risk corrupting identifiers.
- The parser is tuned and validated for the supplied TESTRX manual. General PDF
  parsing is not a Phase 1 goal.
- The source repeats printed figure identifier `Snp.3`; unique canonical IDs use
  page qualification and validation reports the anomaly.

## Resolved parsing review items

- Section 16.2.2 interface labels are explicit `local_group` elements.
- Their descriptions, lists, and figures are recursively owned.
- Procedures are distinguished with action-word and sequence evidence.
- Table continuation also checks owner and column geometry; repeated headers are
  removed.
- Short heading-like labels can own `labelled_block` content.
- Cross-page paragraph and multi-fragment table joins are reported as warnings.

## Generality limits

- Native versus unsupported non-native input is detected by native-text coverage.
- Cover page 1 and TOC pages 2-4 are fixed.
- No OCR, multi-column order, borderless tables, unnumbered hierarchy.
- Footer uses position/exact strings. No repetition detector.
- Tags, links, annotations, colors, style flags, exact cell boxes discarded.

## Deliberately pending

- Chunking experiments. The seed evaluation corpus now exists independently.
- Table-level versus row-level retrieval representation.
- Parent-context injection and token budgets.
- Embeddings, indexes, retrieval, reranking, and answer generation.
- Screenshot understanding if UI-location questions later require it.

## Golden dataset limitations

- The seed contains 132 answerable questions and no deliberately unanswerable
  cases. Add unanswerable cases only under a separately defined evaluation goal.
- Figure questions rely on captions and surrounding explanatory text; screenshot
  pixels remain uninterpreted.
- Independent PDF text extraction produces weaker token matches for some lists,
  procedures, and local groups. These cases remain listed in the QC report and
  are not treated as parser failures.
- The manual's description of `In Range` versus `Entire Range` is internally
  awkward. The corresponding question is retained as a manual-review candidate.
- Hard negatives are included only where the manual contains a naturally
  confusing neighboring concept. They are not exhaustive.
- The seed does not encode final chunks, embedding-model assumptions, or ranking
  thresholds.
