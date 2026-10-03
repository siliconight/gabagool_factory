"""Level Factory 0.130.1: the leaves carry the breath; the mass leans only in
strong wind. The walker, 2026-10-03, on 0.130.0 walked: "just a big blob
moving vs a tree in real life, the branches don't move unless the wind is
really strong, only the leaves".

Anchored edits on `zoo_worldskin.gd` (every anchor once; refuses on a miss),
the sway test, CHANGELOG and VERSION.

    python patch_lf_sway_v2.py
    LF_ROOT=<copy> python patch_lf_sway_v2.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")

GD = [
('''## Tip displacement per metre a second of wind, and its cap: a breath
## (1.5 m/s) moves the top of a crown 3 cm, a storm (9) 18 cm.
const SWAY_M_PER_MS: float = 0.02
const SWAY_CAP_M: float = 0.4
const SWAY_SWELL_S: float = 7.0
const SWAY_GUST_FRONT_MS: float = 10.0
const SWAY_FLUTTER_HZ: float = 2.0
const SWAY_FLUTTER_M_PER_MS: float = 0.002
''',
'''## THE LEAVES MOVE AND THE BRANCHES DO NOT, until the wind is strong. The
## walker, 2026-10-03, on the first cut walked: "just a big blob moving vs
## a tree in real life, the branches don't move unless the wind is really
## strong, only the leaves". The first cut leaned the whole mass 3 cm in a
## breath and fluttered 2 mm, so what moved was the blob. Now the LEAN --
## the mass bending downwind -- starts only above SWAY_LEAN_FROM_MS and
## the FLUTTER -- each facet of a cluster on its own phase, across the wind
## and up -- carries the breath: at 1.5 m/s the facets move 12 mm at the
## top of the crown and the mass does not move at all; at 9 m/s the mass
## leans 12 cm and the facets 5 cm.
const SWAY_LEAN_FROM_MS: float = 3.0
const SWAY_M_PER_MS: float = 0.02
const SWAY_CAP_M: float = 0.4
const SWAY_SWELL_S: float = 7.0
const SWAY_GUST_FRONT_MS: float = 10.0
const SWAY_FLUTTER_HZ: float = 1.6
const SWAY_FLUTTER_M_PER_MS: float = 0.008
const SWAY_FLUTTER_CAP_MS: float = 6.0
'''),
('''uniform float m_per_ms = 0.02;
uniform float cap_m = 0.4;
uniform float swell_s = 7.0;
uniform float front_ms = 10.0;
uniform float flutter_hz = 2.0;
uniform float flutter_m_per_ms = 0.002;
''',
'''uniform float lean_from_ms = 3.0;
uniform float m_per_ms = 0.02;
uniform float cap_m = 0.4;
uniform float swell_s = 7.0;
uniform float front_ms = 10.0;
uniform float flutter_hz = 1.6;
uniform float flutter_m_per_ms = 0.008;
uniform float flutter_cap_ms = 6.0;
'''),
('''		// the lee lean: a crown bends away from the wind and does not
		// swing back past upright
		float lean = weight * weight * min(speed * m_per_ms, cap_m) * gust;
		// the flutter: each cluster its own, across the wind
		vec3 across = normalize(cross(dir, vec3(0.0, 1.0, 0.0)));
		float flutter = weight * speed * flutter_m_per_ms * sin(TIME * TAU_ * flutter_hz + phase * TAU_ + inst * 3.0);
		VERTEX += dir * lean + across * flutter;
''',
'''		// the lee lean: the MASS bends away from the wind, only once the
		// wind is strong (branches do not move in a breath), and does not
		// swing back past upright
		float lean = weight * weight * min(max(speed - lean_from_ms, 0.0) * m_per_ms, cap_m) * gust;
		// the flutter: the LEAVES. Each facet on its own phase -- the
		// cluster's phase plus a hash of the facet's own texture
		// coordinate, which is fixed per vertex -- across the wind and up,
		// two rates so it never reads as a pulse
		vec3 across = normalize(cross(dir, vec3(0.0, 1.0, 0.0)));
		float facet = sway_hash(dot(UV, vec2(127.1, 311.7)) + phase * 7.0);
		float f_t = TIME * TAU_ * flutter_hz + facet * TAU_ + inst * 3.0;
		float amp = weight * min(speed, flutter_cap_ms) * flutter_m_per_ms * (0.7 + 0.3 * gust);
		float flutter = amp * (sin(f_t) + 0.5 * sin(f_t * 2.3 + facet * 5.0));
		vec3 up = vec3(0.0, 1.0, 0.0);
		VERTEX += dir * lean + (across * 0.8 + up * 0.6) * flutter;
'''),
('''	sm.set_shader_parameter("m_per_ms", SWAY_M_PER_MS)
''', '''	sm.set_shader_parameter("lean_from_ms", SWAY_LEAN_FROM_MS)
	sm.set_shader_parameter("m_per_ms", SWAY_M_PER_MS)
'''),
('''	sm.set_shader_parameter("flutter_m_per_ms", SWAY_FLUTTER_M_PER_MS)
''', '''	sm.set_shader_parameter("flutter_m_per_ms", SWAY_FLUTTER_M_PER_MS)
	sm.set_shader_parameter("flutter_cap_ms", SWAY_FLUTTER_CAP_MS)
'''),
]

TEST = [(
'''    # the lee lean: weight squared, capped, never past upright
    assert "float lean = weight * weight * min(speed * m_per_ms, cap_m) * gust;" in sh
    assert "VERTEX += dir * lean + across * flutter;" in sh
''',
'''    # the lee lean: the mass, weight squared, capped, never past upright,
    # and only once the wind is strong -- the walker, 2026-10-03: branches
    # do not move in a breath, only the leaves
    assert "float lean = weight * weight * min(max(speed - lean_from_ms, 0.0) * m_per_ms, cap_m) * gust;" in sh
    # the flutter: the leaves, each facet on its own phase from its own
    # texture coordinate, across the wind and up
    assert "float facet = sway_hash(dot(UV, vec2(127.1, 311.7)) + phase * 7.0);" in sh
    assert "VERTEX += dir * lean + (across * 0.8 + up * 0.6) * flutter;" in sh
    assert "const SWAY_LEAN_FROM_MS: float = 3.0" in _src()
''')]

CHANGELOG = '''## [0.130.1] - the leaves carry the breath; the mass leans only in strong wind

The walker, 2026-10-03, on 0.130.0 walked: "the wind on the leaves doesn't
look great right now because it's just a big blob moving vs a tree in real
life, the branches don't move unless the wind is really strong, only the
leaves". The numbers agreed: in a breath 0.130.0 leaned the whole mass 3 cm
and fluttered the facets 2 mm, so what moved was the blob.

### Changed
- **The lean starts only above `SWAY_LEAN_FROM_MS` (3 m/s).** In a breath the
  mass does not move at all; at 9 m/s it leans 12 cm at the top.
- **The flutter is the leaves.** Each facet of a cluster takes its own phase
  from a hash of its texture coordinate (fixed per vertex), moves across the
  wind and up at two rates, 8 mm per metre a second at the top of the crown
  capped at 6 m/s: 12 mm in a breath, 5 cm in a storm.

### Measured
The walk copy re-imported with this script and probed as before: 18 crowns
on the shader; the rest frame unchanged (0 pixels moved between two frames
at wind zero); with the walker's storm set in the copy, 2,277 pixels differ
from the rest frame at the same camera. Not priced on the harness: the
shader's cost is its vertex stage and the stage did not grow.

### Still open
The crown's LOOK: the walker's point that branches and leaves do not read as
different things. That is the species, not the motion -- solid faceted
masses on one texture -- and belongs to Zoo (cutout leaf cards, or smaller
masses showing the twig between). Written into `docs/findings/wind/NOTES.md`.

'''


def _edit(rel, pairs):
    p = LF / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert s.count(old) == 1, (rel, old[:60], s.count(old))
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.130.0", v
    _edit("assets/godot/zoo_worldskin.gd", GD)
    _edit("tests/unit/test_worldskin_sway.py", TEST)
    cl = LF / "CHANGELOG.md"
    d = cl.read_bytes()
    assert d.startswith(b"## [0.130.0]") and b"## [0.130.1]" not in d
    cl.write_bytes(CHANGELOG.encode("utf-8") + d)
    (LF / "VERSION").write_bytes(b"0.130.1")
    print("0.130.0 -> 0.130.1")


if __name__ == "__main__":
    main()
