"""Roadmap item 168: greybox survives into themed packages where theming has
no pass for it -- found by the walker as a grey collar around every ladder
shaft and stairwell.

Anchored on the file's final paragraph, which must match exactly once. The
roadmap is LF and ~1.08 MB; read this session at 1,075,980 bytes, 0 CRLF,
matching the figure the listing reported.

Does NOT touch the generated index or the counts line -- `roadmap_status.py
--write` regenerates those, and `--check` must then print that the index
matches its items.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ANCHOR = """a customer worth it -- all the repeated interior stock at once, not one strip
of felt.*
"""

ITEM = """
*STATUS: NARROWED 2026-09-23 -- THE SLAB CLASS IS CLOSED, MEASURED AND GATED;
THREE OTHER GREYBOX SURFACES REMAIN AND ARE NOW COUNTED. Slab surfaces drawing
a greybox material: 344 -> 0 on cold run 9070's package re-imported with LF
0.106.0's `_skin_slabs`, and the new `greybox_skin` gate was measured REFUSING
that package before the fix and passing after. What remains, attributed in
full: gb_ladder 38 surfaces, gb_wall 28 (roof parapets), gb_floor 2 (vault
ledges) -- absent capabilities, not regressions, and deliberately reported
rather than refused on.*

**168. Greybox survives into a themed package wherever theming has no pass
for it, and only a person looking at the screen has ever caught it.** Walked
2026-09-23.

**What the walker saw.** On a ladder in cold run 9070's package, looking down:
the floor below read grey and untextured, and the real texture appeared on the
way down. Then the same descending a staircase, reported independently.

**Four cheaper explanations, all measured, all wrong.** They are kept here and
in `zoo_worldskin.gd` above the rule that replaced them, because a retracted
finding is cheaper to keep than to rediscover -- and because three of the four
were the obvious answer:

    NOT draw distance or texture loading. Every mesh in that column reports
      `visibility_range begin/end = 0`, `lod_bias = 1.0` and no distance fade.
      NOTHING in the scene changes with camera distance at all.
    NOT occlusion culling. Two package copies differing only in
      `use_occlusion_culling` in `project.godot` -- never at runtime, which
      `occluders_ab.gd`'s own header forbids -- drew identical counts at all
      four eye heights (52/38/82/12).
    NOT z-fighting. The two VISIBLE faces are 20 mm apart (+3.320 against
      +3.300) and a 24-bit buffer separates about 0.03 mm at ladder range. The
      coplanar pair that made this look plausible is the themed floor's
      UNDERSIDE against the slab's top, which backface culling never draws.
    NOT a gap in the floor. Themed floor area equals slab area to 0.1 m2
      (3192.0 against 3192.0), and the ladder hole is cut through BOTH to the
      same rectangle -- x 53.45..54.55, z 21.9..23.2, 1.10 x 1.30 m.

A fifth instrument was discarded rather than believed: the saved frames from
the first probe were 7-of-8 pure black (mean 0.0, stddev 0.00), the same dead
instrument that once reported a merge "pixel-identical" from frames that were
99.7% black.

**What it is.** Theming skins a slab's TOP (as a floor) and its BOTTOM (as a
ceiling) and never touches the faces that a hole cut through it CREATES.
`deli_counter._slab_holes_cut` (`deli_counter.py:2234`) boolean-subtracts the
opening and the new interior faces inherit the slab's flat `gb_floor`. A slab
is `floor_thick` deep, so a 1.10 x 1.30 m ladder hole is ringed by 1.44 m2 of
bare greybox -- THE SAME AREA AS THE OPENING IT SURROUNDS, which is why it
fills the view from anywhere but straight down, and why descending past it
reveals the themed floor below. 8 of 344 slabs in that package are cut,
carrying 10.44 m2 between them: every ladder shaft and every stairwell.

