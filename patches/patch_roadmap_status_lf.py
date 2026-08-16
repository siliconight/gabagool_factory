#!/usr/bin/env python3
"""roadmap_status.py --write rewrites every line ending in the document.

WHAT IS WRONG

    175:  text = DOC.read_text(encoding="utf-8", errors="replace")
    209:  DOC.write_text(text.replace(current, block), encoding="utf-8")

`read_text` opens with universal newlines, so whatever the file used arrives in
memory as `\\n`. `write_text` opens in text mode with `newline=None`, so Python
translates every `\\n` back out to `os.linesep` -- `\\r\\n` on Windows. The round
trip looks lossless in Python and rewrites all 4,525 line endings on disk.

MEASURED 2026-08-16. `PIPELINE_ROADMAP.md` was renormalised to LF, a patch
applied cleanly and reported `0 CRLF, 4525 lone LF`, then
`roadmap_status.py --write` ran and the file came back 4,525 CRLF and 277,331
bytes against 272,802 in the repository -- a 4,529-byte phantom. `git status`
said NOTHING, because git compares through the `text=auto eol=lf` clean filter
and sees no difference. That silence is why this survived: the conventions
require `--write` after every roadmap edit, so it has been happening on every
one, and only `.gitattributes` made git start announcing it.

THE FIX IS `newline=""`, which disables translation and writes the string's
own `\\n` verbatim. It does NOT key the ending off the file, because `read_text`
has already destroyed that information by the time line 209 runs -- preserving
would mean changing the read to `read_bytes` and detecting, which is a larger
change to a tool that rewrites a 277 KB document. LF is now canonical
repo-wide (`.gitattributes`, commit f2713e9), so writing LF unconditionally is
the correct behaviour rather than merely the convenient one.

NOT FIXED HERE, AND WORTH A LOOK: line 175 reads with `errors="replace"`, and
line 209 writes the result back. Any byte that fails to decode is silently
replaced with U+FFFD and then PERSISTED over the original on the next
`--write`. Nothing has hit it, and this patch does not touch it, but a
lossy-read-then-write-back on the project's largest document is a live hazard.

USAGE

    python patches\\patch_roadmap_status_lf.py --check
    python patches\\patch_roadmap_status_lf.py --selftest
    python patches\\patch_roadmap_status_lf.py
    python patches\\patch_roadmap_status_lf.py --revert
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r52statuslf"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "tools" / "roadmap_status.py"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)

EXPECT_BYTES = 8954


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


def _n(t: str) -> str:
    return t.replace("\r\n", "\n")


OLD = '''    if "--write" in argv:
        DOC.write_text(text.replace(current, block), encoding="utf-8")
        print(f"  rewrote the generated block in {DOC.name}")
'''

NEW = '''    if "--write" in argv:
        # `newline=""` or this rewrites every line ending in the document.
        # `read_text` above opens with universal newlines, so the file arrives
        # as `\\n` whatever it was on disk; `write_text` with the default
        # `newline=None` translates those back out to `os.linesep`, which is
        # `\\r\\n` on Windows. Measured 2026-08-16: the roadmap went from
        # 0 CRLF / 4,525 LF to 4,525 CRLF in a single `--write`, 277,331 bytes
        # on disk against 272,802 in the repository -- and `git status` stayed
        # SILENT, because git compares through the `text=auto eol=lf` clean
        # filter and saw no change. The conventions require `--write` after
        # every roadmap edit, so this fired on all of them.
        #
        # This writes LF rather than restoring what the file had, because
        # `read_text` has already discarded that by the time we get here, and
        # LF is canonical repo-wide since `.gitattributes` (f2713e9).
        DOC.write_text(text.replace(current, block), encoding="utf-8",
                       newline="")
        print(f"  rewrote the generated block in {DOC.name}")
'''

EDITS = [("roadmap_status.py --write: stop translating line endings", OLD, NEW)]


def _load():
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET} does not exist.")
    raw = TARGET.read_bytes()
    return raw, _eol(raw), _n(raw.decode("utf-8"))


def _identity(raw: bytes):
    crlf = raw.count(b"\r\n")
    lone = raw.count(b"\n") - crlf
    mark = "" if len(raw) == EXPECT_BYTES else "   <-- not the size this was read against"
    print(f"  {TARGET.relative_to(ROOT)}")
    print(f"    bytes  : {len(raw)}   (expected {EXPECT_BYTES}){mark}")
    print(f"    sha256 : {_sha(raw)}")
    print(f"    endings: {crlf} CRLF, {lone} lone LF")


def check() -> int:
    raw, _e, text = _load()
    _identity(raw)
    print()
    n = text.count(OLD)
    print(f"  [{'ok' if n == 1 else 'MISSING'}]  the --write branch (found {n})")
    print()
    print("APPLICABLE." if n == 1
          else "NOT APPLICABLE: refusing rather than fuzzy-matching.")
    return 0 if n == 1 else 1


def apply() -> int:
    raw, eol, text = _load()
    _identity(raw)
    if text.count(OLD) != 1:
        raise SystemExit("REFUSING: the --write branch is not present exactly "
                         "once. Nothing written.")
    if SIDECAR.exists():
        raise SystemExit(f"REFUSING: {SIDECAR.name} exists. Use --revert.")
    shutil.copy2(TARGET, SIDECAR)
    out = text.replace(OLD, NEW, 1)
    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
    TARGET.write_bytes(data)
    print()
    print(f"  {len(raw)} -> {len(data)} B  ({len(data) - len(raw):+d})")
    print(f"  sha256 {_sha(data)}")
    print()
    print("  NEXT -- the roadmap on disk is still CRLF from the last --write.")
    print("  Re-run it and confirm the endings hold:")
    print()
    print("    python tools\\roadmap_status.py --write")
    print("    python tools\\roadmap_status.py --check")
    print("    git status --short        # expect the roadmap to now show as "
          "MODIFIED")
    print("    git add -A; git commit -m \"roadmap_status --write no longer "
          "rewrites every line ending\"")
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
    ok(text.count(OLD) == 1, "the --write branch is present exactly once")

    # The read side must still be the thing that makes this necessary; if it
    # ever becomes read_bytes, the reasoning in the comment stops being true.
    ok('text = DOC.read_text(encoding="utf-8", errors="replace")' in text,
       "line 175 still reads with read_text, which is why newline= is needed")

    out = text.replace(OLD, NEW, 1)
    ok(out != text, "the edit changes the file")
    # Counted on CODE lines only: the comment added above quotes `newline=""`
    # in prose, so a bare count reads 2. Seventh time in this arc that a naive
    # count has been wrong about text its own documentation contains.
    code = "\n".join(l for l in out.split("\n") if not l.lstrip().startswith("#"))
    ok(code.count('newline=""') == 1,
       f"exactly one newline=\"\" reaches the CODE "
       f"(bare count including the comment is {out.count(chr(110)+chr(101)+chr(119)+chr(108)+chr(105)+chr(110)+chr(101)+chr(61)+chr(34)+chr(34))})")
    ok(out.count("DOC.write_text(") == 1,
       "there is still exactly one write of the document")
    ok('DOC.write_text(text.replace(current, block), encoding="utf-8")\n'
       not in out,
       "no untranslated write_text call is left behind")

    try:
        compile(out, str(TARGET), "exec")
        ok(True, "roadmap_status.py compiles after the edit")
    except SyntaxError as exc:
        ok(False, f"roadmap_status.py compiles after the edit ({exc})")

    # -- BEHAVIOURAL: prove the bug is real and the fix removes it ---------
    # Both forms are exercised against a temp file rather than argued about.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "doc.md"
        p.write_bytes(b"alpha\nbeta\ngamma\n")          # LF on disk
        loaded = p.read_text(encoding="utf-8")          # universal newlines
        ok("\r" not in loaded, "read_text hands back no CR, whatever was on disk")

        p.write_text(loaded, encoding="utf-8")          # the OLD behaviour
        old_bytes = p.read_bytes()
        p.write_bytes(b"alpha\nbeta\ngamma\n")
        p.write_text(loaded, encoding="utf-8", newline="")   # the NEW behaviour
        new_bytes = p.read_bytes()

        import os
        if os.linesep == "\r\n":
            ok(old_bytes.count(b"\r\n") == 3,
               f"OLD form translates LF -> CRLF here ({old_bytes!r})")
        else:
            print(f"        (this host's os.linesep is {os.linesep!r}, so the "
                  f"OLD form is a no-op here; the bug is Windows-specific and "
                  f"was measured on the real tree)")
        ok(new_bytes == b"alpha\nbeta\ngamma\n",
           f"NEW form writes the string verbatim ({new_bytes!r})")
        ok(b"\r" not in new_bytes, "and introduces no CR on any platform")

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
