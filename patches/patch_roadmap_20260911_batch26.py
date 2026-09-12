"""Roadmap batch 26, 2026-09-11 (evening): cold run 9006 and the re-walk copy
built from it; four status REPLACEs (17, 18, 44, 144), each keeping the old
block verbatim, and one APPEND (148) from the walker's feedback. Asserts
every anchor once; refuses on a miss.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

R = []

# ---------------------------------------------------------------- 17
R.append(("""*STATUS: NARROWED 2026-09-10 -- COLD RUN 9005 SCORED ZERO ON AN ARCHETYPE
NOBODY HAD BUILT, AND THE ROUTE WAS COMPLETED FOR THE FIRST TIME.""",
"""*STATUS: NARROWED 2026-09-11 -- COLD RUN 9006 SCORED ZERO ON THE SAME BRIEF
AS 9005 THROUGH FOUR TOOLS THAT MOVED THAT DAY, THE FOURTH ZERO IN THE
PROJECT AND THE FIRST WHOSE INPUT WAS A RE-RUN ON PURPOSE. The brief under
test was 9005's `county_hospital_001`, byte for byte; what changed between
the two runs is Deli Counter 0.116.0, Pixelcoat 0.28.0, Lux 0.33.0 and Level
Factory 0.72.0 -- seven fixes from the first human walk (items 138-146), and
this run is the measurement of whether they compose. 0 interventions, 0
retries, 0 unattributed file changes; the three files that moved were the
per-candidate DC specs LF is expected to write; 2,463 source files hashed,
every tool repo clean at --begin. All stages succeeded, the package
exported clean (`LF_county_hospital_001.portable-godot`, export exit 0),
58 minutes end to end (20:31 -> 21:29). Both `run` commands exited 1 with
"structural checks passed, blockers open: 0" printed above the exit --
the exit code carries something the log does not name, and the driver
went on because the approvals and export it gates on are separate
commands; that is a finding about the CLI's exit semantics, not about the
level, and it is not an intervention. Log and journal:
`docs/cold_runs/cold_9006/`. EARLIER STATUS, KEPT VERBATIM: NARROWED
2026-09-10 -- COLD RUN 9005 SCORED ZERO ON AN ARCHETYPE
NOBODY HAD BUILT, AND THE ROUTE WAS COMPLETED FOR THE FIRST TIME."""))

# ---------------------------------------------------------------- 18
R.append(("""*STATUS: NARROWED 2026-09-11 -- A PERSON WALKED A SHIPPED PACKAGE, WHICH IS
THE WHOLE ASK, AND EIGHT THINGS CAME BACK THAT NO INSTRUMENT HAD REPORTED.""",
"""*STATUS: NARROWED 2026-09-11 (evening) -- THE RE-WALK COPY IS BUILT FROM A
COLD EXPORT, THE FIXES ARE MEASURED ON IT, AND A CONFOUND IN THE DAY'S OWN
MEASUREMENTS IS NAMED. `_runs/walk_export_county_hospital_001` is
`tools/walk_export.py`'s copy of cold run 9006's package (item 17), Blue
Hour, spawn at (13.5, 1, -10); it is the copy to walk, and the hand-patched
9005 copy is retired as `_runs/walk_county_hospital_001_9005_handpatched`.
MEASURED ON THE 9006 COPY, straight from the export: (a) `texel_density`
537 kit surfaces, every skin at 0.500 world-triplanar, worst mismatch 1.0x
(item 141 -- the export's project.godot declares the script and 49 of 49
sidecars bind it); (b) `anchor_wall_probe` on its shell: 0 lamp points
inside a wall, 6 at exactly 0.250 m from a face (item 143); (c)
`look_shots --station` in a ward: tile floor, drywall walls, ceiling-tile
grid, two skinned concrete props, the lamps on (items 146, 140); (d) the
same ward's supply cart, a metal prop, pure black on a lit tile floor --
the walked defect reproduced from a station 3 m off (item 142); (e)
`mesh_light_census` 3 plates over 8 (11, 10, 10; item 147); (f) the
stairs: 0 of 76 skinned by LF 0.72.0's file-name lookup on this package,
76 of 76 by 0.72.1's module-material lookup (item 144). THE CONFOUND:
the 9005 walk copy I re-spawned and re-shot for items 139, 142 and 144
had lost its LuxRoot in the re-pack (`light_census`: LuxRoot 0, sun 0,
environment 0, against 1/1/1 on the 9006 copy), so every "after" frame
taken on it that day was unlit -- the flat sky and 62% crush recorded
under 139, and the "metallic 0.85 vs 0.0: 6.5 vs 6.5" A/B under 142,
which measured darkness against darkness. REDONE on the lit 9006 copy:
the cart's own pixels are mean luminance 5.7 at metallic 0.85 and 6.2 at
0.0 (92% and 91% at or under 8), its normal map is a proper one (mean
127.5/127.5/254.5), and the conclusion survives: a rust-brown albedo with
no lamp within 4.0 m under blue-hour ambient reads black whatever its
metallic -- item 147's finding, now measured where the lights are on.
WHAT THE RE-WALK ASKS: 138 (windows from outside), 139 (the sign), 140
(the drywall mottle at 8 cm), 143, 144, 145, 146 by eye; and the walker's
new feedback, item 148. EARLIER STATUS, KEPT VERBATIM: NARROWED
2026-09-11 -- A PERSON WALKED A SHIPPED PACKAGE, WHICH IS
THE WHOLE ASK, AND EIGHT THINGS CAME BACK THAT NO INSTRUMENT HAD REPORTED."""))

# ---------------------------------------------------------------- 44
R.append(("""*STATUS: OPEN 2026-08-14 -- specified by `Semantic_Proxy_Replacement_Art_Pass` and `City Collision ArtPass Substitutes`; nothing built. The gate it needs was built today and works*""",
"""*STATUS: OPEN 2026-09-11 -- RE-RAISED BY THE WALKER, FROM THE INSIDE, AND
MEASURED: "a lack of set dressing, in terms of props that make the building
seem more like whatever it says it is -- a bank should have windows/tellers,
ATMs, desks, water fountains." The interior half of this item, and the
number is the same shape as the exterior one. Deli Counter's 176 specs
carry 1,448 placements named for what they are -- `teller_counter` 23,
`desk_manager_office` 40, `nurse_station` 18, `supply_cart` 18,
`aisle_shelf` 22, `vending`... -- and every one reaches Zoo as slot role
`prop` (`kit.VOLUME_ROLES`), which `plan_kit` resolves to the `prop`
species: a box wearing the slot's material. Zoo HAS the species the names
ask for -- `atm`, `teller_line`, `desk`, `filing_cabinet`,
`vending_machine`, `queue_stanchion`, `counter`, `shelving`,
`safe_deposit_boxes`, `drop_safe`, `water_tank`, `crt_tv`,
`security_camera`, 56 in all -- and nothing routes a placement's NAME to
one of them: `species_for` reads only an interactive's `state_geometry`.
So a hospital ward ships two skinned boxes where a nurse station and a
supply cart were authored, and a bank ships a box where its teller line
was. The walker's framing, which is this item's thesis said from the
floor: "the blocks should really just be placeholders until they are
replaced by something more diegetic." That is the contract -- a placement
box says what belongs here, not what it looks like -- and the pipeline
currently ships the placeholder as the product. The gap protocol's
cleanest case: the design already says the word,
the tool already builds the thing, and the wire between them is one
mapping (placement-name keyword -> species, the way `level_design.py`
already keys furniture archetypes on room role + id). EARLIER STATUS, KEPT
VERBATIM: OPEN 2026-08-14 -- specified by `Semantic_Proxy_Replacement_Art_Pass` and `City Collision ArtPass Substitutes`; nothing built. The gate it needs was built today and works*"""))

# ---------------------------------------------------------------- 144
R.append(("""*STATUS: NARROWED 2026-09-11 -- THE CHEAPEST OF THE TWO ANSWERS SHIPPED IN
LEVEL FACTORY 0.72.0 AND MEASURED ON THE WALKED COPY; NOT YET RE-EXPORTED OR
RE-WALKED.""",
"""*STATUS: NARROWED 2026-09-11 (evening) -- 0.72.0 REFUTED ON THE FIRST COLD
EXPORT AND REPLACED BY 0.72.1, MEASURED ON THAT EXPORT'S COPY. The
file-name version found its concrete in a walk copy that happened to carry
loose PNGs beside its kit GLBs; cold run 9006's package embeds every
texture in the GLB (`_write_import_sidecars` mode 3) and ships no PNG, so
on the real thing the import log said "no concrete albedo under art/zoo,
stairs left alone" and 0 of 76 were skinned. LF 0.72.1 loads a `wall_*`
module's IMPORTED scene and duplicates the concrete material it wears,
textures embedded or not, at the tile period the kit pass resolved:
`site_base.glb 76 stair surface(s) skinned on 76 mesh(es); material from
wall_delco_1997_01_w200.glb`, `uv1_scale` 0.49999, world triplanar, on
the 9006 copy. The lesson is item 18's confound in another coat: a copy
is not the package, and a fix measured on a copy is measured once.
EARLIER STATUS, KEPT VERBATIM: NARROWED 2026-09-11 -- THE CHEAPEST OF THE
TWO ANSWERS SHIPPED IN LEVEL FACTORY 0.72.0 AND MEASURED ON THE WALKED
COPY; NOT YET RE-EXPORTED OR RE-WALKED."""))

APPEND = """
*STATUS: OPEN 2026-09-11 -- RAISED BY THE WALKER BEFORE THE RE-WALK; THE
INTERIOR HALF OF LAYER 3, WHICH TODAY HAS ONLY AN EXTERIOR*

