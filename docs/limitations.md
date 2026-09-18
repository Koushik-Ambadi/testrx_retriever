# Known limitations and deferred work

Status: living  
Owner: project architecture  
Last reviewed: 2026-09-17  
Source of truth for: limitations that remain true across the current project

Detailed threats to validity for a fixed experiment belong in that experiment's
record. Resolved limitations remain in `progress.md`, dated reviews, and the
decision log rather than this living list.

## Source and parsing

- The parser is tuned and validated for the supplied TESTRX manual; it is not a
  general PDF parser.
- Screenshot pixels are not OCRed or visually interpreted. Captions and source
  regions are preserved.
- The cover and table-of-contents page ranges, footer rules, and numbered-heading
  heuristics contain document-specific assumptions.
- Multi-column reading order, borderless tables, unnumbered hierarchy, PDF tags,
  links, annotations, colors, style flags, and exact cell geometry are not part
  of the canonical contract.
- Table reconstruction depends on ruled geometry and explicit continuation
  evidence. Ambiguous content is preserved with warnings rather than invented.
- Conservative normalization may retain awkward source punctuation to avoid
  corrupting identifiers.

## Benchmark

- The benchmark contains answerable questions from one manual and no deliberate
  unanswerable, adversarial, or unseen-document population.
- Sixteen controlled paraphrase families are diagnostic, not a statistically
  broad sample of natural language variation.
- Paraphrases were manually controlled rather than independently authored or
  blinded, and cloned families retain the same required/acceptable lineage.
- Hard negatives exist only where a naturally confusing neighboring concept was
  identified; they are not exhaustive.
- Figure questions depend on captions and surrounding prose, not screenshot
  interpretation.
- A small number of independently extracted PDF lineage matches and one source
  explanation remain explicit manual-review candidates in the generated QC
  report.

## Retrieval and evaluation

- The frozen retriever was selected from one manual's diagnostic benchmark. A
  family-grouped robustness view did not reverse the decision, but no external
  manual or prospective query population has validated generalization.
- Lineage relevance does not prove that one chunk contains the complete required
  text span or enough focused context for generation.
- Recall@K is strict for multi-unit questions while MRR rewards the first partial
  evidence hit; both must be interpreted together with evidence coverage.
- Fixed K exposes different fractions of differently sized indexes. Index
  exposure and evidence completeness must accompany cross-chunker comparisons.
- Pairwise reranking optimizes individual chunks and can reduce multi-chunk
  evidence diversity or completeness.
- Exact in-memory NumPy retrieval is appropriate for this corpus, not evidence of
  production scalability.
- Current latency captures exclude model loading, chunking, and index building;
  reranked hierarchy runs use explicit sentinel questions rather than a full
  production latency distribution. Fresh local wrapper startup measured about
  20 seconds, so process reuse is required.
- The system evaluates retrieval only. It has no context-assembly, answer
  generation, grounded-answer, or end-user outcome evaluation.

## Deliberately deferred

- Table-level versus row-level retrieval representation.
- Parent-context injection and generation-oriented token budgets.
- Held-out model/chunk-policy selection and multi-chunk evidence assembly.
- Alternative large-scale indexes, query rewriting, and multi-query retrieval.
- Answer generation and generator-facing evaluation.
- Screenshot understanding unless future questions require pixel-level evidence.
