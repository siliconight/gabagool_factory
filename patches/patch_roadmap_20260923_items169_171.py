"""Roadmap items 169-171: the ladder skin, the open roof holes, and the
exterior-access frequency.

All three came out of the walker's direction on 2026-09-23 and every number in
them was measured before it was written.

Anchored on the file's final paragraph (item 168's close), which must match
exactly once. Does NOT touch the generated index -- `roadmap_status.py --write`
regenerates that and `--check` must then agree.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ANCHOR = """opening -- a gate that passes is not the same as a level that reads right.*
"""

ITEMS = """
*STATUS: OPEN 2026-09-23 -- DESIGNED, STAGED AND DRY-RUN CLEAN, HELD BEHIND A
COLD RUN. Four anchored patches (`patches/patch_worldskin_ladders.py`,
`patch_dc_ladder_mode_in_name.py`, `patch_fixture_material_tint.py`,
`patch_worldskin_ladders_test.py`) apply cleanly against the live files and
were not run because cold run 9072 was in flight.*

**169. A ladder ships in the greybox yellow, and skinning it spends a
legibility signal the palette deliberately bought.** The walker's call,
2026-09-23, with two reference photographs: rusted outside, clean inside.

**What ships today:** nothing skins a ladder. 38 surfaces and 22.82 m2 of flat
`gb_ladder` on cold run 9070's package. The `greybox_skin` gate from item 168
counts them and does NOT refuse, because an absent capability is not a
regression.

**The correction that shaped the design, recorded because it was made out
loud and was wrong.** The ladder was described as "still grey". It is not:
`GREYBOX_PALETTE` (`deli_counter.py:326`) gives `gb_ladder` (1.00, 0.90, 0.55)
-- luminance 0.897, the BRIGHTEST value on the site -- beside `gb_stair`'s
(1.00, 0.78, 0.32). Its own comment says why: a ladder "gets the brightest
value on the site because it is the smallest thing that has to be found". Only
the slab collar of item 168 was grey (`gb_floor`, 0.52). The claim had been
inferred from the word "greybox" rather than read off the palette.

**So the signal is MOVED, not spent.** A rusted ladder on a weathered wall is
the "amber and grey reading as one surface" failure that palette's own comment
warns about. Deli Counter emits rails and rungs as SEPARATE meshes
(`deli_counter.py:2032`), so reference 2's read -- matte near-black frame,
bright galvanised treads -- is reproducible with no new geometry: rails take
the darkest metal the building owns, rungs the lightest. Outside, both halves
take the rust (reference 1, where the ladder reads against grey concrete
rather than against itself).

**Measured, so none of it is chosen:**

    both looks already ship   M_Skin_metal_delco_1997 IS metal_rusted_street;
                              M_Skin_metal_bare_* / _painted_* are the clean
                              ones. Nothing needs authoring in Pixelcoat.
    source family prop_       1 of 3 buildings owns metal in a KIT family;
                              3 of 3 own it in prop_ (27, 21, 41 modules).
                              A kit lookup repeats the refuted STAIR_KIND
                              mistake and would refuse on two in three.
    tint from albedo_color    31 distinct metals spanning luminance 0.015 to
                              0.789; the name's hex suffix is a weaker source
                              than the value it encodes.
    discriminator exists      Ladder.placement_mode (spec_types.py:217),
                              authored per ladder. 109 interior (52 explicit,
                              54 unset taking the dataclass default, 3 shaft)
                              against 3 exterior.

**It refuses rather than shipping something worse than yellow:** a building
with only one tinted metal gets a `push_error`, because a uniformly metal
ladder has no contrast in it at all and the yellow at least reads.

*STATUS: OPEN 2026-09-23 -- MEASURED, NOT STARTED. 58 of 58 `roof_access`
ladders cut the slab they arrive through, and 74 `hatch` links do the same.
Nothing in any tool emits a lid.*

**170. Every roof opening in the library is an open hole, and a building does
not have an open hole in its roof.** The walker, 2026-09-23.

**Measured across 370 specs:**

    roof_access ladders            58   all 58 cutting a slab
    hatch vertical_links           74   cut the slab, emit a HATCH_ marker
    floor_hole vertical_links      24
    lid / panel / cover geometry    0   in Deli Counter, Zoo or Lot

`_vertical_links` (`deli_counter.py:2556`) already records the gameplay
intent: a hatch cuts its slab, emits `HATCH_<x>_<y>` into `gameplay.markers`
and carries `breachable`. `ladder.py:47` already classifies a termination as
`roof_hatch_exit`. The CONTRACT is there and the GEOMETRY is not, so the
result is a marker floating over a hole.

