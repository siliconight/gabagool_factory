## [0.162.0] - Each responder arrival names the car it brings

**Roadmap 212.** Lot 0.101.0 has Zoo's site kit build the responders'
cruiser. Its themed assembly copies the car into `cover/` beside the scene,
a sibling this package already carries, stands it nowhere, and names it in
`responders.json`.

### `responder_arrivals.json`, schema v3

- **`vehicle_scene`** on each arrival: the car's `res://` path, matched by
  its stop to the themed site's `responders.json`.
- **It is null** when the themed site names no car for that stop, or names
  a file the package does not hold.
- **`vehicle_findings`** says which. Lot from before 0.101.0 writes no
  `responders.json`, and that is said once.
- **The file's presence is checked here.** This file is one of
  `closure._METADATA_FILES`, so the closure gate does not read the `res://`
  path inside it.

`write_responder_arrivals` takes the themed site's directory, and the
export passes the one it already copies the scene and siblings from.

### Tests

`tests/unit/test_responder_arrivals_in_package.py` has 8 tests:
- the schema is v3, and with no themed site no car is named, said once;
- **each arrival names the car it brings:** the themed site's cruiser in
  the package's `cover/`, its `res://` path on the arrival;
- **a car named but not in the package** is null, and said.

On 0.161.0 the file fails 3.

**Suite:** 2,032 passed, 14 skipped, 1 xfailed, 0 failed (exit 0; progress
characters tallied): 0.161.0's 2,030 and the two new tests.
