"""Roadmap 269, opened and closed: stairs and ladders are the way between floors, and a hole in a floor is a rare,
optional route -- Level Factory 0.221.0 and Deli Counter 0.237.0, proven by cold runs 9345 and 9346.

Anchored: the end of item 268, the roadmap's last item when this was written, must be there exactly once and end the
file; nothing is written otherwise. Every line LF. Then `python tools/roadmap_status.py --write` and `--check`
regenerate and verify the index.

    python patches/patch_roadmap_269.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
END = "and what the stair guards should look like. **What would close it:** each family a species and a recipe that places it where its building's purpose says, priced in draws (most repeat across a block: one module a building, merged per material), and seen in a cold run's frames.\n"
NEW = 'and what the stair guards should look like. **What would close it:** each family a species and a recipe that places it where its building\'s purpose says, priced in draws (most repeat across a block: one module a building, merged per material), and seen in a cold run\'s frames.\n\n*STATUS: CLOSED 2026-10-20 -- SHIPPED AND PROVEN. Level Factory 0.221.0 (2706673) decides per level whether it carries a hole in a floor, at `FLOOR_HOLE_RATE` 0.25 (a call meant to be changed; a brief\'s `floor_holes` overrides it), swapping a drawn family\'s variant and building the mission\'s own building `--holes off`; Deli Counter 0.237.0 (1b9650ad) leaves a preset\'s holes out on request and keeps a deli variant without the drop (deli_a01). The replay (`docs/findings/hole_frequency/`): lot levels with a hole 54 of 300 -> 17 of 300; restaurant_row_001 and urban_row_001 12 -> 2 of 12 each; deli_001 and county_hospital_001 every level -> 2 and 5 of 12. Cold run 9345 (urban_row_001, seed 9003, 0 interventions): every candidate placed deli_a01 as predicted, drop edges 0 at a declared drop. Cold run 9346 (deli_001, seed 9191, 0 interventions): every candidate built `--holes off`, its shell\'s only vertical link the stair, declared-drop edges 28 -> 0 against 9330. The rate is the walker\'s dial.*\n\n**269. Stairs and ladders are the way between floors; a hole in a floor is a rare, optional route.** The walker, 2026-10-20, while 265\'s causes were being proven: "stairs and ladders should be the primary way to get between floors in this game...with the holes in floors being somewhat rare...but still at our disposal to use if needed/desired to add some more ways to navigate levels". **Measured first** (`docs/findings/hole_frequency/`: Level Factory\'s own lot draw replayed over every staged brief, twelve candidates each; a hole is a drop Deli Counter gave a `cause`, not one into a stair\'s own well): 54 of 300 lot levels (25 missions) carried one, bunched where a family that always carries one anchors the mission -- restaurant_row_001 and urban_row_001 12 of 12, both themeable deli variants carrying the cut drop; warehouse_yard_001 7 of 12 -- and every single-building deli_001 and county_hospital_001 level carried its preset\'s, the hospital\'s bare elevator shafts among them. **The rule** (Level Factory 0.221.0, `patches/patch_lf_floor_holes.py`): per candidate, `holes_wanted` at the brief\'s rate; `apply_hole_rule` swaps a drawn family\'s VARIANT -- without a hole on a level left without, with one on a level that wants one and has none, one only -- never the family, so `pick_lot`\'s draw stands; `draw_lot` is the one place the draw and the rule meet, for the planner, the compose spec and the site spec\'s own draw; the mission\'s own building is built `--holes off`. Deli Counter 0.237.0 (`patches/patch_dc_optional_holes.py`): `hole_causes.without_holes` leaves out every drop a player would see and the authored slab holes under it on every storey (a recipe authors the slab hole beside the link, and an atrium or a shaft cuts every storey its one link passes); `presets.make(holes=False)`; `new_level.py --holes`; `migrate_hole_free_variants.py` makes deli_a01 hole-free (a call: deli_a03 keeps the drop 9340 and 9341 proved), refurnished, its nav gate re-run on the rebuilt shell and navigable as before. **Found on the way, kept:** the coin was first a crc32 of the candidate id, and restaurant_row_001\'s and urban_row_001\'s answers came out identical for 200 seeds of 200 at 0.5 -- CRC is affine over GF(2) -- so it is a SHA-256 (0.248 of 4,000 at 0.25); the cluster test\'s guard over every lot draw outside the library looked for `pick_lot(` and failed on the site\'s `draw_lot(`, and reads both now. **After** (the same replay): 17 of 300 lot levels; restaurant_row_001 and urban_row_001 2 of 12 each, warehouse_yard_001 4, precinct_yard_001 3, deli_001 2, county_hospital_001 5 -- twelve seeds, so some read above 0.25; the rate is pinned at 0.248 over 4,000 by Level Factory\'s `test_floor_holes.py`. A swap can make two candidates place the same three buildings (urban_row_001\'s 9003 and 9104), placement still differing by seed. restaurant_row_001\'s seed 9003, cold runs 9340 and 9341\'s level, keeps its drop. **The cold runs:** 9345 (`docs/cold_runs/cold_9345/`) placed the predicted lot on every candidate -- deli_a01 where `pick_lot` had drawn deli_a03 -- and the four draws agreed through the export\'s closure; 9346 (`docs/cold_runs/cold_9346/`) ran `--preset corner_deli --seed N --holes off` for each candidate, every shell holding its stair and no hole, 0 undeclared drop edges indoors. Neither shot frames. **REFUTED, KEPT:** Deli Counter 0.237.0\'s and Level Factory 0.221.0\'s CHANGELOGs and the `FLOOR_HOLE_RATE` comment say 54 of 288 lot levels (the Deli Counter entry, 24 missions); the census counts 54 of 300 and 25, the first figure a count made by eye; each repo\'s next change corrects its text. **Left for the walker:** the rate, one number.\n'


def main():
    raw = ROADMAP.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap has CRLF lines; nothing written")
    text = raw.decode("utf-8")
    if "**269. " in text:
        raise SystemExit("REFUSED: the roadmap has an item 269 already; nothing written")
    if text.count(END) != 1 or not text.endswith(END):
        raise SystemExit("REFUSED: item 268 is not the roadmap's last item, ending as it did; nothing written")
    ROADMAP.write_bytes((text[: -len(END)] + NEW).encode("utf-8"))
    print("roadmap 269 added; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
