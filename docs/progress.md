# Progress Log

Status: append-only  
Owner: project delivery  
Last reviewed: 2026-09-29
Source of truth for: chronological completed work and verification

## 2026-09-03 - Phase 1 started

DONE
- Read the supplied project instruction and prior inspection report.
- Confirmed the workspace was empty and not yet a Git repository.
- Copied the source PDF into the project without modifying the original.
- Verified source and project-copy SHA-256 hashes match.
- Confirmed 61 pages, A4, native text, no encryption/forms/JavaScript.
- Rendered representative pages for visual inspection.
- Tested native table discovery on pages 9, 10, 29, 30, and 42.

OBSERVED
- Numbered headings have consistent typography and up to four numeric levels.
- Procedure numbering is visually distinct from section headings.
- Tables use merged cells; Table 7 continues from page 29 to page 30.
- Figure captions are native text and screenshots are separate image objects.
- Page number, certification marks, and legal text form repeated footer noise.
- Page boundaries split semantic units and therefore cannot terminate sections.

DECIDED
- Use `pdfplumber` as the single primary extraction dependency.
- Keep physical and logical representations together.
- Preserve boilerplate as classified evidence but exclude it from semantic elements.
- Use native captions/regions for figures; no OCR.
- Use standard-library `unittest` so development does not require pytest.

CHANGED
- Added the project source, package skeleton documentation, and output location.

NEXT
- Implement models and extraction modules.
- Generate the first canonical output.
- Validate and visually spot-check difficult cases.

## 2026-09-03 - First-pass audit and corrections

DONE
- Generated and inspected the first canonical artifact.
- Checked all root sections, section 12, tables 1/7/8, figure IDs, cross-page
  elements, classifications, and source-line ownership.

OBSERVED
- Sections 4 and 12 contain valid headings using regular Calibri instead of the
  more common Calibri Light.
- Pdfplumber omitted visible merged value `Action` from Table 7's raw cell grid.
- The manual prints `Snp.3` twice on pages 10 and 11.
- The body contains six valid `16.2.4.x` headings absent from the printed TOC.

DECIDED
- Expand heading evidence without accepting ordinary numbered procedures.
- Recover missing first-column merged text from its native geometric region.
- Page-qualify canonical figure IDs and preserve printed IDs separately.
- Validate TOC identifiers as a subset of body identifiers.

CHANGED
- Corrected the complete section 1-18 hierarchy.
- Corrected Table 7 merged context across pages 29-30.
- Added stronger landmark, uniqueness, TOC, and coverage checks.

NEXT
- Run final compile, regression, determinism, and artifact inspection.

## 2026-09-03 - Phase 1 implementation complete

DONE
- Compiled all source and test modules.
- Passed 13 regression tests.
- Generated `canonical.json`, `validation.json`, and `page_inventory.csv` twice.
- Confirmed byte-identical SHA-256 hashes across independent runs.
- Confirmed all 683 eligible body lines belong to logical elements.
- Confirmed 25 validation checks: 24 pass, 1 documented source warning, 0 fail.

OBSERVED
- Final model contains 61 pages, 89 sections, and 217 semantic elements:
  50 paragraphs, 98 lists, 9 procedures, 9 tables, and 51 figures.
- The only warning is the duplicate printed `Snp.3` identifier.

DECIDED
- Phase 1 is technically complete and awaits human acceptance.
- No chunking or retrieval work will start without a separate Phase 2 agreement.

CHANGED
- Added schema documentation, operating runbook, and final outputs.

NEXT
- Human review of representative canonical sections/tables.
- After acceptance, plan chunking experiments as a new phase.

## 2026-09-03 - Implementation review

DONE
- Inspected code, outputs, tests, validation, PDF tags, hardcoding.
- Viewed pages 20-23, 27-31, 42-45, 47-50.
- Added the review now archived as
  `docs/reviews/2026-09-12-project-review-history.md`.
- Documentation changed. Parser code unchanged.

FOUND
- Core hierarchy/provenance/tables strong.
- PDF tags and 83 internal links ignored.
- 16.2.2 interface labels mis-typed as procedures.
- Interface-to-figure relation implicit.
- Continuation/TOC/footer rules tightly tuned.

