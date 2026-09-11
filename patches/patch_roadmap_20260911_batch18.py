"""Roadmap batch 18, 2026-09-11: two more findings from the walk of cold run
9005's package, each fixed in a tool repo the same day and filed with the
measurement that decided the fix. APPEND only (batch 6's mechanism);
asserts item 144 is the last item and 145/146 are absent.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

APPEND = """
*STATUS: NARROWED 2026-09-11 -- FOUND BY A PERSON, FIXED THE SAME HOUR IN LUX
0.32.3, NOT YET RE-WALKED*

**145. A window's light pools on the wall it sits in.** Walked 2026-09-11
on cold run 9005's package: a warm pool on the ceiling and the floor at the
wall under a window, read as "light coming out of this wall". Not item
143's lamp-in-a-partition -- this is the window rig itself. A window's
anchor in `site.lights.json` is the wall CENTRELINE, and Lux 0.30.0's
loader put the area rig's Compatibility-tier omni exactly there: a point
light in the plane of the wall lights the wall's inner face at grazing
incidence, and the ceiling and the floor symmetrically above and below it,
which is a wall sconce, not a window. What it should light is the floor in
front of the glass. **FIXED:** `LuxAreaLightRig` gains `light_offset`
(rig frame, +Z = the panel's forward = the room since 0.30.1's quarter
turn); the panel quad stays in the wall plane and the loader sets every
window's source 0.35 m into the room -- clear of any wall this kit builds
(0.30 m thick, so 0.35 from the centreline stands 0.20 past the inner
face) and short enough that the 3-4 m sphere item 137 derived still
reaches the glass. Signs and hand-placed rigs keep a zero offset. **RESIDUE:** the
number is chosen against the kit's wall thickness, not derived from it;
the loader should read the thickness the manifest carries once it carries
one. Not re-walked.

*STATUS: NARROWED 2026-09-11 -- FOUND BY A PERSON, MEASURED, FIXED IN DELI
COUNTER 0.115.0; NOT YET RUN THROUGH ZOO OR RE-WALKED*

**146. The floor, the walls and the ceiling of a room all wear the same
skin.** Walked 2026-09-11: a ward on cold run 9005's hospital with
concrete underfoot, concrete overhead and concrete-grey walls, said as
"the floor, side and ceiling shouldn't all be the same texture; it looks
good when they are different but uniform in some way (human design)".
MEASURED on that shell's `shell.slots.json`: 7 of 9 floors and 9 of 9
ceilings at style 1 (concrete's), the two `ceiling_tile` ceilings
included; 2 floors at style 4 (`tile`, the only finish this preset's
palette declared). Two causes, both in Deli Counter and both already
written down there. (a) `floors.FLOOR_BY_ROLE` / `CEILING_BY_ROLE` knew
four roles -- public_entry, connector, fortifiable, objective_room --
and the hospital's rooms are `safe_room`, `route_node`, `connector`,
`finale`; over all 176 specs the unmapped roles are open_floor 18,
route_node 17, loot_room 13, None 12, safe_room 4, staging 3, utility 3,
vault 2, stairwell 1, finale 1. Unmapped means the spec default:
concrete. (b) `carpet`, `tile`, `ceiling_tile` and `plaster` were in no
authored palette (122 of 176 specs carry exactly concrete / drywall /
glass / metal / wood), so `skin_style.style_for` fell through to the
default's style -- concrete's Pixelcoat pack and concrete's module stem --
for every finish the maps DID name. Zoo's `kit.py` measured this on
2026-08-21 (410 of 574 plate pairs at style 1) and DC's builder has
printed UNRESOLVED MATERIALS about it since the same day; neither was
read. **FIXED (DC 0.115.0):** the maps cover all 13 emitted roles under
a rule `test_floors` now holds -- for every role the floor and the ceiling
are different materials and no floor wears the partitions' drywall
(objective_room's ceiling moves concrete -> plaster for that reason) --
and a `FINISH_PALETTE` is appended to `spec.materials` by the loader,
after the authored list so authored styles keep their numbers. On the
hospital spec: floors tile 7 (style 4), carpet 1 (7), concrete 1 (1);
ceilings ceiling_tile 8 (8), plaster 1 (9); walls drywall (2). Three
surfaces, uniform by role. All 176 specs load; 669 DC tests pass; every
shell rebuilds because `floors.py` is a geometry source. **RESIDUE:** the
packs exist (`carpet_delco_1997`, `tile_`, `ceiling_tile_`, `plaster_`
all in the theme library) but no Zoo kit has been built from a 0.115.0
manifest yet, so the new stems are unmeasured; the values in the maps are
opinions with reasons, not derived, and the first re-walk judges them.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    lines = raw.decode("utf-8").split("\n")
    for n in (145, 146):
        if any(l.startswith(f"**{n}. ") for l in lines):
            print(f"item {n} already present", file=sys.stderr)
            return 1
    heads = [i for i, l in enumerate(lines) if l.startswith("**144. ")]
    if len(heads) != 1:
        print("item 144 heading matched %d times" % len(heads), file=sys.stderr)
        return 1
    later = [l for l in lines[heads[0]:] if l.startswith("**") and l[2:5].isdigit()
             and not l.startswith("**144. ")]
    if later:
        print("144 is not the last item: %r" % later[0][:40], file=sys.stderr)
        return 1
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines += [""] + APPEND.strip("\n").split("\n") + [""]
    out = "\n".join(lines).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 2 appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
