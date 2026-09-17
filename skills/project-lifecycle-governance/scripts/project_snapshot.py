#!/usr/bin/env python3
"""Emit a read-only JSON snapshot of a project's structure and Git state."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_EXCLUDES = {
    ".git", ".idea", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".venv", ".vscode", "__pycache__", "build", "dist", "node_modules", "venv",
}


def run_git(root: Path, *args: str) -> dict[str, Any]:
    command = ["git", "-C", str(root), *args]
    try:
        result = subprocess.run(
            command, capture_output=True, check=False, text=True, timeout=15
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        return {"ok": False, "error": type(error).__name__}
    if result.returncode != 0:
        return {"ok": False, "error": result.stderr.strip() or result.stdout.strip()}
    return {"ok": True, "value": result.stdout.strip()}


def git_value(root: Path, *args: str) -> str | None:
    result = run_git(root, *args)
    return result.get("value") if result.get("ok") else None


def scan_files(root: Path, excluded: set[str]) -> tuple[list[dict[str, Any]], Counter[str]]:
    files: list[dict[str, Any]] = []
    extensions: Counter[str] = Counter()
    for current, directories, names in os.walk(root):
        directories[:] = sorted(name for name in directories if name not in excluded)
        current_path = Path(current)
        for name in sorted(names):
            path = current_path / name
            try:
                size = path.stat().st_size
            except OSError:
                continue
            relative = path.relative_to(root).as_posix()
            extensions[path.suffix.lower() or "[no-extension]"] += 1
            files.append({"path": relative, "bytes": size})
    return files, extensions


def classify_paths(files: list[dict[str, Any]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {
        "documentation": [], "tests": [], "configuration": [], "skills": []
    }
    config_names = {
        ".editorconfig", ".gitignore", "dockerfile", "makefile", "package.json",
        "pyproject.toml", "requirements.txt",
    }
    for item in files:
        path = item["path"]
        parts = path.lower().split("/")
        name = parts[-1]
        if name.endswith((".md", ".mdx", ".rst")) or "docs" in parts:
            groups["documentation"].append(path)
        if "test" in parts or "tests" in parts or name.startswith("test_") or name.endswith("_test.py"):
            groups["tests"].append(path)
        if name in config_names or name.endswith((".toml", ".yaml", ".yml", ".ini")):
            groups["configuration"].append(path)
        if "skills" in parts or name == "skill.md":
            groups["skills"].append(path)
    return groups


def build_snapshot(root: Path, largest_count: int, excluded: set[str]) -> dict[str, Any]:
    files, extensions = scan_files(root, excluded)
    largest = sorted(files, key=lambda item: (-item["bytes"], item["path"]))[:largest_count]
    top_level = Counter(item["path"].split("/", 1)[0] for item in files)
    is_repository = git_value(root, "rev-parse", "--is-inside-work-tree") == "true"
    git: dict[str, Any] = {"is_repository": is_repository}
    if is_repository:
        git.update({
            "branch": git_value(root, "branch", "--show-current"),
            "status_porcelain": (git_value(root, "status", "--short") or "").splitlines(),
            "upstream": git_value(root, "rev-parse", "--abbrev-ref", "@{upstream}"),
            "branches": (git_value(root, "branch", "--format=%(refname:short)") or "").splitlines(),
            "remotes": (git_value(root, "remote", "-v") or "").splitlines(),
            "identity": {
                "name": git_value(root, "config", "user.name"),
                "email": git_value(root, "config", "user.email"),
            },
            "recent_commits": (
                git_value(root, "log", "-10", "--pretty=format:%h %ad %an <%ae> %s", "--date=short") or ""
            ).splitlines(),
        })
    return {
        "root": str(root),
        "excluded_directory_names": sorted(excluded),
        "git": git,
        "inventory": {
            "file_count": len(files),
            "total_bytes": sum(item["bytes"] for item in files),
            "files_by_extension": dict(sorted(extensions.items())),
            "files_by_top_level_entry": dict(sorted(top_level.items())),
            "largest_files": largest,
        },
        "relevant_paths": classify_paths(files),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="project root")
    parser.add_argument("--largest", type=int, default=20, help="largest files to list")
    parser.add_argument(
        "--exclude", action="append", default=[], metavar="DIR_NAME",
        help="additional directory name to exclude; may be repeated",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"project root is not a directory: {root}")
    if args.largest < 0:
        raise SystemExit("--largest must be non-negative")
    snapshot = build_snapshot(root, args.largest, DEFAULT_EXCLUDES | set(args.exclude))
    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
