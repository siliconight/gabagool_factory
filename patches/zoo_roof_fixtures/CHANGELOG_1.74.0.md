## [1.74.0] - an Empty's TV antenna and satellite dish

The comps' rowhome has "a TV antenna on the roof", and the street has "the
odd early satellite dish". From across the road an Empty's roofline was a
flat parapet edge against the sky.

Deli Counter (>= 0.185.0) authors which houses have them. Patina (>= 0.29.0)
orders them on the roof, set back from the front parapet. Both are built
here, as two new covers.

- **`tv_antenna`** (`core.dressing.antenna_parts`), a 1990s VHF/UHF aerial
  on a mast:
  - a plate on the roof, and the mast up from it;
  - a boom across the mast's top, 40 % of it behind the mast;
  - an element about every 20 cm along the boom, tapering from 1.6 m at the
    back (the reflector) to 36 cm at the end that points at the
    transmitter, which is local +x, the order's tangent;
  - `size2` is [boom, mast];
  - drawn about twice real thickness, as the gutter's sheet is, so a 2 cm
    tube holds at street distance.
- **`sat_dish`** (`core.dressing.dish_parts`), an 18-inch DSS dish:
  - an oval 46 x 50 cm on a pole on a roof plate;
  - its bowl looks along the tangent, tilted up 41 degrees: Philadelphia's
    elevation to the DSS satellites at 101 W;
  - the recipe builds the head (bowl, feed arm, LNB) level and tilts it
    about the bowl's centre;
  - `size2` is [width, the bowl's height above the roof].
- **Both are `METAL_COVERS`**, the gutters' white aluminium. On a side that
  has a gutter, downspout or air conditioner, they merge into that side's
  metal mesh. Up-facing, each takes the side it stands nearest, which for a
  fixture set back from the front parapet is the front.

**Price, expected:** no new mesh where the front already has white metal,
which on every rowhome Empty it does (gutter and downspouts). To be measured
in the cold run.

**The cheaper choice, and what the other would buy:** a bare-aluminium
material would give the antenna a metallic sheen where a lamp catches it,
for one more surface per house.
