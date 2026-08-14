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
import sys
from pathlib import Path

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

    # -------------------------------------------------- compare_candidates --
    ("tools/compare_candidates.py",
     'DEFAULT_WS = "lot-demo-ws"',
     'DEFAULT_WS = "workspaces/lot-demo-ws"'),
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
            try:
                compile(out, str(p), "exec")
            except SyntaxError as exc:
                print(f"REFUSING: {rel} -- does not parse after the edit: {exc}")
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

    check("DEFAULT_WS points at workspaces/",
          'DEFAULT_WS = "workspaces/lot-demo-ws"' in cc)

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
