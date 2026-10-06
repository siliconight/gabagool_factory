"""PIPELINE_ROADMAP.md after the breadth sweep (cold runs 9166-9177):

  * item 17: a new status era, the sweep, with the 2026-09-21 status folded
    in after "Previously:" -- the convention that block itself follows;
  * item 106: CLOSED, the Empties placed by default; the earlier status kept
    verbatim at the item's end, as 182's was;
  * item 185, new: demo and reference shells drawn into real levels.

Every anchor must match exactly once. The generated index is left to
`tools/roadmap_status.py --write`.

    python patch_roadmap_breadth_sweep.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

# --- item 17 ----------------------------------------------------------------
S17_HEAD = "*STATUS: NARROWED 2026-09-21 -- FOUR MORE ZEROS, ONE REFUSAL AND ONE\n"
S17_TAIL = "`roadmap_status.py --unclassified` lists.*\n\n**17. The pipeline has never been run cold"
S17_NEW_ERA = (
    "*STATUS: NARROWED 2026-10-06 -- THE BREADTH SWEEP: TEN MISSIONS, EIGHT\n"
    "UNTOUCHED FIRST TIME AND TWO AFTER ONE TOOL FIX EACH. Cold runs 9135 to\n"
    "9165 had all built gas_block_001, so the zeros were one level's. On\n"
    "2026-10-05 the walker made the Empties and the light bake the defaults\n"
    "(Level Factory 0.144.0) and asked for the ten mission families, on their\n"
    "briefs as last run cold. Cold runs 9166-9177, recorded in\n"
    "`docs/findings/breadth_sweep_2026-10-06/`:\n"
    "- **Eight exported first time, `INTERVENTIONS: 0`:** gas_block_001 (the\n"
    "control, every number equal to 9165's), club_block_014, bank_block_001,\n"
    "video_block_001, precinct_yard_001, restaurant_row_001, warehouse_yard_001\n"
    "and gas_stop_001. Their briefs were last run cold between 9001 and 9134.\n"
    "- **Two stopped at export.** Each was a defect in Level Factory, fixed there\n"
    "and proven by a re-run of the same brief:\n"
    "  - 9170, card_block_001: refused over a blocker on a candidate nobody\n"
    "chose. `_open_blockers` read the candidate from `location`, and the\n"
    "finding carried it in `candidate_id`. Fixed in 0.144.1; 9174 exported.\n"
    "  - 9171, county_hospital_001: its site was re-assembled after the\n"
    "functional lock. With no lot library, the site spec was written before\n"
    "the shell it measures existed. Fixed in 0.144.2; 9173 exported. That\n"
    "path is the default for every new brief.\n"
    "- **The defaults found a third defect before any run:** a failed light\n"
    "bake wrote an absolute path into its report, and the closure scan refused\n"
    "the export (fixed in 0.144.0).\n"
    "A `0` on 9170 and 9171 counts hand-touches and nothing more: neither\n"
    "level shipped until the tool changed. WHAT THE SWEEP DOES NOT SHOW: every\n"
    "brief had been through the pipeline before, on older tools. The\n"
    "acceptance test below asks for a spec that never has. Previously: ")


def fold_17(text):
    assert text.count(S17_HEAD) == 1, "item 17's status head"
    assert text.count(S17_TAIL) == 1, "item 17's status tail"
    start = text.index(S17_HEAD)
    end = text.index(S17_TAIL) + len("`roadmap_status.py --unclassified` lists.*")
    old = text[start:end]
    body = old[len("*STATUS: NARROWED 2026-09-21 -- "):]
    assert body.endswith(".*")
    return text[:start] + S17_NEW_ERA + body + text[end:]


# --- item 106 ---------------------------------------------------------------
S106_OLD = """*STATUS: OPEN 2026-09-13 -- AN EMPTY HAS NO WINDOWS, AND THE ART-PASS PATH
ITS PRESETS WERE WRITTEN AGAINST DOES NOT EXIST. All three presets seal the
exterior; the two built shells are 48 and 60 slots, every one a `wall`. Their
docstrings expect the art pass to turn wall slots into windows, and no code in
Zoo does. The opaque-glazing tag an Empty's windows need was lost in Deli
Counter's f54ebfe and is restored in 0.128.1. The rename and the wiring half
are unchanged.*
"""
S106_NEW = """*STATUS: CLOSED 2026-10-06 -- PLACED, AND PLACED BY DEFAULT. Level Factory
0.137.0 stands a terrace of Empties along the far side of the through road
(`empties: "across"`), drawn from Deli Counter's rowhome family: 0.174.0
first, twelve designs by 0.184.0, windows over dark rooms. 0.143.0 merges
each one a side per material (item 182). 0.144.0 makes the terrace the
brief's default wherever a lot library and two or more buildings allow it.
The breadth sweep (cold runs 9166-9177) stood all twelve designs on seven of
its ten missions, six of which never asked, and each of those seven exports
merged 1,061 meshes into 236. What remains is not this item: a brief with no
`lot_library` gets no Empties (three of the ten), because the library is
opt-in for the reason its own comment gives; and `gs_facade_rowhome` and
`gs_facade_storefront`, the two sealed boxes this item began from, are still
not offered.*
"""
S106_BODY_END = """`plan_kit`, not on building a shell through Zoo and looking at it.

