## 0.106.0 - a lamp or a tree keeps out of a shop band's span

**Seen in cold run 9222's frames.** deli_a01's band read SCRAPPLE & SONS DELI,
and a street lamp's pole stood in front of it and hid the E.
- **Where the two stood.** The band spans stations 26 to 35 of road 0's left
  kerb. The lamp spacing put Lamp_2 at 30, 2.46 m in front of the facade.
- **Why nothing stopped it.** `site_furniture.plan_furniture` stands lamps
  every 25 m and steps one 2 or 4 m around a marker, and it never knew a band
  was there. `building_signs` and the scene writer hang the band later, from
  the spec.

**What reaches the band.** The band's centre is at 3.6 m, 0.75 m either side
at the widest. A lamp (6 m) or a tree's crown reaches it. A hydrant, a post,
a meter or a shelter does not.

**Now.**
- **`lot.sign_bands(site_spec, roads)`** gives every dealt band's centre,
  half-width and axis. It uses the same `sign_placement` and `sign_size` as
  the scene writer, so the span a pole keeps out of is the span that is
  drawn.
- **`plan_furniture(..., sign_bands=)`** keeps a lamp or a tree out of each
  band's span on the kerb it faces:
  - the kerb is on the band's side of the road nearest its centre, the road
    `sign_placement` turns it to;
  - the span is widened by `SIGN_CLEAR`, 0.5 m, at each end;
  - when the spacing lands a piece inside, it steps to the nearer end of the
    span, past `PIECE_GAP`, because a 2 or 4 m nudge cannot leave a 9 m band;
  - if neither end is clear of the cuts, the other pieces and the markers,
    the piece does not stand.
- **Each move is said:**
  `LOT_BAND_KEPT_CLEAR: <piece> would have stood at station <t>, in front of
  a shop band; it stands at <t'>`.
- **With no band, the planner is unchanged, piece for piece.**

**Replayed on cold run 9222's drawn site:** its roads, buildings and band,
before and after, with markers left out of both sides of the comparison:
- the planner places the same 107 pieces;
- exactly one moves: Lamp_2, from station 30.00 to 25.05;
- the lamp's light moves with it.

**Tests.** `tests/test_site_band_clear.py`, 7, on the probe spec's one road:
- a lamp in front of a band steps to its nearer end, and none stands inside
  the span;
- a band across the road moves nothing on this kerb, only the other kerb's
  lamp;
- a band facing another road moves nothing on this one;
- without a band in the way nothing changes, piece for piece;
- a tree keeps out too;
- the finding names the piece and both stations;
- `sign_bands` is the band the scene draws: the same centre and half-width,
  along x for a facade facing the road.

All 7 fail on 0.105.0, where neither `sign_bands` nor the keyword exists.

Suite: 739 passed, exit 0. 0.105.0 gave 732; the 7 tests here account for all 7.
