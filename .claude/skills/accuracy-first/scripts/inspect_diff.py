#!/usr/bin/env python3
"""Read-only Git diff hygiene inspector. Does not validate functional correctness."""
from __future__ import annotations
import argparse
import subprocess
import sys


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def run_check(label: str, *args: str) -> bool:
    p = git(*args)
    if p.returncode == 0:
        print(f"PASS: {label} (only Git diff hygiene)")
        return True
    print(f"FAIL: {label} (exit={p.returncode})")
    print((p.stdout + p.stderr).strip() or "No details")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Optional trusted base ref for reviewing committed changes")
    args = parser.parse_args()
    inside = git("rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        print("ERROR: run inside a Git worktree", file=sys.stderr)
        return 2
    print("== Working tree changes (read-only) ==")
    status = git("status", "--short")
    if status.returncode:
        print(status.stderr.strip(), file=sys.stderr)
        return 2
    print(status.stdout.rstrip() or "(clean)")
    print("== Diff summary ==")
    for label, argv in (
        ("unstaged", ("diff", "--stat")),
        ("staged", ("diff", "--cached", "--stat")),
    ):
        p = git(*argv)
        print(f"{label}:\n{p.stdout.rstrip() or '(none)'}")
    print("== Whitespace and patch consistency ==")
    ok = run_check("unstaged diff", "diff", "--check")
    ok = run_check("staged diff", "diff", "--cached", "--check") and ok
    if args.base:
        ok = run_check(f"commits since {args.base}", "diff", "--check", f"{args.base}...HEAD") and ok
    print("IMPORTANT: untracked files are listed but not validated by git diff --check.")
    print("IMPORTANT: PASS here is NOT a proof of compilation, tests, safety, or correctness.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
