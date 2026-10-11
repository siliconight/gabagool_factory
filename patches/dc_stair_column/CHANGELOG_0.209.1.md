## [0.209.1] - a stair's column ends at the ceiling of the top floor it serves

**Cold run 9245, the first with roof props** (Zoo 1.101.0 through Level
Factory 0.179.0): the circulation gate's new roofprops arm reported eight
conflicts on two buildings and none a body could meet -- seven HVAC parts on
the office's roof, 10.8 m up, "in" `office_stair_0`, which serves floors 0 to
2 and ends two slabs below them; and a dish on the deli's roof over
`deli_stair_down`, the BASEMENT stair. `stair_volume` reached +/-1e6 in z:
a prop anywhere over a stair's footprint, on any floor, was in the shaft.
The dressing and shell arms never met it because nothing they place stands
over a stairwell on a floor the stair does not serve; the roof does.

- **`stair_column(system)`** reads the stair's own landings: from its lowest
  `nav_endpoints` z to one storey above its highest, the storey being the
  landings' rise over the floors they span (`floors_served`), so no manifest
  field is guessed. The office's stair: 0.0 to 7.2 over floors 0..2, a 3.6 m
  storey, column 0.0 to 10.8 -- the roof's top face, which a prop standing on
  it grazes by nothing, under the gate's 2 cm floor. A stair without
  endpoints keeps the full column, as before.
- **`circulation_volumes`** bounds every stair by it. `stair_volume`'s
  signature and its explicit-z callers are unchanged.
- A stair that reaches the roof carries the roof's floor in `floors_served`,
  so its column still covers the hatch; the landing beside it is Zoo's
  keep-out (0.209.0), as before.

**Re-gated on 9245's composed buildings** (`docs/findings/roof_props/regate_9245.py`,
the patched module against the old packages): RESULT_PACKAGE

### Tests

`test_circulation.py`: a stair's column reaches one storey above its upper
landing (fails on 0.209.0); a roof prop over a stair two slabs down is not in
its column while a table in the well is; a stair without endpoints keeps the
full column.

**Suite:** RESULT_SUITE
