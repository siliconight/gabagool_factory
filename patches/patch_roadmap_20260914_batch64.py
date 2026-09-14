"""Roadmap batch 64, 2026-09-14 (afternoon): cold run 9053 was refused at
export over a stale building library and 9054 is the zero it should have been
(17); the rain-walk ledger gains the vault, bare-metal and freshness fixes
(155); furnishing shipped (159); the vault room and hero door shipped (160);
items 161 (a stale library is invisible to every gate), 162 (the walker's
vending machines and Delco brands) and 163 (the strip club slice) are filed.

Anchored; each anchor must match exactly once; refuses to write on a miss.
Run from the factory root, then `python tools/roadmap_status.py --write` and
`--check`.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

EDITS = [
    ("item 17", """*STATUS: NARROWED 2026-09-14 -- 9051 AND 9052 ARE TWO MORE ZEROS, AND 9052
IS THE FIRST PACKAGE WALKED IN THE RAIN.""",
     """*STATUS: NARROWED 2026-09-14 (afternoon) -- 9053 WAS REFUSED AT EXPORT OVER
A STALE LIBRARY AND IS NOT A ZERO; 9054, THE SAME BRIEF OVER THE REBUILT
LIBRARY, IS. 9053: 0 interventions, 0 retries, export exit 2 on
`PRESENTATION_PLACEMENT_MISMATCH` -- Deli Counter 0.130.0 and 0.131.0 had
been merged as tracked files while the gitignored `build/*.glb` stayed at
0.129.0 (item 161). No package came out, so the run's own zero does not
count. 9054: 0 interventions, 0 unattributed, 0 retries, export exit 0
(docs/cold_runs/cold_9054/run.log); walk copy `_runs/walk_9054_rain`. It
carries DC 0.131.1 (rooms furnished by kind, surface stock), Zoo 0.86.0, Lot
0.72.2 (the hydrant faces the road), Pixelcoat 0.41.0 (bare metal without
bars), LF 0.86.1. Its lot drew bank_branch_a04, credit_union_a02 and
museum_a03 -- none of the three banks carrying the new vault room, so the
hero door is not in this walk. Previously: 9051 AND 9052 ARE TWO MORE ZEROS,
AND 9052 IS THE FIRST PACKAGE WALKED IN THE RAIN."""),
    ("item 155 status", """*STATUS: NARROWED 2026-09-14 -- THE RAIN WALK (COLD RUN 9052) ADDED FIFTEEN
FINDINGS; ELEVEN HAVE A SHIPPED FIX, NONE YET WALKED.""",
     """*STATUS: NARROWED 2026-09-14 (afternoon) -- EVERY RAIN-WALK FINDING HAS A
SHIPPED FIX; COLD RUN 9054 CARRIES THEM AND NONE IS YET WALKED. Entries 45-47
below record the afternoon's: the vault as a room behind the hero door (item
160), bare metal that stopped mirroring the room in bars, and the two agent
findings closed (the breached vault is deterministic; the Lot spine
difference stands, unexplained). Previously: THE RAIN WALK (COLD RUN 9052)
ADDED FIFTEEN FINDINGS; ELEVEN HAVE A SHIPPED FIX, NONE YET WALKED."""),
    ("item 155 agents", """FOUND BY AGENTS, NOT FIXED: the hero vault's breached state is not
repeatable (shard vertex order changes per build); Lot 0.72.0 did not rebuild
9052's own scene byte for byte from today's inputs, and its walktest spine
differed (302 m against 405 m) -- unexplained.
""",
     """45. **The vault is a room behind the hero door** (DC 0.130.0, Zoo 0.83.0;
    item 160). Slot width to the module (3.6 m for a 1.3 x 2.1 aperture),
    facing, four machine states, swing zone as lint L22, vault rooms
    generated in bank_branch_a02/a03, bank_job and the bank preset; a02's
    objective and loot moved into the vault they named.
