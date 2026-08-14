#!/usr/bin/env python3
r"""Take the 44 files git holds in four scratch folders and decide each one.

    python factory_untrack.py            # report only, changes nothing
    python factory_untrack.py --apply
    python factory_untrack.py --selftest

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

`factory_folders.py` refused `_bridge_fresh/`, `_scratch2/`, `_scratch_walkable/`
and `_send/` with the same sentence -- *git tracks it; that is content, not
scratch* -- because moving tracked files under an ignored path leaves them
tracked but invisible to anyone reading the ignore file. That refusal was
right and it was also a stopping point, not an answer. This is the answer.

NOTHING IS DELETED FROM DISK. Every removal here is `git rm --cached`, which
drops a file from the index and leaves the bytes where they are. If a call is
wrong, `git checkout HEAD -- <path>` puts it back, and the commit before this
one still has all 44.

FOUR GROUPS, FOUR DIFFERENT ARGUMENTS. Lumping them together as "scratch" is
what got them here.

  RESCUE      `_scratch2/pcdiag/art_standard_audit.py` is 19 KB of real tool.
              It measures the shipped material library against the Controlled
              Contrast Environment Art Standard -- Oklab chroma mean and p95,
              per grammar, synthesized rather than read off the stated
              palette. That is a check, and it has been sitting in a folder
              named after a mood where nothing would ever find it. It moves to
              `tools/` with `git mv`, so its history follows.

  DUPLICATE   `_send/PACKAGE_README.md` is byte-identical to
              `docs/PACKAGE_README.md`. `make_package.ps1` stages it into the
              zip; the copy in `docs/` is the one people edit. Untracked ONLY
              while the two still match -- if they have diverged, the one in
              `_send/` holds an edit nobody moved back, and this refuses.

  CACHE       `_scratch_walkable/relprobe/.godot/*` is Godot editor state:
              a filesystem cache, project metadata, a script class cache, a
              scene-folding file. Godot rewrites all of it on open. It never
              belonged in git.

  SUPERSEDED  `_bridge_fresh/*_v2.py` and `*_v3.py` are staging copies of code
              that has since landed in a tool repo. `check_all.py`'s own
              comment says what this kind of folder is -- "staging copies. A
              finding here points at a copy, and the next reader patches a
              file that is not the file."

THE SUPERSEDED GROUP IS THE ONE THAT COULD LOSE WORK, SO IT IS NOT ASSERTED.
It would be easy to write "these are old drafts" and untrack all ten. This
looks instead: for each file it takes the first line of the module docstring
and searches every other .py IN THE TOOL REPOS for it. `lf_commands_v3.py`
opens with "CLI command implementations (TDD 28)." and that line also opens
`level_factory`'s live commands module, which is 111 KB against this file's
84 KB. That is a twin, and the twin is bigger and newer.

THE SEARCH HAS TO WALK DISK, NOT ASK GIT, AND THE FIRST VERSION GOT THIS
WRONG. It built its haystack from `git ls-files` and reported "no live twin
found" for all ten -- because every tool is its own git repo and this one
ignores those directories, so that call cannot see a single file in
`level_factory/`. A draft in `_bridge_fresh/` is staged FOR a tool repo; its
twin is never in this repo, by definition. See `twin_haystack`.

A FILE WITH NO TWIN IS REFUSED AND REPORTED. It might be the only copy of
something, and a script cannot tell unique work from a draft whose twin was
renamed. That is a person's call, and it gets made with the file's name in
front of them rather than by a rule that guessed.

AND ANY .py IN A SWEEP GROUP IS REFUSED. `_scratch2/` was 17 files of
measurement output and one real tool; the only reason that was noticed is
that a Python file stood out from a pile of JSON. So the rule is now explicit:
in a folder being swept, source refuses and says so.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"

#: Moved into the repo proper, not untracked. (source, destination)
RESCUE: list[tuple[str, str]] = [
    ("_scratch2/pcdiag/art_standard_audit.py", "tools/art_standard_audit.py"),
]

#: Untracked only while still byte-identical to the file it copies.
#: (the staged copy, the original)
DUPLICATES: list[tuple[str, str]] = [
    ("_send/PACKAGE_README.md", "docs/PACKAGE_README.md"),
]

#: Untracked because a tool rewrites them. Matched on path fragment.
CACHE_FRAGMENTS = ("/.godot/",)

#: Swept wholesale, minus anything RESCUE claims and minus any .py.
SWEEP_DIRS = ("_scratch2", "_scratch_walkable", "_send")

#: Swept only where a live twin is found. See the module docstring.
TWIN_DIRS = ("_bridge_fresh",)


def git(root: Path, args: list[str]):
    try:
        return subprocess.run(["git", "-C", str(root)] + args,
                              capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError):
        return None


def tracked_under(root: Path, *dirs: str) -> list[str]:
    r = git(root, ["ls-files", "--"] + list(dirs))
    if not r or r.returncode != 0:
        return []
    return [x.strip() for x in r.stdout.splitlines() if x.strip()]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def first_doc_line(p: Path) -> str | None:
    """The first non-empty line of the module docstring, if there is one.

    A weak fingerprint on purpose. It survives the edits a file picks up after
    it lands in a tool repo -- which is exactly the case being detected --
    where a hash would not. Being weak is why a match is reported for reading
    rather than acted on silently.
    """
    try:
        src = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    src = src.lstrip()
    for q in ('"""', "'''", 'r"""', "r'''"):
        if src.startswith(q):
            body = src[len(q):]
            for line in body.splitlines():
                if line.strip():
                    return line.strip()
            return None
    return None


