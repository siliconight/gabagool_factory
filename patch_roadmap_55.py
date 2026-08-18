#!/usr/bin/env python3
"""Roadmap item 55: the level ships sign fixtures with no sign art.

Found 2026-08-18 by a human circling a white square in a walk preview, then
survived FIVE wrong explanations from the tooling side before the artifact was
read properly. Worth recording as much for how it was found as for what it is:
every file-level instrument this repo owns said nothing was wrong, and all of
them were right, because the thing is created at runtime.

Usage:
    pwsh> python patch_roadmap_55.py --check
    pwsh> python patch_roadmap_55.py
    pwsh> python patch_roadmap_55.py --selftest
    pwsh> python patch_roadmap_55.py --revert

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
TAG = "pre_r55"

ANCHOR = """`PER_OBJECT_CEILING = 40` and its comment go with it.

## Commands
"""

ITEM = """`PER_OBJECT_CEILING = 40` and its comment go with it.

*STATUS: OPEN 2026-08-18 -- MEASURED. Four `AreaPanel_Surface` nodes ship in
`lot_demo_001`, each a 1.4 x 1.4 m single-sided `QuadMesh` at y 2.5 under
`LuxFixtureLights`, spawned by `LuxFixtureSpawner` as the emitter face of an
area-light rig. The LIGHT works. The SURFACE is blank, so it reads in-level as
a white card -- photographed 2.9 m from a doorway on `arena_a03`. One of the
four rigs is named `Spawned_sign`, which is what the fixture type is; the other
three are `@Node3D@27`, `@Node3D@71`, `@Node3D@99` -- engine-generated names,
so nothing downstream can select them. NOT CLAIMED HERE: whether a blank
emitter is a defect or simply unfinished content. That is an art decision and
this item does not make it*

**55. The level ships sign fixtures with no sign art, and three of four cannot
be addressed.**
Raised 2026-08-18 from a walk of `LF_lot_demo_001.portable-godot`: a white
rectangle beside a doorway, circled in a screenshot, which no automated check
had ever mentioned.

**WHAT IT IS.** Four nodes, in the whole five-building lot:

```
@Node3D@27/AreaPanel_Surface     world (  -1.4, 2.5,  80.2)
@Node3D@71/AreaPanel_Surface     world (  40.8, 2.5, -17.0)   <- the one photographed
@Node3D@99/AreaPanel_Surface     world (  73.2, 2.5, -84.2)
Spawned_sign/AreaPanel_Surface   world ( -75.2, 2.5,  63.6)
```

Each is a `QuadMesh`, `size = Vector2(1.4, 1.4)`, carrying a material. They are
the emitter faces of Lux area-light rigs: Zoo exports a `LuxEmit_*` marker,
`LuxFixtureSpawner` builds the rig, and the rig includes a visible panel
because a real luminaire has one. The light is correct. Nothing ever puts
artwork on the panel, so it renders as a blank 1.4 m card at head height. The
walker's own word for it was "signs", before any evidence existed -- and the
fixture type agrees.

**WHY EVERY FILE-LEVEL INSTRUMENT MISSED IT, AND WAS RIGHT TO.** The panel is
created at RUNTIME by the spawner and packed into `lux.applied.tscn`. It is in
no GLB and is not authored in any `site.tscn`. Five explanations were published
and refuted in order, each by a measurement:

```
broken glass material      refuted: nearest window is 7.41 m away, one storey up
a degenerate plane         refuted: `glb_nodes --flat`, 150 GLBs, 0 degenerate
the doorway module         refuted: it holds 4 nodes -- 2 jambs, a header, a collider
untextured jambs/header    refuted: `glb_materials`, all 3 visible prims textured
a rendered collision mesh  refuted: 0 visible surfaces with no material, 2093
                                    StaticBody3D -- `-colonly` converts correctly
```

