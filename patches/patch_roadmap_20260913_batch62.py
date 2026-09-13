"""Roadmap batch 62, 2026-09-13 (late night): cold runs 9044-9050 are seven
more zeros and 9050 carries the walker's second round (17); item 155's ledger
records what that round fixed, what is unverified in game, and what is left;
items 156 (fire escapes and uneven massing), 157 (weather) and 158 (cars) file
the walker's three new asks with the surveys behind them.

Anchored; each anchor must match exactly once; refuses to write on a miss.
Run from the factory root, then `python tools/roadmap_status.py --write` and
`--check`.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

ITEM17_OLD = """*STATUS: NARROWED 2026-09-13 (night) -- 9043 IS THE THIRTY-FIRST ZERO AND
IT CARRIED THE ART DIRECTION'S FIRST FOUR TOOL CHANGES."""

ITEM17_NEW = """*STATUS: NARROWED 2026-09-13 (late night) -- 9044 THROUGH 9050 ARE SEVEN
MORE ZEROS, AND 9050 CARRIES THE WALKER'S SECOND ROUND. Each: 0
interventions, 0 unattributed, 0 retries, export exit 0 (docs/cold_runs/
cold_90NN/run.log). 9050 ran Deli Counter 0.126.0, Lot 0.69.4, Zoo 0.78.0,
Pixelcoat 0.39.0, Lux 0.34.0 and Level Factory 0.82.0 -- the fixes item 155
lists -- and its frames were read before the walk copy went out: the office
stair's hole now stands inside the office behind wood rails, the teller line
has a locked staff side, and the signalised T-junction carries a signal and
no stop signs, which is what the rules say. The same frames found what no
gate did, again: a one-storey switchback cuts its hole two runs wide, and the
unused run stands open for the 2.05 m the guards leave clear at the landing
(item 155). Previously: 9043 IS THE THIRTY-FIRST ZERO AND
IT CARRIED THE ART DIRECTION'S FIRST FOUR TOOL CHANGES."""

ITEM155_STATUS_OLD = """*STATUS: NARROWED 2026-09-13 (evening) -- THE WALKER PLAYED THE LEVEL, AND
SIX OF TWENTY-ONE FINDINGS ARE FIXED."""

ITEM155_STATUS_NEW = """*STATUS: NARROWED 2026-09-13 (late night) -- EIGHTEEN OF THE ROUND'S
FINDINGS HAVE A SHIPPED FIX, SOME NOT YET SEEN IN GAME, AND THE
FRAMES OF THE FIX FOUND A NEW ONE. Cold run 9050 carries every fix listed
under "FIXED IN THE SECOND ROUND" below; the walk copy is `_runs/walk_9050`.
Left: the fizz, the seams, the white boxes, the corrugated-steel lighting
(the walker deferred the question), and the open unused run of a one-storey
switchback. Previously: THE WALKER PLAYED THE LEVEL, AND
SIX OF TWENTY-ONE FINDINGS ARE FIXED."""

ITEM155_CLOSE_OLD = """**WHAT WOULD CLOSE THIS:** every entry above fixed or explicitly declined by
the walker, and a walk of a fresh cold package that raises none of them
again."""

