"""Roadmap 296 NARROWED (a level's package carries its buildings' drawings and names them: Deli Counter 0.257.0,
Level Factory 0.232.0 and 0.232.1, cold runs 9377 and 9378, the walker's review page) and 298 filed (the walker's
main-drag comp). Copied from `patch_roadmap_284_296_desk_move.py`: the status block the paragraph directly above its
heading, asserted to be the one this was written against, replaced with one that keeps it after "Earlier status
kept:"; the new item appended after the last, asserted to be 297. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_296_298_drawings.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUSES = [(296, '\n\n**296. A level\'s package carries no drawing of its buildings, so neither a reviewer nor a player can scope one out.** The walker, 2026-10-21, asked where a reviewer should see roadmap 293\'s exploded axonometric -- a walker-review page, a level\'s export, or both: "both. It could even get into the game where the players can \'scope out\' the level and see the buildings the level assembles". Read for it (Level Factory\'s export, 2026-10-21, against cold run 9375\'s package): a building reaches a package only through the presentation compose, which calls Deli Counter\'s `portable_building.build_package` and publishes the whole composed package, and the export\'s copy of the composed root, by exclusion, into `lot/<id>/` (`level_factory/packages/exporting/export.py:2160-2175`); a package names a building by Deli Counter\'s file stem and a drawing carries the spec\'s name -- one library building differs, cbp_town_finale_midbalanced_schemafixed, whose `build/<id>.gameplay.json` names it `cbp_town_finale_midbalanced`; which buildings a level stands is recorded only in `site.tscn`\'s instances; a cold run draws nothing for a library building (`build/floorplans/` is the commit gate\'s ignored side effect of `validate.py --all`), and a facade is never drawn (`validate.py:116-120`); no Level Factory test names an `.svg`, and `test_export_standing_lot.py` pins the folders under `lot/`, so a drawing belongs inside `lot/<id>/`. **What would close it:** each building\'s package carrying its drawings, rendered from its spec when it is composed rather than copied from a build folder that may be stale or empty -- the exploded axonometric and its storey plans, a facade\'s or the reason it has none -- kept as files the engine does not import, since an SVG imported as a texture spends every level\'s disk and import time on a screen no game has built: price it before it ships; an index at the package\'s root naming each building the level stands (its node, its id, its spec, its drawings, where it stands); a walker-review page built from a cold run\'s package, so the reviewer sees what ships; and the in-game screen left to the game, the factory\'s part the drawings and the index.', "*STATUS: OPEN 2026-10-21 -- the walker's answer on roadmap 293; not started.*", "*STATUS: NARROWED 2026-10-21 -- a level's package carries its buildings' drawings, and names them. Deli Counter 0.257.0 (9b1d5238, `patches/patch_dc_drawings.py`): `build_package(..., spec_path=)` draws a building from its spec into its package's `drawings/` -- the exploded axonometric and a plan a storey, each beside a `.import` that keeps it as the file it is (measured on Godot 4.7, `patches/dc_drawings/keep_probe.py`: left to the default import, deli_a03's axonometric is a 136,248-byte texture in every level; kept, none is made, and a game still reads it and draws it with `Image.load_svg_from_string`), and `drawings.json`; a facade gets its reason instead, its drawing an empty walled box; an axonometric's canvas holds its own text. Level Factory 0.232.0 (6ce0e8e, `patches/patch_lf_drawings.py`): the library and the compose name each building's spec, and the export writes `buildings.json` at the package's root -- every standing instance, where it stands, its drawings as `res://` paths the closure verdict resolves. Cold run 9377 (0 interventions; the level 9376's, the bake's 2,947 users the same): ten drawings shipped, present, kept, none made a texture -- and two holes, closed by Level Factory 0.232.1 (fb4707d, `patches/patch_lf_drawings_fix.py`): the 26 Empties composed with no spec, and the mission shell's drawings at a varied lot's package root. Cold run 9378 (0 interventions, the level 9377's) proved both. The walker's review page, built from 9378's package: https://claude.ai/artifact/BG8SRKn7xVCEz3L3JFyg3y (`docs/findings/walker_review_2026-10-21_drawings/`). LEFT: the walker's answers there -- each building's drawing, whether a facade should carry a front elevation, what players should see; the in-game screen, which is the game's. Earlier status kept: OPEN 2026-10-21 -- the walker's answer on roadmap 293; not started.*")]
NEW_ITEMS = ['*STATUS: OPEN 2026-10-21 -- the walker\'s comp, written up in `docs/reference/MAIN_DRAG_COMP.md`; filed for later, as the walker asked.*\n\n**298. A main drag: the walker\'s remix of the Industrial Highway through Tinicum, as a level comp.** The walker, 2026-10-21, with a street map of PA-291 through Essington and Tinicum: "save this for later...do a remix of this street, main drag, to have a cheesteak shop, bank, coffeshop, wawa ,ect ect for a level comp". Written up in `docs/reference/MAIN_DRAG_COMP.md` (the map not stored): a four-lane arterial with a service road on its business side, a freight line right behind it, side streets every block into a rowhome grid, the expressway cloverleaf as the backdrop; along the drag every business under an invented Delco name, the Wawa FLAPPAHS. Read for it (Deli Counter\'s specs, 2026-10-21): the bank, FLAPPAHS and its forecourt, the pizzeria, the dive club, the tow yard and the warehouses exist; a cheesesteak shop, a coffee shop and a hot dog stand have no family; Lot lays no rail; and a lot is drawn by seed, a brief anchoring one building (`building_library.lot_for_brief`). **What would close it:** a cheesesteak shop and a coffee shop grown as Deli Counter families, their fixtures as Zoo species and their signs as Pixelcoat skins under names the walker picks; a brief that names the businesses its main drag stands; a four-lane arterial with a service road, and a rail edge, from Lot; a cold run of the remix, walked by the walker.\n']


def main():
    raw = RM.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\n**298. " in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    for n, heading, old, new in STATUSES:
        if text.count(heading) != 1:
            raise SystemExit("REFUSED: %d's heading is not there once; nothing written" % n)
        h = text.find(heading)
        s = text.rindex("\n\n", 0, h) + 2
        if text[s:h] != old:
            raise SystemExit("REFUSED: %d's status block is not the one this was written against; nothing written" % n)
        text = text[:s] + new + text[h:]
        if text.count(new + heading) != 1:
            raise SystemExit("REFUSED: %d's status no longer adjoins its heading; nothing written" % n)
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\*\*(\d+)\. ", text)]
    if max(heads) != 297 or heads[-1] != 297:
        raise SystemExit("REFUSED: the last item is not 297; nothing written")
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    for item in NEW_ITEMS:
        text = text + "\n" + item
    if len(re.findall(r"(?m)^\*STATUS: [^\n]*\*\n\n\*\*298\. ", text)) != 1:
        raise SystemExit("REFUSED: item 298's status does not adjoin its heading; nothing written")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 296 NARROWED, 298 filed; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
