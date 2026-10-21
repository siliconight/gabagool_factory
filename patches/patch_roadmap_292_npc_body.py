"""Roadmap 292 CLOSED (Level Factory 0.231.0, Lot 0.126.1, Deli Counter 0.253.0: the enemy's body is the
contract's). Copied from `patch_roadmap_284_table_chairs.py`: replaces 292's status block (the paragraph directly
above its heading, asserted to be the one this was written against) with one that keeps it after "Earlier status
kept:". The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_292_npc_body.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [(292, "\n\n**292. The contract's body reaches the crew in a run and not the enemy.** `level_factory/adapters/laser_tag/__init__.py`'s `_FIELDS` writes `characters.player`'s radius, height, eye, walk speed, step-up and chest from `deli_counter/agent_contract.json` into the run's scenario (roadmap 123), and nothing more: `enemy_eye_height_m` is written from `_STOCK_SCENARIO`'s 1.6 whatever the contract states. The contract states it twice -- its NPCs share the player's metrics until a distinct class ships (`characters.npc_standard`), and `sightlines.enemy_sight_height_m` is 1.6 -- and the seam reads neither. A studio stating a 2.05 m character with a 1.85 m eye and a 1.15 m chest gets a crew sighting from 1.85 m against enemies sighting from 1.6, so the evaluator's lines cross at 1.42 m (`Engagement.cover_break_height`) where the crew's body alone crosses at 1.5; Level Factory 0.230.0's `LT_SIGHT_ONE_EYE` says so in the advisory. Laser Tag exposes the enemy's eye and no enemy radius or height (`LT_TestScenario.gd`), so the enemy's body size follows nothing. **What would close it:** which of the contract's two statements governs the enemy's eye settled in the contract, the other derived from it or removed; the seam writing the enemy's eye from it, with a test like roadmap 123's that one stated body moves both sides; the enemy's body size, if the evaluation is to follow it, one bounded Laser Tag change (the walker's rule for Laser Tag).", '*STATUS: OPEN 2026-10-21 -- found shipping Level Factory 0.230.0 (roadmap 289); not started.*', '*STATUS: CLOSED 2026-10-21 -- the enemy\'s body is the contract\'s NPC, and the NPC is the player until it says otherwise. Settled in the contract: Deli Counter 0.253.0 (ca7e45a8, `patches/patch_dc_npc_body.py`) makes `characters.npc_standard` govern -- `npc_body()` is its stated metrics over the player\'s, it states none, and its restated radius and height, read by nothing, are gone -- and `sightlines.crew_sight_height_m` and `enemy_sight_height_m` copies of the bodies\' eyes, `sight_heights()` refusing one that disagrees ("one body, one eye") as `cover_break_height` already refused an aim copy; no sightline copy is merged into a contract that omits it any more, which had refused a contract stating only its body for disagreeing with a 1.0 m aim it never wrote. The seam: Level Factory 0.231.0 (d3cf8d5, `patches/patch_lf_enemy_eye.py`) writes the scenario\'s `enemy_eye_height_m` from that block, the player\'s where it states none, and a test like roadmap 123\'s has one stated 2.05 m body move both sides to a 1.85 m eye, in the scenario `run` writes and the engagement the advisory is given (`test_the_enemy_sights_from_the_contract.py`; on 0.230.0 four of its six fail on behaviour); `LT_SIGHT_ONE_EYE` now speaks only for a distinct NPC eye or a brief moving one side. Lot 0.126.1 (dc4e2a6, `patches/patch_lot_npc_fallback.py`) shipped first: its contract fallback mirrored the NPC\'s two numbers, and Lot 0.126.0\'s guard fails against the new contract (it carries the queued `urban_tree_stations` docstring fix too). Cold run 9375 (restaurant_row_001 at seed 9003, the three tools the only ones moved): 0 interventions; the three staged scenarios byte for byte 9374\'s, the enemy\'s eye now the contract\'s 1.6; findings 108 -> 108, identical; the bake unchanged (`docs/cold_runs/cold_9375/NOTES.md`). REFUTED, kept: the item\'s "the enemy\'s body size follows nothing" -- Laser Tag 0.26.0 (roadmap 197) builds every enemy\'s capsule, mesh and agent from the scenario\'s `player_radius_m` and `player_height_m`, which the seam writes from the contract (`test_enemy_is_the_contracts.gd`, its check [2]); a distinct NPC class with its own radius or height would want a Laser Tag field, one bounded change, when one ships. Earlier status kept: OPEN 2026-10-21 -- found shipping Level Factory 0.230.0 (roadmap 289); not started.*')]


def main():
    raw = RM.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    for n, heading, old, new in ITEMS:
        if new[:80] in text:
            raise SystemExit("REFUSED: %d already applied; nothing written" % n)
        if text.count(heading) != 1:
            raise SystemExit("REFUSED: %d's heading is not there once; nothing written" % n)
        h = text.find(heading)
        s = text.rindex("\n\n", 0, h) + 2
        if text[s:h] != old:
            raise SystemExit("REFUSED: %d's status block is not the one this was written against; nothing written" % n)
        text = text[:s] + new + text[h:]
        if text.count(new + heading) != 1:
            raise SystemExit("REFUSED: %d's status no longer adjoins its heading; nothing written" % n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 292: CLOSED, the earlier status kept; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
