"""`cold_run.py --begin` records what was already dirty (roadmap 77).

Anchored; asserts each target exactly once and refuses to write on a miss.
Run from the factory root:  python patches\\patch_cold_run_dirty.py
"""
import io
import sys

P = "tools/cold_run.py"


def main() -> int:
    t = io.open(P, encoding="utf-8", newline="").read()
    if "def dirty(" in t:
        print("already applied")
        return 0
    edits = []

    edits.append((
        "import sys\nfrom pathlib import Path\n",
        "import subprocess\nimport sys\nfrom pathlib import Path\n"))

    edits.append((
        "def _diff(before: dict, after: dict) -> dict:",
        '''def dirty(root: Path | None = None) -> dict:
    """Tracked files already modified in each tool repo, or None if unreadable.

    Roadmap 77. `--begin` hashed 2357 files and had no idea whether any of
    them were mid-change; on `cold_7003` a tool file moved six minutes into
    the run and 55 seconds before the first job wrote output, and afterwards an
    edit made to RESCUE the run and an edit that was simply still landing when
    `--begin` fired were indistinguishable. That run carries a 1 that may or
    may not describe a defect, and nothing on disk can say which.

    This is not "refuse if dirty". The repos are routinely dirty by design --
    the pipeline writes DC specs into `deli_counter/specs/`. It is "say what
    was dirty", so a file that changes during the run and was ALREADY modified
    at `--begin` is read as an edit in flight rather than as an intervention.

    Untracked files are deliberately excluded: a new workspace, a scratch
    file, a report -- none of those is a source edit, and `snapshot` already
    catches a new hand-authored file as an addition. None (not []) means the
    question could not be asked: no git, not a repository, or git failed.
    """
    root = root or _root()
    out: dict = {}
    for tool in TOOLS:
        base = root / tool
        if not (base / ".git").exists():
            out[tool] = None
            continue
        try:
            res = subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=no"],
                cwd=str(base), capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            out[tool] = None
            continue
        if res.returncode != 0:
            out[tool] = None
            continue
        paths = []
        for line in res.stdout.splitlines():
            if len(line) > 3:
                # `XY path` or `XY old -> new`; the path after the arrow is
                # the one that exists now.
                p = line[3:].split(" -> ")[-1].strip().strip('"')
                paths.append((tool + "/" + p).replace("\\\\", "/"))
        out[tool] = sorted(paths)
    return out


def _diff(before: dict, after: dict) -> dict:'''))

    edits.append((
        '''    snap = snapshot()
    before.write_text(json.dumps(snap, indent=1, sort_keys=True), encoding="utf-8")
''',
        '''    snap = snapshot()
    snap["dirty"] = dirty()
    before.write_text(json.dumps(snap, indent=1, sort_keys=True), encoding="utf-8")
'''))

    edits.append((
        '''    for t, v in sorted(snap["versions"].items()):
        print(f"    {t:<16}{v}")
    print(f"  journal: {journal}")
    return 0
''',
        '''    for t, v in sorted(snap["versions"].items()):
        print(f"    {t:<16}{v}")
    # SAY WHAT WAS ALREADY DIRTY (roadmap 77). Printed, not refused: the repos
    # are dirty by design when the pipeline has written into them, and a run
    # that starts on a dirty tree is fine as long as the diff can be read.
    already = {t: p for t, p in (snap.get("dirty") or {}).items() if p}
    unreadable = [t for t, p in (snap.get("dirty") or {}).items() if p is None]
    if already:
        n = sum(len(p) for p in already.values())
        print(f"  {n} tracked file(s) ALREADY MODIFIED at --begin -- a later change")
        print(f"  to one of these is an edit in flight, not an intervention:")
        for t, paths in sorted(already.items()):
            for p in paths[:10]:
                print(f"    {p}")
            if len(paths) > 10:
                print(f"    ... and {len(paths)-10} more in {t} (see before.json)")
    else:
        print(f"  every tool repo clean at --begin")
    if unreadable:
        print(f"  dirty state UNREADABLE for: {', '.join(unreadable)} "
              f"(no git, or not a repository)")
    print(f"  journal: {journal}")
    return 0
'''))

    edits.append((
        '''    print(f"    UNATTRIBUTED, counted                     {len(unattributed)}")
    for f in unattributed[:20]:
        print(f"      {f}")
''',
        '''    print(f"    UNATTRIBUTED, counted                     {len(unattributed)}")
    was_dirty = set()
    for paths in (before.get("dirty") or {}).values():
        was_dirty.update(paths or [])
    diff["already_modified_at_begin"] = sorted(f for f in touched if f in was_dirty)
    for f in unattributed[:20]:
        flag = "   (was ALREADY modified at --begin)" if f in was_dirty else ""
        print(f"      {f}{flag}")
'''))

    edits.append((
        "    # ---- attribution (roadmap 70) -----------------------------------------",
        '''    # ---- dirty state at --begin (roadmap 77) -------------------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "factory.manifest.json").write_text("{}", encoding="utf-8")
        (root / "lot").mkdir()
        (root / "zoo").mkdir()                       # no .git: unreadable
        try:
            def git(*args):
                return subprocess.run(["git", *args], cwd=str(root / "lot"),
                                      capture_output=True, text=True, check=True)
            git("init", "-q")
            git("config", "user.email", "t@t")
            git("config", "user.name", "t")
            (root / "lot" / "main.py").write_text("x = 1\\n", encoding="utf-8")
            git("add", "main.py")
            git("commit", "-q", "-m", "one")
            clean = dirty(root)
            if clean.get("lot") != []:
                fails.append(f"a clean repo should report [], got {clean.get('lot')!r}")
            if clean.get("zoo") is not None:
                fails.append(f"a non-repo should report None, got {clean.get('zoo')!r}")
            (root / "lot" / "main.py").write_text("x = 2\\n", encoding="utf-8")
            (root / "lot" / "scratch.txt").write_text("", encoding="utf-8")
            d = dirty(root)
            if d.get("lot") != ["lot/main.py"]:
                fails.append(f"modified tracked file not reported: {d.get('lot')!r}")
            # the untracked scratch file must NOT appear: it is not a source
            # edit, and snapshot() already catches additions
            if any("scratch" in p for p in (d.get("lot") or [])):
                fails.append("untracked file reported as dirty")
        except (OSError, subprocess.SubprocessError) as exc:
            fails.append(f"dirty() selftest could not run git: {exc}")

    # ---- attribution (roadmap 70) -----------------------------------------'''))

    for old, new in edits:
        n = t.count(old)
        if n != 1:
            print(f"ANCHOR MISS ({n}): {old[:60]!r}", file=sys.stderr)
            return 1
        t = t.replace(old, new, 1)
    io.open(P, "w", encoding="utf-8", newline="").write(t)
    print("applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
