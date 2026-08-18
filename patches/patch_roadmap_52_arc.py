"""Item 52 gains the arc-exposure measurement.

WHAT THIS RECORDS
-----------------
The standable-ground re-posing named at the end of item 52 was scoped and
probed READ-ONLY against all three `lot_demo_001` candidates on 2026-08-17.
No code shipped. Three results worth keeping:

  * the obvious metric ("count exposed route samples") SATURATES -- every
    sample is already exposed under six enemies, so it carries no information
  * arc exposure DISCRIMINATES, and shows six enemy points occupy ~4% of the
    bearings a shooter could occupy
  * today's placement reduces arc by ~10% on every seed regardless of
    geometry, while a greedy arc-maximising placement reaches 2.4x-3.4x that
    with FEWER pieces

HOW IT ANCHORS
--------------
Structurally, like the reversal patch before it. It locates `**52. ` by the
regex `tools/roadmap_status.py` itself defines, scopes to that item's block,
finds the ONE line that strips to "attempted." -- the last line of the
reversal block, which currently claims the re-posing was not attempted --
rewrites that line, and inserts the measurement after it.

Nothing is matched against text transcribed by hand.

USAGE
    python patches\\patch_roadmap_52_arc.py --check
    python patches\\patch_roadmap_52_arc.py --selftest
    python patches\\patch_roadmap_52_arc.py
    python patches\\patch_roadmap_52_arc.py --revert
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

TAG = "r56arc"
ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "PIPELINE_ROADMAP.md"
FILES = (DOC,)

ITEM_NUM = 52
_ITEM = re.compile(r"^\*\*(\d+)\. (.*)$")
_STATUS_HEAD = "*STATUS:"
ANCHOR = "attempted."
ANCHOR_NEW = ("attempted as code. SCOPED AND MEASURED 2026-08-17 -- "
              "see directly below.")

MARKER = "**MEASURED 2026-08-17. THE OBVIOUS METRIC IS REFUTED.**"

BLOCK = """\

**MEASURED 2026-08-17. THE OBVIOUS METRIC IS REFUTED.** The re-posing above
was scoped and probed read-only against all three `lot_demo_001` candidates.
No code shipped.

**THE SAMPLER IS FREE.** Lot already knows where a body can stand --
`site_spawns.outdoors` is two point-in-rect tests -- and sweeping the route
band at 5 m x 5 m yields 353-713 standable posts in 0.00 s. Cost was never
the obstacle.

**BOOLEAN EXPOSURE SATURATES**, so "count exposed route samples instead of
pairs" is dead on arrival:

```
seed   posts pairs_e pairs_p exposed_e exposed_p samples budget
5017    371      27    1381         9         9       9      7
5118    353      25    1014         8         8       8      6
5219    713      51    3902        16        16      16     11
```

Every route sample is ALREADY exposed under the six enemy points -- 9/9, 8/8,
16/16 -- so the posts add nothing and the number is pinned at maximum. Pairs
fail in the other direction: 3902 against a route budget of 11.

**ARC EXPOSURE DISCRIMINATES.** Bin each sample's threat bearings into 72
slices of 5 degrees and measure what fraction of the full 360 holds a shooter
with a clear line:

```
seed  mean_enemies  mean_posts  at_full_360   spread (posts)
5017      4.0%        68.2%        0 / 9        43% .. 93%
5118      4.2%        65.8%        0 / 8        44% .. 90%
5219      4.3%        79.7%        0 / 16       51% .. 99%
```

`mean_enemies ~ 4%` is the number this item was missing. **Six enemy points
occupy about three of seventy-two bearings.** Lot has been planning cover
against a 4% sample of the directions a shooter could come from, which is the
quantitative form of "15 of 16 pieces are placed against an `Enemy_*` point".

**TODAY'S PLACEMENT IS NEAR-RANDOM AGAINST ARC.** Scoring the pieces Lot
actually placed, against a greedy arc-maximising placement on the same
budget:

```
seed  budget  placed  before   after today     after greedy    greedy cost
5017     7       8     68.2%   57.4%  (-10.8)  34.1%  (-34.1)     3.0 s
5118     6       9     65.8%   55.4%  (-10.4)  41.0%  (-24.8)     1.6 s
5219    11      14     79.7%   69.8%  ( -9.9)  46.4%  (-33.2)    31.1 s
```

