## [0.29.0] - an Empty's TV antenna and satellite dish

### Added
- **`framing.roof_fixture_orders`**: a `tv_antenna` and a `sat_dish` on an
  Empty's roof, up-facing on its top surface, for Zoo (>= 1.74.0) to build.
  - Deli Counter (>= 0.185.0) writes `antenna` / `dish` on the roof slot,
    with `front`: the facing of the wall that holds the front door. The
    slot is the opt-in, as a window's fixtures are. Without a `front` there
    is no parapet to set them back from, and nothing is ordered.
  - **Where:** measured back into the roof from the front parapet's inner
    face. From across the road, anything less than about 0.6 m over the
    parapet per metre behind it is hidden, so both stand close to the
    front.
    - The antenna stands 1.0 to 1.6 m back, within 15 % of the roof's width
      of its centreline. Its mast (2.6 to 3.4 m) and boom (1.6 to 2.6 m)
      are drawn per house.
    - The dish stands 0.25 m back, 18 to 32 % out on the other half from
      the antenna, so the two never share a footing. Its bowl's centre is
      0.6 m over the parapet's top. At 0.45, the pre-flight render from
      across the road showed only the feed arm and a sliver of bowl over
      `gs_empty_rowhome_k`'s 1.0 m parapet.
  - **Which way:** each looks along a bearing in the building's own frame,
    given as the order's `tangent`.
    - The antenna points 325: Philadelphia's TV transmitters stand in
      Roxborough, north-west of South Philly.
    - The dish faces 211: the DSS satellites sit at 101 W.
    - A building turned at placement turns its fixtures with it. Level
      Factory's terrace turns every house of a row the same way, so a row's
      antennas point one way.
  - **Each house draws its own,** from `(seed, kind, building, slot)`.
    Every Empty's roof slot is `roof_footprint`, so keyed by the slot alone
    the whole street would draw the one antenna.
- **`Slot`** carries `antenna`, `dish` and `front`, and `parse` reads them.
- **`openings.EXEMPT`** names both. Nothing walks or shoots across an
  Empty's roof.
