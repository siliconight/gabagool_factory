"""Item 52's retirement of the enemy-enemy exclusion is REVERSED.

WHY THIS PATCH EXISTS
---------------------
Item 52 retired "exclude enemy-enemy pairs from the opening budget" on the
grounds that `LT_OPEN_SIGHTLINE` names those lines with coordinates and a
remedy, so excluding them deletes cover the grader requests.

That change was then re-derived from scratch and shipped in lot 0.44.0
WITHOUT this item being read. The roadmap had already done the analysis.
That method failure is recorded in the item, not hidden.

The retirement is reversed on PRECEDENCE, not on evidence: Laser Tag is
advisory, Lot builds the level, and `Enemy_*` is leaving Lot for the
gameplay layer. Item 52's factual claim was never refuted -- nobody counted
LT_OPEN_SIGHTLINE patched-vs-reverted. The item says so.

HOW IT ANCHORS
--------------
STRUCTURALLY. Nothing is matched against text transcribed by hand:

  1. locate the line matching ^\\*\\*52\\. by regex  (the item heading form
     that `tools/roadmap_status.py` itself defines as `_ITEM`)
  2. its block runs to the next ^\\*\\*<digits>\\.  or EOF
  3. inside that block, find the ONE line whose stripped form ends
     "Retired." -- refuse unless exactly one
  4. walk UP from the heading to the nearest `*STATUS:` line and edit it
     in place, preserving whatever trailing `*` run it already has

Because step 4 rebuilds the status line from what is on disk, the long
prose in it is never retyped.

USAGE
    python patches\\patch_roadmap_52_reversal.py --check
    python patches\\patch_roadmap_52_reversal.py --selftest
    python patches\\patch_roadmap_52_reversal.py
    python patches\\patch_roadmap_52_reversal.py --revert
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

TAG = "r54rev52"
ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "PIPELINE_ROADMAP.md"
FILES = (DOC,)

ITEM_NUM = 52
_ITEM = re.compile(r"^\*\*(\d+)\. (.*)$")
_STATUS_HEAD = "*STATUS:"
RETIRED_SUFFIX = "Retired."

#: appended inside the status line, before its trailing `*` run
STATUS_CLAUSE = (" Its retirement of the enemy-enemy exclusion is REVERSED "
                 "2026-08-17 on precedence, not on evidence -- see the "
                 "reversal below")

MARKER = "**REVERSED 2026-08-17. LOT OUTRANKS THE GRADER.**"

BLOCK = """\

**REVERSED 2026-08-17. LOT OUTRANKS THE GRADER.** The retirement above is
withdrawn. It rested on `LT_OPEN_SIGHTLINE` naming those lines with a
remedy -- that is, on the grader's request being authoritative. It is not.
Laser Tag is advisory, Lot builds the level, and enemy placement is leaving
Lot for the gameplay layer, so a request phrased in `Enemy_*` markers
cannot bind Lot's budget.

**WHAT WAS MEASURED FIRST.** The shipped export carried 16 pieces, each
recording the pair it was placed for:

```
11  route@N -> Enemy_M            the route pass
 3  Enemy_M -> LT_ObjectivePoint
 2  Enemy_M -> Enemy_N
 0  anything touching LT_PlayerSpawn
```

15 of 16 pieces are placed against an `Enemy_*` point. `open_sightlines` is
all-pairs, so K enemies contribute C(K,2) lines. The enemy markers are
functioning as a six-sample approximation of "somewhere a shooter could
stand" -- which is why removing them does not merely trim the budget, it
removes most of the planner's question.

**SEED-MATCHED, BOTH DIRECTIONS, SAME THREE CANDIDATES.** Reverted, re-run,
read per seed, re-applied, re-read -- and the second patched read reproduced
the first exactly, with every stage cache-hitting, so the numbers are not a
rebuild artefact:

```
seed   reverted (placed, route_open)   patched     what moved
5017   (9, 3)   one enemy-enemy        (8, 3)      waste removed, no cost
5118   (9, 0)   one enemy-enemy        (9, 0)      freed slot went to the
                                                   ROUTE: enemy-route 4 -> 5
5219   (16, 14) two enemy-enemy        (14, 15)    one route stretch left open
```

**THE COST IS REAL AND IS NOT ARGUED AWAY.** On seed_5219 `route_open` goes
14 -> 15. One of the two enemy-enemy crates was incidentally blocking a
route line, and the route pass did not replace it because its own density
cap (`ROUTE_METRES_PER_PIECE`) was already met -- the same cap that made
the spare-budget change above wrong. Mission findings went 51 -> 50 across
the three candidates.

**WHAT WAS NOT DONE, STATED PLAINLY.** Which finding disappeared was not
isolated, and `LT_OPEN_SIGHTLINE` was NOT counted patched-versus-reverted
per seed. Item 52's claim that excluding these pairs deletes cover the
grader asks for is therefore UNREFUTED on its own terms. It is overruled
because Lot outranks Laser Tag, not because it was shown to be wrong. If
that ordering is ever revisited, this is the measurement to take first.

