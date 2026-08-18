#!/usr/bin/env python3
"""Item 41: the routing argument stands; every number under it is dead.

Item 41 rests on two measured claims and one count. Re-measured 2026-08-18 on
FIVE buildings from the certified `LF_lot_demo_001.portable-godot` package,
with `tools/glb_nodes.py --json` on each `art/dressing/*.glb` against its own
`site_base.glb`. None of the three survives.

  (a) "a 0.30 m offset below the floor" -- `Cover_curb` at -4.30 against a
      floor at -4.00. NOW: curb and base course are at EXACTLY 0.00 on all
      five, and `--below 0` returns 0 nodes on all five, including
      `pvp_station_ref`, which really does have a basement at -3.75.

  (b) "roughly one extra storey of height" -- a gutter 4.6 m above the roof it
      drains. NOW: every gutter is BELOW its own building's top, by -0.88,
      -0.88, -0.23, -0.98, -0.23 m.

  (c) 1389 `Cover_panel_field`, the largest family and the whole basis of the
      "1389 panel fields is the wrong mechanism" argument. NOW: the family
      does not exist. Neither does `Cover_pilaster` or `Cover_frame`. Five
      families remain and 231-260 nodes per building, against 2255.

What the numbers now show is a placer keyed to roof TYPE, which is a rule
rather than drift: the three buildings carrying `parapet_N/S/E/W` put the edge
strip +0.50 above the shell top and the gutter -0.88..-0.98 below it; the two
carrying `slab` and no parapet use +0.15 and -0.23. Item 41 predicted this
outcome for one family and warned about acting on it -- "a gate written from
the frames would have condemned the one family that is behaving."

WHAT IS NOT REFUTED, and is the reason this is NARROWED and not CLOSED: the
ROUTING argument. Dressing is still emitted through the layer-3 props channel
with no slot, no placement gate, no collision authority and no intrusion
limit. `allowed_inward_intrusion_m` still occurs in exactly one file in this
repo -- PIPELINE_ROADMAP.md, four times, all of them proposing it. Zero
occurrences in any code or manifest. The contract this item asks for has still
never been written.

The item's stated ORDER is now wrong and is corrected: it puts "the two
reference-plane leads first: they are cheap, probably one expression each".
There is nothing there to fix.

Usage:
    pwsh> python patch_roadmap_41_measured.py --check
    pwsh> python patch_roadmap_41_measured.py
    pwsh> python patch_roadmap_41_measured.py --selftest
    pwsh> python patch_roadmap_41_measured.py --revert
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"
TAG = "pre_41measured"

STATUS_OLD = ("*STATUS: OPEN 2026-08-12 -- unchanged, and the one on this list "
              "a viewer notices*")
STATUS_NEW = (
    "*STATUS: NARROWED 2026-08-18 -- THE ROUTING ARGUMENT STANDS AND EVERY "
    "NUMBER UNDER IT IS DEAD. Re-measured on FIVE buildings out of the "
    "certified portable-godot package (`tools/glb_nodes.py --json`, each "
    "`art/dressing/*.glb` against its own `site_base.glb`). The 0.30 m "
    "below-floor offset: GONE -- curb and base course sit at exactly 0.00 on "
    "all five and `--below 0` returns zero nodes on all five, including "
    "`pvp_station_ref`, which does have a basement at -3.75. The extra-storey "
    "height: GONE -- every gutter is BELOW its building's top (-0.88, -0.88, "
    "-0.23, -0.98, -0.23 m). The 1389 `Cover_panel_field`: the family DOES "
    "NOT EXIST, nor do `Cover_pilaster` or `Cover_frame`; five families and "
    "231-260 nodes per building, against 2255. The offsets are now quantised "
    "by roof TYPE -- parapet buildings +0.50 edge / -0.88..-0.98 gutter, slab "
    "buildings +0.15 / -0.23 -- which is a rule, not drift. WHAT SURVIVES: "
    "the routing. Dressing is still on the props channel with no slot, no "
    "placement gate, no collision authority and no intrusion limit, and "
    "`allowed_inward_intrusion_m` still appears in exactly one file in this "
    "repo -- this one, four times, all proposing it, zero occurrences in code "
    "or manifest. The item's stated ORDER is corrected below: the two "
    "reference-plane leads are not cheap fixes, they are not defects*"
)

TAIL_OLD = (
    "**Order.** The two reference-plane leads first: they are cheap, probably one\n"
    "expression each, and the light-anchor fix is the template. Then the intrusion\n"
    "contract. The reclassification and the material question are real work and want\n"
    "a decision before code.\n"
)

TAIL_NEW = TAIL_OLD + """
RE-MEASURED 2026-08-18 -- THE TWO REFERENCE-PLANE LEADS ARE NOT DEFECTS