**148. Nothing dresses the inside of a building: no posters, clocks, vents,
smoke detectors, garbage -- the non-collision layer that gives a room
character and depth.** Said 2026-09-11, before the 9006 package was even
walked: "surface dressing on the walls and floor as extra non-collision
layers to give it character and depth, like posters, garbage, clocks,
vents, smoke detectors." What exists: Layer 3 surface dressing
(`zoo_clutter_build` -> `lot_site_surfaces` -> `patina_surface_dressing`,
item 110) scatters `litter_scrap`, `weed_tuft`, `pebble`, `rubble_frag`
over SITE surfaces -- the ground between buildings -- as one MultiMesh
with no collision, 1,085 instances on 9006's package. Nothing walks an
interior wall, ceiling or floor. Item 45 is the same layer's depth
guidance for large surfaces and item 41 is the structural-art half; this
is the room-scale, wall-mounted half neither names. What it needs, in
the gap protocol's terms: species that are flat or shallow and read at
arm's length (poster, clock, vent grille, smoke detector, light switch,
exit sign, floor litter), a placement rule keyed on the wall slots and
room roles Deli Counter already emits (posters in a `public_entry`, vents
and detectors on every ceiling, litter in `utility`), and the same
no-collision, one-MultiMesh contract the exterior layer already keeps.
**WHAT WOULD CLOSE THIS:** the interior surfaces reachable by the Layer 3
chain, one species placed by one rule, and a walk that finds a room
reading as inhabited rather than modelled.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for old, new in R:
        n = text.count(old)
        if n != 1:
            print(f"anchor matched {n} times; refusing: {old[:60]!r}", file=sys.stderr)
            return 1
    if "\n**148. " in text:
        print("item 148 already present", file=sys.stderr)
        return 1
    for old, new in R:
        text = text.replace(old, new, 1)
    text = text.rstrip("\n") + "\n" + APPEND.rstrip("\n") + "\n"
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 17, 18, 44, 144 replaced; 148 filed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
