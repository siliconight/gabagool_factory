"""Patina 0.37.0: a sidewalk's debris lies at its kerb and its building line (the factory's roadmap 324).

`surface_dressing.plan` thins a sidewalk's candidates by their distance to the strip's nearer long edge.

Proven: tests/test_debris_edges.py's sidewalk test fails on 0.36.0 (fails_on_old.out.txt); the clone's suite
(suite_clone.out.txt); the slice rebuilt and priced (the factory's docs/findings/slice_look/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'patina'
PINS = {'CHANGELOG.md': '9a9a41092a74a7e9', 'VERSION': '0a1f044c0a93e3f9', 'patina/surface_dressing.py': 'b86094b496cea1e7', 'patina/version.py': 'f6d6da46b7579b51', 'tests/test_debris_edges.py': '1965f59e04a75686'}
EDITS = {'CHANGELOG.md': [('lines 4-5', 'versioning follows [SemVer](https://semver.org/).\n\n', "versioning follows [SemVer](https://semver.org/).\n\n## [0.37.0] - a sidewalk's debris lies at its kerb and its building line\n\nThe factory's roadmap 324. The vertical slice's sidewalks carried the densest dressing on the level -- 1,500 pieces\non 3,315 m2, 45 per 100 m2 -- spread evenly across the walking surface (the factory's `docs/findings/slice_look/`,\nslice 4).\n\n### Changed\n- **`surface_dressing.plan`**: in a `sidewalk` zone a candidate survives with probability `max(STRIP_FLOOR,\n  exp(-d / STRIP_FALLOFF_M))` (0.12, 0.6 m), `d` its distance to the strip's nearer LONG edge -- the kerb or the\n  frontage (`strip_edge_distance`); the short ends, where Lot cut the strip, are not edges. Counted with the open\n  ground's in `cost.thinned_open_ground`. Slice 5: the sidewalks 1,500 -> 469 pieces; within 0.4 m of an edge 18 % ->\n  39 %, the middle band 322 -> 48; priced against slice 4, draws +0. Tests: tests/test_debris_edges.py, the same plan\n  with and without the rule (fails on 0.36.0).\n\n")], 'VERSION': [('lines 1-1', 'Patina 0.36.0', 'Patina 0.37.0')], 'patina/surface_dressing.py': [('lines 376-377', 'GATHER_KINDS = ("wall_base", "sidewalk")\n\n', 'GATHER_KINDS = ("wall_base", "sidewalk")\n#: A SIDEWALK\'S DEBRIS LIES AT ITS TWO EDGES (0.37.0, the factory\'s roadmap 324). The slice\'s sidewalks carried the\n#: densest dressing on the level -- 1,500 pieces on 3,315 m2, 45 per 100 m2 -- spread evenly across the walking\n#: surface (the factory\'s docs/findings/slice_look/, slice 4). On a sidewalk it gathers against the building line and\n#: the kerb and the middle is walked clean. A sidewalk zone is a strip: a candidate survives with a probability that\n#: falls off with its distance to the nearer LONG edge -- the kerb or the frontage; the short ends are where Lot cut\n#: the strip, and are not edges.\nSTRIP_KINDS = ("sidewalk",)\nSTRIP_FALLOFF_M = 0.6\nSTRIP_FLOOR = 0.12\n\n\ndef strip_edge_distance(point, aabb) -> float:\n    """Distance from a point to the nearer long edge of a strip\'s rectangle."""\n    x, y = point\n    if (aabb[3] - aabb[0]) >= (aabb[4] - aabb[1]):          # runs along x: its long edges are y0 and y1\n        return max(0.0, min(y - aabb[1], aabb[4] - y))\n    return max(0.0, min(x - aabb[0], aabb[3] - x))\n\n'), ('lines 569-572', '                   and density != "very_high" and bool(gather))\n        for i, (x, y) in enumerate(points):\n            pick_from = usable\n            if is_open:\n', '                   and density != "very_high" and bool(gather))\n        is_strip = zone.get("kind") in STRIP_KINDS\n        for i, (x, y) in enumerate(points):\n            pick_from = usable\n            if is_strip:\n                d = strip_edge_distance((x, y), zone["aabb"])\n                if rng.random() >= max(STRIP_FLOOR, math.exp(-d / STRIP_FALLOFF_M)):\n                    thinned += 1\n                    continue\n            if is_open:\n'), ('lines 731-731', '            # open-ground candidates thinned away from the edges that gather debris (0.34.0)\n', "            # candidates thinned away from the edges that gather debris: open ground (0.34.0), a sidewalk's\n            # middle (0.37.0)\n")], 'patina/version.py': [('lines 9-9', '__version__ = "0.36.0"\n', '__version__ = "0.37.0"\n')], 'tests/test_debris_edges.py': [('lines 73-73', '                  tri_budget=None)["cost"]["thinned_open_ground"] == 0\n', '                  tri_budget=None)["cost"]["thinned_open_ground"] == 0\n\n\ndef _sidewalk_ratio():\n    zones = [zone("sw", "environmental_edge", "high", (0.0, 0.0, 40.0, 3.0), kind="sidewalk")]\n    m = S.plan(surfaces(zones, (), tops=(slab("Ground", (20.0, 1.5), (40.0, 3.0), 0.0),)), _catalogue(),\n               site_id="t", source="t", seed=9104, instance_budget=None, tri_budget=None)\n    ys = [o["pos"][1] for o in m["orders"]]\n    edge = sum(1 for y in ys if y <= 0.4 or y >= 2.6) / (2 * 0.4 * 40.0)\n    middle = sum(1 for y in ys if 1.1 <= y <= 1.9) / (0.8 * 40.0)\n    return edge / max(middle, 1e-9), m\n\n\ndef test_a_sidewalks_debris_lies_at_its_kerb_and_its_building_line(monkeypatch):\n    """FAILS ON 0.36.0: a sidewalk\'s debris lay evenly across its walking surface. The same plan with the rule and\n    without it: per square metre, the 0.4 m at each long edge against the middle, at least twice the ratio. (The\n    planner clumps its candidates, so a single strip\'s absolute ratio is the clumps\' as much as the rule\'s.)"""\n    with_rule, m = _sidewalk_ratio()\n    monkeypatch.setattr(S, "STRIP_KINDS", ())\n    without, _m = _sidewalk_ratio()\n    assert m["cost"]["thinned_open_ground"] > 0\n    assert with_rule > 2.0 * without, (with_rule, without)\n    assert S.strip_edge_distance((39.9, 1.5), [0.0, 0.0, 0.0, 40.0, 3.0, 0.0]) == pytest.approx(1.5)\n')]}
WHOLE = {}
NEW_FILES = {}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s/%s has mixed line endings; nothing written" % (REPO.name, name))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %s/%s is %s, not the %s this patch was written against; nothing written"
                         % (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %s/%s: the anchor at %s is there %d times; nothing written"
                                 % (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
