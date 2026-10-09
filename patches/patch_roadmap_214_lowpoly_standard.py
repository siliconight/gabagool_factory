"""Roadmap 214 OPEN: Zoo's minting meets the walker's modern low-poly standard.

Appended after item 213, anchored on 213's last line, which must be the end
of the file; refuses otherwise.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

TAIL = (
    "- **Not settled.** Whose light 9204's dim wash was: the 8x copy kept 9204's bake and still matches 9205 on "
    "the stage top to 0.1 codes, and the stage lip's neon is the candidate, untested. And the resource is still "
    "named \"Stage Light (baked)\" on a live rig: the loader names every club rig so, and `lux_lighting.gd` ranks "
    "shadows by those names.\n"
)

ITEM = (
    "\n"
    "*STATUS: OPEN 2026-10-08 -- filed, not adopted. The walker's production standard for Delco Dangerous, "
    "`docs/reference/MODERN_LOW_POLY_ASSET_STANDARD.md` (the original `.docx` beside it), is the brief for "
    "\"a human artist or procedural asset tool\"; `docs/reference/MODERN_LOW_POLY_IN_ZOO.md` maps it onto Zoo "
    "1.86.0's minting, measured: what Zoo already does, seven gaps, and where a measured house rule decides. "
    "Next: the asset record's missing fields, a budget class per genome, and the standard's A/B/C review on its "
    "three approval assets.*\n"
    "\n"
    "**214. Zoo's minting meets the modern low-poly standard.** The walker, 2026-10-08, with "
    "`Blender_Modern_Low_Poly_Asset_Standard.docx`: \"this should go with Zoo and help future minting?\"\n"
    "\n"
    "**WHAT THE STANDARD IS.** Seventeen sections, from budgets and viewing distance through construction, "
    "bevels and normals, baking, trim sheets, materials and wear, lighting, LODs and collision, export, three "
    "worked examples (a deli cabinet, a payphone, a storefront), proof of improvement and cost, and a "
    "handoff record with acceptance checks. Its default target is \"modernized low poly: small bevels, "
    "controlled normals, restrained materials, and stable lighting\". It calls its own numbers \"proposed "
    "starting points\", not measured limits.\n"
    "\n"
    "**WHAT ZOO ALREADY DOES** (the mapping has each with its source):\n"
    "- **Colour and surfaces.** One material per part family, with colour in vertex colour, merged at export "
    "by family and material.\n"
    "- **Bevels and normals.** Style bevels applied through one-segment `bevel_edges` in most recipes, and "
    "smooth-by-angle shading at 50 degrees.\n"
    "- **Mesh and placement.** No subdivision, primitive collision, and enforced centre pivots.\n"
    "- **Checks and record.** A coincident-face census of every species, wear placed by cause, and a "
    "`meta.json` validation record.\n"
    "\n"
    "**THE GAPS, as the work** (from `MODERN_LOW_POLY_IN_ZOO.md`):\n"
    "- **The asset record.** `meta.json` lacks viewing conditions, the features the construction serves, "
    "exported vertices per LOD, the surface count, texture size and texel density, and review evidence. The "
    "standard's tool instructions: \"Emit the asset record with the mesh.\"\n"
    "- **A budget class per genome** (clutter, medium, hero, assembly).\n"
    "  - Across 122 species the median budget is 900.\n"
    "  - 7 are over the standard's 8,000 hero range: mostly whole assemblies (snack_gondola 22,000, "
    "cubicle_bank 24,000), and the getaway van at 16,000.\n"
    "  - A named class makes an exception stated; the standard rejects \"silent budget overruns\". CLAUDE.md "
    "calls a triangle budget a regression detector, not a frame cost.\n"
    "- **The A/B/C review** (basic boxes; construction; bevels and normals) under identical neutral light on "
    "the three approval assets: Zoo's `deli_case` and `counter`, `payphone` (roadmap 210) and Deli Counter's "
    "storefront. It has never been run.\n"
    "- **Priced trials, not adoptions.** Weighted normals, and baked normal maps on selected close props. "
    "Each is a look, so each is priced first (CLAUDE.md, performance over look).\n"
    "- **LODs.** `bpylayer/lods.py`'s Decimate copies are off, and stay so unless a measurement says a level "
    "is triangle-bound; here submissions dominate.\n"
    "- **Trim sheets** are Pixelcoat's and Patina's, not Zoo's. The standard's deli and convenience-store trim "
    "family is their brief.\n"
    "\n"
    "**FOUND WHILE MAPPING.** `simple_car` skips its style bevel on purpose. It models a car's chamfers into "
    "its sections, because bevelling every edge took 12-triangle boxes to 44. So its genome's style bevels, "
    "0.01-0.014 m, do nothing: a knob with no effect, which CLAUDE.md calls a defect. Small; recorded here, "
    "not fixed.\n"
)


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    if text.count(TAIL) != 1 or not text.endswith(TAIL):
        sys.exit("refusing: item 213's last line is not the end of the file")
    if "\n**214. " in text:
        sys.exit("refusing: an item 214 already exists")
    ROADMAP.write_bytes((text + ITEM).encode("utf-8"))
    print("roadmap 214 appended; %d -> %d bytes" % (len(data), len((text + ITEM).encode("utf-8"))))


if __name__ == "__main__":
    main()
