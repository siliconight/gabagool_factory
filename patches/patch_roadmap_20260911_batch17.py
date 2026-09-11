"""Roadmap batch 17, 2026-09-11: the first human walk of a shipped package.

Item 18 (sentence-classified) gets a status block recording the walk; items
138-144 are filed from it, each with the measurement taken the same hour.
INSERT (batch 4's mechanism) and APPEND (batch 6's). Each asserts its anchor.
"""
import io
import re
import sys

P = "PIPELINE_ROADMAP.md"

INSERT = {
    18: """*STATUS: NARROWED 2026-09-11 -- A PERSON WALKED A SHIPPED PACKAGE, WHICH IS
THE WHOLE ASK, AND EIGHT THINGS CAME BACK THAT NO INSTRUMENT HAD REPORTED.
cold run 9005's `LF_county_hospital_001.portable-godot`, walked through
`tools/walk_export.py`'s copy, Blue Hour, about forty minutes. In the order
they were said: (1) pieces that looked rotated -- NOT REPRODUCED by the new
`tools/module_pose_census.py`, which judged every placed module against its
own slot: 443 of 443 wall-family modules standing at the slot's height and
footprint, the only above-floor parts the breach headers at 2.2 m; next time,
a `look_shots --station` at the spot. (2) The drywall skin reads as "fizzy"
digital noise -- MEASURED, item 140. (3) Holes in floors and ceilings -- the
stairwell voids (10 plates) and one designed `floor_hole` vertical link at
(0, 12), which reads as a bug because nothing marks it. (4) Windows blacked
out from outside -- item 138. (5) A white box and a white square at the sign
-- item 139. (6) The facade's texel scale jumps at remainders and openings --
item 141. (7) A prop with no skin, black -- item 142. (8) Light inside a wall
-- MEASURED, item 143: nine lamp points on this shell sit inside a partition.
And the stairs ship in the greybox's fallback yellow -- item 144. THE
INSTRUMENT SCORE: of the eight, two were already known classes with an
instrument that had not been run on THIS shell (143, via item 85's probe),
one was a known residue (139, noted in Lux 0.30.1), one is a measurement the
census refuted (1), and four were invisible to every gate in the pipeline
(2, 4, 6, 7). That ratio -- four of eight -- is this item's number, and it is
the first time it has been measured rather than asserted. What the walk did
not find: anything a body could not traverse.*""",
}