VERDICT
- Minor parser corrections needed first.
- Do not freeze. Do not chunk.

NEXT
- Agree P0/P1 from the review now archived as
  `docs/reviews/2026-09-12-project-review-history.md`.

## 2026-09-04 - Parsing corrections complete

DONE
- Added generic local numbered groups and conservative labelled blocks.
- Nested interface descriptions, lists, and figures under CANoe, Power Supply,
  SDT, FPGA, and VTE.
- Preserved the real five-step procedure in 16.2.1.
- Strengthened table continuation using owner, geometry, and repeated headers.
- Added native/non-native input detection without OCR.
- Added readable semantic structure and structured parsing warnings.
- Changed generated output to the agreed five-file contract.
- Expanded regression tests for hierarchy, cross-page content, semantic groups,
  tables, renderer output, provenance, validation, and artifact names.

DECIDED
- Parsing is complete enough to close this phase.
- Warnings describe review-worthy joins/associations; they are not hidden.
- No chunking or retrieval logic belongs in the parser.

NEXT
- Agree the chunking contract, test cases, token policy, and evaluation method.
- Implement chunking only after that agreement.

## 2026-09-09 - Golden evaluation seed complete

DONE
- Initialized the repository with a Phase 1 baseline commit and created the
  `feature/golden-evaluation-dataset` branch.
- Reviewed all 61 PDF pages plus the canonical hierarchy, tables, procedures,
  figures, warnings, and validation output.
- Added a deterministic builder for JSONL, CSV, statistics, coverage, and QC.
- Created 132 source-grounded questions with required and acceptable retrieval
  sets, exact metadata lineage, hard negatives, and analysis flags.
- Added contract tests for size, IDs, categories, source resolution, retrieval
  consistency, and JSONL/CSV row parity.
- Imported and rendered the CSV through the spreadsheet runtime.

DECIDED
- Keep the PDF authoritative and the parsed model as supporting evidence.
- Freeze the initial benchmark independently of future chunking policy.
- Preserve manual-review candidates and parser warnings in the QC report.
- Add failure-driven questions as a new reviewed wave, not silent edits.

NEXT
- Define chunk objects, token accounting, overlap, and parent-context policy.
- Run fixed-dataset Recall@K, MRR, and nDCG comparisons across chunkers.

## 2026-09-11 - Baseline chunking and retrieval complete

DONE
- Created `feature/baseline-retriever` from the completed golden-set baseline.
- Added a validated configuration, pinned regex tokenizer, and deterministic
  500-token/50-overlap chunker.
- Preserved pages, section paths, semantic ancestors, source elements, and content
  types for every chunk.
- Added one 4,096-dimensional local word/bigram hashing embedder and exact cosine
  index with deterministic tie-breaking.
- Evaluated all 132 unchanged golden questions at K=1, 3, 5, and 10.
- Persisted 22 chunks, embeddings, ordered chunk IDs, complete raw results,
  aggregate metrics, a human report, resolved configuration, and checksums.
- Added focused and integration tests, including byte-identical whole-run output.

MEASURED
- Recall@1: 0.667; Recall@3: 0.811; Recall@5: 0.879; Recall@10: 0.924.
- MRR: 0.780; mean evidence coverage@10: 0.933.
- Complete required evidence at K=10: 122 of 132 questions.
- Failures: 8 with no required unit retrieved and 2 with incomplete multi-unit
  evidence.

DECIDED
- Accept this as a deliberately lexical and structure-unaware comparison point.
- Keep metric definitions, golden data, and K values fixed for the first strategy
  comparisons.
- Inspect raw failures before designing the next chunker or embedder.

NEXT
- Review the ten K=10 failures and label likely chunking versus lexical retrieval
  symptoms without changing the baseline.
- Design the first alternative chunking experiment as a separate phase and branch.

## 2026-09-11 - Chunk-size and dimension investigation complete

DONE
- Created `codex/chunk-dimension-study` from synchronized `main`.
- Added a deterministic 29-run experiment driver, configuration, diagnostics,
  compact artifacts, checksum manifest, and integration tests.