46. **Black streaks on the vault door's steel** (Zoo 0.86.0, Pixelcoat
    0.41.0). Not Zoo's UVs (1.000 UV/m every triangle): `metal_bare`'s
    roughness held exactly two values, 0.165 on 27% of the tile in horizontal
    bars, and at metallic 0.9 the glossy bars mirrored the dark room.
    Pixelcoat's `synthesize` stepped roughness on an even 0-1 grid, so every
    grammar's +/- variation held one or two grid points -- 63 of 72 grammars
    changed roughness, no albedo or normal. The door is painted steel now,
    with bare hardware; water tank highlight gradient ratio 1.93 -> 0.96.
    NOT VERIFIED: the bank and casino themes' brass scored slightly worse on
    the bar measure and was not rendered.
47. **The floor safe with its back to the vault door** (DC 0.131.0). Floor
    pieces were written with no rotation; `_front_turn` faces safes,
    cabinets and furnaces into their room.

FOUND BY AGENTS: the hero vault's breached state was not repeatable --
`geometry.subdivide`/`fracture` iterated Python sets; FIXED in Zoo 0.86.0
(rubble_frag and litter_scrap were changing shape per build too; sphere
primitives -- pebble, bollard, six others -- still are, because Blender 5.1.1's
`create_uvsphere` returns faces in a different order per call). Lot 0.72.0
did not rebuild 9052's own scene byte for byte from today's inputs, and its
walktest spine differed (302 m against 405 m) -- STILL UNEXPLAINED. New,
2026-09-14: the same Deli Counter code and specs built in a worktree and in
the checkout chose a different `destination` for one patrol route in
deli_a01, mansion_a03 and warehouse_a02 (`build/*.gameplay.json`, 0.131.1's
rebuild) -- route choice is not deterministic across builds. Unattributed.
"""),
    ("item 159 status", """*STATUS: OPEN 2026-09-14 -- ZOO SIDE SHIPPED; DELI COUNTER'S FURNISH REWRITE
NOT STARTED.*""",
     """*STATUS: NARROWED 2026-09-14 (afternoon) -- SHIPPED IN DELI COUNTER 0.131.0
AND WALKED-READY IN COLD RUN 9054; NOT YET JUDGED. Over 693 rooms of 9 m2 or
more: species per room 2.65 -> 4.97, distinct species 16 -> 24, pieces
carrying surface stock 0 -> 537, pieces per room 15.0 -> 12.2 (chairs 5,817
-> 1,381). country_club_a01's wine cellar: 27 pieces of 2 species -> 20 of 5.
Nav gate unchanged shell for shell -- after two fixes outside furnishing: the
gate had snapped an office objective onto a desk top 1.050 m away instead of
the floor 1.092 m away (the first explanation, furniture blocking the
approach, was WRONG and is recorded as such in nav_gate.gd), and stair
re-seating now evicts generated furniture. Open: the 560 m2 cellar still
reads sparse (density unchanged); Zoo's vending_machine failed its own fit
check (fixed in Zoo 0.87.0, item 162); wine rack, reach-in cooler, dartboard,
hand truck and water cooler have no genome.*"""),
    ("item 160 status", """*STATUS: OPEN 2026-09-14 -- THE DOOR IS BUILT; THE ROOM AROUND IT IS IN
PROGRESS.*""",
     """*STATUS: NARROWED 2026-09-14 (afternoon) -- THE ROOM IS BUILT AND GATED;
NO COLD PACKAGE HAS DRAWN A BANK THAT CARRIES IT. DC 0.130.0: vault rooms
in bank_branch_a02/a03, bank_job and the bank preset (which went from 3 lint
FAIL to 0), lint L22 keeps the swing clear, a02/a03/bank_job navigable as
before. Zoo 0.86.0 painted the door (entry 46 of item 155). Cold run 9054's
lot drew bank_branch_a04 instead, whose authored basement `vault_room` has an
ordinary door: an AUTHORED vault room does not get the hero door, only a
converted vault box does -- that is the next gap. `bank.json` (no rooms, not
modular) is not converted.*"""),
]

APPEND = """

*STATUS: NARROWED 2026-09-14 -- THREE GUARDS NOW ASK; THE LIBRARY IS
REBUILT.*

