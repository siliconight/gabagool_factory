"""Roadmap 242 and 240, the same afternoon: across seven mission families the physics engine is NOT the
fix (`docs/findings/route_snag/engine_breadth.py`; "choose Jolt" retracted), and the street lights'
shadow levers measured on bodies (`docs/findings/pole_line/shadow_options.py`). Replaces 242's status
and the end of 240's (each asserted once and still above its heading) and appends one paragraph to
each body. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_242_engine.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S242_OLD_HEAD = "*STATUS: NARROWED 2026-10-12 -- the snag found, and it is the physics engine's "
S242_OLD_TAIL = ("what is left tracks the fights. Left: which engine the game, and so the grader, runs (the "
                 "walker's call); the second place, beside a meter at (35, -17), unattributed.*")
S242_NEW = ("*STATUS: NARROWED 2026-10-12 -- the snag found: a body pinned at a corner the crew bot cuts "
            "into, and NOT the physics engine's (`docs/findings/route_snag/`). On restaurant_row_001 it is "
            "the deli register counter's corner, where Godot Physics' `move_and_slide` slides on the floor's "
            "normal and never turns; Jolt slides past it there (player-stuck 72 -> 7). Across seven mission "
            "families -- 16 lots, today's Laser Tag, each lot's two Godot Physics passes identical -- Jolt "
            "pins more elsewhere: without the counter's lot player-stuck 36 under Godot Physics against 53, "
            "pinned 8 against 23, in 2 lots against 4. Each engine pins at different corners; what both "
            "share is the bot turning toward its next point within its 0.44 m arrival radius where the "
            "navmesh leaves the body 5 cm. Left: Laser Tag's bot keeps the path's clearance at corners (the "
            "fix, whichever engine the game ships); the engine, the game's choice, the default standing "
            "until it is made; the second place, beside a meter at (35, -17).*")

BODY_242 = """

**ACROSS FAMILIES THE ENGINE IS NOT THE FIX, 2026-10-12** (`docs/findings/route_snag/engine_breadth.py`). **RETRACTED, KEPT: "choose Jolt"** -- the recommendation given the walker that afternoon, on restaurant_row_001 alone. The other families' staged lots ran their jobs before Laser Tag's fixed clock and cannot be reproduced, so each copy got today's Laser Tag and ran under Godot Physics twice (the control: the two passes identical, 16 of 16) and under Jolt once, 25 runs from its job's seed: restaurant_row_001 3 lots, deli_001 3, warehouse_yard_001 3, bank_block_001 1, club_block_014 1, gas_block_001 2, crossroads_9600 3. All 16: player-stuck 108 under Godot Physics, 60 under Jolt, pinned 74 against 25 -- but 66 of the 74 are the one counter. Without it, 36 against 53 and 8 against 23; club_block_014 seed_9282 pinned 0 -> 5 under Jolt, crossroads_9600 seed_9701 0 -> 8, warehouse_yard_001 seed_9206 0 -> 4; grades move both ways (gas_block_001 seed_9181 PASS_WITH_TUNING 75 -> WARN 65). Both engines pin bodies at corners; only where differs. The walker does not yet know which engine the game will ship ("we are going to use Godot"); `engine_probe.gd` read off Godot 4.7 that a project naming none runs Godot Physics and one naming "Jolt Physics" runs Jolt, both in the stock binary. **WHAT WOULD CLOSE IT NOW.** The bot keeping its path's clearance at corners, measured on these 16 lots under both engines (pins near zero on each, the grades' spread the fights'), and the place beside the meter attributed."""

S240_OLD = ("Left: the street lights' shadow cost, the walker's call among the levers; the frames beside the "
            "comps for the walker's eye; then the rowhouse front and the silver roofs.*")
S240_NEW = ("The street lights' shadow levers measured on bodies: each budget cut darkens what moves (a body "
            "8 %, a far road band of cars 26 %) and under a steady, baked light no body casts a shadow on "
            "the road in any arm. Left: the street lights' shadow cost, the walker's call with that seen; "
            "the frames beside the comps for the walker's eye; then the rowhouse front and the silver roofs.*")

BODY_240 = """

**WHAT THE SHADOW MAPS BUY, SEEN ON BODIES, 2026-10-12** (`docs/findings/pole_line/shadow_options.py`; the walker: "What helps us learn?"). Two grey capsules the crew body's size stand under two steady lights of 9264's package -- pole 22, shadowed as built and the first to lose its map at a budget of 4, and pole 24, 60 m from the far camera -- in four arms: as built, a budget of 4, of 0, and every steady street light faded out whole past 30 m. **Under a steady light the body casts no shadow on the road in any arm**: the road is lightmapped and nothing at runtime darkens it, so a baked light's map shades only what moves. **Cutting the budget darkens what moves**: the near body's mean luma 30.70 -> 28.26 (8 %), the far crop's road band of parked cars 14.58 -> 10.84 (26 %), the road itself unchanged; the likely mechanism, unmeasured, is GL Compatibility drawing a shadowed light in its own pass while unshadowed lights share each object's eight-light list. **The whole-light fade changed nothing measured**, including where the far body should have lost its light -- a knob with no visible effect, not a result. Every cheap lever on the maps costs light on players and enemies at night; none applied."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "ACROSS FAMILIES THE ENGINE IS NOT THE FIX" not in text, "already applied"
    i = text.find(S242_OLD_HEAD)
    assert i >= 0 and text.count(S242_OLD_HEAD) == 1, "242's status not found once"
    j = text.find(S242_OLD_TAIL, i)
    assert j > i and text.find("\n", i) > j, "242's status end not on its line"
    text = text[:i] + S242_NEW + text[j + len(S242_OLD_TAIL):]
    h = text.find("\n\n**242. ")
    assert h > 0 and text[h - len(S242_NEW):h] == S242_NEW, "242's status does not sit above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**243. ", nxt) > nxt, "243 does not follow 242"
    text = text[:nxt] + BODY_242 + text[nxt:]
    assert text.count(S240_OLD) == 1, "240's status end not found once"
    text = text.replace(S240_OLD, S240_NEW)
    h = text.find("\n\n**240. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and text[s:h].endswith(S240_NEW), "240's status does not sit above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**241. ", nxt) > nxt, "241 does not follow 240"
    text = text[:nxt] + BODY_240 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 242 and 240: statuses and a paragraph each; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