- Evaluated 125/13, 200/20, 250/25, and 300/30 windows at 128, 256, 512, 1,024,
  4,096, 8,192, and 16,384 dimensions.
- Repeated 500/50/4096 as the unchanged control.
- Passed all 38 tests and verified byte-identical full-sweep regeneration.

MEASURED
- At 4,096 dimensions, MRR rises from 0.701 at 125 tokens to 0.724 at 300;
  the 500-token control is 0.780.
- Corresponding Recall@10 is 0.879, 0.894, 0.909, 0.917, and 0.924.
- Random-lineage Recall@10 rises from 0.198 at 125 tokens to 0.529 for the
  500-token control as the index shrinks and lineage per chunk broadens.
- Feature collision fraction falls from 0.982 at 128 dimensions to 0.522 at
  4,096 and 0.186 at 16,384.
- Increasing 4,096 to 16,384 dimensions adds only 0.022-0.039 MRR; increasing
  128 to 16,384 adds 0.285-0.311.

FOUND
- The basic retriever has genuine closed-domain lexical ranking signal.
- Large chunks, broad lineage, and a fixed K over a tiny index materially raise
  high-K coverage and make the baseline look stronger.
- Small embedding dimensions damage quality through collisions; 4,096 is near,
  but not fully at, the observed plateau.
- The current evidence does not establish semantic or cross-document ability.

NEXT
- Add a separately reviewed paraphrase-stress evaluation view.
- Compare fixed retrieval fractions and span-complete evidence metrics.
- Run unigram/bigram and shuffled-query ablations before introducing a learned
  embedding model.

## 2026-09-12 - Reusable output and experiment layout complete

DONE
- Consolidated generated parser files under ignored `output/parsing/`.
- Moved the versioned golden benchmark to `output/datasets/golden/` and the one
  full retrieval bundle to `output/retrieval/reference/`.
- Replaced the per-experiment directory with shared experiment, run, and
  question-metric JSONL stores under `output/retrieval/experiments/`.
- Added a versioned component-grid configuration covering chunkers, embedders,
  retrievers, rerankers, controls, evaluation, inputs, and retention.
- Added stable content-derived run IDs and deterministic experiment upserts.
- Retained dataset analysis fields for difficulty, type, categories, pages,
  section paths, source semantic IDs, failures, coverage, rank, and margins.
- Removed duplicated chunk text, embeddings, and raw rankings from sweep output.

DECIDED
- Only explicitly designated reference runs persist full retrieval artifacts.
- New experiments add shared records, not directories.
- Experiment-specific notes live beside their configurations; all material decisions
  and status changes also update project-level documentation.

## 2026-09-12 - Controlled paraphrase and analytics phase complete

DONE
- Appended 64 paraphrases in 16 source families while preserving all 132 legacy
  questions and grounded fields.
- Added deterministic family IDs, five paraphrase levels, tokenizer-aligned
  lexical diagnostics, threshold flags, and legacy-hash protection.
- Added acceptable-lineage Precision@K and reusable analytics across run,
  component, dataset, category, semantic source, and family dimensions.
- Reproduced the fixed 500/50/4096 reference on all 196 questions and retained
  the earlier 29-run study as an original-only comparison.
- Passed all 44 tests and stored two experiments, 30 runs, and 4,024 compact
  run-question records in the shared store.

MEASURED
- Original versus strong MRR: 0.780 versus 0.379; original versus conceptual:
  0.780 versus 0.418.
- Original/light/moderate/strong/conceptual Recall@1: 0.667, 0.625, 0.438,
  0.125, and 0.188.
- Paired lexical-overlap versus reciprocal-rank Pearson correlation: 0.350.
- Full 196-question Recall@1/3/5/10: 0.561/0.724/0.827/0.893; MRR: 0.703.

FOUND
- Same-document lexical wording materially contributes to the basic hashing
  model's strong original score.
- Broad chunks, lineage density, and a small index still inflate high-K recall.
- The level ladder is not perfectly monotonic: strong mean overlap exceeds
  moderate mean overlap, and Q048-P4 exceeds its review threshold.

