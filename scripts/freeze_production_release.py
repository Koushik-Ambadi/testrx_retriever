"""Create the dev-authoritative lock copied into the standalone TESTRX repo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tomllib

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.append(str(ROOT / "production" / "src"))

from testrx_prod.config import collection_contract  # noqa: E402
from testrx_prod.integrity import (  # noqa: E402
    add_check, canonical_sha256, component_files, config_sha256,
    production_runtime_files, runtime_versions, sha256_file, tree_manifest,
    vectors_sha256,
)
from testrx_retriever import __version__  # noqa: E402
from testrx_retriever.configuration import ChunkingConfig  # noqa: E402
from testrx_retriever.parsing.parser import parse_manual  # noqa: E402
from testrx_retriever.retrieval.hierarchical_chunking import build_chunker  # noqa: E402
from testrx_retriever.retrieval.tokenization import RegexTokenizer  # noqa: E402
from testrx_retriever.retrieval.encoders.sentence_transformer import SentenceTransformerBiEncoder  # noqa: E402


def fail_if(checks: list[dict]) -> None:
    failures = [item for item in checks if item["status"] == "FAIL"]
    if failures:
        for item in checks:
            print(f"{item['status']}: {item['name']} expected={item['expected']} actual={item['actual']}")
        raise SystemExit(f"Release lock not written: {len(failures)} integrity check(s) failed")


def _pinned_dependencies(path: Path) -> dict[str, str]:
    dependencies = (
        tomllib.loads(path.read_text(encoding="utf-8"))["project"]["dependencies"]
        if path.suffix == ".toml" else path.read_text(encoding="utf-8").splitlines()
    )
    pins: dict[str, str] = {}
    for dependency in dependencies:
        match = re.match(r"\s*([A-Za-z0-9_.-]+)==([^\s;]+)", dependency)
        if match:
            normalized = re.sub(r"[-_.]+", "", match.group(1)).lower()
            pins[normalized] = match.group(2)
    return pins


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Verify dev, production code, and both committed locks without writing")
    args = parser.parse_args()
    dev_config_path = ROOT / "configs/retrieval/production.json"
    pdf = ROOT / "source/TESTRX_User_Manual.pdf"
    existing_document = ROOT / "output/parsing/document.json"
    prod_config_path = ROOT / "production/config.yaml"
    dev_config = json.loads(dev_config_path.read_text(encoding="utf-8"))
    prod_config = yaml.safe_load(prod_config_path.read_text(encoding="utf-8"))
    checks: list[dict] = []

    pdf_sha = sha256_file(pdf)
    add_check(checks, "source PDF checksum", prod_config["source"]["sha256"], pdf_sha)
    add_check(checks, "frozen chunking settings", {
        key: dev_config["chunking"][key] for key in ("strategy", "max_tokens")
    }, {key: prod_config["chunking"][key] for key in ("strategy", "max_tokens")})
    tokenizer = RegexTokenizer()
    add_check(checks, "tokenizer identity", tokenizer.name, prod_config["chunking"]["tokenizer"])
    add_check(checks, "tokenizer version", tokenizer.version,
              prod_config["chunking"]["tokenizer_version"])
    expected_ks = {
        "candidate_k": dev_config["retrieval"]["candidate_k"], "top_k": 5,
    }
    actual_ks = {key: prod_config["retrieval"][key] for key in expected_ks}
    add_check(checks, "candidate/final K", expected_ks, actual_ks)
    for role, dev_key, prod_key in (
        ("bi-encoder", "encoder", "bi_encoder"),
        ("cross-encoder", "reranker", "cross_encoder"),
    ):
        dev_model, prod_model = dev_config[dev_key], prod_config["models"][prod_key]
        for field in ("id", "revision", "batch_size"):
            add_check(checks, f"{role} {field}", dev_model[field], prod_model[field])
        expected_algorithm = ("sentence_transformer" if role == "bi-encoder"
                              else "sentence_transformer_cross_encoder")
        add_check(checks, f"{role} algorithm", dev_model["algorithm"], expected_algorithm)
        add_check(checks, f"{role} frozen implementation", expected_algorithm, prod_model["algorithm"])
    add_check(checks, "bi-encoder query prefix", "", prod_config["models"]["bi_encoder"]["query_prefix"])
    add_check(checks, "bi-encoder document prefix", "", prod_config["models"]["bi_encoder"]["document_prefix"])
    add_check(checks, "embedding normalization", True, prod_config["models"]["bi_encoder"]["normalize_embeddings"])
    dev_pipeline = json.loads((ROOT / "configs/pipelines/production_evaluation.json").read_text(encoding="utf-8"))
    add_check(checks, "frozen chunk policy also matches evaluation", dev_pipeline["chunking"],
              {key: prod_config["chunking"][key] for key in dev_pipeline["chunking"]})
    add_check(checks, "frozen candidate K also matches evaluation", dev_pipeline["retrieval"]["candidate_k"],
              prod_config["retrieval"]["candidate_k"])
    add_check(checks, "frozen final K included by evaluation", True,
              prod_config["retrieval"]["top_k"] in dev_pipeline["evaluation"]["top_k"])
    add_check(checks, "frozen parser implementation", "native_pdf", prod_config["parser"]["implementation"])
    add_check(checks, "parser schema version", "1.0", prod_config["parser"]["document_schema_version"])
    add_check(checks, "document encoder normalization", True,
              prod_config["models"]["bi_encoder"]["normalize_embeddings"])
    encoder_model_config = ROOT / dev_config["encoder"]["model_path"] / "config.json"
    model_dimension = json.loads(encoder_model_config.read_text(encoding="utf-8"))["hidden_size"]
    add_check(checks, "bi-encoder model vector dimension", model_dimension,
              prod_config["models"]["bi_encoder"]["dimension"])

    source_code = component_files(ROOT / "src/testrx_retriever")
    production_code = component_files(ROOT / "production/src/testrx_retriever")
    add_check(checks, "parser/chunker code parity", source_code, production_code)
    runtime_code = production_runtime_files(ROOT / "production")
    versions = runtime_versions()
    add_check(checks, "Python major/minor", "3.13", versions["python_minor"])
    requirements_pins = _pinned_dependencies(ROOT / "production/requirements.txt")
    project_pins = _pinned_dependencies(ROOT / "production/pyproject.toml")
    for package, expected in versions["packages"].items():
        normalized = re.sub(r"[-_.]+", "", package).lower()
        add_check(checks, f"requirements pin {package}", expected, requirements_pins.get(normalized))
        add_check(checks, f"pyproject pin {package}", expected, project_pins.get(normalized))
    for package, expected in prod_config["runtime"]["application_packages"].items():
        normalized = re.sub(r"[-_.]+", "", package).lower()
        add_check(checks, f"requirements pin {package}", expected, requirements_pins.get(normalized))
        add_check(checks, f"pyproject pin {package}", expected, project_pins.get(normalized))

    document = parse_manual(pdf)
    document_dict = document.to_dict()
    document_sha = canonical_sha256(document_dict)
    stored_dict = json.loads(existing_document.read_text(encoding="utf-8"))
    stored_sha = canonical_sha256(stored_dict)
    add_check(checks, "canonical parse matches dev artifact", stored_sha, document_sha)
    add_check(checks, "parser version", prod_config["parser"]["version"], document.parser_version)
    add_check(checks, "document schema", prod_config["parser"]["document_schema_version"], document.schema_version)

    chunking = prod_config["chunking"]
    chunks = build_chunker(ChunkingConfig(
        strategy=chunking["strategy"], max_tokens=chunking["max_tokens"]
    ), RegexTokenizer()).chunk_document(document_dict)
    chunks_sha = canonical_sha256([chunk.to_dict() for chunk in chunks])
    model_records = {}
    for config_key, role in (("encoder", "bi_encoder"), ("reranker", "cross_encoder")):
        spec = prod_config["models"][role]
        model_root = ROOT / dev_config[config_key]["model_path"]
        model_records[role] = {
            "id": spec["id"], "revision": spec["revision"],
            "dimension": spec.get("dimension"),
            "artifact": tree_manifest(model_root),
        }

    dev_encoder_spec = dict(dev_config["encoder"])
    dev_encoder_spec["model_path"] = str(ROOT / dev_encoder_spec["model_path"])
    dev_encoder_spec["device"] = "cpu"
    encoder = SentenceTransformerBiEncoder(dev_encoder_spec)
    document_vectors = encoder.encode_documents([chunk.text for chunk in chunks])
    vector_hash = vectors_sha256(document_vectors)
    add_check(checks, "development document embedding shape",
              (len(chunks), prod_config["models"]["bi_encoder"]["dimension"]),
              tuple(document_vectors.shape))

    if prod_config["config_id"] != "testrx-manual-h384-bge-minilm-v1":
        add_check(checks, "config identity", "testrx-manual-h384-bge-minilm-v1", prod_config["config_id"])
    fail_if(checks)

    lock = {
        "schema_version": "1.0",
        "config_id": prod_config["config_id"],
        "index_release_id": prod_config["index_release_id"],
        "source": {"path": "TESTRX_User_Manual.pdf", "sha256": pdf_sha},
        "development_config_sha256": canonical_sha256(dev_config),
        "development_evaluation_config_sha256": canonical_sha256(dev_pipeline),
        "production_config_sha256": config_sha256(prod_config),
        "contract": collection_contract(prod_config),
        "production_runtime_code_files": runtime_code,
        "application_packages": prod_config["runtime"]["application_packages"],
        "parser": {
            "implementation": prod_config["parser"],
            "code_files": {name: digest for name, digest in source_code.items()
                           if name == "__init__.py" or name == "configuration.py" or name.startswith("parsing/")},
            "canonical_document_sha256": document_sha,
        },
        "chunking": {
            "config": prod_config["chunking"],
            "code_files": {name: digest for name, digest in source_code.items()
                           if name.startswith("retrieval/")},
            "chunk_count": len(chunks),
            "ordered_chunks_sha256": chunks_sha,
            "document_vectors_sha256": vector_hash,
        },
        "models": model_records,
        "runtime": versions,
    }
    lock_text = json.dumps(lock, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    lock_sha = canonical_sha256(lock)
    config_text = prod_config_path.read_text(encoding="utf-8")
    embedded_match = re.search(r"(?m)^\s*expected_lock_sha256:\s*(\S+)\s*$", config_text)
    if args.check:
        add_check(checks, "production config references the current lock", lock_sha,
                  embedded_match.group(1) if embedded_match else None)
        for target in (ROOT / "configs/retrieval/production.lock.json", ROOT / "production/release-lock.json"):
            actual = canonical_sha256(json.loads(target.read_text(encoding="utf-8"))) if target.is_file() else None
            add_check(checks, f"committed lock matches current dev inputs ({target.relative_to(ROOT)})",
                      lock_sha, actual)
        fail_if(checks)
        for item in checks:
            print(f"{item['status']}: {item['name']}")
        print(f"VERIFIED: {prod_config['index_release_id']} sha256={lock_sha}")
        return 0
    updated, count = re.subn(
        r"(?m)^(\s*expected_lock_sha256:\s*)\S+\s*$",
        rf"\g<1>{lock_sha}", config_text, count=1,
    )
    if count != 1:
        raise SystemExit("Could not update integrity.expected_lock_sha256 in production/config.yaml")

    lock_targets = [ROOT / "configs/retrieval/production.lock.json", ROOT / "production/release-lock.json"]
    prod_config_path.write_text(updated, encoding="utf-8")
    for target in lock_targets:
        target.write_text(lock_text, encoding="utf-8")
    for item in checks:
        print(f"{item['status']}: {item['name']}")
    print(f"LOCKED: {prod_config['index_release_id']} sha256={lock_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
