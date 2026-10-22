"""Write patches/patch_roadmap_284_296_desk_move.py: roadmap 284's and 293's statuses replaced (the block above each
heading, embedded exactly, the earlier status kept), and 296 and 297 appended after the last item (asserted to be 295).
284: a host no chair fits beside is moved where one does (Deli Counter 0.256.0); 293: the walker's answer on where the
drawing is seen; 296: the drawings in a level's package and the in-game scope-out; 297: two Level Factory rules that
ask for a name the files do not carry. Copied from `roadmap_293_treads/make_roadmap_293_treads.py` and
`roadmap_floor_plan_guide/make_roadmap_floor_plan_guide.py`. Refuses if the name is taken, or while the cold run's
sentence is still a placeholder.

    python patches/roadmap_284_296_desk_move/make_roadmap_284_296.py
"""
import pathlib
import re
import subprocess

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_284_296_desk_move.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t

# Deli Counter 0.256.0's commit, read from the repo, not typed
assert (F / "deli_counter" / "VERSION").read_bytes() == b"Deli Counter 0.256.0"
line = subprocess.run(["git", "-C", str(F / "deli_counter"), "log", "-1", "--format=%h %s"], capture_output=True,
                      text=True, check=True).stdout.strip()
DC, SUBJECT = line.split(" ", 1)
assert SUBJECT.startswith("0.256.0: "), SUBJECT

COLD = ("Cold run 9376 (restaurant_row_001 at seed 9003, Deli Counter the only tool moved; "
        "`docs/cold_runs/cold_9376/`): 0 interventions; the three staged scenarios and the 108 findings 9375's; office's "
        "exec_suite desk back beside its chair -- the bake's users 2,940 -> 2,947, office's scene six merged meshes, one "
        "lit face and two collision bodies more, every other building's the same but for the ids the engine renumbers.")
assert COLD != "COLD_RUN_9376", "the cold run's sentence is still a placeholder"


def status_of(n):
    m = list(re.finditer(r"(?m)^\*\*%d\. " % n, t))
    assert len(m) == 1, n
    h = m[0].start()
    s = t.rindex("\n\n", 0, h - 2) + 2
    block = t[s:h - 2]
    assert block.startswith("*STATUS: ") and block.endswith("*") and "\n" not in block, n
    heading = t[h - 2:t.index("\n", h)]
    assert t.count(heading) == 1, n
    return heading, block


H284, OLD284 = status_of(284)
assert OLD284.startswith("*STATUS: NARROWED 2026-10-21 -- every piece that must seat somebody stands with its chair."), \
    OLD284[:120]
NEW284 = (
    "*STATUS: NARROWED 2026-10-21 -- a host no chair fits beside is moved, not taken away (the walker, asked whether "
    "a desk with no room for its chair should be moved instead of removed: \"yes\"). Deli Counter 0.256.0 (" + DC
    + ", `patches/patch_dc_desk_move.py`): such a host moves LAST, when the room is furnished, so every piece the "
    "recipe drew stands where it stood -- to the nearest spot on the room's grid where it clears as `_host` placed it "
    "and its chair fits, both off the room's routes, narrowing no pair of its route endpoints (`room_necks`, the "
    "census's own neck asked of one room; read against the census, 187 pairs in 64 rooms of twelve specs, every one "
    "the same to the millimetre). Of the 25 hosts 0.252.0 took away, 18 stand again in 17 specs (desks 239 -> 256, "
    "dining tables 254 -> 255), each with its chair; the census (`docs/findings/furnish_route_cost/`, re-run) reads "
    "every summary line and every room kind as at 0.252.0 -- over 10 % 26, closed to the bake 5, narrowed to single "
    "file 151 -- and ten pairs lost width, every one still two abreast; the 17 rooms' floor shares 1.9 to 7.5 %. "
    "Measured and kept (`patches/dc_desk_move/arms.py`): held off the routes alone, the move brought 19 back and "
    "narrowed nine pairs to single file in two rooms -- keeping off a route keeps its length, not its width; on a "
    "route where nothing else stood, 21 and the same nine; its chair relaxed too, 24, the same nine and one pair over "
    "10 %. " + COLD + " LEFT: seven hosts still go -- every spot on their rooms' 25-spot grids refused (9 to 19 on a "
    "route, 6 to 14 by `_seed_clear`, the rest by the chair or the guard; `patches/dc_desk_move/still_gone.out.txt`), "
    "a finer grid for the move the next lever; and a table's regular chairs still spend the room's stream. Earlier "
    "status kept: " + OLD284[len("*STATUS: "):])

H293, OLD293 = status_of(293)
assert OLD293.startswith("*STATUS: NARROWED 2026-10-21 -- the stairs drawn as treads"), OLD293[:120]
NEW293 = (
    "*STATUS: NARROWED 2026-10-21 -- where a reviewer finds the drawing, the walker's answer: \"both\" -- a "
    "walker-review page and a level's export -- \"It could even get into the game where the players can 'scope out' "
    "the level and see the buildings the level assembles\"; filed as 296, which carries it. LEFT here, as before: "
    "ramps, platforms and fire escapes in either drawing; a cut switchback's second leg drawn solid to its own "
    "storey. Earlier status kept: " + OLD293[len("*STATUS: "):])
for s in (NEW284, NEW293):
    assert "\n" not in s and s.endswith("*")