NEXT
- Use the recorded category/source-family views to select failure-focused tests.
- Consider unigram/bigram, shuffled-query, fixed-index-fraction, and span-complete
  ablations before adding learned embedding families or reranking.

## 2026-09-12 - Cross-setting failure analysis complete

DONE
- Added exact reusable analytics filters and explicit max-K failure counts/rates.
- Compared all settings by dimension and token window, then sliced failures by
  question type, difficulty, category, paraphrase level, source, and family.
- Identified persistent question failures and separated rank degradation from
  complete-evidence misses.

DECIDED
- Keep 500/50/4,096 as the historical control.
- Carry 300/30/8,192 as the next diagnostic anchor because it records the fewest
  K=10 failures with substantially lower index exposure.
- Audit Q080 and Q092 before expanding model complexity.

## 2026-09-13 - Retrieval expansion roadmap agreed

PLANNED
- Establish one evidence-backed chunk policy using span-complete containment,
  fixed-index-fraction views, and persistent-failure audits.
- Compare lexical, static semantic, and contextual attention-based bi-encoder
  families on identical chunks and original/paraphrased evaluation populations.
- Add a cross-encoder reranker only after candidate evidence coverage is
  sufficient, preserving a no-reranker control and identical candidate lists.
- Use family-grouped development and held-out partitions to prevent paraphrase
  variants of the same question from leaking across tuning and selection.
- Select a single or hybrid retriever using held-out quality plus latency and
  resource cost, then proceed to generator evaluation before product UI work.

NOT YET IMPLEMENTED
- BM25, installed attention-model artifacts, the new evidence metrics, and
  controlled model-selection experiment configurations.

## 2026-09-13 - End-to-end retrieval baseline implemented

DONE
- Added separate model stores and registries for bi-encoders, cross-encoders,
  and future LLMs; large model artifacts are ignored by Git.
- Added a single configurable chunk-to-evaluation pipeline with exact vector
  retrieval, reciprocal-rank fusion, pairwise reranking, and per-system outputs.
- Added built-in lexical hashing and corpus-fitted LSA bi-encoder baselines.
- Added a deterministic lexical pairwise reranker to validate candidate-to-rank
  flow without requiring downloaded weights.
- Added lazy Sentence Transformers adapters for attention-based bi-encoders and
  cross-encoders, with an explicit optional dependency and local model path.

NEXT
- Run and verify the full baseline configuration on the controlled dataset.
- Add span-complete and fixed-index-fraction evaluation before selecting chunks.
- Install and register pinned attention-model candidates, then run controlled
  model and reranker comparisons through the same pipeline.

## 2026-09-13 - Production candidate comparison complete

DONE
- Applied the repository audit's first safe migration stages: isolated package
  imports, extracted shared artifact I/O, formed retrieval/evaluation/workflow
  packages, removed duplicate dense ranking, and retained compatibility imports.
- Renamed the local weight area to generic role directories under
  `model_store/{encoders,rerankers,generators}`.
- Installed pinned BGE and E5 encoder snapshots plus the MiniLM cross-encoder in
  the ignored local model store.
- Generalized the comparison workflow for multiple encoders, fusions, and
  rerankers, with cached bulk cross-encoder inference.
- Added reusable analysis over all golden-set columns and a complete per-system,
  category, question-type, paraphrase, difficulty, source, and evidence report.
- Ran ten candidate systems on all 196 questions and passed all 48 tests.

MEASURED
- E5 + MiniLM reranker: R@1 0.760, R@10 0.980, MRR 0.872, coverage 0.983.
- BGE + MiniLM reranker: R@1 0.755, R@10 0.980, MRR 0.869, coverage 0.986.
- Dense retrieval materially outperformed lexical hashing; current RRF hybrids
  did not improve aggregate results but led selected categories.

## 2026-09-15 - Hierarchical chunking raw experiment complete

DONE
- Added canonical hierarchy traversal, pure hierarchy diagnostics, configurable
  max-token descent, concise parent context, stable IDs, and bounded leaf fallback.