**METHOD FAILURE WORTH RECORDING.** The exclusion was re-derived from
scratch and shipped before this item was read. The roadmap had already
analysed it, with the grader's coordinates, and retired it -- and this item
also already carried `seed_5219 placed 16 ... route_open 14`, the exact
"before" numbers that were re-measured with a full pipeline run. Same
failure as item 3. The measurement got done; the search did not.

**SHIPPED** in lot 0.44.0, `site_cover.py`, inside `plan_cover`'s nested
`outstanding()`. Deliberately NOT in `open_sightlines`, which is byte-
identical and still returns every pair, so Laser Tag and
`level_factory/packages/validation/` see exactly what they saw.

**WHAT ACTUALLY DECOUPLES LOT.** Re-pose the question on standable ground:
cover the stretches of the crew's route visible from anywhere a shooter
could legally stand within `OPENING_RANGE`, rather than from six sampled
enemy points. That removes `Enemy_*` from `cover_points` altogether. Not
attempted.
"""


def _sidecar(p: Path) -> Path:
    return p.with_name(p.name + ".pre_" + TAG)


def _eol(p: Path) -> str:
    """Keyed off the FILE. Refuses on mixed or bare CR."""
    b = p.read_bytes()
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    cr = b.count(b"\r") - crlf
    if cr:
        raise SystemExit(f"REFUSING: {p.name} contains {cr} bare CR")
    if crlf and lf:
        raise SystemExit(
            f"REFUSING: {p.name} has mixed endings ({crlf} CRLF, {lf} LF)")
    return "\r\n" if crlf else "\n"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()[:16]


def _locate(lines):
    """-> (item_index, block_end_exclusive, retired_index, status_index)."""
    heads = [i for i, ln in enumerate(lines)
             if (m := _ITEM.match(ln)) and int(m.group(1)) == ITEM_NUM]
    if len(heads) != 1:
        raise SystemExit(
            f"REFUSING: {len(heads)} heading(s) match **{ITEM_NUM}. , expected 1")
    i = heads[0]

    end = len(lines)
    for j in range(i + 1, len(lines)):
        if _ITEM.match(lines[j]):
            end = j
            break

    retired = [j for j in range(i, end)
               if lines[j].strip().endswith(RETIRED_SUFFIX)]
    if len(retired) != 1:
        raise SystemExit(
            f"REFUSING: {len(retired)} line(s) in item {ITEM_NUM} end "
            f"{RETIRED_SUFFIX!r}, expected 1. Already applied, or drifted.")

    status = None
    for j in range(i - 1, max(-1, i - 6), -1):
        if lines[j].lstrip().startswith(_STATUS_HEAD):
            status = j
            break
    if status is None:
        raise SystemExit(
            f"REFUSING: no {_STATUS_HEAD} line within 5 lines above "
            f"**{ITEM_NUM}.")
    return i, end, retired[0], status


def _restatus(line: str) -> str:
    """Append the clause INSIDE the line's existing trailing `*` run."""
    stripped = line.rstrip()
    n = 0
    while n < len(stripped) and stripped[len(stripped) - 1 - n] == "*":
        n += 1
    body = stripped[:len(stripped) - n] if n else stripped
    tail = stripped[len(stripped) - n:] if n else ""
    if body.endswith("."):
        body = body[:-1]
    return body + STATUS_CLAUSE + tail


def transform(text: str) -> str:
    if MARKER in text:
        raise SystemExit("REFUSING: the reversal marker is already present")
    lines = text.split("\n")
    _i, _end, retired, status = _locate(lines)

    out = list(lines)
    out[status] = _restatus(out[status])
    block = BLOCK.split("\n")
    if block and block[-1] == "":
        block = block[:-1]
    for b in block:
        if _ITEM.match(b):
            raise SystemExit(
                f"REFUSING: the inserted block contains an item heading: {b!r}")
    return "\n".join(out[:retired + 1] + block + out[retired + 1:])


def _rs():
    sys.path.insert(0, str(ROOT / "tools"))
    import roadmap_status
    return roadmap_status


