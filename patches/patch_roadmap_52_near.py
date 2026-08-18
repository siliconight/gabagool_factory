"""Item 52: prediction 3 fixed, and the bound got better.

The arc measurement banked earlier today left greedy scoring at 31.1 s on
seed_5219 against `assemble`'s own 0.18 s, and called candidate restriction
MANDATORY rather than an optimisation. It was done. This records the result.

31.1 s -> 0.2 s, and the restricted band BEATS the unrestricted one on every
seed -- the opposite of the quality loss that was expected.

ANCHORING
Structural, same as the two patches before it: locate `**52. ` by the regex
`tools/roadmap_status.py` defines, scope to that item's block, find the ONE
line that strips to the probe's old location note, and replace that line and
the one above it. Nothing transcribed by hand.

USAGE
    python patches\\patch_roadmap_52_near.py --check
    python patches\\patch_roadmap_52_near.py --selftest
    python patches\\patch_roadmap_52_near.py
    python patches\\patch_roadmap_52_near.py --revert
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

TAG = "r57near"
ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "PIPELINE_ROADMAP.md"
FILES = (DOC,)

ITEM_NUM = 52
_ITEM = re.compile(r"^\*\*(\d+)\. (.*)$")
_STATUS_HEAD = "*STATUS:"
ANCHOR = "geometry, about 35 s for all three seeds."
ANCHOR_ABOVE = "Probe: `_scratch/probe_standable_sweep.py` -- read-only, stages its own"

MARKER = "**PREDICTION 3 FIXED, AND THE BOUND GOT BETTER.**"

BLOCK = """\
**PREDICTION 3 FIXED, AND THE BOUND GOT BETTER.** The 31.1 s was scoring
every bearing key against every candidate. Three changes: a bounding-box
reject before the real segment test; per-candidate TOUCHED KEYS, so a
candidate scores against the ~50 bins it can affect rather than all ~900; and
a candidate band restricted to 12 m of the route. `COVER_SEPARATION` (6 m) is
now enforced between chosen pieces, which the first bound ignored.

```
seed  budget  today     greedy WIDE          greedy NEAR (12 m, 6 m sep)  kept
5017     7    -10.8%    -34.1%  (233 cand)   -40.3%  ( 99 cand)           118%
5118     6    -10.4%    -24.8%  (227 cand)   -38.2%  ( 79 cand)           154%
5219    11     -9.9%    -33.2%  (236 cand)   -51.0%  (242 cand)           153%
```

**31.1 s -> 0.2 s worst case, and the RESTRICTED band beats the unrestricted
one on every seed.** A `COVER_SIZE` piece at distance d subtends about
2*atan(COVER_SIZE/2/d) -- 33 degrees at 5 m, 11 at 15 m, 4 at 45 m -- so
sampling the whole post set evenly diluted the near candidates that carry the
arc. Restricting concentrated the budget where the geometry says it belongs.

Today's placement reduces arc by ~10% on every seed. A restricted, separated,
realistic greedy reaches 38-51%. That is **3.7x-5.2x**, not the 2.4x-3.4x an
unconstrained bound suggested. The bound became more honest AND better, which
is the opposite of what was expected when candidate restriction was written
down as a risk.

STILL AN UPPER BOUND. Candidates are standable posts, not verified legal
piece positions, and nothing checks them against `_usable`. A real planner
lands below this.

Probe: `tools/probe_standable_sweep.py` -- read-only, stages its own
geometry, about 2 s for all three seeds."""


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
    if lines[retired[0] - 1].strip() != ANCHOR_ABOVE:
        raise SystemExit(
            "REFUSING: the line above the anchor is not the probe note "
            f"({lines[retired[0] - 1].strip()[:60]!r})")

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
    block = BLOCK.split("\n")
    if block and block[-1] == "":
        block = block[:-1]
    for b in block:
        if _ITEM.match(b):
            raise SystemExit(
                f"REFUSING: the inserted block contains an item heading: {b!r}")
    # the two probe lines are REPLACED; a blank line keeps the paragraph break
    return "\n".join(out[:retired - 1] + [""] + block + out[retired + 1:])


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
    ok(grew == len(blk) - 1,
       f"line count grew by {grew}, derived expectation {len(blk) - 1} "
       f"(two probe lines replaced by the block plus one blank)")
    ok(ANCHOR not in new, "the stale 35 s / _scratch probe note is gone")
    ok(new.count("tools/probe_standable_sweep.py") == 1,
       "the probe's new location is recorded once")
    ok(new.count("31.1 s") >= 1 and new.count("0.2 s") >= 1,
       "both the old cost and the new cost are stated")

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
