# TESTRX Retriever Decisions

This is the living source of truth. Entries are never silently rewritten when a
later observation changes an earlier decision; a new entry supersedes the old.

## O001 - Source identity

Observation:
- Manual has 61 A4 pages and a native text layer.
- Project copy and original share SHA-256 `9CC50B...73B99`.
- No encryption, forms, JavaScript, or PDF outline.

Impact:
- Native extraction is viable and reproducible.
- Hierarchy must be reconstructed.

Decision:
- Preserve a byte-identical copy at `source/TESTRX_User_Manual.pdf`.
- Treat PDF plus checksum as source truth.

Implementation consequence:
- Parser input is read-only.
- Outputs record checksum and parser version.

Status:
- Accepted.

## O002 - Extraction tooling

Observation:
- Bundled `pdfplumber 0.11.9` exposes words, characters, fonts, coordinates,
  images, ruled tables, and page geometry.
- It detects relevant tables on pages 9, 10, 29, 30, and 42.
- PyMuPDF is not bundled.

Impact:
- One library can supply the physical evidence required for Phase 1.
- Adding PyMuPDF would increase setup cost without demonstrated need.

Decision:
- Use pdfplumber as the sole runtime PDF dependency.

Implementation consequence:
- Pin a compatible dependency range in `pyproject.toml`.
- Revisit only if validation exposes a concrete extraction gap.

Status:
- Accepted.

---

## O003 - Physical and logical layers

Observation:
- Pages are physical boundaries, but paragraphs, lists, sections, and tables
  can continue across them.

Impact:
- A page-only or plain-text model would lose semantic continuity or provenance.

Decision:
- Store physical pages and reconstructed logical sections in the same canonical
  document, linked by source spans.

Implementation consequence:
- Logical elements reference page, line/block IDs, and bounding boxes.

Status:
- Accepted.

---

## O004 - Heading hierarchy

Observation:
- Section headings use numeric paths (`14`, `14.6`, `14.7.1`, `16.2.4.1`).
- Typography distinguishes headings from numbered procedure steps.
- No bookmark tree exists.

Impact:
- Text regex alone can confuse procedures with headings.

Decision:
- Require numeric pattern plus heading typography/line evidence.
- Derive depth from numeric components and parent from nearest prefix.

Implementation consequence:
- Preserve font size/name in physical lines.
- Validate parent existence and monotonic sequence.

Status:
- Accepted.

---

## O005 - Tables

Observation:
- Tables contain retrieval-critical descriptions and merged cells.
- Table 1 spans pages 9-10; Table 7 spans pages 29-30.
- Table 7 page 30 begins without a repeated header and is followed by Table 8.

Impact:
- Flat text or per-page table objects lose relationships.

Decision:
- Tables are first-class objects.
- Retain raw rectangular cells and a semantic row view with merged context
  forward-filled only where layout clearly signals inheritance.
- Join fragments only with caption/position/schema evidence.

Implementation consequence:
- Separate physical fragments from logical tables.
- Store every fragment page and bounding box.

Status:
- Accepted.

---

## O006 - Figures

Observation:
- Screenshots are large image objects with native captions such as `Snp.27`.
- Most operational meaning is repeated in nearby prose.
- Footer logos are also image objects.

Impact:
- OCR would add duplicate/noisy text; treating all images as figures adds logos.

Decision:
- Preserve native caption, printed ID, page, owning section, and associated large
  image region. Ignore pixel semantics in Phase 1.

Implementation consequence:
- Filter small/repeated image regions by size and position.
- Mark figures as not semantically interpreted.

Status:
- Accepted.

---

## O007 - Boilerplate and TOC

Observation:
- Page numbers, legal footer text, dots, and certification marks repeat.
- Pages 2-4 are table-of-contents pages useful for structural QA.

Impact:
- Boilerplate and TOC entries would pollute later searchable content.

Decision:
- Retain them in the physical view with classifications.
- Exclude them from logical semantic elements.
- Use TOC only for validation.

Implementation consequence:
- Page type and line classification are explicit fields.

Status:
- Accepted.

---

## O008 - Normalization