**161. A stale building library is invisible to every gate, and the guard
that should have said so had been silent since 0.116.0.** Cold run 9053
composed Deli Counter 0.131.0's slots over 0.129.0's shells and the export
was refused four stages in (item 17). Three facts, each measured:

- `deli_counter/build/*.glb` is gitignored; the manifest, slots and gameplay
  beside it are tracked. A fast-forward merge of a branch built in a worktree
  moves the tracked half and leaves the old shells: `bank_tower_a03.slots.json`
  named `chair_waiting_rbeaaca49_3` and `_4`; the GLB drew `_1`, `_4`, `_10`,
  `_13` at 0.129.0's sizes. Deli Counter's own `build_freshness.py`, run after
  the failure: "130 of 132 shell(s) are OLDER than spec_types.py". Nothing
  ran it before the run.
- Level Factory's consumer-side guard (`building_library._geometry_sources`)
  cut `GEOMETRY_SOURCES` out of that tool with a regex that stopped at the
  first ")". Deli Counter 0.116.0 wrote a comment inside the tuple ending
  "(0.116.0)"; `literal_eval` failed; the guard returned [] and printed
  nothing over every run since. Its docstring's premise -- a check that cannot
  find its rule should be silent -- is REFUTED by this: the silence WAS the
  fresh report. LF 0.86.1 parses with `ast` and prints FRESHNESS UNKNOWN when
  the rule is there and unreadable.
- mtime cannot see a checkout that leaves an untracked shell behind. DC
  0.131.1 records `outputs_sha256_16` in every tracked manifest and
  `build_freshness.content_stale` names a GLB that is not its manifest's
  build, or a spec edited since (compared with CRLF folded: `gas_station_a02`
  measured 743 CRLF on disk against an LF hash -- endings alone are not a
  change). `tools/cold_run.py --begin` now asks Deli Counter's tool and
  refuses a stale library unless `--allow-stale-library`, which the journal
  records.

Second-order, and said so: none of this reduces interventions on a fresh
library. It stops a run measuring a library that no longer exists and
calling the result a zero.

**WHAT WOULD CLOSE THIS:** a merge of a Deli Counter branch followed by
`--begin` that refuses, once, for the right reason.


*STATUS: NARROWED 2026-09-14 -- ZOO SHIPPED THE MACHINE; NOT YET IN A COLD
PACKAGE.*

**162. Vending machines should glow, and sell something.** The walker, with a
Deus Ex vending-mod reference: "vending machines should glow" and "we want
fake products that are funny and a bit crass...Delco themed". Zoo 0.87.0:
a 1990s machine (cabinet, backlit front panel, six lit buttons, lit price
display, coin mech, delivery flap, kick plate; 464 tris at every size; the
0.86.0 machine was 0.795 m deep in a 0.75 m slot and now fits exactly), with
emission on the panel, buttons and display at strength 1.0 -- the highest
with no pinned pixel in the basement (panel luma 28.9 -> 110.8) or under the
summer-afternoon preset (1.5 pinned 68.5% of the panel). Twelve invented
brands in one table (`zoo_keeper/core/brands.py`: WOODER, JAWN JUICE, IGGLES
TEARS, SCRAPPLE SODA, MACDADE MUD, SHORE THING, HOAGIE SWEAT, YOUSE GRAPE,
NANA'S BASEMENT, BLUE ROUTE BACKUP, CHESTER GOLD, WIT OR WITOUT -- two renamed
away from real marks), lettered in Pixelcoat's own typeface, chosen by
variant so four variants of one slot are four brands. Compatibility draws the
glow; Heavy Rain's glow threshold (1.1) means no halo at 1.0. Light spill on
the floor was prototyped (one colour-matched omni per machine, +51 luma on
the floor) and needs a Zoo marker, a Lux `vending` rig row and LF's light
census. Open: SCRAPPLE SODA and NANA'S BASEMENT carry a pure-white disc that
blooms; DC's `vending` piece had variants off so every machine in a building
was one brand (in progress, DC 0.132.0); single-size slogans do not read at
4.7 m (4 px cap height) -- a content call for the walker.

**WHAT WOULD CLOSE THIS:** the walker reads a machine's brand from across a
room and laughs, or at least does not ask what the grey box is.


