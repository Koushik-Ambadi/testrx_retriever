"""Install pinned model-registry candidates into the local model store."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", action="append", default=[], help="Install only this registry ID; repeatable")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "300")
    try:
        from huggingface_hub import snapshot_download
    except ImportError as error:
        raise SystemExit("Install the project's transformers optional dependencies first") from error
    selected = set(args.model)
    installed = 0
    for role in ("encoders", "rerankers"):
        registry_path = root / "model_store" / role / "model_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        for model in registry["models"]:
            if not model.get("artifact_required") or (selected and model["id"] not in selected):
                continue
            destination = root / model["artifact_path"]
            snapshot_download(
                repo_id=model["repository"], revision=model["revision"],
                local_dir=destination,
                allow_patterns=[
                    "*.json", "*.txt", "*.model", "*.safetensors",
                    "1_Pooling/*",
                ],
                max_workers=1,
            )
            print(f"Installed {model['id']} -> {destination}")
            installed += 1
    if selected and installed != len(selected):
        raise SystemExit(f"Unknown or non-installable model IDs: {sorted(selected)}")
    print(f"Installed {installed} pinned model candidate(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
