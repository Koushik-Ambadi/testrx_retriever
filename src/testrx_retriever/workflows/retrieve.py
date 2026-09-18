"""Command-line entry point for the configurable retrieval application."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..application import RetrievalApplication


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieve grounded TESTRX chunks for one query")
    parser.add_argument("query", help="Natural-language retrieval query")
    parser.add_argument(
        "--config", type=Path, default=Path("configs/retrieval/production.json"),
    )
    parser.add_argument("--candidate-k", type=int, default=None)
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()
    application = RetrievalApplication.from_config(args.config)
    response = application.retrieve(
        args.query, candidate_k=args.candidate_k, top_k=args.top_k,
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

