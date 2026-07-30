"""Close the hole in the reconstruction rule: line endings.

The Grounding rule now says to rebuild a stale file from its nearest clean
ancestor plus the patches that followed, and to confirm the rebuild by byte
count. That verification is the load-bearing part -- a count landing exactly on
the device's figure is not coincidence at four significant figures -- and it
fails for a reason that has nothing to do with staleness.

Python reads text with universal newlines. A file stored CRLF comes back with
every "\\r\\n" collapsed to "\\n", so len(text) is short by exactly one byte per
line. `lot.py.pre_accessor` read as 81,669 characters against 83,419 bytes on
disk: a 1,750-byte gap that is precisely its 1,750 CRLFs, and for a few minutes
it looked like the reconstruction had failed.

So the rule has to say how to compare. Both of these are correct:

    len(text.replace("\\n", "\\r\\n").encode("utf-8"))     # restore the endings
    len(text.encode("utf-8")) + text.count("\\n")          # or add the count back

and reading the ancestor with `read_bytes()` before decoding avoids the trap
entirely, which is what the amended rule recommends.

Asserts its anchor, refuses on a miss, idempotent.
"""
import pathlib

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
MD = ROOT / "CLAUDE.md"

ANCHOR = """Both files above reconstructed to delta zero. Do that before
declaring a file unreadable; ask only when no clean ancestor exists.
"""

ADD = """Both files above reconstructed to delta zero. Do that before
declaring a file unreadable; ask only when no clean ancestor exists.

**Compare bytes, not characters, or the check fails for the wrong reason.** These
files are CRLF and Python reads text with universal newlines, so `len(text)` is
short by exactly one byte per line — `lot.py.pre_accessor` read as 81,669
characters against 83,419 bytes on disk, a 1,750-byte gap that is precisely its
1,750 CRLFs. Read the ancestor with `read_bytes()` and normalise deliberately, or
restore the endings before measuring:

    len(text.replace("\\n", "\\r\\n").encode("utf-8"))     # restore, then count
    len(text.encode("utf-8")) + text.count("\\n")          # equivalent

Git's `autocrlf` means a file's on-disk endings can also change under you between
sessions without its content changing at all, so a byte count is evidence about
one working tree at one moment. When it disagrees by roughly the line count,
suspect the endings before suspecting the bridge.
"""


def main() -> int:
    if not MD.exists():
        raise SystemExit(f"missing {MD}. Nothing written.")
    src = MD.read_text(encoding="utf-8")
    if "Compare bytes, not characters" in src:
        print("CLAUDE.md: already carries the line-ending amendment.")
        return 0
    if src.count(ANCHOR) != 1:
        raise SystemExit(
            f"CLAUDE.md: the reconstruction anchor appears {src.count(ANCHOR)} "
            f"time(s), expected exactly 1. Run patch_claude_md.py first, or read "
            f"the file. NOTHING WRITTEN.")
    backup = MD.with_suffix(".md.pre_endings")
    if not backup.exists():
        backup.write_bytes(MD.read_bytes())
    out = src.replace(ANCHOR, ADD)
    MD.write_text(out, encoding="utf-8")
    print(f"CLAUDE.md: Grounding now says how to compare a reconstruction "
          f"({len(src)} -> {len(out)} characters)")
    print(f"CLAUDE.md: previous file kept at {backup.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
