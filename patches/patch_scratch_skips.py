r"""Teach the two checks about `_scratch/`, so the folders can move.

    python patch_scratch_skips.py --check
    python patch_scratch_skips.py
    python patch_scratch_skips.py --selftest   (run it AFTER applying)
    python patch_scratch_skips.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

WHY. `factory_folders.py` refused all eleven of its moves, and eight of those
refusals were correct: the folders are named in skip lists, not in prose.

    check_all.py:98    SKIP_GENERATED  "_bridge", "_scratch_archive", "_runs"
    never_wired.py:70  _SKIP_DIRS      "_bridge", "_scratch_archive"
    compare_candidates.py:53           DEFAULT_WS = "lot-demo-ws"

Move `_bridge/` out from under those names and `check_all.py` stops skipping
it, which is not a crash -- it is worse. It is a check that starts raising
findings against staging copies, so the next reader patches a file that is
not the file. `check_all.py`'s own comment says exactly that, which is how
the entries got there.

WHAT MAKES THIS WORTH DOING RATHER THAN JUST UPDATING NAMES. Once the scratch
folders live under one parent, ONE entry replaces three in both lists:

    SKIP_GENERATED = ("_bridge", "__pycache__", "_scratch_archive",
                      os.sep + "dist" + os.sep, os.sep + "_runs" + os.sep,
                      ".godot")
                                    becomes
    SKIP_GENERATED = ("__pycache__", "_scratch" + os.sep,
                      os.sep + "dist" + os.sep, ".godot")

Three names that each had to be remembered separately become one that is
true by construction: anything under `_scratch/` is scratch. The comment
above the list says "anyone adding an entry has to say which of the two they
are claiming" -- this removes the occasion to add one.

`"_scratch" + os.sep` HAS NO LEADING SEPARATOR ON PURPOSE. The existing
`os.sep + "_runs" + os.sep` only matches `_runs` when something precedes it,
so it never matched the root-level `_runs/` it was written for -- a latent
miss this inherits if it copies the shape. Without the leading separator it
matches both `_scratch\bridge\x` and `deli_counter\_scratch\y`. The cost is
that a directory named `my_scratch\` would also match; there is none, and a
skipped file is a quieter failure than a phantom finding.

TWO THINGS THIS DELIBERATELY DOES NOT TOUCH.

`SKIP_EVIDENCE = (os.sep + "rockay-ws" + os.sep,)` needs no edit. The
workspace moves to `workspaces/rockay-ws`, and the path still contains
`\rockay-ws\`, so the wrapped form keeps matching. It was written
location-independently and it stays that way.

`__pycache__` and `.pytest_cache` keep their entries. Those are not scratch
that moved -- Python and pytest recreate them anywhere, in every tool repo,
the moment anything runs. They are deleted, not relocated.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path


def _joined(src: str) -> str:
    """Adjacent string literals concatenated, so a split path reads whole.

    `probe_glb_void.py` builds its default across two lines. Checking the
    assembled path rather than either fragment is the difference between
    proving the path is right and proving the edit ran.
    """
    return re.sub(r'"\s*"', "", src)

SIDECAR = ".pre_scratch"

EDITS: list[tuple[str, str, str]] = [
    # ---------------------------------------------------------- check_all --
    ("tools/check_all.py",
     '#:   generated  _bridge, __pycache__, _scratch_archive, dist, _runs, .godot.',
     '#:   generated  _scratch, __pycache__, dist, _runs, .godot. The\n'
     '#:              `_scratch` entry replaced _bridge and _scratch_archive\n'
     '#:              when those moved under it -- anything below that folder\n'
     '#:              is scratch by construction, so the list cannot fall\n'
     '#:              behind. `_runs` keeps its own entry because it has NOT\n'
     '#:              moved: tools/factory_tidy.py still files measurements\n'
     '#:              and dead sidecars into it by that name.'),

    ("tools/check_all.py",
     'SKIP_GENERATED = ("_bridge", "__pycache__", "_scratch_archive",\n'
     '                  os.sep + "dist" + os.sep, os.sep + "_runs" + os.sep, ".godot")',
     'SKIP_GENERATED = ("__pycache__", "_scratch" + os.sep,\n'
     '                  os.sep + "dist" + os.sep, os.sep + "_runs" + os.sep,\n'
     '                  ".godot")'),

    # -------------------------------------------------------- never_wired --
    ("tools/never_wired.py",
     '_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules",\n'
     '              "build", "dist", ".godot", "_bridge", "_scratch_archive"}',
     '_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules",\n'
     '              "build", "dist", ".godot", "_scratch"}'),

    # ---------------------------------------------------- orphan_artifacts --
    # FOUND BY THE DRY RUN, NOT BY ME. `factory_folders.py` refused `_bridge`
    # and `_scratch_archive` a second time and blamed this file, which I had
    # not read and did not know skipped them. That is the refusal earning its
    # keep: a list I would have missed, surfaced by asking the repo instead of
    # my memory of it.
    ("tools/orphan_artifacts.py",
     '_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules",\n'
     '              ".godot", ".import", "_scratch_archive", "_bridge", "venv",\n'
     '              ".venv", "site-packages", "dist", "build"}',
     '_SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules",\n'
     '              ".godot", ".import", "_scratch", "venv",\n'
     '              ".venv", "site-packages", "dist", "build"}'),

    # -------------------------------------------------- compare_candidates --
    ("tools/compare_candidates.py",
     'DEFAULT_WS = "lot-demo-ws"',
     'DEFAULT_WS = "workspaces/lot-demo-ws"'),

    # ------------------------------------------------------- probe_glb_void --
    # ALSO FOUND BY THE DRY RUN. `compare_candidates.py` was the only file I
    # had read that named the workspace, and the first version of
    # `factory_folders.py` excused the whole folder on that basis -- which
    # would have moved `lot-demo-ws/` out from under this hardcoded default
    # and left `--selftest` pointing at a path that no longer exists. Narrowing
    # REVIEWED to the ONE file that was actually read surfaced it immediately.
    ("tools/probe_glb_void.py",
     '        default = Path("lot-demo-ws/.level_factory/preview/lot_demo_001_walk/"',
     '        default = Path("workspaces/lot-demo-ws/.level_factory/preview/"\n'
     '                       "lot_demo_001_walk/"'),

    # ------------------------------------------------------- the .ps1 side --
    # Listing EVERY namer rather than the first turned this from four separate
    # discoveries into one work order. `_scratch_archive` and `lot-demo-ws`
    # are each named by two runbooks, and none of them is a Python file, which
    # is why three rounds of scanning .py had not surfaced them.
    ("scripts/archive_scratch.ps1",
     '$dest = Join-Path $root ("_scratch_archive\\" + (Get-Date -Format yyyyMMdd_HHmmss))',
     '$dest = Join-Path $root ("_scratch\\archive\\" + (Get-Date -Format yyyyMMdd_HHmmss))'),

    ("scripts/tidy_docs.ps1",
     '#   *.pre_*     -> _scratch_archive\\pre_patch\\   editor backups, already',
     '#   *.pre_*     -> _scratch\\archive\\pre_patch\\   editor backups, already'),
    ("scripts/tidy_docs.ps1",
     '$bakDir  = Join-Path $root "_scratch_archive\\pre_patch"',
     '$bakDir  = Join-Path $root "_scratch\\archive\\pre_patch"'),
    # The two below are display text, not paths. They are edited anyway: a
    # message that names a folder the script no longer writes to is a false
    # statement the next reader has to disprove by reading the code.
    ("scripts/tidy_docs.ps1",
     '  Write-Host ("  {0} file(s), {1:N0} bytes -> _scratch_archive\\pre_patch\\" -f $baks.Count, $tot)',
     '  Write-Host ("  {0} file(s), {1:N0} bytes -> _scratch\\archive\\pre_patch\\" -f $baks.Count, $tot)'),
    ("scripts/tidy_docs.ps1",
     'docs/; backups move to _scratch_archive/pre_patch/, which is gitignored, and are',
     'docs/; backups move to _scratch/archive/pre_patch/, which is gitignored, and are'),

    ("scripts/make_package.ps1",
     '    [string]$Workspace = "lot-demo-ws"',
     '    [string]$Workspace = "workspaces\\lot-demo-ws"'),

    ("scripts/run_0809.ps1",
     '$WS      = "$FACTORY\\lot-demo-ws"',
     '$WS      = "$FACTORY\\workspaces\\lot-demo-ws"'),
]

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor.

    `check_all.py` is CRLF and the other two are LF, in the same repo, in the
    same commit. An anchor written with `\\n` matches neither reliably.
    """
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    rc = 0
    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            rc = 1
            continue
        raw = p.read_bytes()
        body = raw.decode("utf-8")
        eol = _eol(body)
        out = body
        done = 0

        for old, new in edits:
            o, n = _as(old, eol), _as(new, eol)
            if n in out:
                done += 1
                continue
            count = out.count(o)
            if count != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {count} time(s), "
                      f"expected 1:\n    {old.splitlines()[0][:70]}")
                rc = 1
                break
            out = out.replace(o, n, 1)
        else:
            if done == len(edits):
                print(f"  already applied  {rel}")
                continue
            bare = out.count("\n") - out.count(_CRLF)
            if eol == _CRLF and bare:
                print(f"REFUSING: {rel} -- would leave {bare} bare LF line(s).")
                rc = 1
                continue
            if p.suffix == ".py":
                # PowerShell has no compiler here, so a .ps1 gets the anchor
                # check and nothing more. Stated rather than hidden: these
                # edits are single tokens inside a line whose shape does not
                # change, which is the only kind of .ps1 edit worth making
                # without a parser to catch you.
                try:
                    compile(out, str(p), "exec")
                except SyntaxError as exc:
                    print(f"REFUSING: {rel} -- does not parse after the "
                          f"edit: {exc}")
                    rc = 1
                    continue
            data = out.encode("utf-8")
            if check:
                print(f"  would patch  {rel}  {len(raw):,} -> {len(data):,} "
                      f"bytes ({len(data) - len(raw):+,})")
                continue
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                side.write_bytes(raw)
            p.write_bytes(data)
            print(f"  patched      {rel}  {len(raw):,} -> {len(data):,} bytes "
                  f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return rc


def selftest(root: Path) -> int:
    """Check the post-conditions, not that the edit ran."""
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    ca = (root / "tools/check_all.py").read_text(encoding="utf-8")
    nw = (root / "tools/never_wired.py").read_text(encoding="utf-8")
    cc = (root / "tools/compare_candidates.py").read_text(encoding="utf-8")

    gen = ca[ca.index("SKIP_GENERATED"):ca.index("SKIP_EVIDENCE")]
    check('SKIP_GENERATED skips _scratch', '"_scratch" + os.sep' in gen)
    for gone in ("_bridge", "_scratch_archive"):
        check(f'SKIP_GENERATED no longer names {gone}', f'"{gone}"' not in gen)
    # THE ONE THAT MUST STAY. `_runs/` is refused by factory_folders.py
    # because tools/factory_tidy.py files into it by name, so it does not move
    # -- and dropping its skip entry while it sits at the root would point a
    # check at 13 files of dead sidecars and call them findings. An entry is
    # only safe to remove in the same operation that moves its folder.
    check("SKIP_GENERATED still names _runs -- that folder has not moved",
          'os.sep + "_runs" + os.sep' in gen)
    check("SKIP_EVIDENCE is untouched -- it survives the move",
          'SKIP_EVIDENCE = (os.sep + "rockay-ws" + os.sep,)' in ca)
    check("__pycache__ is still skipped -- it is not scratch that moved",
          '"__pycache__"' in gen)

    skip = nw[nw.index("_SKIP_DIRS"):nw.index("}", nw.index("_SKIP_DIRS")) + 1]
    check("_SKIP_DIRS skips _scratch", '"_scratch"' in skip)
    check("_SKIP_DIRS no longer names _bridge", '"_bridge"' not in skip)
    check("_SKIP_DIRS keeps .pytest_cache", '".pytest_cache"' in skip)

    oa = (root / "tools/orphan_artifacts.py").read_text(encoding="utf-8")
    osk = oa[oa.index("_SKIP_DIRS"):oa.index("}", oa.index("_SKIP_DIRS")) + 1]
    check("orphan_artifacts _SKIP_DIRS skips _scratch", '"_scratch"' in osk)
    check("orphan_artifacts no longer names _bridge", '"_bridge"' not in osk)
    check("orphan_artifacts keeps .import -- Godot makes those anywhere",
          '".import"' in osk)
    try:
        compile(oa, "orphan_artifacts.py", "exec")
        check("orphan_artifacts.py parses", True)
    except SyntaxError as exc:
        check(f"orphan_artifacts.py parses ({exc})", False)

    check("DEFAULT_WS points at workspaces/",
          'DEFAULT_WS = "workspaces/lot-demo-ws"' in cc)

    gv = (root / "tools/probe_glb_void.py").read_text(encoding="utf-8")
    check("probe_glb_void's selftest default points at workspaces/",
          '"workspaces/lot-demo-ws/.level_factory/preview/"' in gv)
    check("  and the path it builds is unchanged apart from the prefix",
          "workspaces/lot-demo-ws/.level_factory/preview/lot_demo_001_walk/"
          "lot/bank_branch_a04/site_base.glb" in _joined(gv))
    try:
        compile(gv, "probe_glb_void.py", "exec")
        check("probe_glb_void.py parses", True)
    except SyntaxError as exc:
        check(f"probe_glb_void.py parses ({exc})", False)

    for rel, needle in (
            ("scripts/archive_scratch.ps1", '"_scratch\\archive\\'),
            ("scripts/tidy_docs.ps1", '"_scratch\\archive\\pre_patch"'),
            ("scripts/make_package.ps1", '"workspaces\\lot-demo-ws"'),
            ("scripts/run_0809.ps1", '"$FACTORY\\workspaces\\lot-demo-ws"')):
        txt = (root / rel).read_text(encoding="utf-8")
        check(f"{rel.split('/')[-1]} points at the new path", needle in txt)
        check(f"  and no longer names the old one",
              "_scratch_archive" not in txt
              and '"lot-demo-ws"' not in txt
              and '\\lot-demo-ws"' not in txt.replace(
                  "workspaces\\lot-demo-ws", ""))

    for rel, src in (("check_all.py", ca), ("never_wired.py", nw),
                     ("compare_candidates.py", cc)):
        try:
            compile(src, rel, "exec")
            check(f"{rel} parses", True)
        except SyntaxError as exc:
            check(f"{rel} parses ({exc})", False)

    print()
    print("  the folders can move now" if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel in dict.fromkeys(r for r, _o, _n in EDITS):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        return bad

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print("\n  now re-run: python tools\\factory_folders.py")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
