#!/usr/bin/env python3
"""Make LF canonical, in the repo and in the working copy.

WHAT WAS WRONG

`core.autocrlf = input`, no `.gitattributes`, no attributes on any path. That
combination stores every blob as LF and NEVER converts back on checkout, so
git left whatever a Windows editor had written sitting in the working copy:

  * `PIPELINE_ROADMAP.md` was 4,453 CRLF on this disk and LF in the repository.
  * `.gitignore` was 32 CRLF and 26 LF AT THE SAME TIME.
  * The five `workspaces/unlit-3b-ws` files committed as factory-v1.26.0 were
    CRLF, and git warned on each that it would replace them.

A fresh clone would therefore have produced an LF `PIPELINE_ROADMAP.md`, and
`CLAUDE.md`'s rule -- "PIPELINE_ROADMAP.md is CRLF; everything under
level_factory\\ is LF" -- would have been false there. The patch machinery
itself was never at risk: `_eol()` is keyed off the file it is editing, so it
adapts. What was at risk is every check written against the DOCUMENTED
constant, including `patch_roadmap_51_mechanism.py`'s selftest, which asserts
`eol == "\\r\\n"` and would fail on a clone for a reason that looks like a
broken patch rather than a renormalised file.

`text=auto eol=lf` makes the two agree: git normalises on commit exactly as it
already did, and now also writes LF on checkout.

THIS PATCH ONLY CREATES THE FILE. It cannot change the working copy on its
own -- attributes apply when git next writes a file. The renormalise step is
git's to run and is printed after applying.

AFTER THIS, `CLAUDE.md` AND THE HANDOFF STILL SAY CRLF. That sentence becomes
wrong the moment this is renormalised, and correcting it needs a verified read
of `CLAUDE.md`, which this patch does not have. It is deliberately left as a
separate change rather than guessed at.

USAGE

    python patches\\patch_r52_gitattributes.py --check
    python patches\\patch_r52_gitattributes.py --selftest
    python patches\\patch_r52_gitattributes.py
    python patches\\patch_r52_gitattributes.py --revert
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / ".gitattributes"

CONTENT = """# Line endings are LF in the repository AND in the working copy.
#
# Before this file existed, `core.autocrlf = input` stored every blob as LF
# and never converted back on checkout, so the working copy kept whatever a
# Windows editor had written. PIPELINE_ROADMAP.md was 4,453 CRLF on one disk
# and LF in the repository; .gitignore was 32 CRLF and 26 LF at once. Every
# patch script keys its `_eol()` off the file it is editing and coped fine --
# but CLAUDE.md's documented rule that the roadmap "is CRLF" was true of one
# working copy by accident of history and false of the repository, and a
# fresh clone would have exposed that as a wave of failing patch selftests.
#
# `text=auto` keeps git's own binary sniffing; `eol=lf` makes checkout write
# what commit already stored.
* text=auto eol=lf

