"""Undo `patch_lf_themed_selection.py` exactly, and touch nothing else.

Save next to `patch_lf_themed_selection.py` in the factory root and run:

    python unpatch_lf_themed_selection.py --check
    python unpatch_lf_themed_selection.py

## Why this exists instead of `git checkout`

The checkout I sent first is wrong and could cost real work. `building_library.py`
and `commands/__init__.py` also carry `patch_lf_art_inputs`, `patch_lf_lot_rule`,
`patch_lf_fanout`, `patch_lf_layer_resolve` and `patch_lf_layer_fingerprint`. If
any of those is not committed, `git checkout` discards it along with the one
change we want gone, and the byte counts would be the only clue.

`level_factory` may also be its own repository, in which case a checkout run
from the factory root matches no pathspec and silently changes nothing -- which
is consistent with the suite still failing after the revert was issued.

So this reverses the edit list rather than the file.

## Why it imports the forward patch instead of restating the edits

It reads `TARGETS` out of `patch_lf_themed_selection` and applies every
`(before, after)` pair backwards. Retyping ~200 lines of anchor text into an
inverse script is a transcription error waiting to happen, and an inverse that
does not exactly mirror the forward patch is worse than no inverse: it leaves a
file that is neither state.

The same refusal rule applies -- every anchor must be present and unique on
every file before anything is written, so a half-undo cannot happen.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

def _factory_root() -> Path:
    """The directory holding `factory.manifest.json`, found by walking up.

    Was `Path(__file__).resolve().parent`, which required this file to sit AT
    the factory root and kept eleven scripts pinned there. Walking up means it
    works from `tools/`, `patches/` or anywhere else, and still returns the
    root when it IS the root -- the first candidate tested is its own
    directory.

    The manifest is the marker because it is the one file that defines this
    place and exists in no tool repo. `.git` would match every tool repo.
    """
    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        if (base / "factory.manifest.json").is_file():
            return base
    return here.parent


ROOT = _factory_root()
# cwd is not trusted: the forward patch's targets are relative paths, and three
# of this week's mistakes were a command run from the wrong directory.
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    try:
        fwd = importlib.import_module("patch_lf_themed_selection")
    except ModuleNotFoundError:
        print("[unpatch] patch_lf_themed_selection.py is not in the factory "
              "root next to this file -- it holds the exact anchor text and "
              "this script will not restate it from memory.")
        return 2

    plan = []
    for target, edits in fwd.TARGETS:
        target = Path(target)
        if not target.is_file():
            print(f"[unpatch] {target} not found")
            return 1
        raw = target.read_bytes()
        crlf = b"\r\n" in raw
        text = raw.decode("utf-8").replace("\r\n", "\n")
        print(f"[unpatch] {target}: {len(raw)} bytes, "
              f"endings={'CRLF' if crlf else 'LF'}")
        problems = []
        for name, before, after in edits:
            if before in text and after not in text:
                print(f"[unpatch]   ALREADY REVERTED: {name}")
            elif after not in text:
                print(f"[unpatch]   ANCHOR NOT FOUND: {name}")
                problems.append(name)
            elif text.count(after) != 1:
                print(f"[unpatch]   ANCHOR NOT UNIQUE "
                      f"({text.count(after)}x): {name}")
                problems.append(name)
        if problems:
            print(f"[unpatch] REFUSING to write: {len(problems)} anchor(s) on "
                  f"{target} did not match cleanly. The file is in neither "
                  f"state and needs eyes on it, not another script.")
            return 1
        plan.append((target, raw, crlf, text, edits))

    total = 0
    for target, raw, crlf, text, edits in plan:
        for name, before, after in edits:
            if after not in text:
                continue
            text = text.replace(after, before)
            print(f"[unpatch]   reverted: {name}")
        payload = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
        if payload == raw:
            print(f"[unpatch]   no change ({len(raw)} bytes)")
            continue
        if check_only:
            print(f"[unpatch]   --check: would write {len(raw)} -> "
                  f"{len(payload)} bytes ({len(payload) - len(raw):+d})")
            continue
        target.write_bytes(payload)
        total += len(payload) - len(raw)
        print(f"[unpatch]   wrote {len(raw)} -> {len(payload)} bytes "
              f"({len(payload) - len(raw):+d})")
        left = target.read_text(encoding="utf-8")
        for token in ("ThemedShellsUnavailable", "require_themed_shells",
                      "themed=True"):
            if token in left:
                print(f"[unpatch]   STILL PRESENT after revert: {token} -- "
                      f"something else in the tree references it")
    if check_only:
        print("[unpatch] --check: all anchors matched, no write")
    else:
        print(f"[unpatch] total {total:+d} bytes "
              f"(expect building_library 18711 -> 10241 and "
              f"commands 91985 -> 90612 if nothing else moved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