APPEND = """
*STATUS: NARROWED 2026-09-11 -- FOUND BY A PERSON, FIXED THE SAME HOUR IN LUX
0.32.2 (the quad is double-sided), NOT YET RE-WALKED; the glass skin's own
darkness is the residue*

**138. The windows read as black rectangles from outside.** Walked 2026-09-11
on cold run 9005's package. Lux 0.30.0 lights each window with an area rig
whose emissive quad faces INTO the room (`_place` turns it to the anchor's
inward normal, correctly, since 0.30.1), and a `QuadMesh` with a
`StandardMaterial3D` is single-sided: from the street the panel is
back-face culled and what remains is the glass module's own material, whose
Pixelcoat albedo measures a luminance spread of 3.7 -- near-black. So a lit
window at night shows a white pane from the ward and a black one from the
road, which is the wrong way round for the only viewer who was ever going to
judge it. **WHAT WOULD CLOSE THIS:** the quad rendered double-sided
(`cull_mode = CULL_DISABLED`, one line in `_build_quad`), and a look at
whether the glass skin should carry a night-time tint of its own.

*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON; THE RESIDUE LUX 0.30.1 WROTE
DOWN, NOW SEEN*

**139. The sign is a white box with a white square standing off it.** Walked
2026-09-11. Two things in one frame. The square: Zoo writes its `LuxEmit_*`
markers with a translation only (`build.py:661`), so a rig spawned on the
marker path inherits an identity basis and its emissive quad faces +Z
whatever the wall -- for this sign, perpendicular to the facade. The box:
`lf_county_hospital_001_9005_fixtures.glb` gives the cabinet
`M_SignBox_metal` at 0.28 grey and the face `M_SignBox_Face` emissive
(1.0, 0.9, 0.7); under a 3.0-energy rig at 0.2 m the whole cabinet reads
white. **WHAT WOULD CLOSE THIS:** Zoo stamps the anchor's `rot_z` into the
marker's basis so `LuxFixtureSpawner` inherits a facing, and the spawner
applies the same quarter turn `_place` does for an area rig (Lux 0.30.1's
derivation, f = t + 90); then a look at the sign's energy against its own
cabinet.

*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON, MEASURED THE SAME HOUR*

**140. The drywall skin is white noise.** Said on the walk as "fizzy, too
much digital noise, a small concentration of texture would read better".
Measured on the `delco_1997` packs `pixelcoat_build` shipped for cold run
9005, per albedo: luminance spread (std, 0-255) and the correlation between a
texel and its neighbour (1.0 = smooth, 0.0 = every texel independent):

    drywall_orangepeel   std 23.8   ac1 0.12    <- the fizz
    carpet               std 10.4   ac1 0.09
    plaster              std 11.9   ac1 0.34
    concrete             std 28.2   ac1 0.75
    brick                std 29.8   ac1 0.85
    ceiling_tile         std 15.6   ac1 0.52

Drywall has brick's amplitude at carpet's correlation: a large per-texel
random term with no spatial structure, which at the wall's texel density
reads as static rather than as orange peel. Concrete, at the same amplitude
but 0.75 correlation, reads as concrete. **WHAT WOULD CLOSE THIS:** the
`drywall_orangepeel` grammar in Pixelcoat rewritten as a low-frequency
mottle -- a target of ac1 >= 0.5 at std 10-14, the plaster/tile band -- and
the two numbers above kept as the check that a texture reads as surface
rather than as noise; carpet is next on the same list.

*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON, INSTRUMENT NAMED, NOT YET RUN*

**141. The facade's texel scale jumps at the remainders and the openings.**
Walked 2026-09-11: on the north elevation the voronoi cells are visibly larger
on the wall remainders beside the door and on the doorway module than on the
2.00 m segments either side. `zoo_worldskin.gd` -- the world-space UV import
script roadmap 80 shipped for exactly this seam -- is in the package
(`lot/shell/zoo_worldskin.gd`) and scoped to `wall_`, `wallEnd_`, `window_`,
`doorway_`, `breach_`; so either the import script is not bound to those GLBs
in the shipped `.import` sidecars, or it applied and the density fallback
("without a UV density") fired for those modules. **WHAT WOULD CLOSE THIS:**
`tools/texel_density.gd` over the running package, per module family, and
the `.import` sidecars read for `import_script/path`; then whichever half is
missing.

*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON, HALF MEASURED*

**142. A prop ships black.** Walked 2026-09-11: a waist-high box in a ward,
pure black on every face, beside skinned walls. The kit's
`prop_delco_1997_01_*.glb` carry `M_Skin_concrete_delco_1997` WITH a
texture, and their meshes carry `TEXCOORD_0` on one of two primitives. The
worldskin script excludes props on purpose (a small movable object swims
under world projection), so a prop wears only its baked UVs -- and a
primitive with no UVs samples one texel. **WHAT WOULD CLOSE THIS:** the prop
recipe's second primitive (the collision or the top?) given UVs or no skin
at all, and `texel_density.gd` extended to report a mesh with a textured
material and no UV set, which is the shape that is black.

*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON, MEASURED, AND THE INSTRUMENT
ALREADY EXISTED*

**143. Ceiling lamps sit inside partitions on this shell.** Walked 2026-09-11
as "light inside the wall": a warm pool on the ceiling and floor at the top
and bottom of a partition's edge. `tools/anchor_wall_probe.py` -- built for
item 85 and run that morning over the LIBRARY (2,422 lamp points, none inside
a wall, min 1.35 m) -- run over THIS shell, the pipeline-built
`lf_county_hospital_001`: 35 lamp points, NINE inside a wall's thickness at
-0.150 m, the wall centreline exactly: the lobby and ward_south rows at
x = +-8.0 on `int_0_1_seg3` / `int_0_2_seg3` / `int_1_4_seg3` /
`int_1_5_seg3`, and the helipad bulbs at x = -16, -8, 0 on the roof's
`int_2_6` partitions. A row laid across a room's length at its derived
spacing lands a lamp on a partition whenever the room's partitions fall on
that spacing -- which the library's rooms happened not to and this hospital's
do. **WHAT WOULD CLOSE THIS:** `lights._row_runs` nudging or dropping a lamp
point within half a wall's thickness of a partition (the manifest carries no
walls, so the caller passes them the way it passes ceiling voids), and the
probe run as a gate over the deli job's outputs -- item 85's residue, now
with a shell that fails it.

*STATUS: OPEN 2026-09-11 -- FOUND BY A PERSON; THE GAP PROTOCOL'S CASE*

**144. The stairs ship in the greybox's fallback yellow.** Walked 2026-09-11:
every stair in the level is Deli Counter's greybox flight in the default
material, between skinned walls. Correctly so today: the composer keeps the
whole greybox base (floors, collision, stairs) and swaps only the slotted
modules; Zoo has no stair species (`stair_rail` is a rail, not a flight) and
`zoo_worldskin.gd` scopes to the five kit families and never sees the base
GLB. This is item 62's protocol from the other end: the design asked for a
themed stair and no tool can make one. **WHAT WOULD CLOSE THIS,** cheapest
first: the world-space skin applied to the base GLB's `stair*` meshes with
the building's concrete pack (the stairs are concrete in every 1990s
hospital there is), which is a scope change in the import script and a
sidecar binding for the base; or, later, a Zoo stair species built to DC's
flight geometry. The `floor_hole` vertical link is the same family of
finding: designed, unmarked, and reads as a bug until something visual says
"drop here".
"""


def insert_status(lines, num, block):
    heading = re.compile(r"^\*\*%d\. " % num)
    hits = [i for i, l in enumerate(lines) if heading.match(l)]
    if len(hits) != 1:
        raise SystemExit(f"item {num}: heading matched {len(hits)} times")
    h = hits[0]
    for i in range(max(0, h - 3), h):
        if lines[i].startswith("*STATUS:"):
            raise SystemExit(f"item {num}: a status block already sits above it")
    lead = [] if lines[h - 1].strip() == "" else [""]
    lines[h:h] = lead + block.split("\n") + [""]


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    lines = raw.decode("utf-8").split("\n")
    for num in sorted(INSERT, reverse=True):
        insert_status(lines, num, INSERT[num])
    for n in range(138, 145):
        if any(l.startswith(f"**{n}. ") for l in lines):
            print(f"item {n} already present", file=sys.stderr)
            return 1
    if not any(l.startswith("**137. ") for l in lines):
        print("item 137 not found; refusing to append after it", file=sys.stderr)
        return 1
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines += [""] + APPEND.strip("\n").split("\n") + [""]
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 1 inserted, 7 appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
