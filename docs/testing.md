# Testing strategy

Status: living  
Owner: software quality  
Created: 2026-09-17  
Last reviewed: 2026-09-17  
Source of truth for: test levels, commands, dependencies, and extension rules

## Test levels

- Unit tests exercise deterministic parsing rules, tokenization, chunking,
  scoring, metrics, configuration validation, and component factories with
  small in-memory inputs.
- Integration tests execute parser, reference-run, experiment, and configurable
  retrieval workflows against repository fixtures and temporary output folders.
- Contract tests verify stable schemas, IDs, hashes, manifests, import isolation,
  and reproducibility requirements.
- Model-backed tests require the optional transformer dependency and explicitly
  installed local artifacts. They must not download models implicitly.

The current suite is stored in `tests/`. Test files are organized by behavior,
not one-to-one with production modules. A separate Markdown file per test or
module is unnecessary; names, fixtures, docstrings, and assertions should make
local intent clear.

## Commands

Install the declared runtime dependencies and run the complete standard-library
suite from the repository root:

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
```

Install optional model support only for model-backed workflows:

```powershell
python -m pip install -e ".[transformers]"
python scripts/install_model_candidates.py
python -m unittest discover -s tests -v
```

Validate the generated benchmark review view when Node.js is available:

```powershell
node scripts/verify_golden_csv.mjs
```

## Isolation and determinism

- Importing retrieval, evaluation, or configuration modules must not load the
  PDF parser or `pdfplumber`; `test_import_isolation.py` protects this boundary.
- Tests must write to temporary directories, never overwrite durable reference
  evidence unless regeneration is the explicit task.
- No test may require network access or an implicit model download.
- Stable inputs and configuration must produce stable IDs, ordering, JSON/JSONL,
  checksums, and metrics.
- Floating-point comparisons must use deliberate tolerances while deterministic
  rank tie-breaking remains exact.

## Adding behavior

For a new parser rule, add a focused rule test and an integration regression if
the canonical output changes. For a new chunker, encoder, retriever, fusion
method, or reranker, test configuration rejection, deterministic identity,
empty/invalid inputs, ranking behavior, metadata, and workflow integration. For
an artifact change, update the adjacent schema and add a contract test in the
same change.

Slow external-model comparisons belong in explicit workflows and generated
reports. Keep the default suite fast, local, and reproducible.
