"""Roadmap 168 CLOSED and 244 DECIDED, 2026-10-19.

168: every greybox class the item named has an owner (ladders Level Factory 0.136.0, parapets Deli Counter 0.177.0,
vault ledges Level Factory 0.217.0), cold run 9322 is the first themed package with 0 greybox surfaces, and Level
Factory 0.218.0 makes the census refuse any. 244: the walker's call, made under the walker's standing instruction of
2026-10-19 ("make decisions that can be changed later") -- the level as built, which is period-correct and moves
nothing the graders score; how to change it is written into the status.

Each status block is replaced whole, its earlier status kept after it verbatim. Anchored on each block's sha256
and on the item heading below it (asserted once). The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_168_244.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [
    {
        "n": 168,
        "first": "*STATUS: NARROWED 2026-09-23 -- THE SLAB CLASS IS CLOSED, MEASURED AND GATED;",
        "lines": 8,
        "sha": "df5864766068d108f52091524ed160f9fb80ff877f95aa523e015029fa57b512",
        "heading": "**168. Greybox survives into a themed package wherever theming has no pass",
        "old_prefix": "*STATUS: NARROWED 2026-09-23 -- ",
        "new": """*STATUS: CLOSED 2026-10-19 -- every class this item named has an owner, the
zero is measured, and the gate refuses on it. Ladders: a worldskin pass,
Level Factory 0.136.0 (roadmap 169). Roof parapets: wall slots the composer
dresses, Deli Counter 0.177.0 (324 greybox surfaces on cold run 9148's package
before it). Vault ledges: a worldskin pass, Level Factory 0.217.0 (31cc75c),
the building's drywall wall, then any wall, then its floor family -- a call
made 2026-10-19 and meant to be changed (`VAULT_LEDGE_FAMILIES`). Read off the
40 censuses on disk: of 24 packages exported since 2026-10-10 none drew a
greybox ladder or parapet, and the 11 that drew any greybox drew only vault
ledges (1 to 3 surfaces). Cold run 9322 (urban_row_001 on 0.217.0, 0
interventions) is the first themed package with 0 greybox surfaces, where
9321's had 3. Level Factory 0.218.0 (3f7721f,
`patches/patch_lf_greybox_any_role.py`) makes `greybox_skin.assert_skinned`
refuse ANY greybox surface in a themed package, behind
`ExportProfile.require_no_greybox` (default on; off restores slabs only), with
the verdict's first unit tests. Not proven: platform decks (`PLATFORM_<id>`,
the floor role, in the one spec that has one) have no pass and no censused
package carries one; the new verdict will name one if it ships. Earlier status
kept: NARROWED 2026-09-23 -- """,
    },
    {
        "n": 244,
        "first": "*STATUS: OPEN 2026-10-13 -- grounded, and now a walker's call. On cold run 9262's lot (seed_9104) 25",
        "lines": 1,
        "sha": "25d781f1d603f8d131856435d8af6d5c808115d4885933b0ee0dcec001abda1d",
        "heading": "**244. A marked crosswalk lands on a raised kerb.**",
        "old_prefix": "*STATUS: OPEN 2026-10-13 -- ",
        "new": ("*STATUS: CLOSED 2026-10-19 -- DECIDED, a call that can be changed (the walker's standing "
                "instruction of 2026-10-19: make decisions that can be changed later): NONE, the level as built. A "
                "marked crosswalk meets a full kerb unless a road or a path crosses it there -- 11.80 of 48.00 m of "
                "crosswalk ends dropped on seed_9104's lot, as measured -- which is how a 1997 Philadelphia street "
                "not resurfaced since January 1992 met its crosswalks (Kinney v. Yerusalim, 3d Cir. 1993; "
                "`docs/reference/CURB_RAMPS.md`). It moves nothing the graders score, where 'every' would move the "
                "graded lots' kerbs (242's lesson) and 'by street' would need a resurfacing cause per street that no "
                "source sizes. To change it: Lot's kerb model cuts where a crosswalk lands (`site_streets.split_span` "
                "and `crossing_walks`), the walk's width plus `CUT_MARGIN`, to the PROWAG numbers this item "
                "records, priced on the graders first. Earlier status kept: OPEN 2026-10-13 -- "),
    },
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    # apply bottom-up so an earlier item's line count cannot move a later item's index
    found = []
    for it in ITEMS:
        assert "@@" not in it["new"], f"{it['n']}: a placeholder is still in the new status"
        hits = [i for i, l in enumerate(lines) if l == it["first"] or (it["lines"] == 1 and l.startswith(it["first"]))]
        assert len(hits) == 1, f"{it['n']}: the status's first line found {len(hits)} times"
        i = hits[0]
        block = "\n".join(lines[i:i + it["lines"]])
        assert hashlib.sha256(block.encode("utf-8")).hexdigest() == it["sha"], f"{it['n']}: the status block changed"
        assert lines[i + it["lines"]] == "" and lines[i + it["lines"] + 1].startswith(it["heading"]), \
            f"{it['n']}: the status no longer adjoins its heading"
        assert block.startswith(it["old_prefix"]) and block.endswith("*")
        new = it["new"] + block[len(it["old_prefix"]):]
        assert new.startswith("*STATUS: CLOSED 2026-10-19 -- ") and new.endswith("*")
        for ln in new.split("\n"):
            assert not ln.startswith("**"), f"{it['n']}: a status line must not start a parseable heading"
        found.append((i, it["lines"], new))
    for i, n, new in sorted(found, reverse=True):
        lines[i:i + n] = new.split("\n")
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 168 CLOSED and 244 DECIDED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