Observation:
- Native text contains occasional malformed break/hyphen characters and wrapped
  prose, while technical identifiers and punctuation are significant.

Impact:
- Aggressive cleanup can silently corrupt knowledge.

Decision:
- Normalize Unicode controls and whitespace conservatively.
- Join lines only with strong layout and sentence-continuation evidence.
- Keep original physical text alongside normalized logical text.

Implementation consequence:
- Every semantic element remains traceable to untouched source line text.

Status:
- Accepted.

---

## O009 - Scope boundary

Observation:
- Reliable chunking depends on the canonical representation, which is not yet
  validated.

Impact:
- Building retrieval now would lock assumptions before source fidelity is known.

Decision:
- Stop after canonical parsing and validation.

Implementation consequence:
- No chunking, embeddings, vector DB, retrieval, LLM, or API packages.

Status:
- Accepted.

---

## O010 - Mixed heading fonts

Observation:
- Most headings use Calibri Light, but sections 4 and 12 and several section 12
  descendants use regular Calibri while retaining heading size, position, and
  numeric depth.
- The first extraction pass consequently orphaned `12.2.1` and missed `12.5.1`.

Impact:
- Requiring one font family produces an incomplete hierarchy.
- Accepting every numbered line would misclassify numbered procedures.

Decision:
- Combine numeric depth, font family, font size, and left-edge geometry.
- Top-level regular-font headings require large display size; level-two headings
  require heading size; deeper numbered headings may use left-edge evidence.

Implementation consequence:
- Validation requires all top-level sections 1-18 plus section 12 landmarks.

Status:
- Accepted after first-pass correction.

---

## O011 - Missing text inside a merged table cell

Observation:
- Pdfplumber found Table 7 geometry but returned `None` for the vertically merged
  first-column value `Action` even though the native word exists visibly inside
  that region.

Impact:
- Forward filling alone cannot restore a value that never entered the cell grid.

Decision:
- When every data row in the first column is empty, inspect the geometric region
  below the first header cell and recover its native text.
- Then forward-fill that recovered parent context across the logical rows.

Implementation consequence:
- Table 7 validation requires `Action` on every resolved row.
- Raw extracted grid and recovery result remain inspectable.

Status:
- Accepted after first-pass correction.

---

## O012 - Duplicate printed figure identifier

Observation:
- `Snp.3` appears on both page 10 (`Test Case Repository Structure`) and page 11
  (`Test Case Hierarchy`).
- The source therefore contains 51 captions numbered across a nominal 1-50 range.

Impact:
- Using only the printed identifier would create duplicate canonical element IDs.
- Renumbering either caption would falsify the source.

Decision:
- Preserve the printed identifier exactly as metadata.
- Use page-qualified canonical IDs such as `snp_3_p010` and `snp_3_p011`.
- Surface the duplicate as a validation warning, not a parser failure.

Implementation consequence:
- Canonical IDs remain unique while the source anomaly stays visible.

Status:
- Accepted.

---

## O013 - TOC/body difference

Observation:
- Every section listed on TOC pages 2-4 exists in the reconstructed body.
- Body subsections `16.2.4.1` through `16.2.4.6` are real headings but are omitted
  from the printed TOC.

Impact:
- Requiring exact equality with the TOC would incorrectly delete valid body structure.

Decision:
- Require TOC identifiers to be a subset of body identifiers.
- Report body-only identifiers for inspection without treating them as failures.

Implementation consequence:
- TOC validates minimum hierarchy coverage; the body remains authoritative.

Status:
- Accepted.

---

## O014 - Tagged PDF data ignored

Observation:
- PDF has a structure tree.
- 64,106/64,289 characters have MCIDs.
- Tags: P, Span, Artifact.
- 83 internal links. No outline.
- Parser keeps none of this.

Impact:
- Hierarchy stays heuristic.
- Tag/link debug detail lost.

Decision:
- No redesign now. Tags do not directly give H1/H2/Table/Figure.
- P2 debug/generalization work.

Status:
- Reviewed. Deferred.

---

## O015 - Interface labels are not procedures

Observation:
- `1. CANoe` to `5. VTE` are local headings.
- Parser stores five one-item procedures.
- Text/list/figure order survives. Local parent does not.