*STATUS: OPEN 2026-09-14 -- PIECES, SURFACES AND LIGHT TYPES SHIPPED; THE
ROOM IS NOT YET GENERATED, AND INTERIORS DO NOT YET READ DARK.*

**163. Strip clubs are lit like offices.** The walker, with GTA IV Triangle
Club references: "strip clubs should have a dingy lived in feel, dark with
colored lights, couches and bars"; then "lou Turks in delco is our comp for
club vibes" -- the PRE-renovation club, since the game is set in the 1990s:
a one-storey windowless box, two bar areas with poles (the stage is in the
bar, stools round it), CRTs on brackets. Measured before anything moved: the
library has three clubs (strip_club_a01..a03, main floors 416-476 m2); their
`stage` and `bar` volumes routed to NO species; `lights.py` gave every
above-ground room a 5-lamp cool fluorescent row; Lux knew nothing coloured.

Shipped, none yet in a generated level:

- **Zoo 0.88.0**: club_stage (forms round / runway / bar_stage, rope light
  on the lip, rail, pole to the slot top), cocktail_table (cloth / bare, bar
  stock), club_chair, bar_stool, neon_sign (24 invented names in one table,
  variant = index), crt_tv form bracket. Every existing species builds
  byte-identical. Five defects found in its own frames and not fixed there:
  tablecloths render as gold burlap and stool seats one red-orange (the
  delco fabric packs ignore the object colour), neon letters read doubled
  (a dark copy behind the tubes), a slot's `material` overrides a sofa's
  upholstery (DC writes `wood` on seating), and two slots differing only by
  material share one stem so the last build wins. In progress (Zoo 0.89.0,
  Pixelcoat 0.43.0).
- **Pixelcoat 0.42.0**: `ps.medallion` (a printed figure with three ink
  levels; noise primitives can only make blotches), `motif` and `wear`
  layers, and carpet_club / wallpaper_club / velvet (three colourways) /
  wood_stained / paint_block for the delco themes; the 72 existing grammars
  byte-identical. Under the walk's own light the wallpaper reads at luma
  21.6 against 98.1 for the old wall -- right under coloured light, a walk
  call otherwise. The room -> surface path was traced: a room has
  `floor_material` and no `wall_material`; walls are per exterior side or
  per partition, one material on both faces; Zoo drops kinds outside
  `KNOWN_KINDS` silently.
- **Lux 0.37.0**: anchor types club_wash, stage_light (aimed, optional
  colour cycle), neon, room_ambient (a ReflectionProbe the room's size),
  `bake_club`; energies derived from the fluorescent rig's floor level at
  the same drop; Compatibility's `max_lights_per_object` 8 measured (10
  lights on one 470 m2 mesh: 2 missing and which two changes with the
  camera). AND THE FINDING THAT OUTGROWS THE CLUB: the room does not read
  dark because interiors are lit by the preset's shadowless sun, sky ambient
  and scene-wide fog, not by their fixtures -- whole-frame luma 58 as built,
  50 with sun shadows, 30 with the probe replacing sky ambient, 9 with fog
  off; the street darkens 93 -> 85 -> 50 alongside. The walker chose dark
  interiors by default (Lux 0.38.0 / LF 0.87.0 in progress: per-room probes
  for every room, sun shadows at the cheapest cascade, fog kept).
- **Deli Counter 0.132.0** (in progress): the club room kind and recipe, club
  light anchors instead of the row, room_ambient with a size for every
  room, the club materials.

**WHAT WOULD CLOSE THIS:** the walker walks a generated strip club and calls
it dingy.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings; refusing", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for label, old, _new in EDITS:
        n = text.count(old)
        if n != 1:
            print(f"anchor {label} matched {n} times; refusing", file=sys.stderr)
            return 1
    if "**161. " in text:
        print("item 161 already exists; refusing", file=sys.stderr)
        return 1
    for _label, old, new in EDITS:
        text = text.replace(old, new, 1)
    text = text.rstrip("\n") + "\n" + APPEND
    io.open(P, "wb").write(text.encode("utf-8"))
    print(f"{P}: batch 64 applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