# Declared binary rather than sniffed. `text=auto` gets these right in
# practice, but a misdetected .glb is a corrupted building mesh and the cost
# of being explicit is three lines.
*.glb binary
*.png binary
*.jpg binary
*.zip binary
"""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def check() -> int:
    if TARGET.exists():
        raw = TARGET.read_bytes()
        print(f"  NOT APPLICABLE: {TARGET.name} already exists "
              f"({len(raw)} B, sha256 {_sha(raw)[:16]}...)")
        print("  This patch creates it and will not overwrite one it did not "
              "write.")
        return 1
    print(f"  {TARGET.name} does not exist -- APPLICABLE.")
    print(f"  would write {len(CONTENT.encode('utf-8'))} B, LF")
    return 0


def apply() -> int:
    if TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET.name} already exists. This patch "
                         f"creates it; it will not overwrite one it did not "
                         f"write.")
    data = CONTENT.encode("utf-8")          # LF, written as bytes
    TARGET.write_bytes(data)
    print(f"  wrote {TARGET.name}: {len(data)} B  sha256 {_sha(data)}")
    print(f"  endings: {data.count(bytes([13, 10]))} CRLF, "
          f"{data.count(bytes([10])) - data.count(bytes([13, 10]))} LF")
    print()
    print("  THE WORKING COPY HAS NOT CHANGED YET. Attributes apply when git")
    print("  next writes a file. To make this disk match the repository:")
    print()
    print("    git add .gitattributes")
    print("    git commit -m \"LF is canonical, in the repo and the working copy\"")
    print("    git add --renormalize .")
    print("    git status --short          # expect PIPELINE_ROADMAP.md, .gitignore")
    print("    git commit -m \"renormalise CRLF working copies to LF\"")
    print("    git checkout -- .           # rewrites the working copy to LF")
    print()
    print("  Then CLAUDE.md's 'PIPELINE_ROADMAP.md is CRLF' sentence is wrong")
    print("  and needs correcting -- separate change, needs a verified read.")
    return 0


def revert() -> int:
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: no {TARGET.name} to remove.")
    raw = TARGET.read_bytes()
    if raw != CONTENT.encode("utf-8"):
        raise SystemExit(
            f"REFUSING: {TARGET.name} is not the file this patch wrote "
            f"({len(raw)} B, expected {len(CONTENT.encode('utf-8'))}). "
            f"Something else has edited it; remove it by hand if you mean to.")
    TARGET.unlink()
    print(f"  removed {TARGET.name}")
    print("  NOTE: if you already renormalised, the working copy is LF and")
    print("        stays LF. Removing this file does not undo that; it only")
    print("        stops checkout from enforcing it.")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    data = CONTENT.encode("utf-8")
    ok(data.count(bytes([13, 10])) == 0,
       "the file this writes contains no CRLF -- it would be absurd otherwise")
    ok(data.endswith(b"\n"), "it ends with a newline")

    lines = [l for l in CONTENT.split("\n") if l and not l.startswith("#")]
    ok("* text=auto eol=lf" in lines,
       "the catch-all rule is present exactly as intended")
    ok(lines[0] == "* text=auto eol=lf",
       "and it comes FIRST -- later rules override earlier ones in "
       "gitattributes, so a catch-all placed last would beat the binary rules")
    for ext in ("*.glb", "*.png", "*.jpg", "*.zip"):
        ok(f"{ext} binary" in lines, f"{ext} is declared binary")
    ok(lines.index("* text=auto eol=lf") < lines.index("*.glb binary"),
       "binary declarations come after the catch-all, so they win")

    # The claim in the header has to match the repo this is being applied to.
    gi = ROOT / ".gitignore"
    if gi.exists():
        raw = gi.read_bytes()
        crlf = raw.count(b"\r\n")
        lone = raw.count(b"\n") - crlf
        print(f"        (measured now) .gitignore: {crlf} CRLF, {lone} lone LF")
        ok(crlf > 0 or lone > 0, ".gitignore has line endings to speak of")
    rm = ROOT / "PIPELINE_ROADMAP.md"
    if rm.exists():
        raw = rm.read_bytes()
        crlf = raw.count(b"\r\n")
        lone = raw.count(b"\n") - crlf
        print(f"        (measured now) PIPELINE_ROADMAP.md: {crlf} CRLF, "
              f"{lone} lone LF")

    ok(not TARGET.exists(),
       f"{TARGET.name} does not exist yet, so applying creates rather than "
       f"overwrites")

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s)")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("SELFTEST PASSED")
    return 0


def main(argv) -> int:
    arg = argv[1] if len(argv) > 1 else ""
    if arg == "--check":
        return check()
    if arg == "--selftest":
        return selftest()
    if arg == "--revert":
        return revert()
    if arg == "":
        return apply()
    raise SystemExit(f"unknown argument {arg!r}; "
                     f"use --check, --selftest, --revert, or no argument")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
