## [0.161.0] - The package ships a responder's lane as Lot steered it

**Roadmap 212.** Lot 0.100.0 sizes the responders' arrivals for Zoo 1.86.0's
cruiser, and steers a lane round what stands in it. Cold run 9204's getaway
van had closed a rigid lane.
- **How Lot writes it.** The lane is `lane_boxes`, one box a run of 1 m
  slices at one shift, in order from the entry, with `lane_shift` the
  largest.
- **Why not one box.** Drawn round a steered lane, a single box covers the
  van the lane goes round. Shipped, it would tell the gameplay layer that
  the van stands in the reserved lane.

### `responder_arrivals.json`, schema v2

`write_responder_arrivals` ships, for each arrival:
- **`lane_boxes`**, each turned to the package's frame, in Lot's order;
- **`lane_shift_m`**, the largest shift.

They replace `lane_box`.
- **A Lot 0.99 arrival** ships its one `lane_box` as the only box, at shift
  0. A rigid lane never shifted.
- **Level Factory 0.160.0 cannot read Lot 0.100.0's arrivals.** It reads
  `lane_box` and fails on the missing key, so the two go together.
- **Nothing consumes the file yet.** It shipped in 0.157.0, the same day.

### Tests

`tests/unit/test_responder_arrivals_in_package.py`, 6 tests:
- the schema is v2;
- a Lot 0.99 lane ships as its one box at shift 0;
- **a steered lane ships every box in order.** Its fixture is Lot
  0.100.0's record for cold run 9204's road 0 east end, verbatim: nine
  boxes, shifting 0.648 m round the van.

On 0.160.0 the file fails 2: the schema, and a `KeyError` on the steered
record.

**Suite:** 2,030 passed, 14 skipped, 1 xfailed, 0 failed (exit 0; progress
characters tallied): 0.160.0's 2,029 and the steered-lane test.
