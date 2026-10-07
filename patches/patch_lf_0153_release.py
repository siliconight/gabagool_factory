"""Level Factory 0.153.0's release: VERSION and the CHANGELOG entry.

    python patch_lf_0153_release.py

Anchored on VERSION (b'0.152.0') and on CHANGELOG.md's head (629,504 bytes,
LF, as read 2026-10-07).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

HEAD = "## [0.152.0] - The score is the building the brief asked for\n"
ENTRY = """## [0.153.0] - The brief's pacing reaches Lot, and Lot's verdict reaches the operator

**Roadmap 200.** Three disconnections on one dial, each read in the code on
2026-10-07:
- **The window.** `target_minutes` was written at the site spec's top level.
  Lot's `site_pacing._cfg` reads `pacing.target_minutes`, so all 144
  candidate specs on disk were judged against Lot's 7-15 min default. 177 of
  181 cold-run briefs ask for 25-35.
- **The mode.** The site spec carried no `mode`, and Lot's estimate builds
  travel legs only for heist, assault or survival, so it counted no travel
  (cold run 9193: `"mode": null`).
- **The verdict.** The Lot adapter raised `LOT_PACING_OUTSIDE_TARGET` only for
  a status containing "outside target". Only the straddle case carries those
  words, so "likely TOO SHORT vs target" and "likely TOO LONG vs target"
  never surfaced. The fake Lot under `tests/fixtures/` writes only the
  straddle status, so no test could see it.

**What changed:**
- `_write_site_spec` writes `mode` and `pacing.target_minutes`.
- `mission_mode(model)` is the one place the mode is asked; Deli Counter's
  spec reads it too. The brief has no mode field, so every mission is a heist.
- The Lot adapter names every status Lot writes (`LOT_PACING_STATUSES`) and
  reports TOO SHORT and TOO LONG with the phases the estimate counted. An
  unknown status, or no pacing block, is `LOT_PACING_UNREAD`. Every pacing
  finding is non-blocking, as before.
- `batch create` names the brief fields nothing builds from:
  `UNBUILT_BRIEF_FIELDS` is `route_shape`, `objective_hypotheses`,
  `extraction_relationship`, `verticality`, `landmark` and `seed_policy`. The
  first five are read only by `functional_signature`, so changing one
  re-locks a mission and changes no geometry. Every cold-run brief sets those
  five; none sets `seed_policy`.

**What the mode switches on.** Lot's heist gate (`site_tactical.gate`) fails
the build unless spawn, objective and extraction are joined. It was measured
before the mode was set: all 144 candidate specs on disk pass
(`docs/findings/brief_pacing_mode/heist_gate_census.py`). Those specs hold
sites of 1 to 5 buildings.

**What to expect: one new non-blocking `LOT_PACING_OUTSIDE_TARGET` on nearly
every level.** With the mode and the window, Lot's estimate on those 144
specs reads 2.5-3.6 min (median 2.8) against the brief's 25-35. Its phases
are travel, setup, objective work and loot trips, and none counts fighting.
The estimate and the window measure different things until the walker
decides what `target_minutes` means.

**Tests:** `tests/unit/test_brief_pacing.py`, 13. On 0.152.0, 10 fail
(`FFF.FF.F.FFFF`). The three that pass are the heist-gate guard, the straddle
status and "within target". One test reads Lot's own source and fails if
Lot's statuses and the adapter's list ever differ. Suite: 1,997 passed, 14
skipped, 1 xfailed (exit 0). That is 13 new tests, plus one new case of
`test_sibling_locator`, which runs once per source file.

"""


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.152.0", repr(v)
    c = (LF / "CHANGELOG.md").read_bytes()
    assert len(c) == 629504 and b"\r\n" not in c, len(c)
    text = c.decode("utf-8")
    assert text.startswith(HEAD) and text.count(HEAD) == 1
    (LF / "VERSION").write_bytes(b"0.153.0")
    (LF / "CHANGELOG.md").write_bytes((ENTRY + text).encode("utf-8"))
    print("Level Factory 0.153.0: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
