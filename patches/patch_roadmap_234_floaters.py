"""Roadmap 234: floaters, a Zoo core concept -- details laid on a surface, not cut into it.

Appends item 234 at the end of the roadmap, its status adjoining its heading. Run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_234_floaters.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
TAIL = ("What it must keep: the `LuxEmit_*` markers beside their own hardware (empties, outside the mesh "
        "pool), the lens materials' names (Lux's emissive binder keys on `M_*_Lens`), and each part's "
        "shading (no welding, as `merge.py` keeps it).\n")
ITEM = """
*STATUS: OPEN 2026-10-11 -- filed from the walker's reference, the concept written, not built. The walker asked for "Floaters" as a Zoo core concept: small details made as their own meshes and laid on a surface, origin at the bottom, normals out, snapped aligned to the face, stacked for complex details and bakeable. The concept is staged as a Zoo README section (`patches/zoo_floaters/README_floaters.md`, `patches/patch_zoo_floaters_readme.py`) to land after factory 1.38.0's tags. Owner: Zoo.*

**234. Floaters: details laid on a surface, not cut into it.** The walker's reference, 2026-10-11: a short Blender tutorial (300 frames, kept out of the repo as someone else's video; its node set-up credited to the YouTube channel Penfinity) and the polycount thread "Low poly hard surface modelling - Floaters" (polycount.com/discussion/86536, 2011, pasted by the walker when the site refused a fetch). The tutorial makes a floater read as part of its surface in Cycles with a shader -- back faces transparent, mixing the Geometry and Light Path nodes. **Godot's GL Compatibility renderer has no such pass, so Zoo's translation is a rule, not a shader:** a SOLID floater (a knob, a bezel, a ring with walls) rests on its host with an open bottom and only a skirt below the host plane (`FLOATER_SKIRT`, past the coplanar probe's 2 mm window; Zoo's `flat_forms.JOIN` is 4 mm), so there is no hovering gap to show at grazing angles or in its shadow and almost nothing buried to darken or waste lightmap texels -- the thread's two warnings (a floater pushed deep into its host darkens under vertex lighting and wastes texels, Mark Dygert and SpeCter; welded is cleaner for lightmaps, Xendance); a FLAT floater (art, a label, a printed ring) is one-sided and hovers by a known amount (`FLOATER_PROUD`, at least 3 mm), because two near-parallel faces fight from sqrt(gap x 838871) m on Godot's default depth buffer (`tests/test_coincident_faces.py` `fight_distance_m`): 41 m at 2 mm, 50 m at 3 mm, 65 m at Zoo's `ART_PROUD` 5 mm. Flatter detail is texture. **Zoo already builds floaters without the name:** `flat_forms.JOIN` and `ART_PROUD`, `crt_forms.STAND_BURY` (6 mm), `dartboard_forms.RING_PROUD` and `counter_register.PROUD` (3 mm) -- five species, five numbers. **The work:** (1) the concept in Zoo's README (staged); (2) `geometry.add_floater(bm, point, normal, build, spin, skirt)` and `add_flat_floater(bm, point, normal, w, h, proud)` with the two constants derived from the probe's window and `fight_distance_m`, a test that fails without them, the census the judge; (3) a first species detailed with it, priced and framed -- the tutorial's own example is a CRT's front panel, and roadmap 181's roof props (an HVAC unit's grilles and panels, an exhaust fan's hood band) are the next hard-surface props to ship; (4) floaters baked into a normal map for detail too flat to model and for a distant LOD -- a channel Zoo does not ship, priced (texture memory per module) before it is built.
"""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "\n**234. " not in text, "already applied"
    assert text.endswith(TAIL), ("the roadmap does not end where this patch read it", text[-160:])
    text = text + ITEM
    assert text.endswith("\n")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: item 234 opened; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