**This is the same class as item 168 and worth seeing as one:** an opening
whose treatment was never finished. 168 was the cut edge nobody skinned; this
is the cut itself, uncovered. Item 168's reveal skin dresses the shaft, which
is still right -- a hatch is open some of the time -- but with the lid missing
the hole shows sky or interior from the wrong side at all times.

**The machinery to build it already exists and should be reused rather than
invented.** `interactives.py` carries `door` and `garage` kinds with
`closed` / `open` states and `collision_per_state`; `derive_interactive`
computes a stable id from the authored opening and its wall so the geometry
pass and the gameplay pass agree without talking to each other.

**THE BULKHEAD IS THE BETTER ANSWER, and it arrived as a reference before
this item was written.** The walker's photograph is a Delco/NYC-shaped
tenement roofscape: a flat roof behind a parapet, roof vents and chimney
stacks, a facade fire escape of per-storey balconies with drop ladders, and --
the point -- a small enclosed BULKHEAD standing on the roof with a dark,
graffitied door in its side. That is how an urban building of any size
actually reaches its roof: the stair does not stop at a hatch, it runs up into
a little house and you walk out of a DOOR.

Which collapses the problem. A bulkhead turns a hole in a HORIZONTAL slab
needing a lid nobody has built into a DOORWAY IN A VERTICAL WALL -- and Deli
Counter already builds doorways, already cuts them with `_box_with_holes`,
already derives their interactive through `_opening_to_hole` ->
`_machine_for` -> `interactives.derive_interactive`, and Zoo already has a
`doorway_` family that every building's pack carries. The networked open is
then an ordinary door to the game code outside Level Factory, with no new
interactive kind at all.

It is also the honest reading of the existing stairs. `_stairs` already runs a
flight to the top storey; a bulkhead is the enclosure over its top landing,
not a new circulation element.

**Owners, revised.** Zoo -- a `bulkhead` species: four short walls, a shallow
mono-pitch or flat roof, and a doorway slot on one side, sized to the stair
landing below it and skinned from the building's own pack like any other
module. Deli Counter -- stand one over the top landing of any stair that
reaches the roof, cut its doorway, and let the existing opening path derive
the interactive; the roof slab under it then needs no hole at all, which
removes 58 of them rather than covering them. Level Factory -- nothing, if the
above hold.

**Where a lid is still the right answer:** a ladder-only service opening,
where a bulkhead would be absurd on the roof area available -- a plant hatch,
a small shop's roof. So the two live together: a bulkhead where a STAIR
reaches the roof, a lid where a LADDER does. The 58 `roof_access` ladders
above are the population to split between them, and that split is the first
thing to measure rather than assume.

**What would falsify the framing:** a roof opening that should stay open -- a
light well, a plant deck. Those exist and the rule must not close them
blindly, which argues for the treatment being a property of the LINK rather
than of every hole.

*STATUS: OPEN 2026-09-23 -- A BUILT CAPABILITY THAT IS ESSENTIALLY UNUSED. 2
fire escapes in 370 specs; 3 ladders in the whole library are exterior.*

**171. Exterior access exists and almost never gets placed.** The walker,
2026-09-23: more outdoor ladders would be good for fire escapes and alternate
entry points -- but not on every building, because urban fire code does not
put them there.

**Measured across 370 specs:**

    specs carrying a fire escape       2   (2 assemblies in total)
    fire_escape_termination ladders    2
    ladders with an exterior mode      3   (2 exterior_wall, 1 platform)

`Builder._fire_escapes` (`deli_counter.py:2184`) already builds the whole
assembly: a stack of balcony decks one per served story, short stair segments
between them, guard rails on the three open sides, hung outside the shell and
tagged `FIREESCAPE_<id>_<story>`. It is not a capability gap. It is a
PLACEMENT gap -- nothing in the recipes reaches for it.

**The rule should be derived, not dialled.** Fire escapes are a second means
of egress, so the condition is a property the spec already knows: storey count
and how many independent interior stairs a building has. A three-storey walkup
with one stair needs one; a two-storey retail box does not; a warehouse with
two protected stairs does not. That is a rule this pipeline can compute, and
picking a percentage instead would be exactly the kind of chosen constant
CLAUDE.md asks to be derived from something.

**Why it matters beyond the look:** an exterior stack is an alternate entry
route, so placing them changes the site's readable approaches -- which is
Laser Tag's and Dispatch's business as much as it is art. Any rule here should
be measured against route counts, not only counted.

**Coupled to 169 and 170:** exterior ladders are the ones that take the rusted
skin, and today there are three of them in the entire library, which is why
169's interior look is the half worth getting right first. And a fire escape
that terminates on a roof meets 170's missing hatch.
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
    out = (text + ITEMS).encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"PIPELINE_ROADMAP.md: {before} -> {len(out)} bytes "
          f"(+{len(out) - before}), {out.count(10)} lines, LF")


if __name__ == "__main__":
    main()
