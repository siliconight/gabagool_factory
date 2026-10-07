"""Roadmap: item 200, four brief fields that reach nothing.

    python patch_roadmap_200.py

Appends after item 199, anchored on the file's last line in full, as left by
patch_roadmap_night_and_brief.py (LF). Then run `tools/roadmap_status.py
--write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

TAIL = ("**NEXT.** Map the brief's hard failures and design warnings onto those gates one by one, and measure "
        "the gap on a few briefs before any layout changes.\n")

ADD = """
*STATUS: OPEN 2026-10-07 -- found writing the level standard (`docs/LEVEL_STANDARD.md`, Appendix A): four mission-brief fields reach nothing that uses them. `target_minutes` is written where Lot's pacing does not look, so cold run 9193's level was judged against Lot's default 7-15 min, not the brief's 25-35; `landmark`, `verticality` and `extraction_relationship` have no reader in any repo.*

**200. Four brief fields reach nothing.** Found 2026-10-07 mapping the walker's level standard onto the mission brief (`level_factory.mission_brief.v0.1`).

**WHAT WAS MEASURED.**
- **`target_minutes`.** Level Factory writes it at the site spec's top level (`apps/cli/commands/__init__.py`, the site spec writer: `"target_minutes": list(model.target_minutes)`). Lot's `site_pacing._cfg` reads `site_spec["pacing"]["target_minutes"]`. On cold run 9193's pick, the shipped gameplay manifest's `pacing` reads `"target_min": "7-15 min"` (Lot's `TARGET_MIN_S`/`TARGET_MAX_S` defaults) against a brief of [25, 35], and reports "likely TOO SHORT vs target" for an estimate of 1.6-3.4 min.
- **`landmark`.** Read by nothing. `docs/LEVEL_RECIPE.md` recorded it on 2026-09-24, and a search of every repo on 2026-10-07 finds only comments and other meanings of the word.
- **`verticality` and `extraction_relationship`.** Defined in `packages/core/models.py` and serialised; no reader in any repo.

**WHY IT MATTERS.** `CLAUDE.md`: a knob with no effect is itself a defect, because the next person turns it and is not believed. These four sit in every brief ever written. The level standard's request template marks them GAP until each reaches a reader or is removed.

**NEXT.**
- Route `target_minutes` to `pacing.target_minutes`, with a test that the brief's number appears in the manifest's `pacing.target_min`.
- Decide, with the walker, what each of the other three should drive -- or retire them from the schema.
"""


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(TAIL) and text.count(TAIL) == 1, "the tail anchor is not the file's end"
    RM.write_bytes((text + ADD).encode("utf-8"))
    print("roadmap: 200 appended; %d -> %d bytes" % (len(data), len((text + ADD).encode("utf-8"))))


if __name__ == "__main__":
    main()
