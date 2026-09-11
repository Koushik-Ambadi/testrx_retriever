# TESTRX Parser Review

## Resolution - 2026-09-04

Status: **all agreed parsing corrections implemented. Parsing gate passed.**

- 16.2.2 now has five explicit local groups with recursively owned descriptions,
  lists, and figures.
- Genuine procedures remain procedures.
- Heading-like local labels have explicit blocks.
- Table continuation checks owner and column geometry; repeated headers are removed.
- Native-source detection, structured warnings, semantic Markdown, and the
  five-file output contract are implemented.
- Regression, validation, deterministic-output, and manual semantic checks pass.
- Chunking and retrieval are still absent by design.

The dated findings below are retained as the evidence that caused these changes.

## Golden dataset review - 2026-09-09

Status: **seed gate passed with explicit manual-review candidates.**

- 132 questions cover all required question categories.
- Difficulty mix: 61 easy, 54 medium, 17 hard.
- 28 questions require multiple semantic units; 25 require procedures; 17
  require tables; cross-reference and multi-hop cases are explicit.
- 123 unique required semantic units are represented across 78 of 89 numbered
  sections.
- Every referenced element and hard-negative ID resolves against the canonical
  document.
- Independent pypdf page-text comparison found no lineage failures. Weaker token
  matches remain listed for manual review rather than being hidden.
- All 61 PDF pages were rendered as contact sheets; tables, procedures, control
  logic, TBC interfaces, mapping, execution reports, and Jama pages were checked.
- CSV import produced 132 data rows and the expected 25 fields.
- Dataset and parser contract tests pass together.

Open review item:
- The manual's wording for `In Range` and `Entire Range` is contradictory enough
  to warrant product-owner confirmation before using that single question as a
  strict behavioral oracle.

## Baseline retrieval review - 2026-09-11

Status: **baseline gate passed.**

- Existing parser and golden-set schemas were not redesigned.
- 22 deterministic chunks were generated at 500 tokens with 50-token overlap.
- All chunk IDs and ordered records are content/configuration derived.
- Recursive semantic ownership, source elements, pages, paths, and content types
  survive chunking.
- One versioned 4,096-dimensional local hashing embedder is used for chunks and
  unchanged queries.
- Exact cosine retrieval returns rank, score, text, and metadata.
- Evaluation records strict Recall@1/3/5/10, semantic-unit coverage, MRR, raw
  top-10 results, and simple failure groups.
- Full output bundles are byte-identical in the integration test.
- 36 parser, dataset, chunking, retrieval, evaluation, and integration tests pass.

Measured baseline:
- Recall@1 0.667; Recall@3 0.811; Recall@5 0.879; Recall@10 0.924.
- MRR 0.780; mean evidence coverage@10 0.933.
- 122 of 132 questions retrieve every required unit by K=10.

This is accepted as the comparison reference, not as an optimal design.

Date: 2026-09-03

Rule:
- Code inspected.
- Output inspected.
- Tests run.
- PDF pages 20-23, 27-31, 42-45, 47-50 viewed.
- Parser code not changed.

Verdict:
- **Minor parser corrections needed first.**
- Do not freeze.
- Do not chunk yet.

## Evidence baseline

- Source: `source/TESTRX_User_Manual.pdf`
- SHA-256: `9CC50B1955AB92884CB0C1AA1A1B6ED437BDBD419962A2FDC6818B4D17073B99`
- Output at review time: `output/canonical.json` (superseded by `output/document.json`)
- Validation: 25 checks. 24 pass. 1 warning. 0 fail.
- Tests: 13 pass.
- Result: 61 pages. 89 sections. 217 elements. 9 tables. 51 captions.

## A. Source handling - Q1-13

Status: Partial.

Evidence:
- `parser.py:12,39-56,74-99`
- `figures.py:15-22`
- `tables.py:23-48`
- `models.py:28-67`

How:
- Library: pdfplumber only.
- Requests: pages, text lines, line characters, fonts, sizes, boxes, page
  geometry, images, table regions/cells, metadata.
- Stores: line text, normalized text, page, order, font name, max font size,
  line box, page size, table fragments, large image boxes.
- Uses: text, font name/size, x/y box, order, image box, table box/cells.
- Discards: character objects, MCID, tag, color, matrix, upright, advance,
  per-character boxes, exact cell boxes.
