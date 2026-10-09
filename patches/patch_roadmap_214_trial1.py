"""Roadmap 214 NARROWED: trial 1, weighted normals, shipped (Zoo 1.87.0, cold
run 9211). The Zoo mapping says so where it said "No Weighted Normal".

Anchored: 214's status line (by its unique opening, then to its line end),
the body's A.5 line, and the mapping's normals row and gap 4. Each must
match exactly once, or nothing is written.
"""
import pathlib
import sys

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"
MAPPING = ROOT / "docs" / "reference" / "MODERN_LOW_POLY_IN_ZOO.md"

STATUS_HEAD = "*STATUS: OPEN 2026-10-08 -- filed, not adopted. The walker's production standard"
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-09 -- trial 1 shipped: Zoo 1.87.0 weighs every part's corner normals by face "
    "area at export. Every bevelled part at the 50-degree default had shipped as a dome, 28.89 degrees off flat "
    "on all 36 big-face corners of a bevelled crate; weighted, 2.40. Census of 121 species: vertices, triangles, "
    "primitives and bytes identical, big-face corners over 10 degrees 15,114 to 5,498. Priced at 53 station "
    "headings against two controls: no measurable frame or draw cost (median -0.066 and -0.316 ms). Cold run 9211, "
    "0 interventions. The walker, on the frames: \"yeah looks better\". Open: the asset record, a budget class per "
    "genome, the A/B/C review on the three approval assets, and trials 2-4, convex-edge wear next.*"
)

A5 = ("- **A.5 What does not change.** No subdivided mesh at runtime; a normal map is a texture in the part "
      "family's one material; triangles are counted on the game mesh.\n")
TRIAL1 = (
    "\n"
    "**ZOO 1.87.0, DONE: TRIAL 1, WEIGHTED NORMALS (2026-10-09)** (`patches/patch_zoo_weighted_normals.py`; "
    "finding `docs/findings/weighted_normals/`). Look work, the \"good\" gate (item 18): it reduces no "
    "interventions.\n"
    "- **What was wrong.** `shade_by_angle` smooths every fold under 50 degrees, so a one-segment chamfer joins "
    "both faces it touches. The default corner normal weighs a fan's faces by corner angle, so every big-face "
    "corner leaned toward its chamfer: 28.89 degrees on a bevelled crate, the same 28.9 `bm_to_object`'s "
    "docstring measured on a wall panel and called a dome. The walls had kept every edge hard; the props kept the "
    "dome.\n"
    "- **The change.** `core.normals.weighted_corner_normals`, pure Python: each corner's normal is the "
    "area-weighted sum of its fan, the fan being Blender's own split. Applied at export to every visual part, after "
    "everything that moves a vertex; the merge carries corner normals; ingest opts out; `--no-weighted-normals` is "
    "the control. 12 tests, all failing on 1.86.0.\n"
    "- **Found on the way:** 1.86.0's merge dropped an ingested asset's authored normals when two of its parts "
    "shared a material, 8 of 104 kept. 1.87.0 keeps 104 of 104.\n"
    "- **What it does, across the library** (`census.py`):\n"
    "  - 121 of 122 species built (`boots` does not build through the kit path, already recorded);\n"
    "  - vertices, triangles, primitives and bytes identical in 121 of 121;\n"
    "  - 81 species changed; the 40 that did not are faceted on purpose, walls or flat panels;\n"
    "  - big-face corners over 10 degrees, 15,114 to 5,498. canopy_lights, safe_deposit_boxes, pallet_stack, "
    "pool_table, back_bar, stair_rail, payphone and teller_line go to 0.\n"
    "- **A retraction, kept.** The census's first run reported normals flipped by up to 178 degrees. It had "
    "paired the two GLBs' vertices by index, and a card's front and back share a position, so the exporter's "
    "re-ordering read as flips. Paired by triangle corner, the largest move is 40.08 degrees, the figure "
    "`fan_probe.py` reads in the mesh.\n"
    "- **The frames.** Ten species rendered both ways from one build, with a control that reads 0.000. The "
    "payphone, counter, cabinet, pallets and tank read as made things.\n"
    "  - The booth seat's cushions lose an accidental plumpness: rounded geometry is the fix, if wanted.\n"
    "  - The walker: \"yeah looks better\".\n"
    "- **The price** (`price_robust.txt`). Against the mean of two controls, the median frame moved -0.316 and "
    "-0.066 ms, inside the controls' own -0.69 to +0.59. Draw calls are unchanged at the median, and the 8-light "
    "cap is identical.\n"
    "- **In the level** (cold run 9211 against 9210, `docs/cold_runs/cold_9211/NOTES.md`):\n"
    "  - the packages differ in normals, the vertex order that follows them, Godot's lightmap unwrap (119 caches) "
    "and the bake;\n"
    "  - everything else differs in the 9209-9210 control too;\n"
    "  - at night the frames move by 0.2 codes of mean at most.\n"
    "- **The payphone is still the old model.** It has no keypad, coin slot or decals, as the walker noted. Item "
    "210 is its redraw.\n"
)

