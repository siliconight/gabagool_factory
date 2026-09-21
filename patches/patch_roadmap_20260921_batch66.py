"""Roadmap batch 66: six more cold runs, the card shop walked, and the day
the draw-call budget was measured.

Anchored: every anchor must match exactly once or this refuses to write.
Run from the factory root, then `python tools\\roadmap_status.py --write`.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"

# --- 1. item 17: six more runs ----------------------------------------------

A17 = """*STATUS: NARROWED 2026-09-16 -- FOUR MORE ZEROS AND THREE MORE REFUSALS IN"""

B17 = """*STATUS: NARROWED 2026-09-21 -- FOUR MORE ZEROS, ONE REFUSAL AND ONE
ABANDONED RUN IN 9061-9066, AND THE TWO THAT PRODUCED NO PACKAGE BOTH PAID
FOR THEMSELVES. Journals in `docs/cold_runs/cold_9061..9066/`.
- **9061 and 9062: zeros.** 9061 drew the first generated card shop; 9062 the
same brief one stack later, and its walk is where the whole performance
campaign started (item 166).
- **9063: ABANDONED before any stage**, and recorded as an intervention
because a note was written under a running clock. `doctor` read FAIL --
zoo had crossed 1.0.0 and Level Factory's contract check calls a major-number
difference INCOMPATIBLE against a pin of 0.30.2. Setup is a prerequisite, not
the measurement, so the run was ended rather than measured through. The pin
was then certified against a passing real-tool smoke (9 of 10 ran) and the
run re-begun.
- **9064: REFUSED at export**, 0 interventions, on
`ZOO_FIXTURES_MARKER_MISMATCH: emitter_markers (18) != fixtures_built (25)`.
The generator was right and the gate was wrong: Zoo 0.94.0 builds club light
hardware that carries no emitter marker ON PURPOSE (`neon` IS its sign,
`back_bar` IS the bar's own bulbs) and writes `markerless_fixtures: 7`
alongside, which LF's v0.30-era check had never heard of. LF 0.97.0 fixed it,
and added a tally against the index's own `placements` array because the
arithmetic invariant alone is a tautology -- Zoo DERIVES markers as
`built - markerless`, so on anything Zoo wrote the sum cannot fail.
- **9065: a zero**, and it caught the next defect by shipping it:
`use_occlusion_culling=true` with ZERO occluders. The bake ran against a
project Godot had never imported -- `_write_import_sidecars` deleted the
`.godot` cache one line before the only export step that has to `load()` a
scene -- so every load failed and the package shipped a 90-byte
`occluders.json` reading `{"error": "cannot load res://site.tscn"}` beside a
flag claiming otherwise. LF 0.98.0 moved the cache drop after the bake and
made the disagreement unrepresentable.
- **9066: a zero, with 301 occluders in the shipped package.** The proof the
walker asked for -- the club brief, unchanged since 9060, carrying work
developed against a card shop.

THE PATTERN WORTH KEEPING: four of these six runs produced a package and two
did not, and the two that did not are the only reason two shipped defects
were caught before a walker met them. A refusal that names itself is the
instrument working. Previously: FOUR MORE ZEROS AND THREE MORE REFUSALS IN"""

# --- 2. item 164: the card shop is built and walked -------------------------

A164 = """*STATUS: OPEN 2026-09-16 -- SPECIFIED FROM THE WALKER'S OWN PHOTOS; THE FIRST
SLICE IS BEING BUILT.*"""

B164 = """*STATUS: NARROWED 2026-09-21 -- THE CARD SHOP IS BUILT, GENERATED AND
WALKED; THE CONVENIENCE STORE AND ITS FORECOURT ARE UNTOUCHED. Shipped
across Zoo 0.95.0-1.0.0 (display case, pack wall, pennant row, folding table
and chair, the invented card brands with a denylist test, posters, banners,
ceiling hangers, aisle signs, printed playmats, and a cash register whose
green display reads as a price at 6 m), Pixelcoat 0.44.0-0.45.0 (wood
panelling, slatwall, tournament carpet, and the kinds mapped into the themes
levels actually run on), and Deli Counter 0.139.0-0.141.2 (the preset, the
room kind, a 1.25 m staff aisle derived rather than chosen, product to the
ceiling, islands in the open floor, and the flat art placed). Cold runs 9061
and 9062 drew it; the walker walked both.

WHAT THE WALKS FOUND, all four by a person looking at a screen and none by an
instrument (item 18): a white untextured corner that was 21 surfaces asking
for a kind `delco_1997` did not map; stairs in the greybox fallback yellow
(item 144, a remedy that had shipped in 0.72.0 and could never fire because
it asked a building for a `concrete` finish a card shop does not own); a room
that read as a hall because caps set against a measured reference were
mistaken for a budget; and the chugging that became item 166.

WHAT REMAINS: the convenience store and the pump forecourt, with the two
measured defects this item already names (3.0 m end aisles against a
4.3-4.8 m car; two canopy columns in the outer lanes' swept path). The
walker settled its name on 2026-09-16: FLAPPHAS, on the fascia, the pump
price signs, the cups, the bags and the wrappers.*"""

# --- 3. item 165: the budget was measured, and it was the wrong quantity ----

A165 = """*STATUS: ANALYSIS 2026-09-16 -- A STANDING CONSTRAINT ON EVERY LOOK THIS
PIPELINE SHIPS, NOT A DEFECT.*"""

B165 = """*STATUS: ANALYSIS 2026-09-21 -- STILL A STANDING CONSTRAINT, AND NOW A
MEASURED ONE. The rule as written was right and the QUANTITY it was being
applied to was wrong: frame time tracks DRAW CALLS and barely notices
triangles. Measured on cold run 9062's package -- 1,730 draw calls read
9.49 ms with 13% of frames over 16.7 ms, 6,376 read 25.59 ms with 99.6%
over, while the primitive count sat at 1.4M the whole way and never moved.
That is written into `CLAUDE.md` as its own hard-rule subsection, with the
four rules it implies in the order to reach for them, and with the
admission that a room was being held to 25,008 triangles against a borrowed
24,000 ceiling while 1.4M triangles were on screen. Zoo's per-species
triangle budgets are REGRESSION DETECTORS, not frame costs. The campaign
that followed is item 166.*"""

# --- 4. two new items -------------------------------------------------------

TAIL = """**WHAT THIS IS NOT:** a reason to narrow a look quietly. An undocumented
narrowing is not a performance decision."""

NEW = TAIL + """


*STATUS: NARROWED 2026-09-21 -- SUBMISSION COST AND MEMORY ARE FIXED AND
PROVEN ON A COLD RUN; THE WARM-UP'S LOAD COST IS THE OPEN HALF.*

**166. A generated level chugged, and everything this repo believed about why
was wrong.** The walker, walking cold run 9062's card shop: "the performance
of the walk seems to be chugging... the framerate is dropping and struggling
to stay consistent and smooth". Four measurements later the cause was neither
of the two things anyone had budgeted for.

**What it was not.** Not triangles (item 165). Not lights: disabling all 12
shadow casters and capping `max_renderable_lights` at 8 both made it WORSE
and neither moved the primitive count. Not the average: standing still
measured 96 fps, and the first instrument to report a "cause" -- Godot's own
GPU timer through `look_shots` -- gave figures that moved the wrong way when
cost was removed (one station read 0.00 ms at six frames and 170.18 ms at
ninety), which is a measurement of the instrument, not the level.

**What it was, in two parts.** (1) SUBMISSION COUNT: frame time tracks draw
calls almost linearly, and a Zoo prop shipped one MeshInstance3D per PART --
a pack wall was 1,416 triangles in 118 meshes using 4 materials, a draw call
for every box on every shelf. (2) FIRST-SIGHT COMPILATION: a GL Compatibility
shader program is compiled on first draw and specialised on the LIGHTING
CONTEXT of that draw, so a level stalled for seconds the first time a camera
stood somewhere new.

**What shipped, each with its own control.**

- **Zoo 1.1.0** merges a module's parts by material -- 118 meshes to 4,
  triangles identical, the same shell `strip_club_a02` going 687 to 355
  meshes across 78 modules in a building nobody had touched.
- **LF 0.96.0/0.98.0** bakes occluders from the package's own solid modules.
  Interiors fell 74-79% in draw calls; the control that makes it evidence is
  the same package with the culling flag flipped off, which read draw calls
  IDENTICAL to the broken build at all six stations, to the call.
- **Zoo 1.2.0 + LF 0.99.0** stop embedding the same pack texture in every GLB.
  Godot does NOT dedupe identical embedded images -- twenty GLBs with
  identical bytes cost the same as twenty with different bytes, to the byte --
  so 961 embedded images holding 1.41 MiB of unique pixels were 1,841 resident
  textures. After: 157 textures, video memory 348.9 MB to 63.1 MB, package
  45.4 to 23.5 MiB.
- **LF 0.100.0** warms the shader programs at load, standing where a player
  will stand. Lap 1's worst frame 9,283 ms to 143 ms.

**The end-to-end number, on a brief nobody tuned:** walking cold run 9066's
club package, frames missing 60 fps went from 44.3% (9062, before any of it)
to 0.0% of 4,972 on a warm lap, with draw calls per leg 1,730-6,376 down to
380-2,050.

**WHAT IS STILL OPEN:** the warm-up costs 48.2 s on a machine whose driver
cache has never seen the content and 4.8 s on every launch after -- roughly
conserved from the ~30 s the package used to spend compiling in play, but a
real trade, and the spacing has never been priced. Every figure here is one
GPU (RTX 2060, NVIDIA 616.56) on GL Compatibility; the shapes should hold on
other hardware and the magnitudes will not.


*STATUS: ANALYSIS 2026-09-21 -- A CAPABILITY GAP WITH A MEASURED CEILING, NOT
A DEFECT.*

**167. Per-instance variation has no home in this pipeline, and a GLB cannot
give it one.** `pennant_row` shipped 89 meshes and 13 materials differing in
nothing but `baseColorFactor` -- colour variation expressed as material
variation, which `CLAUDE.md`'s submission rules name as the cheapest mistake
to make by accident. The obvious fix is per-instance colour, and it was
refused by the engine.

**Measured 2026-09-21, four ways:** Godot 4.7 does not implement
`EXT_mesh_gpu_instancing` -- the only way a `.glb` can express instancing --
and discards it SILENTLY, keeping the node's mesh and dropping every instance
after the first. The exported GLB declares the extension and holds 3
instances; the runtime import reads one MeshInstance3D with 3 verts and 1
triangle; the editor agrees; and the string does not occur anywhere in the
engine binary, while 267 other extension names do. On a 44-pennant row that is
43 pennants deleted from a file that still validates and still censuses at
892 triangles. Zoo 1.1.1 forbids any Zoo GLB from claiming the extension, for
that reason.

**Where the capability actually lives:** not in Zoo and not in Lot.
`level_factory/packages/exporting/dressing_scene.py` writes MultiMesh as
`.tscn` text over meshes extracted from Zoo's GLBs -- that is the "4,107
instances in 4 draw calls" this repo keeps citing. It has no `use_colors`, so
per-instance COLOUR does not exist there either; both halves would have to be
built.

**Priced, and deliberately not taken.** A pennant row is ~12 draw calls after
Zoo 1.1.0's merge, about 40 in a card shop, against 5,454 with a street in
view. The walker was given three options and chose MultiMesh over folding the
tint into the existing wear colour channel, which would have saved one further
draw call per row at the cost of an art capability forever. The work waits for
a customer worth it -- all the repeated interior stock at once, not one strip
of felt.*"""


def _apply(text, anchor, replacement, label):
    n = text.count(anchor)
    if n != 1:
        raise SystemExit(f"REFUSED: anchor {label} matched {n} times, expected 1")
    return text.replace(anchor, replacement)


def main():
    data = ROADMAP.read_bytes()
    if data.count(b"\r\n"):
        raise SystemExit("REFUSED: roadmap is LF; CRLF found")
    text = data.decode("utf-8")
    before = len(data)
    text = _apply(text, A17, B17, "item 17")
    text = _apply(text, A164, B164, "item 164")
    text = _apply(text, A165, B165, "item 165")
    text = _apply(text, TAIL, NEW, "tail / items 166-167")
    ROADMAP.write_bytes(text.encode("utf-8"))
    print(f"roadmap {before} -> {len(ROADMAP.read_bytes())} bytes")


if __name__ == "__main__":
    main()
