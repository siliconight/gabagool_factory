"""Roadmap 230: neighbours with reasons -- the walker's adjacency and layout guide informs the draw and the audit.

Appends item 230 after 229's body, which closes the file once `patch_roadmap_9229.py` has run.
The anchor must be the file's last line; nothing is written otherwise. The generated index is
regenerated afterwards by `tools/roadmap_status.py --write`.

    python patches/patch_roadmap_230_adjacency.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ANCHOR = (
    "room; and the grids are perfectly regular, the tile snap being the only structural cause so "
    "far. The draws are the number to watch as the species grow: every fixture is hardware.\n"
)
STATUS = (
    "*STATUS: OPEN 2026-10-10 -- filed, not started. The walker's guide "
    "(`docs/reference/PA_1990S_ADJACENCY_AND_LAYOUT_GUIDE.md`, \"would this help level factory "
    "and lot in terms of placement?\"): an 84-type building catalog in nine categories, a 9 x 9 "
    "affinity matrix, 32 pair rules with verdicts, a connector catalog with owners and users, 18 "
    "cluster templates, a dressing contract and measurable gameplay targets. It names the thing "
    "the factory does weakest: the buildings beside the objective are a seeded draw with no "
    "reason to be neighbours. Three adoptions, as data for the deterministic planners, never a "
    "layout brain: the draw by cluster template, the pair rules as audit findings, the connectors "
    "for roadmap 199's grammars. Owner: Level Factory (the brief and the draw) and Lot (the "
    "audit and the connectors).*\n"
)
BODY = (
    "**230. Neighbours with reasons: the adjacency guide informs the draw and the audit.** The "
    "walker, 2026-10-10, with `PA_1990s_Building_Adjacency_and_Level_Layout_Guide.md`: \"would "
    "this help level factory and lot in terms of placement?\" Yes, and more than the tree guides "
    "did, because it is written for the gap this repo has measured twice: roadmap 199 found every "
    "level is one T with two mirrored approaches and no loop, and `library-growth-reshuffles-lots` "
    "found that a new building family changes every seed's neighbours, which is what a draw with no "
    "reasons does.\n"
    "\n"
    "**WHAT THE GUIDE IS.** A specification for a \"layout brain\": settlement profiles "
    "(`philly_rowhouse`, `mature_inner_suburb`, `borough_center`, `rail_suburb`, "
    "`arterial_strip`, `river_industry`, `creek_mill_edge`, `institutional_campus`, "
    "`airport_edge`...); a typed adjacency vocabulary (spatial relations from `same_structure` to "
    "`visual_only`, directional functional relations, edge channels, access classes, verdicts "
    "`prefer / allow / condition / repair / reject`); a 9 x 9 category affinity matrix (housing, "
    "commerce, civic, recreation, nightlife, light industry, heavy industry, transport, farming); "
    "84 building records each with the support program it `requires` (public entry, goods "
    "access, refuse, parking strategy, separation...); 32 pair rules P01-P32 with evidence and a "
    "repair; an exception contract (0 to 2 conspicuous exceptions a small level, each with a "
    "spatial fact); a connector catalog (sidewalk, local street, rear passage, service lane, "
    "shared court, driveway, loading apron, parking walk, crossing, gate, stair, ramp, desire "
    "path) with owner, users and state; greybox dimensions (a single-file passage 1.0 to 1.5 m, "
    "two-way 1.8 to 3.0, a frontage strip 3 to 5, a service lane 3.5 to 5, a court 10 to 25 m "
    "across, a focal point every 20 to 50 m, a detour of 10 to 40 s); a dressing contract "
    "(owner, purpose, anchor, support surface, clearance group; layers fixed infrastructure, "
    "working equipment, current activity, wear, rare story detail; randomise owner first and "
    "transform last); period rules (no TSA before November 2001, PHL's terminal dates, no "
    "borer-killed ash in the 1990s); gameplay targets (3 to 8 enterable buildings, ordinary "
    "fabric 50 to 75 % of all instances, one or two landmarks, two meaningful approaches, a return "
    "loop preferred, 2 to 3 choices at a decision); 18 cluster templates; an output contract in "
    "three stages; checks V01-V14 and cases T01-T16. Its numbers are authored starts, by its own "
    "word.\n"
    "\n"
    "**WHERE THE FACTORY STANDS AGAINST IT.**\n"
    "- **The draw.** `site_variation` places the objective archetype and fills the row from the "
    "library by seed; no affinity, no template, no reason. The guide's cluster templates are our "
    "missions seen from the other side: restaurant_row_001 (rail station, deli, office) is its "
    "C03 station neighbourhood by accident; county_hospital_001 is C11; gas_stop_001 is C08; "
    "warehouse_yard_001 is C04/C05; club_block_014 is an `adult_venue` the P07 rule keeps off a "
    "school's edge.\n"
    "- **The library maps onto the catalog** almost one to one: deli, pharmacy, clinic, "
    "courthouse, marina, museum, brewery, funeral_home, country_club, parking_garage, "
    "rail_station, airport_terminal, video_store, warehouse as themselves; gas_station is "
    "`fuel_station`, supermarket `grocery`, stop_n_go `corner_store`, strip_retail `strip_center`, "
    "auto_shop `repair_garage`, credit_union and bank_branch `bank`, bank_tower `office`, "
    "apartment_walkup `apartment`, twin `twin_house`, mansion `detached_house`, the Empties "
    "`rowhouse`, market_hall `produce_market`, landmark_hall `municipal_hall` or `union_hall`, "
    "depot `bus_depot` or `truck_depot`, freight_terminal `truck_depot` or `airport_cargo`, "
    "strip_club `adult_venue`; stadium, arena, train_yard, construction_site (a state, not a type) "
    "and pawn_shop have no record; casino is a period problem by the guide's own rule, "
    "Pennsylvania's first opening in 2006, which a brief must declare as fiction.\n"
    "- **The connectors.** Lot lays sidewalks, roads, driveways, walks to doors (0.91.0), kerb "
    "cuts and crossings, pads and parking fields (0.93.0, 0.94.0), dumpsters at the back "
    "(0.90.0), the fence and the backdrop (228). No rear passage, service lane, shared court or "
    "gate with declared users; the loop 199 lacks is exactly a service lane behind the row.\n"
    "- **The targets.** Enterable buildings 2 to 3 a level (the guide's 3 to 8); ordinary fabric "
    "about 80 % (the twelve Empties against three enterables, above the guide's 50 to 75 %); two "
    "mirrored approaches and no loop; one landmark (the sign, the tower); the furnish's "
    "correlated variation (`_PALETTE`, `_SAME_PIECE_MAX`, `_seed_clear`) and the authorship "
    "guide already say what the dressing contract says.\n"
    "\n"
    "**WHAT TO BUILD, IN ORDER, as data for the planners that exist.**\n"
    "- **The draw by cluster template** (Level Factory): `MissionBrief.cluster` names a template "
    "(or the archetype implies one: a hospital is C11, a gas station C08, a deli or a station C03, "
    "a warehouse C04); `site_variation`'s draw takes the supporting and ordinary-fabric types from "
    "it through the mapping above, so a level has a premise and a new building family changes "
    "only the levels whose template names it. Recorded in the spec as `cluster_resolved`.\n"
    "- **The pair rules as audit findings** (Lot): `site_audit` matches each adjacent pair's "
    "(category, relation) against P01-P32 and the affinity matrix and reports `S_ADJACENCY` with "
    "the verdict, the rule and its repair: INFO for prefer and allow, MED for condition, HIGH for "
    "repair and reject. A finding, not a gate, until the draw above makes the verdicts mostly "
    "prefer.\n"
    "- **The connectors for 199** (Lot, with 199's inversion): the `service_lane` behind the row "
    "with its owner and users, the `rear_passage`, the `shared_court`, the `gate` with a state; "
    "the audit counts them beside approaches and loops.\n"
    "- **The targets in the audit** (Lot): enterable count, ordinary share, approaches, loops, a "
    "focal point every 20 to 50 m along the critical route, a parking strategy declared a "
    "building.\n"
    "\n"
    "**NOT TO BUILD.** The layout brain, its output contract and its LLM planner: the factory's "
    "planners are deterministic and measured, and stay so. The airport, farm and marina material "
    "waits on buildings the library has not drawn in a level.\n"
    "\n"
    "Owner: Level Factory (the brief and the draw) and Lot (the audit and the connectors).\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(ANCHOR) == 1, text.count(ANCHOR)
    assert text.endswith(ANCHOR), "229's body no longer closes the file"
    assert "**230. " not in text, "230 already exists"
    text = text + "\n" + STATUS + "\n" + BODY
    i = text.index(STATUS)
    assert text[i + len(STATUS):].startswith("\n**230. "), "230's status is not above its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 230 added: neighbours with reasons")


if __name__ == "__main__":
    main()