- Does not extract/store: words, paragraph blocks, spans, bold/italic flags,
  underline, hyperlinks, annotations, structure tree.
- Page mapping survives. Logical elements have page provenance.

PDF fact:
- 61/61 pages have characters.
- PDF has `/StructTreeRoot`.
- Character tags: `P`, `Span`, `Artifact`.
- 83 internal-link annotations. Ignored.
- No outline/bookmarks.

Hardcode:
- `source_type = native_pdf`. Asserted. Not detected.
- `ocr_used = false`. OCR absent.

Failure:
- Scanned/hybrid/image-only manuals unsupported.

## B. Native semantics - Q14-20

Status: Not implemented.

Evidence:
- No tag/MCID/outline logic in `src/`.
- `parser.py:75` uses geometric text lines.
- `structure.py:14-45` rebuilds headings.

Truth:
- PDF is tagged. Parser ignores tags.
- No outline exists.
- Replacement: numbering + typography + layout.

## C. Headings - Q21-45

Status: Implemented. Tuned. No confidence.

Evidence:
- `structure.py:14,22-46`

Signals:
- Regex numbering: yes. Mandatory.
- Numeric depth: yes.
- Font family substring `light`: yes.
- Font size: yes.
- X-position: yes for depth 3+.
- Bold/italic/color/spacing/length/case/TOC/tags/model: no.

Rules:
- Light font accepted.
- Level 1 regular font: size >= 15.
- Level 2 regular font: size >= 12.5.
- Level 3/4 regular font: x0 <= 120.
- Level = numeric component count.

Verified:
- Mixed-font sections 4 and 12 work.
- `14 -> 1`, `14.6 -> 2`, `14.7.1 -> 3`, `16.2.4.1 -> 4`.
- `Validation Rules:` and `Parameter Warning` remain non-sections.

Failure:
- Unnumbered/Roman/alphabetic headings missed.
- Max four numeric levels.
- Font/number drift can miss headings.
- Missed heading sends content to last heading until next heading.
- No uncertainty record.

## D. Hierarchy - Q46-60

Status: Implemented for numbered hierarchy.

Evidence:
- `structure.py:49-77,200-220,290-300`
- `models.py:77-88`
- `validation.py:36-48,90-98`

How:
- Parent = numeric prefix.
- Missing prefix fallback = nearest existing prefix.
- Stores ID, level, parent, ancestor path, sequence, pages.
- Child IDs not stored. Derivable.
- Built after physical extraction.
- Pages and sections are separate views.
- Heading state spans pages. Not reset each page.

Verified:
- Section 12 tree complete.
- Section 14 tree complete.
- Section 16.2.4.1-.6 nested under 16.2.4.
- Every TOC ID exists in body.

Failure:
- No numbering: no hierarchy.
- Parent content cannot resume after a child heading.

## E. TOC - Q61-69

Status: Partial. TESTRX-specific.

Evidence:
- `parser.py:42,108-111,123`
- `validation.py:90-98`

How:
- Pages 2-4 hardcoded as TOC.
- Kept physically. Excluded logically.
- Validates section IDs only.

Not checked:
- Names, levels, expected pages.

Failure:
- Different/no TOC: pages 2-4 still excluded.

## F. Paragraphs - Q70-84

Status: Partial.

Evidence:
- `structure.py:176-193`

How:
- Lines manually joined.
- Same page: gap <= max(18, 1.55 x font size).
- Next page: page + 1 and top < 125.
- Same owner section required.
- Heading/table/figure flushes block.

Not used:
- Punctuation, lowercase start, same font, same x, page-bottom proximity.

Failure:
- Cross-page join can over-merge.
- Nearby separate paragraphs can merge.
- No confidence/warning.
- No page pair hardcode.

## G. Lists - Q85-98

Status: Implemented. Limited markers/nesting.

Evidence:
- `normalize.py:41-55`
- `structure.py:139-173`

How:
- Bullets: Word private bullet, `•`, `o`, `○`.
- Numbered: `N. text` + non-Light font.
- Items separate. Marker, level, sources kept.
- Wrapped line: gap + indent.
- Cross-page: next page top < 125.

Verified:
- 12.3: one list. 8 rules. Pages 21-22.

Failure:
- Only two bullet levels.
- Other markers unsupported.
- Numbered local labels can become procedures.

