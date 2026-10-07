"""Roadmap: item 200 widened -- the pacing estimate is under-wired, not only
the target.

    python patch_roadmap_200_mode.py

Anchored on 200's status line and its NEXT block as patch_roadmap_200.py wrote
them (LF). Then run `tools/roadmap_status.py --write` and `--check`.

THE CORRECTION THIS RECORDS. The level standard's first headline read Lot's
pacing estimate (1.6-3.4 min) as how much heist the level held. It is not:
Level Factory sets no `mode` in the site spec, so `site_pacing._critical_legs`
returns no legs and the estimate counts no travel at all.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S_OLD = ("*STATUS: OPEN 2026-10-07 -- found writing the level standard (`docs/LEVEL_STANDARD.md`, Appendix A): four "
         "mission-brief fields reach nothing that uses them. `target_minutes` is written where Lot's pacing does not "
         "look, so cold run 9193's level was judged against Lot's default 7-15 min, not the brief's 25-35; `landmark`, "
         "`verticality` and `extraction_relationship` have no reader in any repo.*\n")
S_NEW = ("*STATUS: OPEN 2026-10-07 -- found writing the level standard (`docs/LEVEL_STANDARD.md`, Appendix A): four "
         "mission-brief fields reach nothing that uses them, and Lot's pacing estimate is under-wired. `target_minutes` "
         "is written where Lot's pacing does not look, so cold run 9193's level was judged against Lot's default 7-15 "
         "min, not the brief's 25-35; Level Factory sets no pacing `mode`, so the estimate counted no travel; "
         "`landmark`, `verticality` and `extraction_relationship` have no reader in any repo.*\n")

N_OLD = ("**NEXT.**\n"
         "- Route `target_minutes` to `pacing.target_minutes`, with a test that the brief's number appears in the "
         "manifest's `pacing.target_min`.\n")
N_NEW = ("- **The pacing `mode`.** `site_pacing._critical_legs` builds the travel legs only for `mode` heist, "
         "assault or survival, read from the site spec. Level Factory writes none, so cold run 9193's manifest "
         "reads `\"mode\": null` and its estimate is setup (30 s) plus one objective (120 s) with no travel "
         "breakdown at all.\n"
         "- **Two counts of objectives.** The estimate counts the objective building's markers in Lot's merged "
         "gameplay (one objective a building, no loot in b0). The package's `gameplay_anchors.json` carries 9 "
         "objective and 5 loot anchors at room level. They are different counts, not a contradiction. Which one "
         "pacing should read is a decision.\n\n"
         "**REFUTED, KEPT.** The level standard's first headline read the 1.6-3.4 min estimate as how much heist "
         "the level held. With no mode and the default target, the number measures neither. It is corrected in "
         "the standard.\n\n"
         "**NEXT.**\n"
         "- Route `target_minutes` to `pacing.target_minutes`, with a test that the brief's number appears in the "
         "manifest's `pacing.target_min`.\n"
         "- Set the pacing `mode` from the brief (a heist's spawn -> objective -> extraction), with a test that the "
         "manifest's breakdown carries travel legs.\n")


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old in (S_OLD, N_OLD):
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:60])
    text = text.replace(S_OLD, S_NEW).replace(N_OLD, N_NEW)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 200 widened; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