def check() -> int:
    if not DOC.exists():
        print(f"  missing: {DOC}")
        return 1
    text = DOC.read_text(encoding="utf-8")
    lines = text.split("\n")
    print(f"marker already present: {MARKER in text}")
    try:
        i, end, retired, status = _locate(lines)
    except SystemExit as exc:
        print(f"  {exc}")
        print("\nNOT APPLICABLE")
        return 1
    print(f"item {ITEM_NUM} heading at line {i + 1}, block ends line {end}")
    print(f"  status line at {status + 1}: {lines[status][:88]}...")
    print(f"  'Retired.' line at {retired + 1}: {lines[retired].strip()[:88]}")
    b = DOC.read_bytes()
    eol = _eol(DOC)
    print(f"\n{DOC.name}  {len(b)} B  sha256 {_sha(b)}  "
          f"eol {'CRLF' if eol != chr(10) else 'LF'}")
    out = transform(text)
    nb = out.replace("\n", eol).encode("utf-8")
    print(f"APPLICABLE: {len(b)} -> {len(nb)} B  ({len(nb) - len(b):+d})")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(("[ok]  " if cond else "[FAIL]  ") + label)
        if not cond:
            fails.append(label)

    ok(DOC.exists(), "PIPELINE_ROADMAP.md exists")
    if fails:
        return 1
    old = DOC.read_text(encoding="utf-8")
    ok(_eol(DOC) == "\n", "the roadmap is LF")

    lines = old.split("\n")
    i, end, retired, status = _locate(lines)
    ok(True, f"item {ITEM_NUM} located structurally at line {i + 1}")
    ok(lines[status].startswith("*STATUS: CLOSED"),
       f"item {ITEM_NUM}'s status is CLOSED (it is: "
       f"{lines[status].split(' -- ')[0][:40]!r})")

    # the 'Retired.' anchor must be unique in the item AND we report how many
    # times the bare word occurs in the whole document, for comparison
    doc_retired = sum(1 for ln in lines if ln.strip().endswith(RETIRED_SUFFIX))
    print(f"        (lines ending 'Retired.': {doc_retired} in the document, "
          f"1 required inside item {ITEM_NUM})")
    ok(True, "the anchor is scoped to item 52's block, not the document")

    new = transform(old)

    ok(new.count(MARKER) == 1, "the reversal marker appears exactly once")
    grew = len(new.split("\n")) - len(lines)
    blk = [b for b in BLOCK.split("\n")]
    if blk and blk[-1] == "":
        blk = blk[:-1]
    ok(grew == len(blk), f"line count grew by {grew}, derived expectation {len(blk)}")

    # the status line: still parseable, still CLOSED, clause added once
    nlines = new.split("\n")
    ns = nlines[status]
    ok(ns.startswith("*STATUS: CLOSED"), "the status line still reads CLOSED")
    ok(ns.count("REVERSED 2026-08-17") == 1, "the clause was added once")
    ok(ns.endswith(lines[status].rstrip()[-1]),
       f"the status line's trailing character is preserved "
       f"({lines[status].rstrip()[-1]!r})")

    # no new item numbers, and the parser agrees
    before_heads = sum(1 for ln in lines if _ITEM.match(ln))
    after_heads = sum(1 for ln in nlines if _ITEM.match(ln))
    ok(before_heads == after_heads,
       f"item headings unchanged: {before_heads} -> {after_heads}")

    try:
        rs = _rs()
        b_items = rs.parse(old)
        a_items = rs.parse(new)
        ok(len(b_items) == len(a_items),
           f"roadmap_status.parse agrees: {len(b_items)} -> {len(a_items)} items")
        # KEY-AGNOSTIC. The dict keys were never read, so nothing here names
        # one. The DERIVED TABLE is the thing that must not move: only prose
        # changed, so render() must be byte-identical.
        rb, ra = rs.render(b_items), rs.render(a_items)
        ok(rb == ra, f"the derived table is byte-identical "
                     f"({len(rb)} B -> {len(ra)} B)")
        ok("CLOSED" in rb, "the derived table mentions CLOSED at all "
                           "(sanity: render() produced real content)")
    except Exception as exc:
        import traceback
        ok(False, f"roadmap_status parses the result ({type(exc).__name__}: {exc})")
        print(traceback.format_exc())

    # idempotence
    try:
        transform(new)
        ok(False, "re-applying refuses")
    except SystemExit:
        ok(True, "re-applying refuses")

    print("\n" + ("SELFTEST PASSED" if not fails
                  else f"SELFTEST FAILED: {len(fails)}"))
    return 1 if fails else 0


def apply() -> int:
    if not DOC.exists():
        raise SystemExit(f"REFUSING: missing {DOC}")
    if _sidecar(DOC).exists():
        raise SystemExit(f"REFUSING: {_sidecar(DOC).name} exists. Use --revert.")
    old_b = DOC.read_bytes()
    eol = _eol(DOC)
    out = transform(DOC.read_text(encoding="utf-8"))
    new_b = out.replace("\n", eol).encode("utf-8")
    _sidecar(DOC).write_bytes(old_b)
    DOC.write_text(out, encoding="utf-8", newline=eol)
    print(f"{DOC.name}")
    print(f"  {len(old_b)} B  sha256 {_sha(old_b)}")
    print(f"  {len(new_b)} B  sha256 {_sha(new_b)}   ({len(new_b) - len(old_b):+d})")
    print(f"  sidecar: {_sidecar(DOC).name}")
    print("\nNEXT:")
    print("    python tools\\roadmap_status.py --write")
    print("    python tools\\roadmap_status.py --check")
    return 0


def revert() -> int:
    s = _sidecar(DOC)
    if not s.exists():
        raise SystemExit(f"REFUSING: no {s.name} to revert from")
    b = s.read_bytes()
    DOC.write_bytes(b)
    s.unlink()
    print(f"reverted {DOC.name} to {len(b)} B sha256 {_sha(b)}")
    return 0


def main(argv) -> int:
    arg = argv[1] if len(argv) > 1 else ""
    if arg == "--check":
        return check()
    if arg == "--selftest":
        return selftest()
    if arg == "--revert":
        return revert()
    if arg:
        raise SystemExit(f"unknown argument {arg!r}; "
                         f"use --check, --selftest, --revert, or no argument")
    return apply()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
