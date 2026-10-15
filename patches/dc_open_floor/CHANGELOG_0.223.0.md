## [0.223.0] - an open floor nobody named: layout_lint L26

**The factory's roadmap 255, found tracing the walker's walk of 2026-10-14, finding 5** (the factory's
`docs/findings/walk_2026-10-14/partition_gaps.py`). The delis' basement divider stopped 7 m short of each wall and
the vault stood open to the utility room, and no spec said so; across the library 59 such stretches stood in 31 of
446 specs, 33 in 20 after 0.222.0 closed the delis'. Some are designed openness -- a lobby flowing into a bullpen
-- and some are the finding again, and nothing told them apart: `tactical.shared_open_edge` has joined every such
pair as one floor since 0.197.0, so the engine walks it, and the spec was silent.

- **`tactical.OPEN_FLOOR_M`** (1.2 m) is the rule's threshold, spelled once where it was spelled four times.
- **`tactical.open_edge(a, b, parts)`** is `shared_open_edge`'s body, returned: the edge two rooms meet along and
  how much of it no partition covers -- ``(axis, pos, lo, hi, uncovered)`` -- or None. `shared_open_edge` asks it;
  `build_graph`, L12 and L24 move nothing.
- **A room's `open_to`** (the schema admits it: a list of room ids) says the floor between them is meant.
- **`layout_lint.open_floors(spec)`** names every pair tactical joins that neither room's `open_to` names;
  **`open_floor_findings`** is L26, an advisory WARN in every mode: "open floor nobody named: 'a' and 'b' (story
  s) meet along x = 0 from -5 to 5 with 2.00 m of it uncovered by any partition; the engine walks it as one floor
  -- say so (`open_to` on either room) or build the wall". `_story_parts` is the one reading of a storey's
  partitions both L24's search and L26 use.
- **`open_floor_baseline.py`** freezes the built library's pairs in `open_floor_baseline.json` for the walker to
  sort, one by one; `test_open_floor.py` fails on a new pair and on a stale one, as `test_walk_reach` does for
  L24. Nothing is a verdict on any pair: the walker's finding 5 was one of them, and the lobbies are others.
- **`test_open_floor.py`:** where a short partition is named; a wall-to-wall one and a 1.0 m gap are not; `open_to`
  silences the lint and not the engine; one threshold for both (moved, both move); a WARN and never a FAIL on
  rowhouse_raid; the schema; the spec left alone; the baseline. The seven that touch the code fail on 0.222.0
  (proven on a copy; the two baseline tests pass there trivially, with no `build/` to read).

Nothing built moves: a lint names, it does not change a shell. Level Factory's findings never carry a Deli Counter
lint warning, so no cold run moves either.

**The census:** 49 open floors nobody named, in 26 of 159 built specs

**Suite:** `python -m pytest -q`: 1549 passed, 2 skipped, 1 warning in 115.66s (0:01:55), exit 0 -- 0.222.0's 1,540 and `test_open_floor.py`'s 9
