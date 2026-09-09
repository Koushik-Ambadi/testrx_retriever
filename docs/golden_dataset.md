# Golden Dataset Strategy

## Purpose

The seed is a retrieval benchmark with answer evidence, not a simple
question-answer list. It is designed to distinguish failures in chunking,
retrieval, reranking, context construction, and generation.

## Authority and lineage

The approved PDF is the factual source of truth. `output/document.json` provides
stable hierarchy, semantic element IDs, page ranges, and structure. Required
units are also checked against independently extracted text from the PDF pages.

## Semantic-unit policy

- A definition includes the term and its defining text.
- A procedure includes context, prerequisites, all required steps, conditions,
  and result when the complete operation is requested.
- A table includes caption/context, headings, relevant rows, and resolved merged
  context.
- A configuration unit includes the concept, settings, constraints, and examples.
- Multi-section and cross-reference questions list every required source unit.
- A numbered step is not independent when the full procedure is required.

## Retrieval contract

Each question records a primary source, complete required source set, acceptable
source set, optional hard negatives, expected answer, required and supporting
evidence, and flags for structural retrieval demands. Expected answer wording is
separate from evidence so retrieval can be evaluated independently of generation.

## Seed distribution

The committed seed contains 132 questions. It balances direct lookups with
procedures, tables, comparisons, configuration, troubleshooting, multi-section
assembly, and cross-reference following. Large chapters do not receive questions
merely in proportion to length.

## Quality controls

- All metadata IDs must resolve.
- Required sources must be a subset of acceptable sources.
- Single/multiple-unit flags must agree with the required set.
- JSONL and CSV must have identical order and row count.
- Every required unit must retain PDF page evidence.
- Exact duplicate questions fail review.
- Known parser warnings and uncertain manual wording remain visible.

## Evaluation lifecycle

Use the same committed dataset for initial chunking and retrieval comparisons.
Report Recall@K for required source sets, MRR for primary sources, and nDCG when
graded acceptable sources are introduced. Do not tune questions to favor a
chosen chunker.

After failure analysis, add a versioned wave for procedure fragmentation, missing
parent context, tables, and multi-section assembly. Preserve seed IDs and record
semantic changes in decisions and progress.
