## 0.120.1 - a storm inlet keeps clear of the paint: none stands in a crosswalk

**Factory roadmap 179, found in cold run 9269's frames** (0.120.0's real drive): the corner frame showed
a grate against a crosswalk's bar. Read off the package (the factory's
`docs/cold_runs/cold_9269/drain_paint.py`: each piece's footprint from the shipped OBJs, against the
job's `site.markings.json`), four of the eight inlets lay over a crosswalk bar, 0.155 m^2 each, 27.8 %
of the grate -- all four on the main road's kerb at its two T's. 0.120.0 stood an inlet a hand past the
kerb's dropped stretch, and on a through road that stretch is the side street's carriageway and
`CUT_MARGIN` each side (59.9-71.1 m along road 0), while the road's own crosswalks there lie in line
with the side street's sidewalks (57.8-60.3 and 70.8-73.3 m, `site_streets.crossing_walks`): the rule
the module quotes -- TxDOT's inlet upstream of the crosswalk -- was asked of the ramp alone.

- **`site_drains.plan(roads, cover, marks)`**: a grate is stepped along the kerb, away from the
  junction, past every marking nearer than `INLET_CLEAR` (0.3 m) -- measured from a corner to an edge,
  never a margin added per axis -- and stands at the first station clear of them all; none where the
  road ends first. Every marking counts but the lines along a road (`LINES_ALONG`): on a street too
  narrow to park on, the edge line runs in the gutter, and clearing it would leave that street no
  inlet. The step lands a grate exactly `INLET_CLEAR` from the bar it passed and the test that asks
  again allows a micrometre, so the two spellings of one distance cannot hold a grate in place.
  `cover` and `marks` are both asked for now, so no caller leaves the paint out unnoticed.
- **`_outdoor_nodes`** passes the paint it draws (`site_streets.markings` and the fields').
- **The covers are unchanged**: two of 9269's four lie on a bar, at the lane's two junctions, where the
  side street paints its crosswalk centred on the lane -- the walker's photograph has a round cover out
  in a crosswalk, and a cover stands 3 mm proud of the paint.

**On the lot cold runs build** (cold run 9262's seed_9104): the main road's four grates (its two T's, both corners) step 2.15 m along the kerb, each near end 0.30 m past its crosswalk's last bar, and their lids with them; the lane's four stand where they stood; 4 covers, 8 inlets and 4 lids as before, none of the eight within a hand of the paint (four over a bar on 0.120.0, the same four cold run 9269's package shows). On two streets crossing (the tests' X) all four grates lay over a bar and none does: 2.15 m on the departure side, 3.80 m on the approach side, past the stop bar as well

**Suite:** 827 passed; `test_no_grate_stands_in_the_paint` fails on 0.120.0's station rule with the new helpers beside it (`--old-station` on a copy: the X's first grate over a bar, gap 0.0)
