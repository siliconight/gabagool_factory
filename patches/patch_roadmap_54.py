#!/usr/bin/env python3
"""Roadmap item 54: one mesh spans a whole room, and two light caps pay for it.

Raised 2026-08-18 from a walk. The lit package blinked, then had areas that
stayed dark, then had a hard brightness seam across a floor. Four releases went
into the symptoms (level_factory 0.43.0 through 0.43.3) and two of them named
the wrong mechanism before the right one was isolated. What is left underneath
is a single fact that no setting addresses: a floor or roof plate 34-52 m
across is ONE mesh, and it competes for the same light budget as a 2 m wall
segment.

This item exists so the caps are read as mitigations with a measured cost
rather than as a fix, and so the number in `packages/core/godot_project.py` has
somewhere to point when a denser mission needs it raised.

Usage:
    pwsh> python patch_roadmap_54.py --check
    pwsh> python patch_roadmap_54.py
    pwsh> python patch_roadmap_54.py --selftest
    pwsh> python patch_roadmap_54.py --revert

After applying:  python tools\\roadmap_status.py --write
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"
TAG = "pre_r54"

ANCHOR = """standalone contract rather than being untidy).

## Commands
"""

ITEM = """standalone contract rather than being untidy).

*STATUS: OPEN 2026-08-18 -- MEASURED AND MITIGATED, NOT FIXED. Raised from a
walk, not from a grep. The subject of this item -- a floor or roof plate 34-52 m
across being ONE mesh -- is untouched. What shipped is two engine caps that pay
for it: level_factory 0.43.3 writes `max_renderable_lights` = the package's own
light count and `max_lights_per_object` = min(count, 40), both derived, neither
round. THE PER-OBJECT ONE COSTS: it sizes the shader light loop for every
object. Measured on lot_demo_001: 111 of 920 meshes exceed the engine's
per-mesh default of 8, 39 exceed 16, one exceeds 32 -- and every single
offender is a building-wide roof or floor/ceiling plate. Room-sized meshes
would sit inside the engine defaults and need no caps at all. Also open and
NOT measured: a first-load frame hitch, smaller after 0.43.2 dropped a cap but
still present*

**54. One mesh spans a whole room, and two light caps are paying for it.**
Raised 2026-08-18, walking `LF_lot_demo_001.portable-godot` with 136 fixture
lights in it. Three symptoms arrived in sequence and only the third named the
cause: lights blinking as the camera moved, then areas that stayed dark
permanently, then -- standing still -- a hard brightness step across a floor
where two slabs met.

**TWO LIMITS, AND THEY FAIL DIFFERENTLY.** GL Compatibility carries both, and
conflating them cost two releases:

```
rendering/limits/opengl/max_renderable_lights   default  32   a GLOBAL budget
rendering/limits/opengl/max_lights_per_object   default   8   a PER-MESH budget
```

Above the global cap lights are not drawn AT ALL, which is why areas stayed
dark permanently rather than flickering -- 136 lights against a budget of 32.
Above the per-mesh cap a single mesh drops lights, which on a building-sized
slab shows up standing still, as a seam.

**THE MEASUREMENT.** Counting lights whose range reaches each mesh's bounding
box, across all five buildings of the shipped package:

```
building              meshes   >8   >16  >32  worst  worst mesh
mansion_a02              163   26    11    0     26  roof_footprint
pvp_station_ref          240   49    15    1     36  roof_footprint
large_warehouse_a01      117    3     1    0     17  roof_footprint
arena_a03                227   10     3    0     26  roof_footprint
strip_club_a03           173   23     9    0     25  roof_footprint
---------------------------------------------------------------
across all five          920  111    39    1
```

Every offender is a roof or floor/ceiling plate 34-52 m across. Wall segments
sit at 6 or below. `arena_a03`'s roof is `roof_rockay_04_w5200_d3200` -- 52 m
by 32 m, one mesh, one light budget, competing with `wall_rockay_04_w200` at
2 m for the same slots. When the big one loses, a whole room goes dark at once.

Caveat on those numbers, stated because they will be quoted: extents come from
the `_w`/`_d` in the module filenames, height is assumed at +/-3 m, and
per-module rotation is ignored. They are indicative. The one that is not
indicative is the single mesh over 32, because it matched the reported symptom
exactly -- "still blink a bit, or just turn off in certain rooms" at a cap of
32, with exactly one mesh above it.

**WHAT WAS RUN ON HARDWARE**, in the walk preview, each a separate walk of the
same route:

```
per-object   global    result
        8        32    heavy blinking
       64        32    still blinks, areas stay dark
        8       256    clean, and the load-in hitch is SMALLER
       64       256    clean
       40       256    clean            <- shipped
```

The global cap is what stopped the blinking and the dead areas. The per-object
cap is what stopped the seam, which only appears when the camera is still and
was therefore missed entirely by the runs above it.

**TWO MECHANISMS WERE PUBLISHED WRONG BEFORE THE THIRD WAS ISOLATED.** 0.43.0
wrote the per-object cap and named it as the cause of the blinking; it was not,
and the engine said so when finally asked directly (`max_renderable_lights
exists=true value=32`). 0.43.2 then REMOVED the per-object cap, having tested
only for blinking -- and reintroduced the seam. 0.43.3 tested the two symptoms
separately and shipped both caps, each derived from the package rather than
picked to make something stop.

