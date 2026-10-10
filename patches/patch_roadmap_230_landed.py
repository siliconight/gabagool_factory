"""Roadmap 230: steps 1 and 2 landed (Level Factory 0.176.0, Lot 0.111.0); cold run 9231 proves them.

Replaces the head of 230's status block and appends the landing record to its body. Each anchor
must match exactly once; nothing is written on a miss, and nothing is written while a RESULT_
placeholder is unfilled. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_230_landed.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

RESULT_LF = "suite 2,202 passed, 14 skipped, 1 xfailed, exit 0 (the 2,191 of 0.175.1, the nine new cases and the two new source files under the sibling guard)"
RESULT_LOT = "suite 768 passed, exit 0 (760 as 0.110.0 and the eight new)"
RESULT_CENSUS = "the library rebuilt reads 1,140 rows and 4,133 lamps where 0.206.0 read 1,156 and 4,217, ten more rooms on the home's one fixture (`docs/findings/fixture_rows/row_census_0206_1.txt`)"

OLD_STATUS_HEAD = (
    "*STATUS: OPEN 2026-10-10 -- filed, not started. The walker's guide "
    "(`docs/reference/PA_1990S_ADJACENCY_AND_LAYOUT_GUIDE.md`, "
)
NEW_STATUS_HEAD = (
    "*STATUS: NARROWED 2026-10-10 -- steps 1 and 2 are LANDED; cold run 9231 (restaurant_row_001 "
    "with `cluster: auto` in its brief) is the first level drawn by a template and audited by the "
    "pair rules. Level Factory 0.176.0 (`patches/patch_lf_cluster.py`, `packages/pipeline/cluster.py`): "
    "`MissionBrief.cluster` names one of the guide's eighteen templates or `auto`, which the "
    "archetype's words pick; `pick_lot` draws the anchor, then the template's families in the "
    "guide's order, then the library's remainder by seed; a brief naming nothing keeps 0.175.1's "
    "draw byte for byte; the site spec records `cluster_resolved` (the template, the families asked, "
    "the families found); " + RESULT_LF + ". Lot 0.111.0 (`patches/patch_lot_adjacency.py`, "
    "`site_adjacency.py`): every pair of lot buildings judged by the guide's nine categories "
    "(from the archetype's words), the relation from geometry (`shared_boundary` within 3 m edge to "
    "edge, `across_local_street` when a road lies between the centres, else `same_block`), the "
    "9 x 9 affinity and the sixteen pair rules Lot can judge, reported as `S_ADJACENCY` in the site "
    "audit: MED where the guide says `condition` or worse or the affinity is -2, INFO where it says "
    "`prefer` or `allow` (the reason a pair is good) or the affinity is merely weak; a finding, not a "
    "gate; " + RESULT_LOT + ". Left: step 3, the connectors for roadmap 199 (the service lane, the "
    "rear passage, the shared court, the gate, each with an owner and users), and step 4, the "
    "targets in the audit. The walker's guide "
    "(`docs/reference/PA_1990S_ADJACENCY_AND_LAYOUT_GUIDE.md`, "
)
BODY_ANCHOR = (
    "Owner: Level Factory (the brief and the draw) and Lot (the audit and the connectors).\n"
)
BODY_ADDED = (
    "\n**STEPS 1 AND 2 LANDED, 2026-10-10.** Drafted and proven on clones first, applied after cold "
    "run 9230 ended. **Level Factory 0.176.0:** `cluster.TEMPLATES` carries the guide's eighteen "
    "cluster templates as ordered family lists through `CATALOG_FAMILIES` (the library's archetypes "
    "mapped onto the guide's catalog); `template_for(name, archetype)` takes a template id, `auto` "
    "(the archetype's words through `TEMPLATE_BY_WORD`: a hospital is C11, a gas station C08, a deli "
    "or a station C03, a warehouse C04) or nothing; `pick_lot(entries, seed, count, anchor, "
    "preferred)` draws the anchor first, then the preferred families in the template's order, then "
    "the library's remainder exactly as 0.175.1 drew it, so a brief that names nothing keeps its "
    "level and every existing brief is unchanged (the functional signature carries `cluster` only "
    "when set); `site_variation.cluster_resolved` records the template, the families asked and the "
    "families found, and the site spec carries it beside `surroundings`. " + RESULT_LF + ". "
    "**Lot 0.111.0:** `site_adjacency.py` is pure: `category_of` from the archetype's words with the "
    "specific row first (a country club is `rec` before the club row makes it `ngt`), `relation` "
    "from footprints and roads, `AFFINITY` the guide's symmetric matrix, `PAIR_RULES` the sixteen "
    "rules whose parties and relations Lot can see (P04, P06, P07, P08, P10 to P14, P17 to P21, "
    "P28, P30), `findings(site)` the `S_ADJACENCY` list the audit appends before its counts, in a "
    "`try` so a site the judge cannot read costs one INFO and never the audit; eight tests. "
    + RESULT_LOT + ". **Not judged:** the Empties' terrace, which Level Factory composes; the "
    "guide's rules about streets Lot does not lay (arterials, the rail line) and about interiors. "
    "**Beside them, Deli Counter 0.206.1** (roadmap 229): the home rule keys on the room's words "
    "too, so a hideout over a deli takes one fixture; " + RESULT_CENSUS + ".\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    for token in (RESULT_LF, RESULT_LOT, RESULT_CENSUS):
        assert not token.startswith("RESULT_"), f"fill {token} before applying"
    assert text.count(OLD_STATUS_HEAD) == 1, text.count(OLD_STATUS_HEAD)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    assert "STEPS 1 AND 2 LANDED, 2026-10-10" not in text, "already applied"
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + BODY_ADDED).replace(OLD_STATUS_HEAD, NEW_STATUS_HEAD)
    i = text.index(NEW_STATUS_HEAD)
    j = text.index("\n", i)
    assert text[j:].startswith("\n\n**230. "), "230's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 230: steps 1 and 2 landed")


if __name__ == "__main__":
    main()
