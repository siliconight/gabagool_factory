# The pole line: utility poles, their wires, and the lamps and signs they carry (proposal, 2026-10-11)

**Status: PLANNED, not built.** Roadmap 240's first build. Mapped read-only
against Lot, Zoo and the comps on 2026-10-11 while cold run 9248 ran; re-read
every cited line before patching (CLAUDE.md, grounding).

## What the comps ask for

`docs/reference/PHILLY_STREET_COMPS.md`: in two of the walker's three
photographs the overhead network is the strongest line in the frame -- a
wooden pole at the corner carrying a cobra-head on a long arm, the
street-name sign, a low side-street signal and equipment, wires crossing in
every direction; on the rowhouse street, cobra-heads on poles at the kerb and
wires overhead. The factory stands none of it: every lamp is its own steel
pole, every sign its own post, and there is not one wire.

## What the factory does today (read, with the lines to re-read)

- **Lamps** (`lot/site_furniture.py`, `plan_furniture` ~800-900):
  a `streetlight` (0.7 x 0.3 x 6.0 m) on BOTH kerb bands of every street,
  every `LAMP_SPACING` 25 m from `LAMP_START` 5 m, nudged off kerb cuts,
  markers and shop bands, a tree halfway between each pair; a road without a
  sidewalk gets `plan_lane_lamps` (one side, at most 40 m apart, 0.116.0).
- **Their light** (`lot/lot.py` `_streetlight_anchors` ~468-560): one Lux
  `streetlight` light per pole at the lens (`base + h - 0.175`), the pole's
  own id, `hardware: slot:cover_i` so Zoo's fixture pass does not stand a
  second pole inside the first.
- **The species** (Zoo): `streetlight` (steel pole, shoebox head, emissive
  lens), `traffic_signal` (galvanised mast arm with a cobra-head luminaire
  arm on the far side of the same pole), `sign_post`.
- **Geometry that is not a slot** (`lot.py` `_marking_meshes` ~2255): the
  road paint is an OBJ beside the scene, one mesh per colour per 40 m cell,
  imported and baked like the buildings, no collision. Wires fit that
  pattern; they are not props.

## The design

1. **Zoo: a `utility_pole` species.** A tapered round wooden pole
   (creosote brown, weathered grey at the base), a crossarm with three
   insulators near the top, a neutral bracket below it, and parts that are
   PARAMETERS Lot sets by cause, never by jitter: `lamp_arm` (a cobra-head
   on a ~2 m arm facing the road, its lens emissive like the streetlight's),
   `transformer` (a pole-top can), `name_sign` (the corner's street-name
   blades), `riser` (conduit down the pole), `tag` (a pole number plate).
   Collision is the pole only; a body walks under an arm. Merged by material
   inside the module (wood, metal, porcelain, lens), never across poles.
2. **Lot: the pole line.** Per street, ONE side, chosen by cause (the band
   with fewer kerb cuts, driveways and shop bands to dodge; the road's hash
   only breaks a tie), poles evenly spaced at most a span apart between the
   street's ends, a pole at each junction corner the line turns or crosses
   at. **The poles carry the lamps on that side**: a pole with `lamp_arm`
   replaces the standalone `streetlight`s there, and the light anchor moves
   to the cobra-head (pole position plus the arm along its yaw, at the lens),
   type `streetlight`, so Lux's rig is reused unchanged. The street-name
   blade moves onto the corner pole where one stands within a metre or two.
   The other kerb keeps today's lamps only where the street is wide enough
   to need them -- a design call to price, not a default.
3. **Lot: the wires, as OBJ beside the scene.** Spans between consecutive
   poles and across the street at the junction poles: the primaries on the
   crossarm, a neutral, a triplex secondary and one or two communication
   cables lower, each a sagging catenary of thin geometry; one mesh per wire
   material per cell, the paint's pattern. No collision, no shadow casting,
   and out of the lightmap (thin ribbons waste a bake's texels): dark
   against the sky by day, silhouettes against lit facades at night.
4. **Price it** the cover merge's way before a level carries it: draws and
   frame time at the fixed stations against the same lot without, with a
   control. Expected direction: fewer lamps (one side), a few draws a pole,
   a dozen for the wires, no new shadow casters.
5. **Gates.** Every wire at least the clearance over every road and path;
   no pole in a kerb cut, crosswalk, driveway or door's landing; the lamps
   still light the street (`tools/light_check.py`); routes unblocked (a
   pole is a 0.3 m column at the band's outer edge, as a lamp is today).

## Reference figures (US practice: they fill blanks, the comps and the walker decide)

- A distribution pole is commonly 35 to 40 ft long with about 6 ft buried:
  roughly 9 to 11 m above grade, 0.25 to 0.33 m across at the base.
- Spans on a street are commonly 100 to 150 ft, about 30 to 45 m.
- Vertical clearance over a road (NESC): roughly 15.5 ft (4.7 m) for
  communication cables to about 18.5 ft (5.6 m) for supply conductors.
- Sag: a few percent of the span at mid-span.
- A cobra-head usually sits 25 to 30 ft up (7.5 to 9 m) on a 4 to 8 ft arm.

## Open, for the walker

- Which side, and every street or residential ones only?
- How many wires: the comps' tangle, or a cleaner two or three?
- Transformers: how often (a can every few poles is typical)?
- Lamps on every pole or every other, given Lux's 14 m reach?