- Added the reusable eight-variant matrix runner without duplicating retrieval,
  reranking, evaluation, or model configuration.
- Added raw per-query first-stage and end-to-end latency records excluding
  chunking, index build, and model load.
- Ran token-window 300/30, pure hierarchy, and hierarchy maxima at
  160/256/384/512/640/768 through all ten production-candidate systems.
- Validated 196 result rows per system, seven timing files per variant, complete
  hierarchy records, configured token bounds, and all 58 tests.

MEASURED
- Pure hierarchy: 311 chunks, maximum 2,263 tokens.
- Bounded hierarchy: 154/111/95/79/68/55 chunks as the maximum increases.
- Fallback fragments: 18/4/2/0/0/0 across the six bounded limits.

DECIDED
- Preserve raw outputs locally under the ignored ordinary-run policy.
- Defer detailed metric comparison, plots, strongest-candidate selection, and
  production decisions to a separate analysis pass.

## 2026-09-17 - Documentation ownership cleanup complete

DONE
- Restricted `docs/` to project-wide governance, progress, testing, and dated
  reviews.
- Moved analytics, retrieval baseline, schemas, runbooks, pipeline guidance,
  benchmark strategy, and experiment records beside their owning code,
  configuration, or durable artifact.
- Renamed the phase plan to `roadmap.md`, standardized Markdown filenames, and
  added `docs/README.md` as the ownership/navigation index.
- Added one project testing strategy instead of per-test documentation.
- Corrected stale descriptions of model comparison, hierarchical chunking,
  artifact classes, current limitations, and experiment locations.
- Preserved older audits and reviews as dated frozen evidence with resolution
  notices rather than rewriting their historical findings.
- Verified project-local Markdown links and ran 58 tests successfully.

## 2026-09-17 - Reusable project lifecycle skill added

DONE
- Reviewed the project task history and Git chronology to extract reusable
  practices from discovery through reproducible experiments and delivery.
- Added `skills/project-lifecycle-governance/` with separate references for
  lifecycle gates, documentation ownership, architecture and code, testing,
  experiments, decisions and learning, Git delivery, and content reuse.
- Added conditional templates rather than mandatory document scaffolding.
- Added a read-only JSON project snapshot utility that inventories structure,
  relevant files, recent Git history, branches, remotes, and configured owner.
- Kept TESTRX-specific retrieval and experiment knowledge outside the general
  skill so future projects can pair it with their own technical skills.

DECIDED
- Engineering projects own factual evidence and provenance; a separate future
  content project will own editorial derivatives, publication workflows,
  impressions, engagement, and feedback analysis.

## 2026-09-17 - Production retriever frozen and wrapper added

DONE
- Analyzed all 80 hierarchy/model system combinations across complete-evidence
  retrieval, MRR, evidence coverage, question slices, chunk/index exposure,
  returned context tokens, and available latency measurements.
- Tuned BGE+MiniLM candidate depth at K=10/12/15/20/30 and final context depth
  at K=1/3/5/10, then regenerated a checked-in candidate-K=10 evaluation config.
- Selected hierarchy-384, BGE small English v1.5, MiniLM-L6 reranking,
  candidate K=10, and final K=5.
- Added a configurable long-lived query-to-chunks application and CLI with
  per-call K overrides, source metadata, token totals, and stage timings.
- Added lightweight wrapper tests and updated architecture, roadmap,
  limitations, runbook, experiment resolution, and retrieval documentation.

MEASURED
- Frozen system: R@1 0.760, R@3 0.918, R@5 0.949, R@10 0.980, MRR 0.883,
  and mean evidence coverage@10 0.986 over 196 questions.
- Context at K=5: 715 tokens mean, 696.5 median, 1,018 p90, 1,262 maximum.
- Candidate K=10 contained complete evidence for 192/196 questions and reduced
  the two cold-pair sentinel cycles from 1,287/1,858 ms at K=20 to 661/1,162 ms.

## 2026-09-17 - Fresh-question statement audit complete

DONE
- Read and visually checked the relevant source-PDF pages, then authored six
  compositional questions that do not copy golden question text.