ITEM296 = "*STATUS: OPEN 2026-10-21 -- the walker's answer on roadmap 293; not started.*\n\n" + (
    "**296. A level's package carries no drawing of its buildings, so neither a reviewer nor a player can scope one "
    "out.** The walker, 2026-10-21, asked where a reviewer should see roadmap 293's exploded axonometric -- a "
    "walker-review page, a level's export, or both: \"both. It could even get into the game where the players can "
    "'scope out' the level and see the buildings the level assembles\". Read for it (Level Factory's export, "
    "2026-10-21, against cold run 9375's package): a building reaches a package only through the presentation "
    "compose, which calls Deli Counter's `portable_building.build_package` and publishes the whole composed package, "
    "and the export's copy of the composed root, by exclusion, into `lot/<id>/` "
    "(`level_factory/packages/exporting/export.py:2160-2175`); a package names a building by Deli Counter's file "
    "stem and a drawing carries the spec's name -- one library building differs, "
    "cbp_town_finale_midbalanced_schemafixed, whose `build/<id>.gameplay.json` names it "
    "`cbp_town_finale_midbalanced`; which buildings a level stands is recorded only in `site.tscn`'s instances; a "
    "cold run draws nothing for a library building (`build/floorplans/` is the commit gate's ignored side effect of "
    "`validate.py --all`), and a facade is never drawn (`validate.py:116-120`); no Level Factory test names an "
    "`.svg`, and `test_export_standing_lot.py` pins the folders under `lot/`, so a drawing belongs inside "
    "`lot/<id>/`. **What would close it:** each building's package carrying its drawings, rendered from its spec "
    "when it is composed rather than copied from a build folder that may be stale or empty -- the exploded "
    "axonometric and its storey plans, a facade's or the reason it has none -- kept as files the engine does not "
    "import, since an SVG imported as a texture spends every level's disk and import time on a screen no game has "
    "built: price it before it ships; an index at the package's root naming each building the level stands (its "
    "node, its id, its spec, its drawings, where it stands); a walker-review page built from a cold run's package, "
    "so the reviewer sees what ships; and the in-game screen left to the game, the factory's part the drawings and "
    "the index.\n")
ITEM297 = "*STATUS: OPEN 2026-10-21 -- found in passing reading the export for roadmap 296; read, not chased.*\n\n" + (
    "**297. Two Level Factory rules ask for a name the files do not carry.** Found reading the export for roadmap "
    "296, read again, not chased. `packages/pipeline/building_library.py`'s facade rule (its docstring, 129-134) "
    "says exactly one complete shell has no validation manifest, cbp_town_finale_midbalanced_schemafixed, and fails "
    "open for it -- but it has one, `deli_counter/build/cbp_town_finale_midbalanced.validation.json`, under its "
    "spec's name, where the library asks for `<id>.validation.json` by the file stem (145), so a facade or demo flag "
    "in it would never be read. And `packages/exporting/export.py:1947-1948` adds \"validation\" to `skip`, which "
    "matches file names (`_copy_tree`, its own comment saying so), so it could not leave the `validation/` directory "
    "out -- while `ExportProfile.include_validation`, which gates it, defaults true and nothing in Level Factory sets "
    "it false (read again). One reads a name nothing writes; the other is a knob with no effect behind a rule that "
    "cannot fire. **What would close it:** the library finding a shell's validation manifest by the name Deli "
    "Counter writes it under (`build/<id>.gameplay.json`'s `level`, the mapping roadmap 296 needs too), its "
    "docstring's claim corrected; the export's validation rule made a directory rule with a profile that uses it, or "
    "removed with the reason the folder ships; a test failing on the old code for each.\n")
for item in (ITEM296, ITEM297):
    assert "\n" not in item[:-1].replace("*\n\n**", "*  **"), "an item spans more than its status and its line"

PATCH = '''"""Roadmap 284 NARROWED again (Deli Counter 0.256.0: a host no chair fits beside is moved where one does), 293
NARROWED with the walker's answer on where the drawing is seen, and 296 and 297 filed. Copied from
`patch_roadmap_293_treads.py` (the status blocks: each the paragraph directly above its heading, asserted to be the
one this was written against, replaced with one that keeps it after "Earlier status kept:") and
`patch_roadmap_floor_plan_guide.py` (the new items, appended after the last, asserted to be 295). The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_284_296_desk_move.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUSES = %r
NEW_ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\\n**296. " in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    for n, heading, old, new in STATUSES:
        if text.count(heading) != 1:
            raise SystemExit("REFUSED: %%d's heading is not there once; nothing written" %% n)
        h = text.find(heading)
        s = text.rindex("\\n\\n", 0, h) + 2
        if text[s:h] != old:
            raise SystemExit("REFUSED: %%d's status block is not the one this was written against; nothing written" %% n)
        text = text[:s] + new + text[h:]
        if text.count(new + heading) != 1:
            raise SystemExit("REFUSED: %%d's status no longer adjoins its heading; nothing written" %% n)
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 295 or heads[-1] != 295:
        raise SystemExit("REFUSED: the last item is not 295; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    for item in NEW_ITEMS:
        text = text + "\\n" + item
    for n in (296, 297):
        if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*%%d\\. " %% n, text)) != 1:
            raise SystemExit("REFUSED: item %%d's status does not adjoin its heading; nothing written" %% n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 284 and 293 NARROWED, 296 and 297 filed; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % ([(284, H284, OLD284, NEW284), (293, H293, OLD293, NEW293)], [ITEM296, ITEM297])
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars; Deli Counter", DC)
