#!/usr/bin/env python3
"""Minimal CNC program collector.

Walks a read-only mounted machine share, copies new/changed files into a
per-machine Git working tree and commits them. Never writes to the source.

Usage:
    python3 collect.py machines.yaml
"""
import hashlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml  # pip install pyyaml

MAX_BYTES = 10 * 1024 * 1024


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args],
                          check=True, capture_output=True, text=True).stdout


def ensure_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    if not (repo / ".git").exists():
        git(repo, "init", "-q")


def collect_machine(name: str, source: Path, repo: Path, patterns: list[str]) -> int:
    if not source.is_dir():
        print(f"[{name}] unreachable: {source}")
        return 0
    ensure_repo(repo)
    changed = 0
    for pattern in patterns:
        for src in source.rglob(pattern):
            if not src.is_file():
                continue
            if src.stat().st_size > MAX_BYTES:
                print(f"[{name}] skipped (too large): {src}")
                continue
            dst = repo / src.relative_to(source)
            if dst.exists() and sha256(dst) == sha256(src):
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            changed += 1
    if changed:
        git(repo, "add", "-A")
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        git(repo, "-c", "user.name=cnc-collector", "-c", "user.email=cnc-collector@localhost",
            "commit", "-q", "-m", f"{name}: {changed} files changed (scan {stamp})")
    print(f"[{name}] {changed} changed")
    return changed


def main() -> None:
    cfg = yaml.safe_load(Path(sys.argv[1]).read_text())
    root = Path(cfg["repo_root"])
    for m in cfg["machines"]:
        name = str(m["name"])  # YAML may parse names like "off" as booleans
        try:
            collect_machine(name, Path(m["mount"]), root / name, m.get("patterns", ["*"]))
        except Exception as exc:  # one failing machine must not stop the others
            print(f"[{name}] error: {exc}")


if __name__ == "__main__":
    main()
