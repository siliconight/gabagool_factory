"""Roadmaps 156 and 249, 2026-10-14: the fire escape merged with its front -- Level Factory 0.209.0, cold run 9304 --
and what attributing that package found.

- 156: the status's Left loses the merge and gains its price; one body paragraph after THE FIRST CUT, VISUAL.
- 249, new, at the end: a package ships the module GLBs its Empties were merged from.

The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_156_merge.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S156_OLD = ("Left: the merge -- each storey draws on its own, Level Factory's per-side merge taking slots by name; "
            "Patina's front dressing read off the stack (248)")
S156_NEW = ("Merged with its front by Level Factory 0.209.0 (3ffe5c6), proven by cold run 9304 (0 interventions): "
            "against 9302, which had none, +2 draws at the worst heading where unmerged it was +26. Left: Patina's "
            "front dressing read off the stack (248)")

B156_ANCHOR = ("(roadmap 248). **Left of this item:** the merge; climbing it, which closes 156; the light well; the "
               "walker's calls.\n")
B156_NEW = B156_ANCHOR + (
    "\n**MERGED WITH ITS FRONT, 2026-10-14** (`docs/findings/fire_escape/README.md`, \"Merged\"; "
    "`patches/patch_lf_merge_fire_escape.py` and `lf_merge_fire_escape/`; `docs/cold_runs/cold_9304/`). **Level "
    "Factory 0.209.0** (3ffe5c6): `_side` gives a `fire_escape_*` slot the front's side, S, as 0.196.0 did the stoop, "
    "and a test reads Deli Counter's schema, whose `fire_escape_stack` must name the front alone, so a back stack "
    "cannot be merged into the front's mesh unseen. Before shipping, on a mirror of 9303's package "
    "(`merge_fire_escape.sh`): 0.208.0's script, the control, took nothing from the walk-ups; 0.209.0's made one "
    "mesh of each one's 5, 6, 5 and 4 storeys and took nothing from the six other Empties. **Cold run 9304** (0 "
    "interventions, seed_9104 named against 9303): every walk-up's front five merged meshes and no storey instance, "
    "lightmap users 3,175 -> 3,153, 0 of 32 fields moved on any candidate. Priced against 9303 at 53 headings: draws "
    "-3.7 a heading on the mean and -24 at the most, none gained, p95 inside a 0.11 ms floor, memory flat. Against "
    "9302, which had no fire escape, read across the two prices (9303, measured in both, reads the same draws at "
    "every heading; `draws_across_prices.py`): +2 at the worst heading and -0.4 on the mean, where unmerged it was "
    "+26 and +3.3. Found attributing the package: 289 of its 612 GLBs are named by no scene (roadmap 249).\n")

ITEM_249 = (
    "\n*STATUS: OPEN 2026-10-14 -- FOUND ATTRIBUTING COLD RUN 9304'S PACKAGE. Of urban_row_001's 612 GLBs, 289 -- "
    "9.2 MB with their import files -- are named by no scene or resource, and 315 of the light bake's 632 model "
    "imports are files no scene names, mostly the modules Level Factory merged the Empties from. Not yet traced: "
    "what else, if anything, loads them.*\n"
    "\n**249. A package ships the module GLBs its Empties were merged from.** Found attributing cold run 9304's "
    "package against 9303's (`docs/findings/fire_escape/unreferenced_glbs.py`, `unreferenced_glbs_9304.out.txt`). "
    "`merge_empties.gd` folds an Empty's sided slots into `lot/<id>/merged/<side>_<n>.res` and removes the slot "
    "children that instanced the kit's module GLBs; the GLBs stay in `lot/<id>/art/zoo/`, and the light bake still "
    "sets each to Static Lightmaps and unwraps it at import. **Measured on 9304's package:** 612 GLBs, 323 named by a "
    "`.tscn` or `.tres`; 289 named by none, 9,203,456 bytes with their `.import` and `.unwrap_cache` -- 23 to 33 in "
    "each of the eleven standing Empties, 2 in `assets/` and 1 in `cover/`; `light_bake.json` lists 632 baked "
    "imports, 315 of them files no scene names. A module checked by name, gs_midrise_c's "
    "`doorway_delco_1997_01_w120_mbrick_orange_egreen_o5519e7.glb`, appears only in `light_bake.json` and "
    "`portable_resource_manifest.json`. **Named by no scene is not unused:** the responder cruiser under `cover/` is "
    "shipped for the gameplay layer to spawn by path, by design (roadmap 212), and `assets/lot.glb` and "
    "`assets/shell.glb` are not yet attributed. **Why it matters:** every export imports them (the editor's 71 s), a "
    "game exporting the package's project would carry them, and a consumer opening it imports them again. **WHAT "
    "WOULD CLOSE IT:** the export leaves out, or never marks for the bake, a module only merged slots instanced, every "
    "file it leaves out attributed and every file a script or the gameplay layer loads kept, priced by the editor's "
    "import time and the package's size against the run before.\n")


def _span(text, number):
    h = text.find("\n\n**%d. " % number)
    assert h > 0, ("no item", number)
    s = text.rfind("\n\n*STATUS:", 0, h)
    e = text.find("\n\n*STATUS:", h)
    return s, h, (e if e > 0 else len(text))


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**249. " not in text, "already applied"
    for old in (S156_OLD, B156_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    s, h, e = _span(text, 156)
    assert s < text.find(S156_OLD) < h, "156's status is not where it was read"
    assert h < text.find(B156_ANCHOR) < e, "156's body anchor is not in 156"
    assert text.endswith("every other shell's dressing unchanged or each change attributed.\n"), \
        "the roadmap does not end where it was read"
    for block in (S156_NEW, B156_NEW, ITEM_249):
        for line in block.splitlines():
            assert not re.match(r"\*\*\d+\.", line) or line.startswith("**249. "), \
                ("a body line would parse as an item", line[:40])
    text = text.replace(S156_OLD, S156_NEW).replace(B156_ANCHOR, B156_NEW) + ITEM_249
    for number, head in ((156, "*STATUS: NARROWED 2026-10-14 -- A FIRE ESCAPE STANDS"),
                         (248, "*STATUS: OPEN 2026-10-14 -- FOUND BY THE FIRE ESCAPE'S COLD RUN"),
                         (249, "*STATUS: OPEN 2026-10-14 -- FOUND ATTRIBUTING COLD RUN 9304'S PACKAGE")):
        s, h, e = _span(text, number)
        assert text[s + 2:].startswith(head), (number, "status does not adjoin its heading", text[s + 2:s + 80])
        assert "\n\n" not in text[s + 2:h], (number, "a blank line inside the status")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 156 merged, 249 filed; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