## H-I. Cross-page - Q99-120

Status:
- Sections: Implemented.
- Paragraphs: Partial.
- Lists: Heuristic. Tested good.
- Procedures: Partial.
- Tables: Heuristic. Tested good.
- Figures: Section continuity only. No cross-page image-caption link.
- Examples: Paragraph only.

Evidence:
- `structure.py:77,81-110,160-193,209-220`
- `tables.py:80-111`

Verified:
- 12.3: pages 21-22. 8 rules.
- 14.6: pages 30-31. Final page-31 bullet retained.
- 14.7 ends 14.6.
- 16.2.2: pages 43-46.
- Table 1: pages 9-10.
- Table 7: pages 29-30.

Representation:
- Source pages/ranges retain page breaks.
- No page-break object.
- Separate blocks can share a section.

## J-K. Tables - Q121-155

Status: Implemented for ruled TESTRX tables. Real structure.

Evidence:
- `tables.py:23-77,80-195`
- `validation.py:56-73`

Detection:
- `pdf_page.find_tables()`.
- Default line/border geometry.
- Caption not needed for physical detection.
- Caption used for ID and current continuation grouping.

Stored:
- Fragment page, box, raw rows.
- Caption, ID, columns, rows, resolved rows, fragment IDs, section.
- Wrapped cell lines become spaces.
- Raw and resolved rows coexist.

Merged cells:
- Context forward-filled.
- Missing first-column rowspan text recovered from native region.

Verified:
- Table 6: 2 columns. 10 rows.
- Table 7: 3 columns. 6 rows. `Action` restored. Pages 29-30.
- Table 8: 3 columns. 10 rows. `Entity Type` propagated.
- Table 9: 2 columns. 5 rows.
- Table 1: pages 9-10. 40 rows.

Continuation signals:
- Adjacent page.
- Prior fragment near bottom.
- Next fragment near top.
- Later fragment has caption.

Not used:
- Same section/schema/geometry/font.
- Repeated header evidence.
- Confidence.

Failure:
- Borderless tables missed.
- Captionless multi-page tables not joined.
- Repeated later header not deduplicated.
- Loose geometry can false-join.
- Cell provenance lacks exact cell box.

## L. Figures - Q156-175

Status: Partial.

Evidence:
- `figures.py:10-52`
- `structure.py:89-95,274-287`

How:
- Reads `page.images`.
- Keeps width >= 140, height >= 70, above bottom 90 points.
- Caption regex: `Snp.N - title`.
- Links nearest image above caption on same page.
- Owning section = latest numbered heading.
- No OCR/vision/description.

Verified:
- 51 captions. 50 image links.
- Duplicate `Snp.3` preserved with page-qualified IDs.
- Snp.28 Power Supply: page 44, section 16.2.2.

Gap:
- Power Supply relation is order-only. No explicit interface link.
- CANoe/Power Supply/SDT/FPGA/VTE labels are procedures. Wrong type.
- Image before caption works.
- Two images: nearest above wins.
- Cross-page caption-image link unsupported.

## M. Boilerplate - Q176-187

Status: Partial. Position/string heuristic.

Evidence:
- `parser.py:104-112`

How:
- Line top >= 770: boilerplate.
- Exact strings: `All rights reserved`, `No passing on to third parties`.
- Kept physically. Excluded logically.
- Page numbers removed semantically.
- Small footer logos fail figure-size gate.

Missing:
- Repetition/frequency detection.
- Generic header detection.
- Confidence/safeguard.

Risk:
- Meaningful bottom text can be removed.
- Different footer can leak.

## N. Normalization - Q188-198

Status: Implemented. Conservative. Imperfect.

Evidence:
- `normalize.py:9-38`

Does:
- NFC, whitespace collapse, soft-hyphen removal.
- Word bullet -> `•`.
- U+FFFE/U+FFFF -> ASCII hyphen.
- Non-breaking hyphen -> ASCII hyphen.
- Trailing hyphen + lowercase line repair.

Does not:
- Broad quote/dash/control normalization.

Verified preserved:
- DBC, A2L, LDF, `{{parameter_name}}`, `.exe`, `Ctrl+S`, numbers, units.

Risk:
- Valid trailing-hyphen identifier can join.
- U+FFFE mapping is source-specific.
- Raw physical text remains for debug.

