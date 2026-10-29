"""Patina 0.33.1: one plane is one bucket (the factory's roadmap 324).

`anchors._plane_keys` chains face planes within 1 mm into one wall segment before `round(_, 1)`, so a float32 plane
that straddled a rounding boundary no longer becomes two segments ordering covers over one another.

Proven: tests/test_plane_buckets.py fails on 0.33.0 (fails_on_old.out.txt); the clone's suite (suite_clone.out.txt);
the library census of 158 shells and the overlap counts (the factory's docs/findings/parapet_flush/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'patina'
PINS = {'CHANGELOG.md': '8330342b192cd0b3', 'VERSION': '4585700512e39cd9', 'patina/anchors.py': 'bef2032614582d62', 'patina/version.py': 'eff504f901820313'}
EDITS = {'CHANGELOG.md': [('lines 4-5', 'versioning follows [SemVer](https://semver.org/).\n\n', "versioning follows [SemVer](https://semver.org/).\n\n## [0.33.1] - one plane is one bucket\n\nThe factory's roadmap 324. The anchor pass groups a shell's exterior-wall faces into wall segments by\n`round(plane, 1)`, and the shell is float32: a wall face on y 11.15 comes back 11.149998664855957 from one box and\n11.15000057220459 from another, which round to 11.1 and 11.2. Two segments then stand on one face, and each orders\nits own roofline, base course and curb along it. Found on Deli Counter 0.292.0's `bank_branch_a02`, whose parapet\nstands flush on its facade: the facade became a segment topping out at 6.9 m and put 24 edge strips across a flat wall\n(the factory's `docs/findings/parapet_flush/`). It was already in the library: `airport_terminal_a01`, whose every\nfacade splits so, carried 35 base courses and 25 curbs lying over one another.\n\n### Fixed\n- **`anchors._plane_keys`**: face planes within `PLANE_TOL` (1 mm) of a neighbour chain into one cluster and take\n  `round(mean, 1)` together; every other plane keeps `round(plane, 1)`, so a shell no rounding split buckets as before.\n  On `airport_terminal_a01` the overlapping pairs go 35 -> 3 base courses and 25 -> 0 curbs (the 3, and 2 edge strips,\n  are the anchors' own jittered spacing, unchanged).\n- **Across the library** (Deli Counter 0.291.0's 158 shells, `--dressing --anchors --gutters`): 76 shells' orders\n  change, 82 are identical; every change seen is a duplicate removed -- on `bank_branch_a02` the overlapping pairs go\n  10 -> 0 base courses and 11 -> 0 curbs, `apartment_walkup_a01` 11/23/22 -> 0/0/1, `funeral_home_a01` 28/26/11 ->\n  0/0/5 (base course / curb / edge strip; the factory's `docs/findings/parapet_flush/plane_census_live.txt` and\n  `overlap_live.txt`).\n\n")], 'VERSION': [('lines 1-1', 'Patina 0.33.0', 'Patina 0.33.1')], 'patina/anchors.py': [('lines 131-132', '    lo, hi = _visual_aabb(scene)\n    for c, n, (zlo, zhi) in _exterior_wall_faces(scene, mirrored):\n', '    lo, hi = _visual_aabb(scene)\n    faces = []\n    for c, n, (zlo, zhi) in _exterior_wall_faces(scene, mirrored):\n'), ('lines 139-139', '        along = 1 - axis\n', '        side = "hi" if horiz[axis] > 0 else "lo"\n        faces.append((axis, side, float(c[axis]), c, horiz, zlo, zhi))\n    plane = _plane_keys(faces)\n    for axis, side, p, c, horiz, zlo, zhi in faces:\n'), ('lines 141-143', '        side = "hi" if horiz[axis] > 0 else "lo"\n        key = (axis, side, round(float(c[axis]), 1))\n        buckets.setdefault(key, []).append((c, horiz, along, zlo, zhi))\n', '        key = (axis, side, plane[(axis, side, p)])\n        buckets.setdefault(key, []).append((c, horiz, 1 - axis, zlo, zhi))\n'), ('lines 156-157', '        }\n\n', '        }\n\n\n#: Faces whose planes stand this close are ONE plane, metres (0.33.1). The\n#: shell is float32: a facade and the parapet carried up from it (Deli Counter\n#: 0.292.0) both stand at y 11.15 on `bank_branch_a02`, and their faces\'\n#: centroids came back 11.149998664855957 and 11.15000057220459 -- either side of\n#: 11.15, which `round(_, 1)` sends to 11.1 and 11.2. The facade became a segment\n#: of its own topping out at 6.9 m, and its roofline anchors put 24 edge strips\n#: across a flat wall (the factory\'s docs/findings/parapet_flush/). Float noise\n#: is micrometres; the nearest real planes here are 5 cm apart.\nPLANE_TOL = 0.001\n\n\ndef _plane_keys(faces) -> dict:\n    """``{(axis, side, plane): bucket}``: each face plane\'s bucket coordinate.\n\n    Planes within :data:`PLANE_TOL` of their neighbour chain into one cluster\n    and take ``round(mean, 1)`` together; every other plane keeps\n    ``round(plane, 1)`` exactly as before, so a shell whose planes were never\n    split by rounding buckets as it did."""\n    out = {}\n    groups: dict = {}\n    for axis, side, p, *_rest in faces:\n        groups.setdefault((axis, side), set()).add(p)\n    for (axis, side), ps in groups.items():\n        run = []\n        for p in sorted(ps) + [None]:\n            if run and (p is None or p - run[-1] > PLANE_TOL):\n                key = round(sum(run) / len(run), 1)\n                for q in run:\n                    out[(axis, side, q)] = key\n                run = []\n            if p is not None:\n                run.append(p)\n    return out\n\n')], 'patina/version.py': [('lines 9-9', '__version__ = "0.33.0"\n', '__version__ = "0.33.1"\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_plane_buckets.py': '"""One plane is one bucket, whichever side of a rounding boundary its float lands (0.33.1).\n\nMeasured on Deli Counter 0.292.0\'s `bank_branch_a02`, whose parapet stands flush on its facade: the facade\'s faces at\ny 11.149998664855957 and the parapet\'s at 11.15000057220459, which `round(_, 1)` sent to 11.1 and 11.2 -- two\nsegments, the facade\'s topping out at 6.9 m, and 24 roofline strips across a flat wall\n(the factory\'s docs/findings/parapet_flush/, bucket_probe.py).\n"""\nfrom patina import anchors\n\nFACADE, PARAPET = 11.149998664855957, 11.15000057220459\n\n\ndef _faces(*planes, axis=1, side="hi"):\n    return [(axis, side, p, None, None, 0.0, 1.0) for p in planes]\n\n\ndef test_a_plane_split_by_float_noise_is_one_bucket():\n    """FAILS ON 0.33.0: there was no clustering, and the two rounded apart."""\n    keys = anchors._plane_keys(_faces(FACADE, PARAPET))\n    assert keys[(1, "hi", FACADE)] == keys[(1, "hi", PARAPET)]\n    assert round(FACADE, 1) != round(PARAPET, 1)          # the split this closes\n\n\ndef test_planes_a_real_distance_apart_bucket_as_they_did():\n    """The control: every plane not within PLANE_TOL of another keeps\n    round(plane, 1) -- the bank\'s 10.95 inner faces still share 11.0\'s bucket\n    and the 15 cm wall still separates the face from its centre line."""\n    ps = (11.0, 10.950000762939453, 11.149998664855957, -11.0, 15.2, 3.3333)\n    keys = anchors._plane_keys(_faces(*ps))\n    assert all(keys[(1, "hi", p)] == round(p, 1) for p in ps)\n\n\ndef test_sides_and_axes_never_cluster_together():\n    keys = anchors._plane_keys(_faces(FACADE) + _faces(PARAPET, side="lo") + _faces(PARAPET, axis=0))\n    assert keys[(1, "hi", FACADE)] == 11.1\n    assert keys[(1, "lo", PARAPET)] == keys[(0, "hi", PARAPET)] == 11.2\n'}


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
