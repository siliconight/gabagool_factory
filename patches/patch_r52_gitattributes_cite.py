#!/usr/bin/env python3
"""Correct three factual errors in the .gitattributes comment I wrote.

`patch_r52_gitattributes.py` wrote a header comment justifying the change. Three
claims in it are wrong, and they are wrong in the direction that matters -- a
future reader would go looking in the wrong file for a rule that is not there.

1. IT CITES THE WRONG DOCUMENT. It says "CLAUDE.md's documented rule that the
   roadmap is CRLF". `CLAUDE.md` contains no such rule; its only mention of
   `PIPELINE_ROADMAP.md` is about item 17. The sentence lives in
   `docs/sessions/SESSION_0816_HANDOFF.md:157`. CLAUDE.md's actual guidance on
   endings was already correct before any of this and explicitly warns that
   "Git's `autocrlf` means a file's on-disk endings can also change under you
   between sessions without its content changing at all".

2. IT REPORTS 4,453 CRLF for the roadmap. That was a count taken from a
   reconstructed sandbox copy, not from the file. Measured on the real one by
   `patch_r52_gitattributes.py --selftest`: 4,525 CRLF, 0 lone LF.

3. IT REPORTS .gitignore AS 32 CRLF / 26 LF without saying when. That was the
   state at discovery, BEFORE `patch_r52_factory_certify.py` appended nine
   entries; by the time `.gitattributes` was written it read 47 CRLF / 26 LF.
   The number is not wrong so much as undated, which for a file whose whole
   subject is drift is the same problem.

The substance of the comment -- what `core.autocrlf = input` did, and why
`text=auto eol=lf` fixes it -- is unchanged and was correct.

NOTHING IS PUSHED. This is intended to be applied and then folded into commit
e25232c with `git commit --amend`, so the file never carries a false citation
in any commit that leaves this machine. The amend command is printed on apply.

USAGE

    python patches\\patch_r52_gitattributes_cite.py --check
    python patches\\patch_r52_gitattributes_cite.py --selftest
    python patches\\patch_r52_gitattributes_cite.py
    python patches\\patch_r52_gitattributes_cite.py --revert
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r52cite"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / ".gitattributes"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)

EXPECT_BYTES = 1041
EXPECT_SHA = "FA21E5ACD3B732D37440E3CD945194DF105E558A81C6C3A87C7B0E44E4BA0176"

OLD = """# Before this file existed, `core.autocrlf = input` stored every blob as LF
# and never converted back on checkout, so the working copy kept whatever a
# Windows editor had written. PIPELINE_ROADMAP.md was 4,453 CRLF on one disk
# and LF in the repository; .gitignore was 32 CRLF and 26 LF at once. Every
# patch script keys its `_eol()` off the file it is editing and coped fine --
# but CLAUDE.md's documented rule that the roadmap "is CRLF" was true of one
# working copy by accident of history and false of the repository, and a
# fresh clone would have exposed that as a wave of failing patch selftests.
"""

NEW = """# Before this file existed, `core.autocrlf = input` stored every blob as LF
# and never converted back on checkout, so the working copy kept whatever a
# Windows editor had written. Measured on 2026-08-16: PIPELINE_ROADMAP.md was
# 4,525 CRLF and 0 lone LF on this disk and LF in the repository, and
# .gitignore was mixed -- 32 CRLF and 26 LF when the drift was found, 47 and
# 26 by the time this file was written. CLAUDE.md was CRLF too and nobody had
# noticed; it lost 379 bytes, one per line, when the working copy was
# renormalised.
#
# Every patch script keys its `_eol()` off the file it is editing, so the
# machinery coped. What did not was the DOCUMENTED rule --
# `docs/sessions/SESSION_0816_HANDOFF.md:157`, "PIPELINE_ROADMAP.md is CRLF;
# everything under level_factory\\ is LF" -- which was true of one working copy
# by accident of history and false of the repository. A fresh clone would have
# turned that into a wave of patch selftests failing on correct files.
# CLAUDE.md itself was already right, and had warned that "Git's `autocrlf`
# means a file's on-disk endings can also change under you between sessions
# without its content changing at all".
"""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def _load():
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET} does not exist. Apply "
                         f"patch_r52_gitattributes.py first.")
    return TARGET.read_bytes()


def _identity(raw: bytes):
    got = _sha(raw)
    mark = "" if len(raw) == EXPECT_BYTES else "   <-- not the size this was written at"
    crlf = raw.count(b"\r\n")
    lone = raw.count(b"\n") - crlf
    print(f"  .gitattributes: {len(raw)} B (expected {EXPECT_BYTES}){mark}")
    print(f"    sha256 : {got}{'' if got == EXPECT_SHA else '   <-- differs'}")
    print(f"    endings: {crlf} CRLF, {lone} LF")


def check() -> int:
    raw = _load()
    _identity(raw)
    print()
    text = raw.decode("utf-8").replace("\r\n", "\n")
    n = text.count(OLD)
    print(f"  [{'ok' if n == 1 else 'MISSING'}]  the comment block to correct "
          f"(found {n})")
    print()
    print("APPLICABLE." if n == 1
          else "NOT APPLICABLE: refusing rather than fuzzy-matching.")
    return 0 if n == 1 else 1


def apply() -> int:
    raw = _load()
    _identity(raw)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if text.count(OLD) != 1:
        raise SystemExit("REFUSING: the comment block is not present exactly "
                         "once. Nothing written.")
    if SIDECAR.exists():
        raise SystemExit(f"REFUSING: {SIDECAR.name} exists. Use --revert.")
    shutil.copy2(TARGET, SIDECAR)
    data = text.replace(OLD, NEW, 1).encode("utf-8")
    TARGET.write_bytes(data)
    print()
    print(f"  {len(raw)} -> {len(data)} B  ({len(data) - len(raw):+d})")
    print(f"  sha256 {_sha(data)}")
    print(f"  endings: {data.count(bytes([13, 10]))} CRLF, "
          f"{data.count(bytes([10])) - data.count(bytes([13, 10]))} LF")
    print()
    print("  NEXT -- fold into e25232c so no pushed commit carries the wrong")
    print("  citation (nothing has been pushed):")
    print()
    print("    git add .gitattributes patches/patch_r52_gitattributes_cite.py")
    print("    git commit --amend --no-edit")
    print("    git log --oneline -1")
    return 0


def revert() -> int:
    if not SIDECAR.exists():
        raise SystemExit(f"REFUSING: no {SIDECAR.name} to revert from.")
    before = TARGET.read_bytes()
    shutil.copy2(SIDECAR, TARGET)
    SIDECAR.unlink()
    after = TARGET.read_bytes()
    print(f"  reverted: {len(before)} -> {len(after)} B, sha256 {_sha(after)}")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    raw = _load()
    ok(len(raw) == EXPECT_BYTES, f"target is {EXPECT_BYTES} B (got {len(raw)})")
    ok(_sha(raw) == EXPECT_SHA, "target sha256 matches what was written")
    ok(raw.count(b"\r\n") == 0, ".gitattributes is LF, as it must be")

    text = raw.decode("utf-8").replace("\r\n", "\n")
    ok(text.count(OLD) == 1, "the comment block is present exactly once")
    out = text.replace(OLD, NEW, 1)
    ok(out != text, "the edit changes the file")

    # -- each of the three errors is actually gone, and its replacement present
    ok("CLAUDE.md's documented rule" in text
       and "CLAUDE.md's documented rule" not in out,
       "the wrong citation is removed")
    ok("SESSION_0816_HANDOFF.md:157" in out,
       "the correct source is named, with a line number")
    ok("4,453" in text and "4,453" not in out,
       "the sandbox-derived 4,453 is removed")
    ok("4,525 CRLF and 0 lone LF" in out,
       "the measured count replaces it")
    ok("32 CRLF and 26 LF when the drift was found" in out
       and "47 and\n# 26 by the time this file was written" in out,
       "the .gitignore figures are dated rather than floating")

    # -- the substance must survive; this is a citation fix, not a rewrite
    for keep in ("core.autocrlf = input", "text=auto eol=lf",
                 "*.glb binary", "* text=auto eol=lf"):
        ok(keep in out, f"unchanged: {keep!r}")
    ok(out.split("\n").index("* text=auto eol=lf")
       < out.split("\n").index("*.glb binary"),
       "rule ordering is untouched -- catch-all still before the binaries")

    # -- prove the check can fail
    damaged = text.replace(OLD, "# gone\n", 1)
    ok(damaged.count(OLD) == 0,
       "check() can fail: removing the block makes it uncountable")

    # -- and the claim about CLAUDE.md having no such rule is itself checked,
    # -- because asserting it in a comment is how the first error happened.
    cm = ROOT / "CLAUDE.md"
    if cm.exists():
        body = cm.read_bytes().decode("utf-8", "replace")
        hits = [l for l in body.split("\n")
                if "PIPELINE_ROADMAP" in l and "CRLF" in l]
        ok(not hits,
           f"CLAUDE.md really does not state the roadmap's ending ({hits})")
    else:
        print("        (CLAUDE.md not found -- claim unverified here)")

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