Impact:
- Chunking can detach settings or screenshot from interface.
- Type is wrong.

Decision:
- P0 before freeze: local-block grouping.
- Preserve printed number.
- Test all five interfaces.

Status:
- Accepted. Implemented 2026-09-04.

---

## O016 - Continuation confidence absent

Observation:
- Paragraph/list continuation uses gap/top thresholds.
- Table continuation uses adjacency/bottom/top/caption.
- No confidence/warning.
- Later repeated table header not removed.

Impact:
- New layout can silently over/under-merge.

Decision:
- P1: add stronger evidence and warnings.
- Compare table owner/schema/geometry when possible.

Status:
- Accepted. Implemented 2026-09-04.

---

## O017 - Local labels are plain paragraphs

Observation:
- Warning, Note, Validation Rules, Invalid Example, Valid Example not typed.
- Text/order/section/provenance survive.

Impact:
- Content remains.
- Local label/body relation can split later.

Decision:
- Decide before freeze: typed block or explicit relation.
- Add type only when retrieval value is clear.

Status:
- Accepted. Implemented conservatively 2026-09-04.

---

## O018 - Semantic groups use recursive element ownership

Observation:
- Formal numbered sections are not enough for local interface and labelled blocks.
- Flattening loses the exact label-to-body-to-figure relation.

Decision:
- Keep the formal section tree unchanged.
- Add recursive `children` to elements.
- Use `local_group` for sequential short numbered nouns.
- Use `labelled_block` only for conservative heading-like labels.
- Keep genuine imperative numbered sequences as `procedure`.

Status:
- Accepted. Implemented and regression tested.

---

## O019 - Parsing output is a five-file contract

Decision:
- Emit `document.json`, `semantic_structure.md`, `page_inventory.csv`,
  `validation_report.json`, and `parsing_warnings.json`.
- JSON remains machine truth. Markdown is the human inspection view.
- Warnings are separate from validation so ambiguity is visible without failing
  an otherwise valid parse.

Status:
- Accepted. Implemented.

---

## O020 - Unsupported non-native input stops at parsing

Decision:
- Detect native-text coverage before claiming the input is supported.
- Classify insufficient coverage as `unsupported_non_native_pdf`.
- Emit an error warning. Do not silently invoke OCR.

Status:
- Accepted. Implemented. OCR remains out of scope.

---

## O021 - Golden dataset precedes chunking

Observation:
- A benchmark created after choosing chunks can encode the chosen boundaries and
  hide chunking failures.

Decision:
- Create and version the seed golden dataset before implementing a final chunking
  strategy.
- Do not add chunk IDs to the benchmark source contract.

Status:
- Accepted. Implemented 2026-09-09.

---

## O022 - PDF truth and parser lineage have different authority

Observation:
- The canonical representation provides stable hierarchy and IDs, but it is a
  derived artifact and carries documented parsing warnings.

Decision:
- Treat the PDF and its checksum as factual truth.
- Use parser hierarchy, element IDs, and page mappings as supporting lineage.
- Fail dataset generation when a required ID is missing or its PDF-page evidence
  is substantially absent; retain weaker extractor matches for manual review.

Status:
- Accepted. Implemented 2026-09-09.

---

## O023 - Retrieval evidence is distinct from answer text

Decision:
- Store `expected_answer` separately from required evidence and retrieval source
  sets.
- Identify a primary source, complete required source set, acceptable source set,
  and optional hard negatives for each question.
- Treat complete procedures as answer-bearing units even when parser elements are
  split across printed steps and continuation paragraphs.

Status:
- Accepted. Implemented 2026-09-09.

---

## O024 - Seed quality and later targeted expansion

Decision:
- Begin with a reviewed 100-200 question seed set distributed across content and
  retrieval difficulty.
- Keep questionable questions out of the accepted set and record manual-review
  candidates explicitly.
- After initial retrieval experiments, add a separately reviewed wave focused on
  observed failures rather than silently rewriting the seed.

Status:
- Accepted. Seed contains 132 questions.

---

## O025 - Baseline chunking is a fixed token window