_HAY_SKIP = {".git", "__pycache__", ".pytest_cache", "_scratch", "_runs",
             ".godot", "node_modules", "venv", ".venv", "build", "dist"}


def twin_haystack(root: Path) -> list[Path]:
    """Every .py a twin could BE -- which means walking, not asking git.

    THE FIRST VERSION ASKED `git ls-files` AND FOUND NOTHING. Run against the
    real factory it reported "no live twin found" for all ten drafts,
    including `lf_commands_v3.py`, whose twin I had already read. The reason
    is structural and worth stating: each tool is its OWN git repo and this
    repo ignores those directories, so `git ls-files` at the factory root
    cannot see a single file in `level_factory/`, `deli_counter/` or `zoo/`.
    It returned `tools/` and `patches/` and nothing else.

    Which is the whole point of a staging folder. A draft in `_bridge_fresh/`
    is staged for a TOOL REPO; the twin is never in this repo, by definition.
    Asking the index that deliberately cannot see the tools was asking the one
    source guaranteed to answer no.

    So it walks the manifest's tool paths from disk. The refusal is what made
    this visible instead of expensive -- ten files would have been untracked
    on a search that could not succeed.

    AND IT IS THE TOOL REPOS ONLY -- NOT `tools/`, NOT `patches/`. The second
    version included those and promptly reported:

        _bridge_fresh/lf_commands_v2.py   82.2 KB
          shadowed by tools/factory_untrack.py  19.4 KB

    which is this file, matching because its own docstring QUOTES the needle
    it searches for. A 19 KB script cannot be the twin of an 82 KB module and
    the sizes said so, but nothing was checking.

    Restricting to the tool repos fixes it structurally rather than by
    special-casing a filename. `_bridge` means a bridge TO THE TOOLS; a
    staging copy is staged for a tool repo, so that is the only place its twin
    can be. It also means no file in this repo -- this one, a patch quoting
    source text, a doc discussing a module -- can ever be mistaken for one.

    The cost is a twin that genuinely lives in `tools/` would be missed and
    the draft REFUSED. That is the safe direction: a refusal is a question,
    and untracking on a false match is a quiet loss.
    """
    roots: list[Path] = []
    try:
        import json
        data = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        for name, entry in data.get("tools", {}).items():
            roots.append(root / str(entry.get("path", name)))
    except (OSError, ValueError):
        pass

    out: list[Path] = []
    for base in roots:
        if not base.is_dir():
            continue
        for p in base.rglob("*.py"):
            if any(part in _HAY_SKIP for part in p.parts):
                continue
            out.append(p)
    return out


