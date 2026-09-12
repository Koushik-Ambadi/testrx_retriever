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

- Table-level versus row-level retrieval representation.
- Parent-context injection and token budgets.
- Learned embeddings, alternative indexes, reranking, and answer generation.
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

## Baseline retrieval limitations

- Token windows deliberately ignore semantic boundaries and can split procedures,
  tables, and sections or combine unrelated units.
- The hashing embedder is lexical and has no learned semantic relationships. Its
  signed feature collisions can produce small negative cosine scores.
- Only one embedding algorithm and one exact vector retriever are implemented;
  the dimension sweep does not add an independent model family.
- The in-memory index is suitable for this 22-chunk corpus, not large-scale use.
- Retrieval evaluates source-unit presence, not whether the exact required text
  span is completely contained in one chunk.
- Recall@K is strict for multi-unit questions; MRR uses the first partial evidence
  hit. These definitions must remain fixed in comparisons.
- The baseline has no query rewriting, hybrid matching, reranking, parent-child
  retrieval, answer generation, or answer evaluation.
- Raw top-10 results repeat full chunk text for inspectability and are larger than
  a normalized production result store.

## Chunk-size and dimension study limitations

- The matrix varies fixed token windows and hashing dimension only; overlap stays
  approximately 10%, and feature weighting does not change.
- Fixed K represents different fractions of each index. A random-lineage control
  exposes this effect but does not replace a future fixed-fraction evaluation.
- Lineage relevance does not prove the entire required evidence span is present
  or sufficiently focused inside a chunk.
- Collision fraction counts occupied hashing buckets; it does not directly
  quantify the effect of collision signs and weights on every query.
- Questions were authored from the same manual and retain substantial source
  vocabulary. There is no paraphrase-stress, adversarial distractor,
  unanswerable, or unseen-document split.
- The compact artifact bundle does not store 29 redundant embedding matrices or
  chunk files. They are deterministically regenerable from recorded inputs.

## Controlled paraphrase study limitations

- Sixteen families provide a diagnostic stress set, not a statistically broad
  sample of language variation.
- Paraphrases were manually controlled, not independently authored or blinded.
- Mean overlap is not perfectly monotonic: strong exceeds moderate; Q048-P4 is
  above its conceptual review threshold. QC retains both observations.
- The same required/acceptable lineage is cloned across a family. This isolates
  wording but does not test alternate valid evidence annotations.
- Precision is lineage precision per returned chunk, not token-span precision.
- The 22-chunk reference index means K=10 exposes 45.5% of the corpus; high-K
  recall cannot be treated as semantic-generalization evidence.
- Category/family slices can contain one question and should guide follow-up
  inspection rather than model selection.