Observation:
- The first measurement needs a deliberately simple reference that does not
  protect semantic units by design.

Decision:
- Flatten canonical content in source order and use configurable token windows.
- Set the initial configuration to 500 tokens with 50-token overlap.
- Permit windows to cross elements, semantic units, sections, and pages while
  preserving every contributor in metadata.

Status:
- Accepted. Implemented 2026-09-11.

---

## O026 - Token boundaries and chunk IDs are versioned

Decision:
- Use `testrx_regex_tokenizer` version `1.0` with an explicit regex contract.
- Derive chunk IDs from source checksum, tokenizer identity, chunk configuration,
  chunk index, and exact text.
- Do not use timestamps, random UUIDs, or object identity.

Status:
- Accepted. Implemented and reproducibility tested.

---

## O027 - The first embedder has no external model state

Observation:
- A downloaded neural model introduces network, cache, revision, and platform
  dependencies before the baseline measurement exists.

Decision:
- Use one local signed word-and-bigram hashing embedder, version `1.0`, with 4,096
  dimensions.
- Record Python and NumPy versions and do not silently substitute another model.
- Accept lexical weakness as a documented baseline limitation.

Status:
- Accepted. Implemented 2026-09-11.

---

## O028 - Retrieval metrics use lineage, not chunk IDs

Decision:
- Match retrieved chunk metadata to golden required semantic/source element IDs.
- Define Recall@K strictly: every required unit must be present for the question
  to count as recalled.
- Report mean semantic-unit coverage separately and calculate MRR from the first
  chunk containing any required unit.

Status:
- Accepted. Implemented for K=1, 3, 5, and 10.

---

## O029 - Baseline artifacts are grouped and checksummed

Decision:
- Separate resolved run configuration, chunks, index, and evaluation artifacts.
- Persist raw top-10 results with full metadata for failure inspection.
- Generate a SHA-256 manifest without timestamps.
- Commit the measured baseline separately from implementation and documentation.

Status:
- Accepted. Implemented 2026-09-11.

---

## O030 - Chunk comparisons hold the benchmark and evaluator fixed

Observation:
- Changing questions, relevance IDs, or metric semantics with the chunker would
  prevent attribution of score changes.

Decision:
- Reuse the unchanged 132-question seed, tokenizer, hashing features, exact
  cosine ranking, and Recall/MRR definitions.
- Vary only chunk size, approximately 10% overlap, and hashing dimension.
- Repeat the original 500/50/4096 configuration as a control.

Status:
- Accepted. Implemented 2026-09-11 in 29 controlled runs.

---

## O031 - Fixed K requires an index-size control

Observation:
- The 500-token baseline has only 22 chunks; K=10 exposes 45.5% of the index.
- Larger chunks own more source IDs, making lineage hits easier.

Decision:
- Record index fraction at maximum K, source-lineage density, relevant-chunk
  prevalence, and fixed-seed random-ranking lineage Recall@K for every window.
- Interpret Recall@10 together with MRR, Recall@1, and the random control.

Status:
- Accepted. The control random-lineage Recall@10 is 0.529 versus measured 0.924.

---

## O032 - Hash dimension is tested through and beyond the baseline

Observation:
- Very small hashing spaces caused severe feature collisions and large quality
  losses in the initial 128-4,096 sweep.

Decision:
- Extend the matrix through 8,192 and 16,384 dimensions.
- Record feature collision fraction and top-1 agreement against the highest
  dimension at each experimental chunk size.
- Treat 4,096 as near a practical plateau for this corpus, not dimension-free.

Status:
- Accepted. Going from 4,096 to 16,384 adds 0.022-0.039 MRR; going from 128 to
  16,384 adds 0.285-0.311.

---

## O033 - Sweep artifacts stay compact but audit-ready

Decision:
- Persist the resolved configuration, hashes, all run metrics and diagnostics,
  per-question ranks/margins, human report, and checksum manifest.
- Do not duplicate chunk text and embedding matrices for every parameter point;
  they are deterministic intermediates already covered by tests and inputs.

Status:
- Accepted. The four-file experiment bundle is committed separately from code.
