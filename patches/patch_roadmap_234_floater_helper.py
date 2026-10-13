"""Roadmap 234, 2026-10-13: the floater helper built -- Zoo 1.106.0 (`patches/patch_zoo_floaters.py`). 234's status
rewritten OPEN -> NARROWED and one paragraph appended after its body, before 235's status. The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_234_floater_helper.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S234_OLD = ("*STATUS: OPEN 2026-10-11 -- filed from the walker's reference, the concept written, not built. The walker "
            "asked for \"Floaters\" as a Zoo core concept: small details made as their own meshes and laid on a "
            "surface, origin at the bottom, normals out, snapped aligned to the face, stacked for complex details and "
            "bakeable. The concept landed as a Zoo README section on 2026-10-11 (Zoo f288f7a, "
            "`patches/patch_zoo_floaters_readme.py`); the helper it describes, `geometry.add_floater` and "
            "`add_flat_floater`, is not built. Owner: Zoo.*")
S234_NEW = ("*STATUS: NARROWED 2026-10-13 -- the helper built: Zoo 1.106.0's `core.floaters` (pure: `FLOATER_SKIRT` 4 mm, "
            "past the coplanar census's 2 mm window; `FLOATER_PROUD` 3 mm, which fights only beyond 50 m on Godot's "
            "default depth buffer; the frame that carries a floater onto its host) and "
            "`bpylayer.geometry.add_floater` / `add_flat_floater`, 54 checks passing in Blender 5.1.1 "
            "(`tests/test_floaters.py`). The walker asked for \"Floaters\" as a Zoo core concept, written as a README "
            "section on 2026-10-11. Left: no species uses the helper -- each chose its own number before the rule had "
            "a name (JOIN 4 and 6 mm, PROUD 3 and 5 mm), and moving one is a mesh change to price and census; baking "
            "floaters into a normal map, which needs a channel Zoo does not ship. Owner: Zoo.*")

BODY_234 = """

**THE HELPER, BUILT, 2026-10-13** (Zoo 1.106.0; `patches/patch_zoo_floaters.py`). **`core.floaters`**, pure Python so the suite checks it without Blender: `FLOATER_SKIRT` 4 mm -- a solid floater rests with only a skirt below its host, past the coplanar census's window (`PROBE_WINDOW`, the census's own `PROBE_TOL`, 2 mm), Zoo's JOIN; `FLOATER_PROUD` 3 mm -- a flat floater hovers one-sided, and on Godot's default 24-bit depth buffer (near 0.05, far 4000) a 3 mm gap fights only beyond 50 m (`tests/test_coincident_faces.fight_distance_m`); `basis` and `frame`, a right-handed frame whose z is the host's normal, turned about it; `solid_frame`, lowered by the skirt; `flat_quad`, wound to face along the normal; a zero normal, a skirt out of the host or a flat floater not off it refuses. **`bpylayer.geometry.add_floater(bm, point, normal, build, spin, skirt)`** carries a floater `build(bm)` made in its own frame (Z up, its base at z = 0) onto its host; **`add_flat_floater(bm, point, normal, w, h, spin, proud)`** lays the quad, gaining `spin` over the README's first sketch so a quad's width can lie along its face. **Measured:** `tests/test_floaters.py` -- the numbers against the census's own, the frame on eleven normals and five spins, a solid floater's points at their height less the skirt, a flat floater proud and facing out, the refusals and determinism -- 48 pure checks, and 6 in Blender building a knob and a quad on three normals each; all 54 pass under Blender 5.1.1, and the file fails to collect on 1.105.0. Zoo's suite 4,614 passed, 455 skipped. **No build moved:** no species calls either helper -- each built its floaters before the rule had a name, with its own number, and adopting the rule species by species is a change to each one's mesh, priced and censused as any other."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**THE HELPER, BUILT, 2026-10-13**" not in text, "already applied"
    assert text.count(S234_OLD) == 1, "234's status not found once"
    text = text.replace(S234_OLD, S234_NEW)
    h = text.find("\n\n**234. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and S234_NEW in text[s:h], "234's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    nh = re.search(r"\n\n\*\*(\d+)\. ", text[nxt:])
    assert nxt > h and nh and nh.group(1) == "235" \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "235 does not follow 234"
    text = text[:nxt] + BODY_234 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 234: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