The instrument that found it was reading `lux.applied.tscn`'s own node list --
the only place the thing exists. `glb_nodes.py`'s docstring already framed this
exact question ("what is that white square I can only see from one side?") and
its `--flat` answer said so: "Whatever you saw is not in this file -- try the
site." A `QuadMesh` is single-sided, which is why that phrasing fits.

**THE NAMING GAP, WHICH IS THE PART THAT COSTS SOMETHING LATER.** Three of the
four rigs are `@Node3D@<n>` -- names the engine generated because the spawner
did not set one. Only `Spawned_sign` is addressable. Anything that later wants
to find these panels, gate them, texture them or count them has nothing stable
to select on, and the numbers shift every time the spawn order does.

**WHAT THIS ITEM DOES NOT DECIDE.** Whether a blank emitter panel is a defect.
An unlit sign face awaiting artwork is a perfectly normal state for content
that is not finished, and this pipeline's job is to place the fixture, not to
draw the sign. What is NOT normal is that nothing anywhere says these panels
exist, so a level ships with four blank white cards at eye height and every
gate reports clean.

**WHAT WOULD CLOSE THIS.** Either artwork on the panel, or a stated decision
that the emitter face is invisible by default and Zoo's marker carries the
sign texture when there is one -- plus, in both cases, a name from the spawner
so the four are addressable, and a count in the validation output so a level
with unfinished sign faces says so instead of being found by somebody walking
past one.

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
        raise SystemExit(f"REFUSING: anchor occurs {n} times, expected 1.")
    if re.search(r"(?m)^\*\*55\. ", text):
        raise SystemExit("REFUSING: an item 55 already exists.")
    nums = [int(h) for h in re.findall(r"(?m)^\*\*(\d+)\. ", text)]
    if max(nums) != 54:
        raise SystemExit(f"REFUSING: highest item is {max(nums)}, not 54.")
    print("  ok  highest existing item is 54")
    return text.replace(ANCHOR, ITEM, 1)


def cmd_check() -> int:
    _require()
    print("   ", _stamp(ROADMAP))
    t = ROADMAP.read_text(encoding="utf-8")
    if re.search(r"(?m)^\*\*55\. ", t):
        print("\nALREADY APPLIED.")
        return 0
    print()
    _plan(t)
    print("  ok  anchor resolves once, immediately before '## Commands'")
    return 0


def cmd_apply() -> int:
    _require()
    src = ROADMAP.read_text(encoding="utf-8")
    if re.search(r"(?m)^\*\*55\. ", src):
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
    ("item 55 exists", lambda t: bool(re.search(r"(?m)^\*\*55\. ", t))),
    ("all four panels are located by coordinate",
     lambda t: "Spawned_sign/AreaPanel_Surface   world ( -75.2, 2.5,  63.6)" in t),
    ("the quad size is recorded",
     lambda t: "size = Vector2(1.4, 1.4)" in t),
    ("the five refuted explanations are kept, not dropped",
     lambda t: "a rendered collision mesh  refuted" in t),
    ("the naming gap is called out",
     lambda t: "names the engine generated because the spawner" in t),
    ("the art decision is explicitly NOT made here",
     lambda t: "WHAT THIS ITEM DOES NOT DECIDE" in t),
    # Needle kept short and WITHIN one wrapped line. This is the second
    # line-spanning needle in one session; a check that cannot match text
    # that is present is a check that tests nothing.
    ("closing the item includes a name and a count",
     lambda t: "a name from the spawner" in t and "a count in the" in t),
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
    if nums != sorted(nums) or len(nums) != len(set(nums)) or max(nums) != 55:
        raise SystemExit(f"SELFTEST FAILED: item numbering: {nums[-4:]}")
    print(f"  ok  {len(nums)} items, strictly increasing, max 55")
    if t.index("**55. ") > t.index("## Commands"):
        raise SystemExit("SELFTEST FAILED: item 55 landed after '## Commands'")
    print("  ok  item 55 sits before the '## Commands' appendix")
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