**WHAT IS ACTUALLY WRONG, AND IT IS NOT A SETTING.**

A single mesh spanning a whole room is the reason either cap is needed. Split
those plates to room-sized pieces and every one of the 111 offenders drops
inside the engine's own default of 8; the per-object cap becomes unnecessary
and its shader cost goes with it. Frustum culling improves for free, because a
52 x 32 m mesh is either fully in frame or fully drawn anyway.

**AND THIS IS ITEM 35's QUESTION FROM THE OTHER SIDE.** Item 41 measured 1389
`Cover_panel_field` nodes and called excessive fragmentation the defect. This
item measures meshes too LARGE to light correctly. Both are the same missing
decision -- what size should a mesh be -- approached from opposite ends, and
neither can be settled by a rule that only says "fewer" or "more".

**THE LOAD-IN HITCH -- OPEN, AND A HYPOTHESIS ONLY.** A frame hitch on first
load was reported from the walk, and it got smaller when 0.43.2 dropped the
per-object cap from 64 to the engine default. That is consistent with shader
variant compilation on first draw -- the per-object light count sizes the
shader's light loop, so more variants to compile -- but NOTHING HAS MEASURED
IT. No frame timing was captured, no variant count, no before-and-after on the
same route. It is recorded here as an observation with a plausible cause, and
it should not be quoted as a finding until somebody times it. It matters
because this layer has to stay cheap while the game grows into it.

**WHAT WOULD CLOSE THIS.** Room-sized floor, ceiling and roof meshes, measured
the same way -- re-run the per-mesh light census and show zero meshes over the
engine default of 8. At that point `packages/core/godot_project.py` stops
writing the per-object cap because no package needs it, and the constant
`PER_OBJECT_CEILING = 40` and its comment go with it.

## Commands
"""


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:8].upper()


def _stamp(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    return f"{p.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


def _require() -> None:
    if not ROADMAP.is_file():
        sys.exit(f"REFUSING: not found: {ROADMAP}")


def _plan(text: str) -> str:
    n = text.count(ANCHOR)
    if n != 1:
        raise SystemExit(f"REFUSING: insertion anchor occurs {n} times, "
                         f"expected 1.")
    if re.search(r"(?m)^\*\*54\. ", text):
        raise SystemExit("REFUSING: an item 54 already exists.")
    nums = [int(h) for h in re.findall(r"(?m)^\*\*(\d+)\. ", text)]
    if nums and max(nums) != 53:
        raise SystemExit(f"REFUSING: highest existing item is {max(nums)}, "
                         f"not 53; this patch would misnumber.")
    print("  ok  highest existing item is 53")
    return text.replace(ANCHOR, ITEM, 1)


def cmd_check() -> int:
    _require()
    print("   ", _stamp(ROADMAP))
    t = ROADMAP.read_text(encoding="utf-8")
    if re.search(r"(?m)^\*\*54\. ", t):
        print("\nALREADY APPLIED.")
        return 0
    print()
    _plan(t)
    print("  ok  anchor resolves exactly once (immediately before '## Commands')")
    return 0


def cmd_apply() -> int:
    _require()
    src = ROADMAP.read_text(encoding="utf-8")
    if re.search(r"(?m)^\*\*54\. ", src):
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
    ("item 54 exists and is the last one",
     lambda t: bool(re.search(r"(?m)^\*\*54\. ", t))),
    ("the two limits are distinguished by name and default",
     lambda t: "max_renderable_lights   default  32" in t
               and "max_lights_per_object   default   8" in t),
    ("the five-building census is present",
     lambda t: "across all five          920  111    39    1" in t),
    ("the hardware matrix records all five runs",
     lambda t: "40       256    clean            <- shipped" in t),
    ("both wrong mechanisms are named, not dropped",
     lambda t: "0.43.2 then REMOVED the per-object cap" in t),
    ("the caps are labelled mitigations",
     lambda t: "MEASURED AND MITIGATED, NOT FIXED" in t),
    ("the measurement caveat is stated",
     lambda t: "They are indicative." in t),
    ("the load hitch is marked unmeasured",
     lambda t: "NOTHING HAS MEASURED" in t),
    ("item 35/41's fragmentation tension is linked",
     lambda t: "approached from opposite ends" in t),
    # Needle kept WITHIN one wrapped line. The first draft of this check
    # spanned a line break and failed on text that was actually present --
    # the same no-op shape this file's own item 53 history records.
    ("closing the item is defined as a re-measurement",
     lambda t: "re-run the per-mesh light census" in t),
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

    nums = [int(h) for h in re.findall(r"(?m)^\*\*(\d+)\. ", t)]
    if nums != sorted(nums) or len(nums) != len(set(nums)):
        raise SystemExit(f"SELFTEST FAILED: item numbering broke: {nums}")
    if max(nums) != 54:
        raise SystemExit(f"SELFTEST FAILED: highest item is {max(nums)}, not 54")
    print(f"  ok  {len(nums)} items, strictly increasing, max 54")

    # The item must sit INSIDE the item list, not after the appendix.
    if t.index("**54. ") > t.index("## Commands"):
        raise SystemExit("SELFTEST FAILED: item 54 landed after '## Commands'")
    print("  ok  item 54 sits before the '## Commands' appendix")
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
