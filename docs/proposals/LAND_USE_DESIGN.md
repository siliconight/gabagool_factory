# Land use: what the ground between buildings is for

The walker, 2026-10-03, filing `docs/reference/LAND_PRESSURE_AND_SPATIAL_LOGIC.md`:
"this should directly inform Lot". This maps the guide onto the pipeline as
it stands, measures where every level is today, and orders the work. It is
a proposal; the census in step 1 is built, the rest is not.

## What the guide asks, in one paragraph

Land is a resource people compete for, so a site is laid out from use
outward: why an activity is here, how much space it needs, how people,
goods and trucks reach it, and what explains the land around it. Every
piece of open ground gets a role that shows in its geometry (parking,
loading, yard, verge, vacant lot), frontage is spent on things that want to
be seen, variation is correlated (a street keeps a building line, with a
few explained exceptions), and the tools measure all of it against a stated
boundary rather than asserting it.

## Who owns what here

The guide's section 8 assigns roles by tool. In this pipeline:

| Guide role | Here | Today |
|---|---|---|
| Settlement planner, district archetype | Level Factory brief (`site_shape`, `road_grammar`, `archetype`) | No district, archetype or land-pressure field |
| Street tool | Level Factory `road_grammar.roads_for`; Lot draws | Roads placed after buildings, south of the row |
| Parcel tool | -- | Nothing: no parcels, lot lines or setbacks |
| Building placement | Level Factory `site_variation.site_placements` | A walk along x with seeded jitter (-6..6 m along, -10..10 m across); yaw drawn at random from 0/90/180/270 |
| Open-land uses, dressing | Lot | Parking only as on-street bays; one dumpster a building; everything else is bare plate |
| Validator, metrics | Lot | `site_landuse` (below) is the first land-use measurement |

So "inform Lot" lands in two repos: Level Factory decides where buildings
stand and which way they face, and Lot decides what the ground around them
is. Both are named below.

## Step 1, built: measure it (`lot/site_landuse.py`, `tools/landuse_census.py`)

One boundary, the resolved ground plate, rasterised at 0.5 m; each cell
takes the first use whose drawn geometry holds it -- building, road, kerb
cut, sidewalk, frontage, walk or landing, courtyard -- and the rest is
REMAINDER, ground with no role. Plus building separation, and per road the
building line (setback spread), frontage occupancy, and whether each
fronting building has a ground door facing it. Measured over the 36
distinct lots on disk (`docs/findings/landuse_baseline.txt`):

    plate with no role (remainder)     median 68 %   range 53-88 %
    building coverage of the plate     median 14 %
    building line along one road       spread up to 26 m
    fronting buildings with a door
      facing their road                67 of 126

The walker's lot (gas_block_001, seed 9080): 61 % remainder, most of it one
10,900 m2 piece; the main road's building line runs 2 to 15 m back; two of
its three buildings have a door on the road.

These are the numbers the steps below should move, and the first numbers
roadmap item 18 ("good" as a gate, not only "works") has had to hold.

## The steps, in the order to take them

**2. A door faces the street (Level Factory, `site_variation`).** Choose
each building's yaw from its own ground doors, so a customer door faces the
road it fronts, instead of drawing yaw at random. Guide 5.3, frontage has a
function. Moves: door-facing from 67/126 toward all of them; the 312 door
spurs that met a wall with no door (`docs/findings/entry_paths/NOTES.md`)
toward none. Cost: every seed's layout changes, so baselines move -- run it
as its own piece with the census before and after.

**3. One building line a street (Level Factory, `site_variation`).** Replace
the per-building across-the-road jitter (+-10 m) with a setback the street
holds, and let a building leave it only for a reason the brief or the
family states (a gas station's forecourt, a set-back bank). Guide 5.7,
correlated variation. Moves: setback spread from up to 26 m to a few
metres, with the exceptions named.

**4. Open land gets a role (Lot).** Partition the remainder by what it
touches, and give each piece geometry or dressing a viewer can read (guide
5.4):

- a PARKING FIELD beside or in front of a car-oriented building (gas
  station, strip retail): striped bays, wheel stops, a drive aisle to the
  road, parked cars from `site_parking`'s fleet;
- a SERVICE YARD behind a building, where the dumpster already stands: a
  concrete apron to the back door, a loading strip, the dumpster on it;
- a VERGE along the plate's edge and between properties: grass with the
  street-tree species, a kerb, maybe a fence that marks a boundary;
- a VACANT LOT for a large leftover piece: cracked pad or gravel, weeds, a
  chain-link fence -- the guide's "vacant lot can preserve the outline of a
  demolished building".

Moves: remainder share from ~68 % toward an authored band (say under 15 %),
largest remainder blob from ~10,000 m2 to small slivers. Runtime: each use
is one material and its repeats (stripes, wheel stops, weeds) are
MultiMesh per field, so the draw cost is a handful per lot, priced on the
harness before it ships (`docs/PERFORMANCE_CONTRACT.md`).

**5. The brief says what kind of place this is (Level Factory brief, both
repos read it).** A `settlement_archetype` (the guide's section 6: suburban
strip, borough main street, industrial corridor, ...) and the guide's
controls that change geometry here -- `land_pressure`, `car_dependence`,
`service_intensity`, `vacancy_level` -- each mapped to metres per archetype
(the guide is firm that a 0-1 control is never a distance by itself).
`maintenance_level` stays a skin control, apart from spacing, as the guide
insists. The gas station lots read as a suburban strip today; a borough
main street (close-set storefronts, rear service) is the pattern the art
direction keeps asking for and this pipeline cannot yet make.

**6. Parcels (Level Factory writes, Lot draws and validates).** The guide's
contract (section 8): each building gets a parcel polygon with its frontage
edge, envelope, access connections and open-space allocations, in the site
spec, with stable ids; Lot partitions the plate into parcels plus the
right-of-way and reports the section 11 hard failures. This is the largest
step and the one the others lead to; 2 to 5 show whether the direction
reads before it is taken.

## What this is, by the repo's own measure

None of these removes an intervention in `CLAUDE.md`'s sense: a level with
68 % of its ground bare is not broken, it is unexplained. This is the
"good" gate (roadmap item 18), which until today had no measurement at
all. The census is that measurement; the steps are judged by it and by the
walker's eye, in that order, and neither alone.

## Open for the walker

- The order. Proposed: 2 and 4 first (the door to the street, and parking
  plus service yards), since they are the two the walks have already
  pointed at.
- Which archetype the existing lots are. Proposed: suburban strip, the
  guide's "detached businesses oriented toward road access, broad gaps
  often occupied by parking or circulation".
