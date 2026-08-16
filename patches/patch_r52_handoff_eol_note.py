#!/usr/bin/env python3
"""Mark the handoff's line-endings rule superseded, without deleting it.

`docs/sessions/SESSION_0816_HANDOFF.md:157` states:

    `PIPELINE_ROADMAP.md` is CRLF; everything under `level_factory\\` is LF.

That was true of one working copy on 2026-08-16 and false of the repository,
which had been storing every blob as LF under `core.autocrlf = input` the whole
time. It is now false of both: `.gitattributes` (commit f2713e9) sets
`* text=auto eol=lf`, and the working copy was renormalised.

WHY ANNOTATE RATHER THAN REWRITE

A dated handoff is a record of what was known then, and the next session reads
this one first -- so the correction has to sit where the wrong claim is, or it
does not get read at the moment it is needed. Deleting the sentence would leave
no trace that the project once believed it, which is the same instinct this
repo already rejects for retracted findings.

WHAT SURVIVES UNTOUCHED, AND SHOULD

The rule the heading states -- `_eol()` is keyed off the FILE, never off an
anchor -- is CORRECT and is what made the whole renormalisation a non-event for
the patch machinery. Every patch this session read its target's endings at
runtime and adapted. Only the sentence naming a specific file's ending as a
constant went stale, which is the distinction the note draws.

The `Path.read_text()` warning after it is also untouched and still correct.

USAGE

    python patches\\patch_r52_handoff_eol_note.py --check
    python patches\\patch_r52_handoff_eol_note.py --selftest
    python patches\\patch_r52_handoff_eol_note.py
    python patches\\patch_r52_handoff_eol_note.py --revert
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r52eolnote"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "docs" / "sessions" / "SESSION_0816_HANDOFF.md"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)

EXPECT_BYTES = 12913
EXPECT_SHA = "66A280C24B5A9B22B45EE679CECA07CE1167CE5F91F868A1E2E8200E8E93D7FA"

OLD = """**`_eol()` is keyed off the FILE, never off an anchor.**
`PIPELINE_ROADMAP.md` is CRLF; everything under `level_factory\\` is LF. And
`Path.read_text()` normalises newlines, so a check written with `read_text`
reports a CRLF file as LF.
"""

NEW = """**`_eol()` is keyed off the FILE, never off an anchor.**
`PIPELINE_ROADMAP.md` is CRLF; everything under `level_factory\\` is LF. And
`Path.read_text()` normalises newlines, so a check written with `read_text`
reports a CRLF file as LF.