*STATUS: OPEN 2026-09-06 -- AN OWNERSHIP QUESTION RAISED FROM A WALK, AND"""
S106_BODY_END_NEW = ("""`plan_kit`, not on building a shell through Zoo and looking at it.

*Earlier status, kept verbatim:* """ + S106_OLD + """
*STATUS: OPEN 2026-09-06 -- AN OWNERSHIP QUESTION RAISED FROM A WALK, AND""")

# --- item 185 ---------------------------------------------------------------
TAIL_ANCHOR = ("the gutter Patina hangs on the neighbouring house's party wall "
               "projects along their slope, about 30 px below them.*\n")
ITEM_185 = """
*STATUS: OPEN 2026-10-06 -- FOUND IN THE BREADTH SWEEP, A QUESTION FOR THE
WALKER. Cold runs 9170 and 9174 (card_block_001) drew `setback_demo` on
seed_9061 and `pvp_station_ref` on seed_9162. Neither candidate was picked,
and seed_9061's map failed Laser Tag in 2 s (`UNREACHABLE_SPAWN`). Not
started.*

**185. Demo and reference shells are drawn into real levels.** Found in the
breadth sweep, 2026-10-06.

**WHAT HAPPENS.** `building_library.source_exclusion`
(`level_factory/packages/pipeline/building_library.py`) keeps two kinds of
shell out of a lot: Level Factory's own composed outputs (the `lf_` prefix it
writes) and facades (Deli Counter's own `facade` flag). Everything else
complete in `deli_counter/build` is a building a lot may draw. That includes
`setback_demo` and `pvp_station_ref`, which carry every manifest a building
does (gameplay, slots, lights, navgate, validation), rebuilt with the rest of
the library on 2026-10-05.

**WHY IT IS A QUESTION AND NOT A FIX.** The exclusion rule refuses to guess
from names, deliberately: "A name rule is normally the weak kind of rule", in
its own comment. Whether a demo or a reference shell belongs in a shipped
level is an art-direction call. If it does not, the house way is the way
`facade` works: Deli Counter says so in the shell's validation manifest, and
Level Factory reads the flag rather than a word in an id.

**NOT CONNECTED, AS FAR AS MEASURED.** seed_9061's `UNREACHABLE_SPAWN` was not
traced to `setback_demo`. Nothing here says the demo shell caused it.
"""


def main():
    text = ROADMAP.read_bytes().decode("utf-8")
    assert "\r" not in text
    text = fold_17(text)
    assert text.count(S106_OLD) == 1, "item 106's status"
    assert text.count(S106_BODY_END) == 1, "the end of item 106's body"
    text = text.replace(S106_BODY_END, S106_BODY_END_NEW)
    # the status that sits above the heading is now the only S106_OLD that is
    # not preceded by the verbatim marker
    i = text.index(S106_OLD)
    assert not text[:i].endswith("*Earlier status, kept verbatim:* ")
    text = text[:i] + S106_NEW + text[i + len(S106_OLD):]
    assert text.endswith(TAIL_ANCHOR) and text.count(TAIL_ANCHOR) == 1, "the file's last line"
    text = text + ITEM_185
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("items 17 and 106 updated, 185 filed")


if __name__ == "__main__":
    main()