Everything above this line was measured on 2026-08-12 against ONE baked layer.
Re-run on the five buildings of the certified `LF_lot_demo_001.portable-godot`
package, `tools/glb_nodes.py --json` on each `art/dressing/*.glb` against that
building's own `site_base.glb`:

```
                      shell y            gutter   vs top      edge strip   vs top
arena_a03            -0.15 .. 12.50       11.62    -0.88    13.00..13.00    +0.50
large_warehouse_a01  -0.15 ..  6.50        5.62    -0.88     7.00.. 7.00    +0.50
mansion_a02          -0.15 ..  7.45        7.22    -0.23     5.90.. 7.60    +0.15
pvp_station_ref      -3.75 ..  7.80        6.82    -0.98     6.90.. 8.30    +0.50
strip_club_a03       -0.15 ..  7.05        6.82    -0.23     5.58.. 7.20    +0.15

Cover_curb          0.00 .. 0.00   on all five      --below 0: 0 node(s), all five
Cover_base_course   0.00 .. 0.00   on all five
```

**(a) is gone.** The curb and base course sit at EXACTLY 0.00, no spread, and
nothing in the dressing layer is below grade -- on `pvp_station_ref` least of
all, which genuinely has a basement at -3.75 and would show it.

**(b) is gone, and inverted.** Not one gutter is above its building; every one
is 0.23 to 0.98 m below the top. The claim was 4.6 m above.

**(c) is gone.** `Cover_panel_field` -- 1389 nodes, the largest family and the
entire basis of the "wrong mechanism, not a wrong number" argument -- does not
exist in any of the five. Neither does `Cover_pilaster` or `Cover_frame`. Five
families survive, 231-260 nodes per building against 2255.

**And the offsets are a rule.** The three buildings whose shells carry literal
`parapet_N/S/E/W` families at the shell max -- arena, large_warehouse,
pvp_station -- place the edge strip +0.50 above it and the gutter -0.88..-0.98
below. The two that top out in `slab` with no parapet -- mansion, strip_club --
use +0.15 and -0.23. Two roof types, two constants each, repeated exactly. An
edge strip half a metre above a parapet is a coping, which is the reading this
item already offered for `Cover_edge_strip` and warned about acting against:
"a gate written from the frames would have condemned the one family that is
behaving."

WHAT THIS DOES NOT TOUCH

The ROUTING argument, which is the item's actual thesis and is unaffected by
any of the above. Dressing is still structural art on the layer-3 props
channel: no slot, no placement gate, no collision authority, no intrusion
limit. `allowed_inward_intrusion_m` occurs in exactly one file in this
repository -- this one, four times, every one of them proposing it. There are
zero occurrences in code or in any manifest. Nothing has been built.

So the ORDER above is wrong and this replaces it. There are no cheap
reference-plane fixes to take first, because there is nothing there to fix.
What is left is the part the item itself called "real work that wants a
decision before code": the intrusion contract, the reclassification, and the
panel-field material question -- and that last one is now moot on this
evidence, because the panel fields are gone.