MAP_ROW_OLD = ("`geometry.shade_by_angle` at 50 degrees on the bmesh. Bevels roll off as highlights; box corners stay "
               "hard. No Weighted Normal. |")
MAP_ROW_NEW = ("`geometry.shade_by_angle` at 50 degrees on the bmesh. Bevels roll off as highlights; box corners stay "
               "hard. Since 1.87.0 the export weighs each part's normals by face area (`core/normals.py`), so a "
               "bevelled face reads flat; before, every bevelled part at 50 degrees was a dome "
               "(`docs/findings/weighted_normals/`). |")
MAP_GAP_OLD = ("**4. Weighted normals** (section 5). Not used. A trial is a look, so it is\n"
               "priced: on/off frames at fixed stations under the three lighting checks.\n"
               "The standard asks for the same comparison in section 14. Addendum A.4 puts\n"
               "it first of four trials: it costs no texture and no triangles.\n")
MAP_GAP_NEW = MAP_GAP_OLD + (
    "- *Shipped, Zoo 1.87.0 (2026-10-09).* Census of 121 species: vertices,\n"
    "  triangles, primitives and bytes identical; big-face corners over 10\n"
    "  degrees 15,114 to 5,498. No measurable frame cost against two controls.\n"
    "  The walker: \"yeah looks better\". `docs/findings/weighted_normals/`.\n"
)


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    if text.count(STATUS_HEAD) != 1:
        sys.exit("refusing: 214's status opening matches %d times" % text.count(STATUS_HEAD))
    i = text.index(STATUS_HEAD)
    j = text.index("\n", i)
    if not text[i:j].endswith(".*"):
        sys.exit("refusing: 214's status line does not end its block on one line")
    text = text[:i] + NEW_STATUS + text[j:]
    if text.count(A5) != 1:
        sys.exit("refusing: the A.5 line matches %d times" % text.count(A5))
    text = text.replace(A5, A5 + TRIAL1)
    mdata = MAPPING.read_bytes()
    if b"\r\n" in mdata:
        sys.exit("refusing: the mapping has CRLF endings")
    mtext = mdata.decode("utf-8")
    for old in (MAP_ROW_OLD, MAP_GAP_OLD):
        if mtext.count(old) != 1:
            sys.exit("refusing: a mapping anchor matches %d times: %r" % (mtext.count(old), old[:50]))
    mtext = mtext.replace(MAP_ROW_OLD, MAP_ROW_NEW).replace(MAP_GAP_OLD, MAP_GAP_NEW)
    ROADMAP.write_bytes(text.encode("utf-8"))
    MAPPING.write_bytes(mtext.encode("utf-8"))
    print("roadmap 214 narrowed; %d -> %d bytes; mapping %d -> %d bytes"
          % (len(data), len(text.encode("utf-8")), len(mdata), len(mtext.encode("utf-8"))))


if __name__ == "__main__":
    main()