ITEM155_CLOSE_NEW = """FIXED IN THE SECOND ROUND (cold run 9050 carries all of it).

21. **The "13" frame** (entry 20; DC 0.126.0). Diagnosed: `bank_branch_a03`'s
    basement stair's hole straddled the office wall by 1.15 m, `wall_voids`
    deleted 3.4 m of that wall, and the office door stood beside the gap. NOT
    caused by 0.124.0's lengthening -- the old 4.0 m run already crossed it; a
    first reading here said otherwise and the older spec refuted it. Layout
    lint L21 now fails a hole that cuts a wall or opens under a doorway;
    `stair_pitch.clear_walls` re-seats the stair (presets run it; 16 library
    stairs moved, two hand fixes). 42 findings in 25 specs and 6 of 18 presets
    when the rule was written -- `bank`, behind every cold run, among them.
22. **"Stair placement needs to be thicker"** (entry 20; DC 0.126.0).
    `stairwell.stair_guards`: full-storey side walls and 1.07 m rails, baked
    as volumes, read by the containment review. The review used to count
    walls the builder had deleted (`corner_deli_heist_01`'s stairwell,
    measured in its glb). The first draft of the guards walled whole flights
    and the nav gate caught three shells sealed off (`twin_a01`, `bank_job`,
    `foundry_heist_vertical`); each long-edge guard now stops 2.05 m short of
    the landing end.
23. **The teller booth** (entry 19; DC 0.126.0). `enclose_teller_lines`: the
    staff side becomes a `staff_only` room behind two doors that ship LOCKED.
    Enclosed: the `bank` preset, `bank_branch_a02`/`a03`, `bank_job`. Left
    open with the reason: `bank_branch_a04` (10.9 m deep), `credit_union_a01`
    (1.1 m).
24. **Furniture wearing the walls** (entries 13 and 18; DC 0.126.0). Every
    placed piece names wood or metal; 67 existing pieces migrated. The
    contrast itself is still unmeasured.
25. **Chairs facing walls** (entry 8; DC 0.126.0). Wall pieces turn into the
    room.
26. **Stop signs** (entries 7 and 9; Lot 0.69.4, Zoo 0.77.0/0.78.0). One per
    junction approach on the driver's right, 1.2 m before the crosswalk, none
    at a footpath cut, none under a signal; plate in front of its pole; STOP
    legend. East/west shop signs faced their walls (0.69.2 read the transform
    as columns; Godot reads rows) and face the street now.
27. **The horizontal path and the asphalt colour change** (LF 0.82.0). Door
    spurs end on the sidewalk; a chain path that crossed the cross street
    mid-block is no longer emitted.
28. **Paint blotches** (entry 10a; Pixelcoat 0.39.0, Lot 0.69.4). 8 m tile,
    wear from 2 m patches to 6 cm; identical bar pairs in one crosswalk 36 of
    36 -> 0 of 36; each marking gets its own texture offset.
29. **Nothing in the cabinets** (entry 10; Zoo 0.78.0). Shelves carry stock.
30. **Traffic lights with no colour** (Zoo 0.77.0). Six lenses had one orange
    material; red, amber and green now.
31. **Light through the basement wall** (Lux 0.34.0). Ceiling lamps are
    downward spots: lamps lighting the storey above 56 -> 0. THE WALKER HAS TO
    JUDGE THE LOOK: ceilings lose the halo around each fixture.
32. **Debug overlay in release builds** (entry 5's to-do; LF 0.82.0).

UNVERIFIED IN GAME (fixed by measurement, not yet walked): the car wheel
jitter (entry 11: tyre faces lay exactly in the body plane, now 2 cm inside),
the safe details (entry 12), the light leak's new look (31), and whether the
white boxes (entry 16) were the unmaterialled cover pieces (24) or the white
bollards and bins visible at the kerb in 9050's street frame.

FOUND BY 9050'S OWN FRAMES.

33. **A one-storey switchback's unused run is a pit.** `flight_rect` cuts a
    switchback's hole both runs wide at every storey; with one leg, the second
    run holds nothing, and the guards leave the first 2.05 m beside the
    landing open. Suspected fix, not measured: cut each slab only across the
    run whose leg arrives there -- a leg's headroom is its own run, and the
    next leg climbs from a landing standing on slab. Changes every switchback,
    so it goes through the nav gate as its own release.

**WHAT WOULD CLOSE THIS:** every entry above fixed or explicitly declined by
the walker, and a walk of a fresh cold package that raises none of them
again."""