ONE THING NOT RE-MEASURED. This is the geometry, read from the node table. It
is NOT the walkthrough that raised the item -- "there is still dressing all
over in a way that doesn't look good" -- and a placer that is arithmetically
correct can still look wrong. The numbers say the two published defects are
not there. They do not say the level looks right.
"""


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:8].upper()


def _stamp(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    return f"{p.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


EDITS = [("status line", STATUS_OLD, STATUS_NEW),
         ("the measured block", TAIL_OLD, TAIL_NEW)]


def _plan(text: str) -> str:
    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(
                f"REFUSING: anchor for '{label}' occurs {n} times, expected 1.")
        text = text.replace(old, new, 1)
        print(f"  ok  {label}")
    return text


def _require() -> None:
    if not ROADMAP.is_file():
        sys.exit(f"REFUSING: not found: {ROADMAP}")


def cmd_check() -> int:
    _require()
    print("   ", _stamp(ROADMAP))
    t = ROADMAP.read_text(encoding="utf-8")
    if "RE-MEASURED 2026-08-18" in t:
        print("\nALREADY APPLIED.")
        return 0
    print()
    _plan(t)
    print("\nboth anchors resolve exactly once.")
    return 0


def cmd_apply() -> int:
    _require()
    src = ROADMAP.read_text(encoding="utf-8")
    if "RE-MEASURED 2026-08-18" in src:
        print("ALREADY APPLIED; nothing to do.")
        return 0
    eol = "\r\n" if b"\r\n" in ROADMAP.read_bytes() else "\n"
    norm = src.replace("\r\n", "\n") if eol == "\r\n" else src
    out = _plan(norm)
    (ROADMAP.parent / f"{ROADMAP.name}.{TAG}").write_bytes(ROADMAP.read_bytes())
    ROADMAP.write_text(out if eol == "\n" else out.replace("\n", "\r\n"),
                       encoding="utf-8", newline="")
    print("\nafter:")
    print("   ", _stamp(ROADMAP))
    print(f"\nsidecar .{TAG}. NEXT: python tools\\roadmap_status.py --write")
    return 0


def cmd_revert() -> int:
    side = ROADMAP.parent / f"{ROADMAP.name}.{TAG}"
    if not side.is_file():
        print("nothing to revert.")
        return 0
    ROADMAP.write_bytes(side.read_bytes())
    side.unlink()
    print(f"  restored {ROADMAP.name}")
    return 0


CHECKS = [
    ("the five-building table is present",
     lambda t: "large_warehouse_a01  -0.15 ..  6.50" in t),
    ("the below-grade result is recorded",
     lambda t: "--below 0: 0 node(s), all five" in t),
    ("the gutter inversion is stated",
     lambda t: "Not one gutter is above its building" in t),
    ("the vanished panel field is recorded",
     lambda t: "1389 nodes, the largest family" in t),
    ("the roof-type rule is named",
     lambda t: "Two roof types, two constants each" in t),
    ("the routing thesis is preserved, not deleted",
     lambda t: "The ROUTING argument, which is the item's actual thesis" in t),
    ("the missing contract is quantified",
     lambda t: "zero occurrences in code or in any manifest" in t),
    ("the wrong ORDER is superseded in place",
     lambda t: "So the ORDER above is wrong and this replaces it" in t),
    ("what was NOT re-measured is stated",
     lambda t: "They do not say the level looks right." in t),
    # Item 53's status line, patched earlier the same day, also begins
    # `*STATUS: NARROWED 2026-08-18 --`. Matching on that prefix passed on the
    # pre-image, so it tested nothing. Keyed to this item's own text instead.
    ("the status verb is one roadmap_status knows, and it is THIS item's",
     lambda t: "*STATUS: NARROWED 2026-08-18 -- THE ROUTING ARGUMENT STANDS" in t),
]


def cmd_selftest() -> int:
    _require()
    t = ROADMAP.read_text(encoding="utf-8")
    bad = []
    for name, fn in CHECKS:
        ok = fn(t)
        print(("  ok  " if ok else "  FAIL ") + name)
        if not ok:
            bad.append(name)
    if bad:
        raise SystemExit("SELFTEST FAILED: " + "; ".join(bad))

    side = ROADMAP.parent / f"{ROADMAP.name}.{TAG}"
    if side.is_file():
        pre = side.read_text(encoding="utf-8")
        useless = [n for n, fn in CHECKS if fn(pre)]
        if useless:
            raise SystemExit("SELFTEST FAILED: these hold on the PRE-IMAGE "
                             "too: " + "; ".join(useless))
        print("  ok  every content check fails on the pre-image")
        # the original evidence must SURVIVE -- this supersedes, it does not erase
        for keep in ("1389  Cover_panel_field", "Cover_curb           -4.30",
                     "Raised 2026-08-02 after a second"):
            if keep in pre and keep not in t:
                raise SystemExit(
                    f"SELFTEST FAILED: the original evidence {keep!r} was "
                    f"DELETED rather than superseded.")
        print("  ok  the 2026-08-12 evidence is still present, superseded not erased")

    nums = [int(h) for h in re.findall(r"(?m)^\*\*(\d+)\. ", t)]
    if nums != sorted(nums) or len(nums) != len(set(nums)):
        raise SystemExit(f"SELFTEST FAILED: item numbering broke: {nums}")
    print(f"  ok  {len(nums)} item headings, strictly increasing, max {nums[-1]}")
    print("\nSELFTEST PASSED")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--revert", action="store_true")
    g.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.check:
        return cmd_check()
    if a.revert:
        return cmd_revert()
    if a.selftest:
        return cmd_selftest()
    return cmd_apply()


if __name__ == "__main__":
    raise SystemExit(main())