Order:
- Normalization before classification.
- Table cell normalization after geometry.

## O. Reading order - Q199-206

Status: Partial.

Evidence:
- `parser.py:75-99`
- `structure.py:77-115,197`

How:
- Trusts pdfplumber line order.
- No explicit x/y sort for lines.
- Logical events sort by page/top/type.
- Table text excluded, table event reinserted.

Limits:
- No multi-column model.
- Visual QA manual only.
- Reviewed TESTRX pages look ordered.

## P. Procedures - Q207-213

Status: Partial.

Evidence:
- `normalize.py:50-55`
- `structure.py:139-173`

How:
- `N. text` + non-Light font.
- Step marker retained.
- Ordered items stored.
- Same-section page continuation allowed.

Failure:
- Nested procedures unsupported.
- Local interface labels falsely classified as procedures.

## Q. Local blocks - Q214-218

Status: Not implemented as types.

Examples:
- Validation Rules, Invalid Example, Valid Example, Parameter Warning, Note.
- All remain paragraphs/text.

Kept:
- Text, order, section, provenance.

Lost:
- Explicit role.
- Label/body parent relation.

Verdict:
- Readable now.
- Unsafe to freeze before local grouping decision.

## R-S. Physical/logical/schema - Q219-232

Status: Implemented with gaps.

Physical:
- Document -> Page -> Line/TableFragment/FigureRegion.
- Not Page -> Block -> Span.
- Raw line, font, box kept.

Logical:
- Document -> Section -> Element.
- Paragraph/list/procedure/table/figure.
- Section independent of page.

Trace:
- Section -> heading line.
- Element -> source lines/pages/boxes.
- Table -> fragments/pages/boxes/raw rows.
- Cell -> fragment/row. No cell box.

Present:
- Document ID/title/source/hash.
- Page/range/box/source IDs.
- Type/section/parent/path/sequence.
- Table/figure IDs.

Absent:
- Child ID list, block/span tree, confidence, per-cell boxes, page-break object,
  local block types, per-element extraction method, original image bytes.

Deferred:
- Chunk ID, tokens, overlap, retrieval flags, context injection.

## T. Metadata - Q233-241

Status: Implemented. Partial versioning.

Document:
- PDF metadata, page count.
- Hardcoded language/type/source type/TOC pages/OCR false.

Structural:
- Section ID/title/level/parent/path/sequence/pages.

Provenance:
- Source hash/file/page/box/source IDs.

Debug:
- Schema/parser versions.
- Raw/normalized text.
- Classifications.
- Raw/resolved tables.

Missing:
- Ingestion version/run/time.
- Manual business version.
- Per-element confidence/warnings.

Version distinction:
- Hash distinguishes bytes.

## U. Hardcoding - Q242-256

Status: Confirmed.

Document configuration:
- Title/ID/language/type: `parser.py:62-68,120-124`.
- Approved hash: `validation.py:12`.

Tuned heuristic:
- Heading regex/font/size/x: `structure.py:14,29-45`.
- Continuation: `structure.py:160-184`.
- Figure rules: `figures.py:10,19-22,41-42`.
- Footer: `parser.py:104-107`.
- Table caption/continuation: `tables.py:70-84`.

Bug workaround:
- Table first-column recovery: `tables.py:52-67`.

TESTRX validation:
- Sections/pages/table context/figure count: `validation.py:12-88`.
- Same facts: `tests/test_parser.py`.

Problematic/generalize later:
- Cover 1. TOC 2-4.
- Native source asserted.
- Weak table continuation evidence.
- Local numbered labels -> procedures.

Not found:
- Table 7/8/9 transformation special case.
- Snp.27 special case.
- Color rule.
- Runtime source filename rule.

## V. Generality - Q257-271

General:
- Native line/font/box extraction.
- Numeric hierarchy.
- Basic lists/procedures.
- Ruled tables.
- Provenance and deterministic JSON.

Configurable:
- Input PDF. Output directory. Nothing else.

TESTRX-specific:
- Metadata, page types, thresholds, captions, footer, validation.

Another manual:
- `1/1.1/1.1.1`: likely if typography fits.
- Chapter/Roman/alphabetic/unnumbered: fails.
- No TOC: bad page exclusion.
- Scanned: fails.
- Multi-column: unsafe.
- Borderless table: likely missed.
- Captionless multi-page table: not joined.
- Image-heavy: no semantics.