**It was not new, and it was not the performance pass.** That was the first
guess and it is recorded because it was wrong. Every package measured back to
`walk_export_county_hospital_001` (2026-09-11, before any of that work) ships
`[('gb_floor', False)]` on its slabs, and no commit has ever touched "slab" in
`zoo_worldskin.gd`. What changed is that 9070 was the first package since Zoo
1.2.0 to ship the textures its GLBs name (item 166's greybox regression):
before it everything was grey and a grey collar was unremarkable. The
performance work REVEALED this rather than causing it.

**The fix** is `_skin_slabs`, beside roadmap 144's `_skin_stairs` and built to
the same shape -- world triplanar, because a greybox box carries POSITION and
NORMAL only and a boolean's new faces carry no usable UVs either way. The slab
takes the floor family: the collar's top edge abuts the themed floor plane, so
sharing that family makes the one seam a walker actually sees continuous. The
WHOLE slab is skinned rather than the collar alone, because the buried top and
bottom are one mesh with one material either way and picking interior faces
out of a boolean result would mean trusting normals the cut generated.

    slabs skinned        120 + 80 + 144 = 344, 0 left flat
    slab material        gb_floor [FLAT]  ->  M_Skin_slab_reveal [tex]
    distinct materials   261 -> 262   (+1, one duplicate per base)
    surfaces submitted   unchanged -- the material is swapped, not added

**And the gate, which is the half that matters to item 18.** CLAUDE.md's
complaint is that every guardrail here measures traversal correctness and none
measures whether the result reads as designed; of the three problems found by
playing a generated level, one was caught by an instrument and two by a person.
This is a third caught by a person. `packages/exporting/greybox_skin.py` (the
verdict) and `assets/godot/greybox_census.gd` (the measurement) count surfaces
still drawing a `gb_*` material in the running scene.

IN THE ENGINE, not over the GLBs: `zoo_worldskin.gd` is an IMPORT
post-processor, so a shipped GLB keeps its greybox materials by design and a
glTF-level check would refuse every package ever built while measuring the
wrong artefact.

WHAT IT REFUSES AND WHAT IT ONLY REPORTS was decided from the census rather
than chosen, and every item in the output is attributed:

    gb_floor   346 surfaces   (344 slabs + 2 vault ledges)
    gb_ladder   38 surfaces
    gb_wall     28 surfaces   (roof parapets)
    -------------------------
               412 surfaces   on 9070's package, before the fix

It refuses on SLABS, where the pass now guarantees zero, and reports the rest.
A greybox ladder is not a regression -- nothing has ever skinned one -- and
refusing over it would block every export on work nobody has done, turning a
gate into an intervention generator.

**A caution recorded with the instrument:** the census reports TOTAL mesh
surface area, not visible area, and the gap is three orders of magnitude.
`gb_floor` reads 17,447 m2, almost all of it slab faces buried under a themed
floor and ceiling, against the 10.44 m2 a walker could actually see. The
refusal keys on surface COUNT for that reason, and the census says so at
length so nobody quotes the square metres as though they were visible.

**What remains open under this item:** the 38 ladder surfaces, 28 parapets and
2 vault ledges above. The ladder is the one the walker is actually holding
while looking at the fixed floor, and its family choice is less obvious than
the slab's -- a ladder is metal, and no building's pack is guaranteed to carry
a metal family the way it carries a floor.

**In flight at the time of writing:** cold run 9071 runs the club brief an
eighth time, deliberately unchanged from 9070's, so the only new variable is
LF 0.106.0. What would falsify the claim: a census still reporting slab
surfaces on a greybox material, a worldskin `push_error` naming a base it
could not find a pack for, or a walk that still shows a grey collar around an
opening -- a gate that passes is not the same as a level that reads right.*
"""


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: roadmap is LF; found CRLF")
    text = data.decode("utf-8")
    hits = text.count(ANCHOR)
    if hits != 1:
        raise SystemExit(f"REFUSED: anchor matched {hits} times")
    if not text.endswith(ANCHOR):
        raise SystemExit("REFUSED: anchor is not the end of the file")
    before = len(data)
    out = (text + ITEM).encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"PIPELINE_ROADMAP.md: {before} -> {len(out)} bytes "
          f"(+{len(out) - before}), {out.count(10)} lines, LF")


if __name__ == "__main__":
    main()