Today's placement reduces arc by ~10% on EVERY seed regardless of geometry.
That flatness is what optimising a 4% sample looks like. Greedy reaches
2.4x-3.4x the reduction using FEWER pieces every time -- 7 against 8, 6
against 9, 11 against 14.

**WHAT THIS DOES NOT ESTABLISH.** The greedy figure is an UPPER BOUND from a
capped 250-candidate set with no separation or legality constraints beyond
`_piece_rect`; a real planner lands below it. Greedy scoring cost 31.1 s on
seed_5219 against `assemble`'s own 0.18 s, so restricting candidates to the
neighbourhood of high-exposure samples is MANDATORY rather than an
optimisation. The opening pass has not been analysed under arc at all --
only the route pass. Nothing was tried on any mission but `lot_demo_001`.

**METHOD NOTE.** The first sweep measured Lot's DECLARED-footprint fallback
without noticing. `package._find_asset` looks for a `.glb` next to the site
spec and then in `<dc>/build/<name>`; the spec names `buildings/<stem>.glb`,
the library stores `<stem>.glb` at `build/` root, and the pipeline's temp dir
had been cleaned of its staged copies -- so neither path resolved and
`assemble` degraded in silence. The probe now stages the geometry itself and
REFUSES to report numbers if `LOT_OCCLUDERS_DECLARED` fired. With staging it
reproduces the recorded run exactly: `LOT_COVER_PLACED 14`,
`LOT_ROUTE_COVER_PLACED 11 of 14`, `LOT_ROUTE_EXPOSED 15` against the
artifact's `placed 14` / `route_open 15`. Saturation was present in both
readings, so the refutation did not depend on the faulty one. Luck, not
method.

Probe: `_scratch/probe_standable_sweep.py` -- read-only, stages its own
geometry, about 35 s for all three seeds.
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

    retired = [j for j in range(i, end) if lines[j].strip() == ANCHOR]
    if len(retired) != 1:
        raise SystemExit(
            f"REFUSING: {len(retired)} line(s) in item {ITEM_NUM} strip to "
            f"{ANCHOR!r}, expected 1. Already applied, or drifted.")

    status = None
    for j in range(i - 1, max(-1, i - 6), -1):
        if lines[j].lstrip().startswith(_STATUS_HEAD):
            status = j
            break
    if status is None:
        raise SystemExit(
            f"REFUSING: no {_STATUS_HEAD} line within 5 lines above "
            f"**{ITEM_NUM}.")
    # This patch does NOT touch the status line. Item 52 is already CLOSED and
    # already carries the reversal; this is evidence appended to it.
    return i, end, retired[0], status


def transform(text: str) -> str:
    if MARKER in text:
        raise SystemExit("REFUSING: the reversal marker is already present")
    lines = text.split("\n")
    _i, _end, retired, status = _locate(lines)

    out = list(lines)
    indent = out[retired][:len(out[retired]) - len(out[retired].lstrip())]
    out[retired] = indent + ANCHOR_NEW
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
    print(f"  anchor line at {retired + 1}: {lines[retired].strip()[:88]}")
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

    doc_anchor = sum(1 for ln in lines if ln.strip() == ANCHOR)
    print(f"        (lines that strip to {ANCHOR!r}: {doc_anchor} in the "
          f"document, 1 required inside item {ITEM_NUM})")
    ok(doc_anchor >= 1, "the anchor exists at all")

    new = transform(old)

    ok(new.count(MARKER) == 1, "the reversal marker appears exactly once")
    grew = len(new.split("\n")) - len(lines)
    blk = [b for b in BLOCK.split("\n")]
    if blk and blk[-1] == "":
        blk = blk[:-1]
    ok(grew == len(blk), f"line count grew by {grew}, derived expectation "
                         f"{len(blk)} (the anchor line is REPLACED, not added)")
    ok(ANCHOR_NEW in new and new.count(ANCHOR_NEW) == 1,
       "the stale 'Not attempted' claim was rewritten exactly once")

    # the status line: still parseable, still CLOSED, clause added once
    nlines = new.split("\n")
    ns = nlines[status]
    ok(ns == lines[status], "the status line is byte-identical (untouched)")
    ok(ns.startswith("*STATUS: CLOSED"), "item 52 is still CLOSED")

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