def find_twin(root: Path, needle: str,
              haystack: list[Path]) -> tuple[str, int] | None:
    """A .py elsewhere whose module docstring opens the same way."""
    for p in haystack:
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:4000]
        except OSError:
            continue
        if needle in head:
            try:
                rel = str(p.relative_to(root)).replace("\\", "/")
            except ValueError:
                rel = str(p)
            return rel, p.stat().st_size
    return None


def plan(root: Path):
    rescue, dup, cache, superseded, refused = [], [], [], [], []

    hay = twin_haystack(root)
    claimed = {s for s, _d in RESCUE}

    for src, dest in RESCUE:
        p, d = root / src, root / dest
        if not p.is_file():
            refused.append((src, "not on disk"))
        elif d.exists():
            refused.append((src, f"{dest} already exists"))
        elif src not in tracked_under(root, src):
            refused.append((src, "git does not track it -- nothing to move"))
        else:
            rescue.append((src, dest, p.stat().st_size))

    for staged, original in DUPLICATES:
        sp, op = root / staged, root / original
        if not sp.is_file():
            continue
        if not op.is_file():
            refused.append((staged, f"{original} is gone -- this may be the "
                                    f"only copy"))
            continue
        if sha(sp) != sha(op):
            refused.append((staged, f"differs from {original} -- it holds an "
                                    f"edit nobody moved back"))
            continue
        dup.append((staged, original, sp.stat().st_size))

    for rel in tracked_under(root, *SWEEP_DIRS):
        if rel in claimed:
            continue
        if any(f in "/" + rel for f in CACHE_FRAGMENTS):
            cache.append(rel)
            continue
        if rel.endswith(".py"):
            refused.append((rel, "a .py in a folder being swept -- source, "
                                 "or say why it is not"))
            continue
        if any(rel == s for s, _o in DUPLICATES):
            continue
        superseded.append(("sweep", rel, None))

    twins = tracked_under(root, *TWIN_DIRS)
    for rel in twins:
        p = root / rel
        if p.suffix != ".py":
            superseded.append(("sweep", rel, None))
            continue
        needle = first_doc_line(p)
        if not needle or len(needle) < 12:
            refused.append((rel, "no usable docstring to match a twin on"))
            continue
        hit = find_twin(root, needle, hay)
        if not hit:
            refused.append((rel, "no live twin found -- this may be the only "
                                 "copy"))
            continue
        twin, size = hit
        superseded.append(("twin", rel, (twin, p.stat().st_size, size)))

    return rescue, dup, cache, superseded, refused


