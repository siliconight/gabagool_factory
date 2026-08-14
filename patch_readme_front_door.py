r"""Fix the two things in README.md that are wrong for somebody else.

    python patch_readme_front_door.py --check
    python patch_readme_front_door.py
    python patch_readme_front_door.py --selftest   (run it AFTER applying)
    python patch_readme_front_door.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

TWO DEFECTS, BOTH IN THE FIRST THING A NEW PERSON READS.

1. THE COUNT IS WRONG. The opening sentence says "nine standalone tools".
   `factory.manifest.json` pins TEN: deli_counter, dispatch, laser_tag,
   level_factory, lot, lux, patina, pipeline, pixelcoat, zoo. A reader who
   counts the directories and gets a different number than the front door
   claims now has to work out which one is lying, on their first minute in
   the repo.

   The fix does not hard-code "ten" either -- it says "the tools pinned in
   `factory.manifest.json`", so the sentence cannot go stale again the next
   time a tool is added. A number that has to be maintained by hand is a
   number that will be wrong; this repo already proved that with the DAG
   table.

2. THE LOCKSTEP COMMAND ONLY WORKS ON YOUR MACHINE.

       level-factory verify-manifest --factory C:\Projects\gabagool_studios\gabagool_factory

   That absolute path is the author's checkout. Anyone else who copies the
   command gets a path that does not exist, and the instruction that proves
   the tool set is consistent is the one instruction they cannot run. `.` is
   the correct argument when you are standing in the factory root, which is
   where the README already assumes you are.

WHAT IT DOES NOT TOUCH. The two-layer versioning explanation and the release
flow are correct and stay as they are. This is a two-line correction to the
front door, not a rewrite.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("README.md")
SIDECAR = ".pre_frontdoor"

OLD_COUNT = """The Siliconight tool factory: nine standalone tools that build DD
missions, plus the coordination layer that versions them as a SET."""

NEW_COUNT = """The Siliconight tool factory: the standalone tools pinned in
`factory.manifest.json` that build DD missions, plus the coordination layer
that versions them as a SET. The manifest is the authority on which tools are
in the certified set -- deliberately not a number typed here, because a count
maintained by hand is a count that goes stale."""

OLD_CMD = r"    level-factory verify-manifest --factory C:\Projects\gabagool_studios\gabagool_factory"

NEW_CMD = r"""    level-factory verify-manifest --factory .

(run from the factory root; `.` is the checkout you are standing in, whoever
you are and wherever you cloned it)"""

EDITS = ((OLD_COUNT, NEW_COUNT), (OLD_CMD, NEW_CMD))

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _find(body: str, anchor: str):
    candidate = _as(anchor, _eol(body))
    return candidate, body.count(candidate)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def selftest(root: Path) -> int:
    import json
    bad = 0
    readme = (root / TARGET).read_text(encoding="utf-8")
    manifest = json.loads((root / "factory.manifest.json").read_text(
        encoding="utf-8"))
    tools = manifest.get("tools", {})

    print(f"  manifest pins {len(tools)} tool(s): {', '.join(sorted(tools))}")

    for word in ("nine standalone tools", "ten standalone tools"):
        if word in readme:
            print(f"  FAIL README still hard-codes a count: {word!r}")
            bad += 1
    if "factory.manifest.json`" not in readme.split("## Start here")[0]:
        print("  FAIL the opening does not point at the manifest")
        bad += 1
    else:
        print("  ok   the opening defers to factory.manifest.json")

    if r"C:\Projects" in readme:
        print(r"  FAIL README still contains an absolute C:\Projects path")
        bad += 1
    else:
        print("  ok   no machine-specific path left in the README")

    # The directories that actually exist, against the pins.
    on_disk = {p.name for p in root.iterdir()
               if p.is_dir() and not p.name.startswith((".", "_"))}
    missing = sorted(t for t in tools
                     if t not in on_disk and t.replace("_", "") not in on_disk)
    if missing:
        print(f"  NOTE pinned but no directory here: {', '.join(missing)}")
        print("       (expected if you have not cloned every tool repo)")

    print()
    print("  the front door is honest" if not bad else f"  {bad} problem(s)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    path = root / TARGET
    if not path.is_file():
        raise SystemExit(f"cannot find {TARGET} under {root} -- run from the "
                         f"factory root")

    if "--selftest" in argv:
        return selftest(root)

    side = path.with_suffix(path.suffix + SIDECAR)
    if "--revert" in argv:
        if not side.is_file():
            print(f"  no sidecar for {path.name}")
            return 1
        path.write_bytes(side.read_bytes())
        print(f"  reverted     {path.name}")
        return 0

    raw = path.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)

    done = sum(1 for _o, new in EDITS if _find(body, new)[1] == 1)
    if done == len(EDITS):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(EDITS)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in EDITS:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()[:70]!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: the edit would leave {bare} bare LF line(s) in a "
              f"CRLF document.")
        return 1

    if "--check" in argv:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0

    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
