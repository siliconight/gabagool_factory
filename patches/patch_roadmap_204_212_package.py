"""Roadmap: 204 NARROWED -- its site-level half fixed by Level Factory 0.156.0
and 0.157.0 (cold runs 9201 and 9202); 212's package step done.

    python patch_roadmap_204_212_package.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_211_212_204.py left it once
its index was regenerated (1,304,646 bytes, LF, as read 2026-10-08): 204's
and 212's status lines by their unique prefixes, directly above their
headings; 204's "Pass Lot's site_markers through" NEXT bullet and the
sentence under it; 212's "The package" NEXT bullet. Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S204_PREFIX = "*STATUS: OPEN 2026-10-08 -- cause found for the site-level markers:"
S204_NEW = (
    "*STATUS: NARROWED 2026-10-08 -- the site-level half is fixed. Level Factory 0.156.0 stages Lot's "
    "`site_markers`: the getaway van's crew spawn as a `player_start` tagged `mission_start`, its extraction "
    "tagged `extraction`, and each responder arrival as an `ai_spawn` tagged `responder`. Cold run 9201's "
    "package binds the mission's spawn and extract beats to the van; 9200's bound them to a start synthesized at "
    "the centroid of every Lot anchor and to three buildings' street points. The walk copy now stands its player "
    "at the van. 0.157.0 ships how each responder arrives beside its anchor (`responder_arrivals.json`): "
    "cold run 9202's package carries it, three arrivals each naming a `responder` anchor at its own stop, listed in the resource manifest, the closure scan clean. Open, as filed: the score is unmarked and its building unnamed, and the "
    "`deli_counter:*` anchors are the mission's unplaced generated shell's.*\n")

S212_PREFIX = "*STATUS: NARROWED 2026-10-08 -- phase 1 proven: Lot 0.99.0 plans an arrival per open road end"
S212_NEW = (
    "*STATUS: NARROWED 2026-10-08 -- the arrivals are planned, kept clear and in the package. Lot 0.99.0 plans "
    "an arrival per open road end and reserves its lane and stop (cold run 9200: three on each of three "
    "candidates, a bot from every stop reaching the nearest crew point). Level Factory 0.156.0 puts each stop in "
    "`gameplay_anchors.json` as an `ai_spawn` tagged `responder` (cold run 9201: three), and 0.157.0 ships how "
    "each arrives, `responder_arrivals.json`: cold run 9202's package carries it, three arrivals each naming a `responder` anchor at its own stop, listed in the resource manifest, the closure scan clean. Open: the cruiser (the walker's comps first), "
    "and `S_RESPONDER_ARC` firing where a site's roads lie to one side of the objective.*\n")

OLD_204_NEXT = (
    "- **Pass Lot's `site_markers` through:**\n"
    "  - `crew_spawn` as the mission's `player_start`, tagged `mission_start`;\n"
    "  - the getaway van's `extraction` as the mission's extraction, tagged `extraction`;\n"
    "  - `responder_spawn` as an `ai_spawn` tagged `responder`.\n"
    "  Carry each arrival's entry, lane and stop pose somewhere the game layer can read them: a Dispatch "
    "anchor holds only a position, a facing and tags.\n")
NEW_204_NEXT = (
    "- **Pass Lot's `site_markers` through** -- *done, below.* As filed:\n"
    "  - `crew_spawn` as the mission's `player_start`, tagged `mission_start`;\n"
    "  - the getaway van's `extraction` as the mission's extraction, tagged `extraction`;\n"
    "  - `responder_spawn` as an `ai_spawn` tagged `responder`.\n"
    "  Carry each arrival's entry, lane and stop pose somewhere the game layer can read them: a Dispatch "
    "anchor holds only a position, a facing and tags.\n"
    "\n"
    "**THE SITE-LEVEL HALF, DONE (2026-10-08).**\n"
    "- **Level Factory 0.156.0** (`patches/patch_lf_site_markers.py`). `site_markers_to_anchors` stages Lot's "
    "site markers ahead of its buildings' markers, mapped as filed above, on the plate. "
    "`ensure_mission_anchors` then finds the start and the exit already tagged, so it synthesizes no start and "
    "tags no building's extraction. No facing is passed: Lot's slot yaw and Dispatch's `rot_y` have not been "
    "shown to share a convention.\n"
    "- **Before the cold run.** Measured on cold run 9200's own outputs, built by the real Dispatch: `spawn` "
    "bound to the van's crew spawn, not the centroid, and `extract` to the van's extraction, not three street "
    "points. Anchors went 64 -> 68 and `responder` tags 0 -> 3, at readiness 100 with 0 blockers.\n"
    "- **Cold run 9201** (0 interventions; `docs/cold_runs/cold_9201/NOTES.md`). The same, in the shipped "
    "package. The package's `player_start` moved from (-7.03, 0, 0.68) to (-4.15, 0, 14.95). "
    "`tools/walk_export.py` stands its body there, so walking a generated heist now starts at the van, where "
    "every earlier walk started at the centroid. Dispatch's ten notes are word for word 9200's.\n"
    "- **Level Factory 0.157.0** (`patches/patch_lf_responder_arrivals_sidecar.py`). `responder_arrivals.json` "
    "carries each arrival keyed by its anchor's id: entry, stop, forward, the stop and lane boxes, the vehicle "
    "and the way-back point it serves, in the frame of `gameplay_anchors.json`. One counting of the ids "
    "(`site_marker_anchor_pairs`) serves the staging and the file. It is written before the closure verdict and "
    "the manifest walk, named in `closure._METADATA_FILES`, and described in `HANDOFF.md`. **Cold run 9202** (0 interventions; `docs/cold_runs/cold_9202/NOTES.md`): the shipped package carries the file, three arrivals, each naming an anchor tagged `responder` at exactly its stop, listed in `portable_resource_manifest.json` (2,746 + 2 declared = 2,748 files), the closure scan ok with 0 issues.\n"
    "- **What is still this item's:** the score unmarked, its building unnamed, and the unplaced shell's "
    "anchors first -- the NEXT bullets below.\n")

OLD_212_PACKAGE = (
    "- **The package** marks them, with the pose and the routes, so the game layer can find them (item 204, "
    "whose cause is now found: Level Factory's Dispatch staging reads no site markers).\n")
NEW_212_PACKAGE = (
    "- **The package** marks them, with the pose and the routes, so the game layer can find them -- *done*: "
    "Level Factory 0.156.0 puts each stop in `gameplay_anchors.json` as an `ai_spawn` tagged `responder` "
    "(cold run 9201), and 0.157.0 ships how each arrives in `responder_arrivals.json` (cold run 9202). Item "
    "204 has the detail.\n")


def _replace_status(text, prefix, new_line, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times: %r" % (len(hits), prefix[:50])
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    lines[i] = new_line.rstrip("\n")
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1304646, "PIPELINE_ROADMAP.md is %d bytes, read at 1,304,646" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    pairs = ((OLD_204_NEXT, NEW_204_NEXT), (OLD_212_PACKAGE, NEW_212_PACKAGE))
    for old, _new in pairs:
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:60])
    for new in (S204_NEW, S212_NEW, NEW_204_NEXT, NEW_212_PACKAGE):
        assert "RESULT_" not in new, "an unfilled result: %r" % new[new.index("RESULT_"):][:40]
    text = _replace_status(text, S204_PREFIX, S204_NEW, "**204. ")
    text = _replace_status(text, S212_PREFIX, S212_NEW, "**212. ")
    for old, new in pairs:
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("204 site half, 212 package; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