def human(n: float) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024 or unit == "MB":
            return f"{n:,.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return str(n)


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    root = Path.cwd()
    if not (root / MANIFEST).is_file():
        print(f"no {MANIFEST} here -- run from the factory root")
        return 1

    rescue, dup, cache, superseded, refused = plan(root)

    print()
    if rescue:
        print("  RESCUE -- git mv into the repo proper")
        for src, dest, size in rescue:
            print(f"    {src}\n      -> {dest}   {human(size)}")
    if dup:
        print("\n  DUPLICATE -- untrack, byte-identical to the original")
        for staged, original, size in dup:
            print(f"    {staged:<44} == {original}  ({human(size)})")
    if cache:
        print(f"\n  EDITOR CACHE -- untrack, a tool rewrites these ({len(cache)})")
        for rel in cache:
            print(f"    {rel}")

    sweep = [s for s in superseded if s[0] == "sweep"]
    twin = [s for s in superseded if s[0] == "twin"]
    if sweep:
        print(f"\n  OUTPUT -- untrack, measurement dumps ({len(sweep)})")
        for _k, rel, _x in sweep[:12]:
            print(f"    {rel}")
        if len(sweep) > 12:
            print(f"    ... and {len(sweep) - 12} more")
    if twin:
        print(f"\n  SUPERSEDED -- untrack, a live twin was found ({len(twin)})")
        for _k, rel, (t, mine, theirs) in twin:
            print(f"    {rel:<40} {human(mine):>9}")
            print(f"      shadowed by {t}  {human(theirs)}")
    if refused:
        print(f"\n  REFUSED -- decide these yourself ({len(refused)})")
        for rel, why in refused:
            print(f"    {rel:<44} {why}")

    total = len(dup) + len(cache) + len(sweep) + len(twin)
    if not total and not rescue:
        print("  nothing to do")
        return 0

    print(f"\n  {len(rescue)} to move, {total} to untrack, "
          f"{len(refused)} refused.")
    print("  Untracking is `git rm --cached`: the files stay on disk and the "
          "previous\n  commit still has every one of them.")

    if "--apply" not in argv:
        print("\n  dry run. Nothing changed. Re-run with --apply.")
        return 0

    print()
    for src, dest, _s in rescue:
        (root / dest).parent.mkdir(parents=True, exist_ok=True)
        r = git(root, ["mv", "--", src, dest])
        if not r or r.returncode:
            print(f"  git mv FAILED {src}: "
                  f"{(r.stderr.strip() if r else 'git unavailable')}")
            continue
        print(f"  moved      {src} -> {dest}")

    paths = ([s for s, _o, _z in dup] + list(cache)
             + [rel for _k, rel, _x in superseded])
    # Batched, because Windows refuses a command line over 32767 characters --
    # the same ceiling check_all.py derives its budget from.
    for i in range(0, len(paths), 100):
        chunk = paths[i:i + 100]
        r = git(root, ["rm", "--cached", "--quiet", "--"] + chunk)
        if not r or r.returncode:
            print(f"  git rm --cached FAILED: "
                  f"{(r.stderr.strip() if r else 'git unavailable')}")
            return 1
    print(f"  untracked  {len(paths)} file(s) -- still on disk")
    print()
    print("  DO NOT RUN `git add -A` YET. Untracking a file that is not")
    print("  ignored does not stick: these folders sit at the root, nothing")
    print("  in .gitignore covers them, and the next `git add -A` puts all")
    print(f"  {len(paths)} straight back. That already happened once -- the")
    print("  commit read '2 files changed' and every one of them returned.")
    print()
    print("  They become ignored by MOVING, because `_scratch/` is what the")
    print("  ignore rule covers. So, in this order:")
    print()
    print("      python tools\\factory_folders.py --apply")
    print("      git add -A")
    print("      git status --short        <- expect deletions, not additions")
    return 0


# ------------------------------------------------------------- selftest ----

