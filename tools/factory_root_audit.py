#!/usr/bin/env python3
r"""What is actually at the factory root, and what git thinks of each thing.

    python factory_root_audit.py
    python factory_root_audit.py --sizes     (adds on-disk size; slower)

Run from the FACTORY ROOT. Read-only -- it opens nothing and moves nothing.

WHY ASK GIT INSTEAD OF READING .gitignore. `.gitignore` at this root has
grown to fourteen rules across five sections, some of them overlapping
(`shots_*/` appears twice), and several tool repos carry their own. Working
out whether `_scratch2/` is covered means simulating git's precedence rules
in your head, and the answer to "is this ignored" is one `git check-ignore`
away. So it asks.

Every root entry lands in exactly one bucket:

    TOOL REPO   its own git repo -- never committed here by design
    TRACKED     committed in this repo; it IS the factory's content
    IGNORED     git is told to skip it; safe to move or delete
    LOOSE       neither tracked nor ignored -- git would commit it if you
                ran `git add -A`, and nothing has decided that it should be

LOOSE is the interesting column. A file that is neither tracked nor ignored
is one `git add -A` away from being in the repo forever, and nobody chose
that.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def git(args: list[str], root: Path):
    try:
        return subprocess.run(["git", "-C", str(root)] + args,
                              capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None


def du(path: Path) -> int:
    if path.is_file():
        try:
            return path.stat().st_size
        except OSError:
            return 0
    total = 0
    for p in path.rglob("*"):
        try:
            if p.is_file():
                total += p.stat().st_size
        except OSError:
            pass
    return total


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:,.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return str(n)


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    sizes = "--sizes" in argv

    tracked = set()
    r = git(["ls-files"], root)
    if r and r.returncode == 0:
        for line in r.stdout.splitlines():
            tracked.add(line.split("/", 1)[0])

    entries = sorted(p.name for p in root.iterdir() if p.name != ".git")

    # One batched call rather than one per entry.
    ignored = set()
    r = git(["check-ignore", "--"] + entries, root)
    if r is not None and r.returncode in (0, 1):
        ignored = {line.strip().rstrip("/") for line in r.stdout.splitlines()
                   if line.strip()}

    rows = []
    for name in entries:
        p = root / name
        is_dir = p.is_dir()
        if is_dir and (p / ".git").exists():
            bucket = "TOOL REPO"
        elif name in ignored:
            bucket = "IGNORED"
        elif name in tracked:
            bucket = "TRACKED"
        else:
            bucket = "LOOSE"
        rows.append((bucket, name, is_dir, du(p) if sizes else None))

    order = {"TOOL REPO": 0, "TRACKED": 1, "IGNORED": 2, "LOOSE": 3}
    rows.sort(key=lambda x: (order[x[0]], not x[2], x[1].lower()))

    width = max(len(n) for _b, n, _d, _s in rows) + 2
    last = None
    counts: dict[str, int] = {}
    total_ignored = 0
    for bucket, name, is_dir, size in rows:
        counts[bucket] = counts.get(bucket, 0) + 1
        if bucket == "IGNORED" and size:
            total_ignored += size
        if bucket != last:
            print(f"\n{bucket}")
            last = bucket
        label = name + ("/" if is_dir else "")
        tail = f"  {human(size)}" if size is not None else ""
        print(f"  {label:<{width}}{tail}")

    print()
    for b in ("TOOL REPO", "TRACKED", "IGNORED", "LOOSE"):
        if counts.get(b):
            print(f"  {b:<10} {counts[b]:>3}")
    if sizes and total_ignored:
        print(f"\n  ignored content on disk: {human(total_ignored)} -- "
              f"regenerable, safe to clear")
    if counts.get("LOOSE"):
        print(f"\n  LOOSE means git has no opinion. `git add -A` would commit "
              f"these.\n  Decide each one: track it, ignore it, or move it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
