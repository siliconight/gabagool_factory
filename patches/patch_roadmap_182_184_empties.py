"""PIPELINE_ROADMAP.md: file items 182-184, all found on the Empties 2026-10-05.

  182  the Empties cost 816 draws / 1.87 ms at the median view; merge each side
  183  an Empty's front door is open to a ray
  184  a gutter on every party wall, lit against an unlit wall

Appends after item 181's last line, each status line directly above its
heading; the generated index is left to `tools/roadmap_status.py --write`.

    python patch_roadmap_182_184_empties.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

TAIL = '''**WHAT WOULD CLOSE IT.** Either a planner that writes the key -- for the
enterable buildings whose flat roofs a player sees from a higher roof or a
ladder -- with the result priced A/B/A2 like any look; or the branch and the
module removed. A path nothing reaches reads as a capability.
'''

ITEMS = '''
*STATUS: OPEN 2026-10-05 -- MEASURED, NOT STARTED. Hiding all 25 Empties saves 816 draws / 1.87 ms at the median view, up to 3,951 / 11.6 ms (9161, interleaved with cool-downs, control 0.05 ms). A prototype merging each Empty's kit modules one mesh a side per material saves 686 / 0.88 ms, up to 3,015 / 6.9 ms (9162, control 0.026 ms).*

**182. The Empties cost 816 draws and 1.87 ms at the median view: merge each
one's sides.** The walker, 2026-10-04: finish the Empties, "then
optimise them for runtime". `docs/findings/empties_merge_proto_9162/` is
the whole of what is known; this is its summary.

**WHAT AN EMPTY SUBMITS.** About 88 kit module instances, one per Deli
Counter slot.
  * A three-storey house is 95 MeshInstance3D and 161 surfaces, in 8
    materials.
  * Its base's 94 meshes are `-convcolonly` and never draw.
  * Its covers are already one mesh a side per material (180).

**THE PROTOTYPE.** `patches/lf_empties/merge_empties_proto.gd`, on an
imported copy of 9162's package.
  * Groups every module surface by (side, material); 95 meshes become 13.
  * Keeps every collider.
  * Renders the same street but for the baked light it no longer reaches.

**WHERE THE REAL ONE BELONGS.** Level Factory's export: after import, before
the light bake.
  * The composer's own transforms (`_fit_rotation`, a 4 mm sink) are not in
    `slots.json`.
  * The imported materials already carry the worldskin's projection and the
    panes' lit faces.
  * Lightmap users are node paths, so a merged mesh must be unwrapped and
    exist before the bake.
  * Deli Counter's compose gates run before any of this.

**WHAT IT MUST CARRY.**
  * `bake_occluders.gd` classifies occluders by module file name, and
    Empties supply 1,002 of the package's 1,316.
  * The doorways' `metadata/interactive_id` (none of them in
    `interactives.json`).
  * The lights each merged side now reaches (180's re-check list).

**THE RULE IT RUNS INTO.** CLAUDE.md says to merge a module's parts and
"never across modules". Its reason is the culling unit: merge the largest
thing that enters and leaves view as one. One side of one sealed Empty is
that thing, as one side of a building's covers was for 180. Merging across
houses stays wrong.

*STATUS: OPEN 2026-10-05 -- MEASURED, NOT STARTED. On gs_empty_rowhome_f in cold run 9162's walk copy, rays at 1.0 and 2.0 m pass 10 m into the shell through the front door (x 1.2-1.8) and stop at the face everywhere else; a 0.4 m capsule stops in the reveal.*

**183. An Empty's front door is open to a ray.**
`patches/lf_empties/door_collision_probe.gd`.
  * **A body cannot get in.** The doorway's jamb colliders leave 0.7 m, and
    the walk capsule is 0.8 m across.
  * **A shot, a thrown object or a line-of-sight test can.** Each passes
    through the door into the hollow shell and meets nothing.
  * A facade window is shut by a pane collider in the base
    (`ext_col_*_open*_pane`); a facade doorway has only its lintel there.
  * The fix is Deli Counter's: a facade doorway gets a leaf collider, as
    its window gets a pane.

*STATUS: OPEN 2026-10-05 -- FOUND, CAUSE NOT ESTABLISHED. Two dashed lines in the sky over gs_empty_rowhome_l's roof in 9160's and 9161's street frames; the gutter Patina hangs on the neighbouring house's party wall projects along their slope, about 30 px below them.*

**184. A gutter on every party wall, and lit covers against an unlit wall.**
Patina's `roofline_slots` gutters every top-storey exterior wall, party
walls included.
  * Between two houses of one height the party-wall gutter is hidden.
  * Where a three-storey house stands beside a two-storey one, its
    party-wall gutter and roof edge are exposed. Against an unlit wall at
    night, they read as lines floating in the sky
    (`docs/findings/empties_roof_9161/lines_zoom_916*.png`).
  * `patches/zoo_roof_fixtures/project_antennas.py`'s camera model put
    every antenna within a few pixels of where the frame drew it. It puts
    `f`'s west party-wall gutter on the lines' slope, about 30 px lower.
    The roof's edge strip along the same wall is the untested candidate for
    the rest.
  * A rowhouse roof drains front and back, and the downspouts already keep
    to faces with openings. A party wall wants a coping, not a gutter.
'''


def main():
    s = ROADMAP.read_text(encoding="utf-8")
    assert "\r" not in s
    assert s.count(TAIL) == 1 and s.endswith(TAIL), "item 181's last line is not the file's end"
    assert "**182." not in s
    ROADMAP.write_text(s + ITEMS, encoding="utf-8", newline="\n")
    print("filed roadmap items 182-184")


if __name__ == "__main__":
    main()