def selftest() -> int:
    import os
    import shutil
    import tempfile

    bad = 0

    def check(label, ok):
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    tmp = Path(tempfile.mkdtemp())
    try:
        root = tmp / "factory"
        for d in ("docs", "tools", "_scratch2/pcdiag", "_send",
                  "_scratch_walkable/relprobe/.godot", "_bridge_fresh",
                  "level_factory"):
            (root / d).mkdir(parents=True)
        (root / MANIFEST).write_text(
            '{"tools": {"level_factory": {"path": "level_factory"}}}',
            encoding="utf-8")
        # THE REGRESSION THIS EXISTS FOR: the twin lives in a tool
        # repo, which is its own git repo AND ignored here, so
        # `git ls-files` at this root can never see it.
        (root / "level_factory" / ".git").mkdir()
        (root / ".gitignore").write_text("level_factory/\n",
                                         encoding="utf-8")

        # RESCUE
        (root / "_scratch2/pcdiag/art_standard_audit.py").write_text(
            '"""Measure the shipped material library."""\n', encoding="utf-8")
        # OUTPUT
        (root / "_scratch2/navgate_all.txt").write_text("x", encoding="utf-8")
        (root / "_scratch_walkable/site.tscn").write_text("x", encoding="utf-8")
        # CACHE
        (root / "_scratch_walkable/relprobe/.godot/filesystem_cache10"
         ).write_text("x", encoding="utf-8")
        # DUPLICATE, matching
        (root / "docs/PACKAGE_README.md").write_text("same", encoding="utf-8")
        (root / "_send/PACKAGE_README.md").write_text("same", encoding="utf-8")
        # SUPERSEDED, with a live twin
        (root / "_bridge_fresh/lf_commands_v3.py").write_text(
            '"""CLI command implementations (TDD 28).\n\nshort draft\n"""\n',
            encoding="utf-8")
        (root / "level_factory/commands.py").write_text(
            '"""CLI command implementations (TDD 28).\n\n' + "live " * 400
            + '\n"""\n', encoding="utf-8")
        # SUPERSEDED, with NO twin -- must refuse
        (root / "_bridge_fresh/orphan_v2.py").write_text(
            '"""Something nobody ever landed anywhere else at all."""\n',
            encoding="utf-8")
        # a .py inside a swept folder -- must refuse
        (root / "_scratch_walkable/helper.py").write_text("x\n",
                                                          encoding="utf-8")
        # A DECOY IN tools/ QUOTING THE NEEDLE. This is the shape that made
        # factory_untrack.py report itself as the twin of an 82 KB module.
        (root / "tools/decoy_quoting_it.py").write_text(
            'r"""A script that mentions "CLI command implementations '
            '(TDD 28)." in prose."""\n', encoding="utf-8")

        subprocess.run(["git", "init", "-q", str(root)], check=True,
                       capture_output=True)
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            subprocess.run(["git", "-C", str(root), "config", k, v],
                           check=True, capture_output=True)
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True,
                       capture_output=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "seed"],
                       check=True, capture_output=True)

        here = Path.cwd()
        os.chdir(root)
        try:
            rescue, dup, cache, superseded, refused = plan(root)
        finally:
            os.chdir(here)

        rf = dict(refused)
        sweep = {r for k, r, _x in superseded if k == "sweep"}
        twin = {r: x for k, r, x in superseded if k == "twin"}

        check("the audit tool is rescued, not swept",
              [s for s, _d, _z in rescue] == ["_scratch2/pcdiag/art_standard_audit.py"])
        check("the identical README is untracked",
              [s for s, _o, _z in dup] == ["_send/PACKAGE_README.md"])
        check("the .godot cache is caught",
              cache == ["_scratch_walkable/relprobe/.godot/filesystem_cache10"])
        check("measurement output is swept",
              "_scratch2/navgate_all.txt" in sweep
              and "_scratch_walkable/site.tscn" in sweep)
        check("a draft with a live twin is swept, and the twin is named",
              "_bridge_fresh/lf_commands_v3.py" in twin
              and twin["_bridge_fresh/lf_commands_v3.py"][0]
              == "level_factory/commands.py")
        check("the twin is reported as bigger",
              twin["_bridge_fresh/lf_commands_v3.py"][1]
              < twin["_bridge_fresh/lf_commands_v3.py"][2])
        check("a file in tools/ quoting the needle is not the twin",
              twin["_bridge_fresh/lf_commands_v3.py"][0]
              == "level_factory/commands.py")
        check("a draft with NO twin is refused",
              "no live twin" in rf.get("_bridge_fresh/orphan_v2.py", ""))
        check("a .py in a swept folder is refused",
              "source" in rf.get("_scratch_walkable/helper.py", ""))

        # And the duplicate check must FIRE when the copies diverge.
        (root / "_send/PACKAGE_README.md").write_text("edited",
                                                      encoding="utf-8")
        os.chdir(root)
        try:
            _r, dup2, _c, _s, refused2 = plan(root)
        finally:
            os.chdir(here)
        check("a diverged copy is refused, not untracked",
              not dup2 and "differs from" in dict(refused2).get(
                  "_send/PACKAGE_README.md", ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("  selftest passed" if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