- Ran the production wrapper, split all Top-5 chunks into 306 atomic statements,
  and recorded explicit relevance and answer-support scores for every statement.
- Added reproducible retrieval and manual-scoring scripts plus an ignored raw
  JSON/Markdown evidence bundle.

OBSERVED
- Five questions were completely answerable from rank 1; all six were complete
  by rank 2. One multi-page table row was fragmented across adjacent chunks.
- The small set used 223/364/489/740 mean tokens through ranks 1/2/3/5 and
  contained 21 direct, 82 topical, and 203 unrelated statements at Top-5.
- Keep Top-5 for benchmark completeness, but make table-row preservation and
  context pruning explicit work for the context-assembly gate.

## 2026-09-28 - Source modules grouped by responsibility

DONE
- Moved parser implementations into `parsing/` beside their shared domain types.
- Grouped the retrieval sweep under `experiments/` and retained its package
  import and `python -m` entry points.
- Renamed shared typed configuration from `baseline_config.py` to
  `configuration.py` and updated implementation imports.
- Removed forwarding modules for retired flat imports; updated test imports and
  active operational commands to use subsystem packages.
- Updated architecture and parser subsystem references to match the code layout.

VERIFICATION
- Static import and command references were updated to the owning package paths.
- The automated suite was not run during this cleanup.

## 2026-09-29 - Retrieval experiments separated from runtime configs

DONE
- Moved the dedicated retrieval experiment definitions and frozen records from
  `configs/retrieval/experiments/` into `experiments/retrieval/`, pairing each
  study configuration with its results record.
- Kept pipeline-specific configurations and reports together in
  `configs/pipelines/`; runtime retrieval and dataset configurations remain in
  `configs/`.
- Updated sweep defaults, active operational instructions, indexes, and
  project-level ownership documentation.

VERIFICATION
- Checked active path references and reviewed the staged diff for whitespace and
  stale paths. The automated suite was not run during this documentation/layout
  change.

## 2026-09-29 - Experiment evidence and project learning connected

GOAL
- Make authored studies, experiment implementation, generated evidence, and
  project-level interpretation distinguishable and traceable.

COMPLETED
- Renamed authored retrieval study records to `studies/retrieval/` and the
  normalized generated store to `output/retrieval/experiment_store/`.
- Updated active config, code defaults, tests, schema docs, runbooks, and indexes;
  left the code package `src/testrx_retriever/experiments/` and pipeline run
  output naming intact because their responsibilities are distinct.
- Added Git code-revision provenance to experiment/run records and bumped their
  output record schemas; generated records are refreshed after the source
  change is committed so the recorded revision identifies the producing code.
- Added `docs/research-synthesis.md` to explain the lexical-baseline question,
  paraphrase-based dataset extension, later model/chunking comparisons, resulting
  default, and current limitations with links to detailed evidence.
- Updated the reusable lifecycle skill to require an explicit evidence-to-
  interpretation-to-decision-to-implementation-to-next-gate trace.

OBSERVATION
- Relevant findings already existed in study records, historical review, and
  dated progress/decision entries; the missing part was a navigable, current
  cross-study synthesis. The 64 controlled paraphrases were appended to the 132
  original grounded questions; the six later smoke-test questions remain
  separate from the scored benchmark.

VERIFICATION
- All 61 project tests passed, including experiment-store reproducibility and
  pipeline integration coverage.
- Markdown links resolved; active path checks found obsolete paths only in
  preserved historical reviews and append-only records. The generated store is
  refreshed after committing the producing implementation revision.

## 2026-09-29 - Experiment records refreshed with source revision

DONE
- Re-ran the 29-run chunk/dimension sweep and the one-run controlled paraphrase
  study with the committed implementation after the store relocation.
- Recorded the producing Git revision on each experiment and run record; the
  compact question-level metrics still join through stable `run_id` values.

VERIFICATION
- Confirmed the store contains two experiments, 30 runs, and 4,024 question
  records, all experiment/run records tagged with commit
  `b2baed336ba128a442add2395fac0fa57ab61b1b`.
- Verified every checksum in the regenerated store manifest. The full 61-test
  suite passed on the source/documentation commit.