> **SUPERSEDED 2026-08-16 -- the second sentence only.** The rule itself is
> right and is why none of this cost anything: every patch reads its target's
> endings at runtime, so the machinery adapted without a line of change. But
> naming a file's ending as a CONSTANT was wrong even when written.
> `core.autocrlf = input` was storing every blob as LF and never converting
> back on checkout, so `PIPELINE_ROADMAP.md` was 4,525 CRLF on that one disk
> and LF in the repository, `.gitignore` was 32 CRLF and 26 LF at the same
> time, and `CLAUDE.md` was CRLF without anyone noticing -- it lost 379 bytes,
> one per line, when the working copy was brought into line. A fresh clone
> would have produced LF files and failed every selftest asserting CRLF, on
> files that were correct.
>
> `.gitattributes` now sets `* text=auto eol=lf` (commit f2713e9) and the
> working copy has been renormalised, so **LF is canonical in both.** Note
> that `.pre_*` sidecars are gitignored and are byte copies of whatever their
> source was, so older ones are still CRLF and are supposed to be.
>
> Do not replace this with "the roadmap is LF". That would repeat the mistake
> with a different constant. Read the file.
"""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def _eol(raw: bytes) -> str:
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    if crlf and lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has mixed line endings "
                         f"({crlf} CRLF, {lf} LF).")
    if not crlf and not lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has no line endings.")
    return "\r\n" if crlf else "\n"


def _load():
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET} does not exist.")
    raw = TARGET.read_bytes()
    return raw, _eol(raw), raw.decode("utf-8").replace("\r\n", "\n")


def _identity(raw: bytes):
    got = _sha(raw)
    crlf = raw.count(b"\r\n")
    lone = raw.count(b"\n") - crlf
    mark = "" if len(raw) == EXPECT_BYTES else "   <-- not the size this was read against"
    print(f"  {TARGET.name}")
    print(f"    bytes  : {len(raw)}   (expected {EXPECT_BYTES}){mark}")
    print(f"    sha256 : {got}{'' if got == EXPECT_SHA else '   <-- differs'}")
    print(f"    endings: {crlf} CRLF, {lone} lone LF")


def check() -> int:
    raw, _e, text = _load()
    _identity(raw)
    print()
    n = text.count(OLD)
    print(f"  [{'ok' if n == 1 else 'MISSING'}]  the line-endings rule (found {n})")
    print()
    print("APPLICABLE." if n == 1
          else "NOT APPLICABLE: refusing rather than fuzzy-matching.")
    return 0 if n == 1 else 1


def apply() -> int:
    raw, eol, text = _load()
    _identity(raw)
    if text.count(OLD) != 1:
        raise SystemExit("REFUSING: the rule is not present exactly once. "
                         "Nothing written.")
    if SIDECAR.exists():
        raise SystemExit(f"REFUSING: {SIDECAR.name} exists. Use --revert.")
    shutil.copy2(TARGET, SIDECAR)
    out = text.replace(OLD, NEW, 1)
    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
    TARGET.write_bytes(data)
    print()
    print(f"  {len(raw)} -> {len(data)} B  ({len(data) - len(raw):+d})")
    print(f"  sha256 {_sha(data)}")
    print(f"  endings: {data.count(bytes([13, 10]))} CRLF, "
          f"{data.count(bytes([10])) - data.count(bytes([13, 10]))} lone LF")
    print()
    print("  NEXT:")
    print("    git add docs/sessions/SESSION_0816_HANDOFF.md "
          "patches/patch_r52_handoff_eol_note.py")
    print("    git commit -m \"mark the handoff's line-endings rule superseded\"")
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

    raw, eol, text = _load()
    ok(len(raw) == EXPECT_BYTES, f"target is {EXPECT_BYTES} B (got {len(raw)})")
    ok(_sha(raw) == EXPECT_SHA, "target sha256 matches the read")
    ok(eol == "\n", "the handoff is LF -- it always was, which is why the "
                    "renormalise did not change its byte count")
    ok(text.count(OLD) == 1, "the rule is present exactly once")

    out = text.replace(OLD, NEW, 1)
    ok(out != text, "the edit changes the file")

    # -- the original survives, in full ------------------------------------
    ok(out.count("`PIPELINE_ROADMAP.md` is CRLF; everything under") == 1,
       "the superseded sentence is KEPT, not deleted")
    ok(out.count("**`_eol()` is keyed off the FILE, never off an anchor.**") == 1,
       "the rule heading survives exactly once")
    ok("`Path.read_text()` normalises newlines" in out,
       "the read_text warning after it is untouched")

    # -- the note lands after the claim, not before ------------------------
    ok(out.index("is CRLF; everything under") < out.index("SUPERSEDED 2026-08-16"),
       "the note sits BELOW the sentence it corrects, where a reader hits it "
       "immediately after the wrong claim")
    ok(out.count("SUPERSEDED 2026-08-16") == 1, "one supersede marker")

    # -- it must be a blockquote, or it reads as more of the original rule --
    note = out[out.index("> **SUPERSEDED"):out.index("> Do not replace this")]
    ok(all(l.startswith(">") or l == "" for l in note.split("\n")),
       "every line of the note is quoted, so it cannot be mistaken for the rule")

    # -- the numbers in the note are the measured ones ---------------------
    for n in ("4,525", "32 CRLF and 26 LF", "379 bytes", "f2713e9"):
        ok(n in NEW, f"the note carries the measured value {n!r}")
    # 4,453 was a sandbox count and must not reappear anywhere.
    ok("4,453" not in NEW, "the sandbox-derived 4,453 does not reappear")

    # -- the note must not itself assert a new constant --------------------
    ok("Do not replace this with" in NEW,
       "the note warns against swapping one constant for another")
    ok("`.pre_*` sidecars are gitignored" in NEW,
       "the sidecar exception is stated, since those stay CRLF on purpose")

    # -- prove the anchor check can fail -----------------------------------
    damaged = text.replace(OLD, "**gone**\n", 1)
    ok(damaged.count(OLD) == 0,
       "check() can fail: removing the rule makes it uncountable")

    # -- round trip --------------------------------------------------------
    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
    lone = data.count(bytes([10])) - data.count(bytes([13, 10]))
    ok(data.count(bytes([13, 10])) == 0 and lone > 0,
       f"the written file stays LF ({lone} LF, 0 CRLF)")

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
