# Quality-Control Report

- Questions reviewed: 132
- PDF lineage failures: 0
- Weaker PDF text matches retained for review: 48
- Exact duplicate questions: 0
- Rejected questions: 0
- Ambiguous questions retained: 0
- Questions requiring external knowledge: 0

## Verification method

Every required semantic-unit ID was resolved against `output/document.json`. Its page range and source text were then checked against text independently extracted from the corresponding page(s) of the original PDF with pypdf. The build fails if the sampled source-token match falls below 35%; matches below 85% remain explicit manual-review candidates because PDF extractors tokenize lists, ligatures, punctuation, and wrapped text differently.

Procedure questions cite all parser elements needed to reconstruct the complete printed procedure. Table questions cite the canonical table element, including joined fragments for Tables 1 and 7.

## Parser warnings carried into review

- warning-001 (possible_table_continuation), pages 9, 10: Multiple physical fragments were joined into one logical table; merge passed structural checks.
- warning-002 (unassociated_figure), pages 10: Caption has no qualifying raster image region; source may use vector/compound artwork.
- warning-003 (possible_cross_page_paragraph_merge), pages 15, 16: Paragraph was joined across a page boundary.
- warning-004 (possible_table_continuation), pages 29, 30: Multiple physical fragments were joined into one logical table; merge passed structural checks.
- warning-005 (possible_cross_page_paragraph_merge), pages 54, 55: Paragraph was joined across a page boundary.

## Manual-review candidates

- Q071: The parser split the two printed creation steps across procedure and paragraph elements; the complete source set is required.
- Q089: The source wording is awkward; retain for manual review if strict semantic interpretation of Entire Range is required.
- Q099: The complete five-step procedure is the answer-bearing unit.
- Q004 / section-3-element-001: independent PDF token match 0.8.
- Q010 / section-5-element-001: independent PDF token match 0.667.
- Q012 / section-6-element-002: independent PDF token match 0.6.
- Q016 / section-6.4-element-001: independent PDF token match 0.8.
- Q025 / section-9-element-003: independent PDF token match 0.571.
- Q037 / section-11.1-element-001: independent PDF token match 0.636.
- Q048 / section-12.2.1-element-001: independent PDF token match 0.825.
- Q048 / section-12.2.2-element-001: independent PDF token match 0.775.
- Q049 / section-12.2.3-element-001: independent PDF token match 0.825.
- Q050 / section-12.2.3-element-001: independent PDF token match 0.825.
- Q055 / section-12.5.1-element-002: independent PDF token match 0.538.
- Q056 / section-12.5.1-element-003-labelled: independent PDF token match 0.55.
- Q057 / section-12.5.2-element-001: independent PDF token match n/a.
- Q057 / section-12.5.2-element-002: independent PDF token match 0.688.
- Q059 / section-12.6-element-001: independent PDF token match 0.75.
- Q060 / section-12.6-element-001: independent PDF token match 0.75.
- Q060 / section-12.6-element-002-labelled: independent PDF token match 0.839.
- Q061 / section-12.7-element-001: independent PDF token match 0.775.
- Q067 / section-13.3.1-element-001: independent PDF token match 0.75.
- Q071 / section-14-element-001: independent PDF token match 0.375.
- Q071 / section-14-element-002: independent PDF token match 0.733.
- Q071 / section-14-element-004: independent PDF token match 0.692.
- Q072 / section-14-element-006: independent PDF token match 0.8.
- Q092 / section-16-element-002: independent PDF token match 0.5.
- Q095 / section-16.1.2-element-001: independent PDF token match 0.778.
- Q102 / section-16.2.2-local-group-01: independent PDF token match 0.725.
- Q103 / section-16.2.2-local-group-02: independent PDF token match 0.773.
- Q104 / section-16.2.2-local-group-03: independent PDF token match 0.75.
- Q105 / section-16.2.2-local-group-04: independent PDF token match 0.425.
- Q106 / section-16.2.2-local-group-04: independent PDF token match 0.425.
- Q106 / section-16.2.2-local-group-05: independent PDF token match 0.65.
- Q118 / section-16.3-element-001: independent PDF token match 0.7.
- Q118 / section-16.3-element-002: independent PDF token match 0.595.
- Q118 / section-16.3-element-003: independent PDF token match 0.8.
- Q120 / section-16.4-element-001: independent PDF token match 0.7.
- Q121 / section-16.5-element-007: independent PDF token match 0.733.
- Q121 / section-16.5-element-009: independent PDF token match 0.667.
- Q122 / section-16.5-element-011: independent PDF token match 0.714.
- Q124 / section-17.1.1-element-001: independent PDF token match 0.625.
- Q124 / section-17.1.1-element-003: independent PDF token match 0.625.
- Q124 / section-17.1.1-element-007: independent PDF token match 0.733.
- Q125 / section-17.1.2-element-001: independent PDF token match 0.8.
- Q126 / section-17.1.3-element-001: independent PDF token match 0.8.
- Q128 / section-18-element-005: independent PDF token match 0.775.
- Q129 / section-18-element-007: independent PDF token match 0.775.
- Q130 / section-17.1.2-element-001: independent PDF token match 0.8.
- Q131 / section-16.2.2-local-group-01: independent PDF token match 0.725.
- Q131 / section-11.1-element-001: independent PDF token match 0.636.

## Duplicate candidates

- None by exact normalized-question comparison.