## W. Failure/ambiguity - Q272-281

Status: Partial.

Behavior:
- No confidence.
- Uncertain heading stays body.
- Detected uncaptions table can stay unidentified.
- Ambiguous continuation usually stays separate unless geometry rule matches.
- No generic uncertainty warning.
- Validation: PASS/WARN/FAIL.
- CLI exits 1 only on FAIL.
- Page inventory exists.

Silent risks:
- Missed/false heading.
- False paragraph merge.
- False procedure.
- False table continuation.
- Wrong figure/local-block relation.
- Footer error.
- Complex reading order.

## X. TESTRX checks - Q282-303

Pages 20-23:
- Section 12 tree: correct.
- 12.3: 8 rules, one list, pages 21-22.
- Validation/Invalid/Valid: kept. Paragraphs, not typed blocks.

Pages 27-31:
- 14.3/14.5/14.6/14.7: correct.
- Tables 6/7/8: correct current rows/columns.
- Table 7: all 6 rows across pages. `Action` restored.
- Table 8: 10 rows. `Entity Type` restored.
- 14.6 page-31 bullet: correct.

Pages 42-45:
- 16.2 hierarchy: correct.
- Table 9: 5 components.
- All interface text retained.
- Local interface labels: wrong `procedure` type.
- Screenshots: right section/order. Exact interface relation implicit.

Pages 47-50:
- 16.2.4 and .1-.6: correct.
- Lists and ancestor path: retained.

## Y. Information loss - Q304-313

PDF -> raw:
- Keeps line text/font/size/box/page/order.
- Keeps table rows/fragment box and qualifying image box.
- Loses char detail, colors, flags, tags, annotations, links, drawings, small
  images, image bytes.

Cleaning:
- Raw line remains.
- Normalized copy changes whitespace/bullets/hyphen artifacts.

Layout:
- Adds classifications.
- No confidence or generic block/span model.

Logical:
- Keeps section/page/source paths.
- Loses local semantic roles.
- Can merge close paragraphs.

Tables:
- Keeps raw/resolved rows and fragment provenance.
- Loses cell boxes and merge-span geometry.

Final:
- Debuggable to line/fragment.
- Not reversible to original layout.

## Z. Final - Q314-end

Architecture:
- Native PDF -> physical evidence -> normalization/classification -> numbered
  hierarchy -> logical elements -> JSON + validation.

Strong:
- Identity, page provenance, TESTRX hierarchy, tested cross-page flow, real
  tables, raw/resolved rows, deterministic output.

Partial:
- Paragraphs, nesting, figure relation, boilerplate, TOC validation,
  warnings, generality.

Missing:
- Local block relations, confidence, scanned/hybrid detection, multi-column,
  borderless tables, tag/link use, cell boxes.

Highest risk:
- Local numbered labels -> procedures.
- Interface/figure link implicit.
- Weak continuation evidence.
- Fixed TOC/footer assumptions.

Cross-page verdict:
- Sections yes. Paragraph/list/table heuristic. Figures same-page only.

Hierarchy verdict:
- Numbering primary. Typography/layout gate. Hardcoded thresholds. No tags.

Table verdict:
- Genuine rows/columns/context. Not flat text. Not full cell geometry.

Information-loss verdict:
- Tag/color/link/char detail, small/image bytes, cell geometry, local roles,
  confidence.

Readiness:
- **Minor parser corrections needed first.**
- Core architecture stays.
- Local grouping must be fixed before chunking.

## Priority. No fixes made.

P0 - must fix:
- Model numbered interface labels separately from procedures.
- Group each interface text/list/figure under its local label.
- Test CANoe, Power Supply, SDT, FPGA, VTE grouping.

P1 - should fix:
- Add ambiguity/warning records for headings and continuation.
- Strengthen table continuation with section/schema/geometry evidence.
- Remove repeated continuation headers.
- Preserve cell boxes or explicit cell coordinates.
- Decide warning/note/example/local-label representation.
- Validate TOC names/levels/pages.
- Detect native/scanned/hybrid. Do not assert.

P2 - optional:
- Frequency-based header/footer detection.
- Preserve tag/MCID/color/style/link debug data.
- Multi-column order.
- Borderless-table strategy.
- Optional OCR/vision route later.