APPEND = """

*STATUS: OPEN 2026-09-13 (late night) -- FILED FROM THE WALKER'S PHOTO,
WITH THE SURVEY OF WHAT EXISTS. Nothing built yet.*

**156. Fire escapes, brick walk-ups, and buildings that are not one box at
one height.** The walker, with a photo of a brick walk-up: "this is
something i'd like to see in our toolset, fireescape stairs brick, uneven
architecture." The photo and the survey are in
`docs/SET_DRESSING_REFERENCES.md` ("The walker's fire escape photo").

MEASURED (2026-09-13, read-only survey):

- **Deli Counter's fire escape is rules, not geometry.** `FireEscape`
  (spec_types.py:242), fifteen placement tests, `ladder_place.
  fire_escape_proposal`, and `_fire_escapes` (deli_counter.py:2126) building
  a 0.12 m deck, ONE rail with no collision on the outer edge only (the
  docstring says three sides), and a 0.6 x 0.6 m visual-only column where the
  stair should be. Nothing is written to slots.json, so no art reaches it;
  the rail is tagged `floor` and the deck sounds like brick. 2 of 132 library
  specs author one, both serving a single floor; 0 of 177 generated specs; no
  preset calls the proposal. Position ignores setbacks.
- **Zoo** has `ladder` and `stair_rail` and no landing, grating, open-tread
  steel flight or drop ladder; no slot role routes to any of them.
- **Brick** works end to end; projecting stone lintels, sills and cornices do
  not exist (DC's are flush infill; Zoo's cornice is cut in by design).
- **Massing**: rectangular setbacks only (2 specs); no recessed bays or light
  wells; one parapet height; no chimneys. Level Factory's rows always leave
  an 8 m street, so no two generated buildings touch.

SMALLEST FIRST SLICE, BY OWNER: Deli Counter rebuilds `_fire_escapes` as
walkable landings and flights with collision and guarded edges, recorded as
slots, and proposes one by default where the profile allows (`rowhome`); Zoo
grows `fire_escape_landing` and `fire_escape_stair`; Pixelcoat grows a steel
grating (its grammar already cuts holes). Then massing: a recessed facade
segment in DC, and a terrace site shape in Level Factory with buildings
touching at different heights. `twin` is missing from the LF adapter's valid
presets.

**WHAT WOULD CLOSE THIS:** a cold package with a walk-up whose fire escape a
body can climb from the drop ladder to the top landing, on a block where the
walker can see two buildings of different heights share a wall.


*STATUS: NARROWED 2026-09-13 (late night) -- THE OWNER IS LUX AND SLICE 1 IS
IN PROGRESS ON A BRANCH. Rain only; wetness and puddles are later slices.*

**157. Weather: rain and wetness on top of the level.** The walker: "another
layer to Level factory ... how to do things like rain and wetness on top of
assets in the level", with two Godot rain tutorials (GPUParticles3D ribbon
streaks, collision boxes/heightfields/SDF, sub-emitter ripples, fog).

MEASURED (survey, 2026-09-13):

- **Lux already owns a stub.** `LuxWeatherProfile` (fog, grade, one
  `surface_wetness`), `LuxRoot.set_weather`, presets `heavy_rain` (fog 0.012,
  wetness 0.85) and `ps1_storm_night`. No particles anywhere in any repo.
- **Wetness reaches no shipped surface.** Lux pushes it only to
  ShaderMaterials in its `lux_materials` group; every surface in the export
  is a StandardMaterial3D (295 in the walk copy, 0 ShaderMaterials).
- **The brief asks and nothing listens.** `MissionBrief.weather` exists,
  briefs set "rain", and `_preset_for` reads `time_of_day` only.
- **Renderer**: packages ship on GL Compatibility; Lux's own project and its
  perf numbers are Forward+. Believed (to verify on 4.7): box particle
  collision works there, heightfield/SDF collision, volumetric fog and decals
  do not. Pixelcoat's generation_7 pipeline makes wet maps no factory grammar
  uses.

SLICES: (1) Lux rain emitter following the camera, one collision box per
roof, LF picks the rain preset from `brief.weather` -- in progress on
`rain-slice1` branches of Lux and Level Factory; (2) wet ground: Lux pushes a
wet response to BaseMaterial3D on exterior surfaces, Lot ground first;
(3) puddles as flat Zoo species placed by Patina; (4) ripple sub-emitters.

**WHAT WOULD CLOSE THIS:** a cold package whose brief says rain, walked: rain
outside, dry inside, wet ground that reads as wet, at a measured frame cost
on the Compatibility renderer.


*STATUS: NARROWED 2026-09-13 (late night) -- ZOO IS REBUILDING THE CAR ON A
BRANCH. Nothing merged.*

**158. The cars read as boxes.** The walker, with a frame of the parked car
and photos of a 1991 Ford Explorer and a 1990s Geo Metro: "we need our cars to
upgrade quite a bit. missing a lot of detail, side windows, transparency, ect
ect". Zoo 0.78.0's `simple_car` is a slab body with a box cabin, one opaque
windshield band, cylinder tyres in no arches, a bar bumper, no lights,
mirrors or door lines. 0.78.0 fixed its tyres z-fighting the body side
(0.00 mm apart, measured by `tools/coplanar_probe.py`).

In progress on Zoo's `cars-1997` branch: sedan, hatchback and SUV styles with
pillars and separate transparent glass (proven in Godot, not by render), a
simple interior, arches, hubs, lamps, mirrors, bumpers, 1990s paint, zero
coplanar pairs, the species id and Lot's dims contract kept.

**WHAT WOULD CLOSE THIS:** the walker walks a street of the new cars and
names them as 1990s cars, with nothing jittering.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings; refusing", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    for label, old in (("item17", ITEM17_OLD), ("155 status", ITEM155_STATUS_OLD),
                       ("155 close", ITEM155_CLOSE_OLD)):
        n = text.count(old)
        if n != 1:
            print(f"anchor {label} matched {n} times; refusing", file=sys.stderr)
            return 1
    if "**156. " in text:
        print("item 156 already exists; refusing", file=sys.stderr)
        return 1
    text = text.replace(ITEM17_OLD, ITEM17_NEW, 1)
    text = text.replace(ITEM155_STATUS_OLD, ITEM155_STATUS_NEW, 1)
    text = text.replace(ITEM155_CLOSE_OLD, ITEM155_CLOSE_NEW, 1)
    text = text.rstrip("\n") + APPEND
    io.open(P, "wb").write(text.encode("utf-8"))
    print(f"{P}: batch 62 applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
