"""Zoo 1.147.0: a scupper and a conductor head (the factory's roadmap 324).

`core.dressing.scupper_parts`, built by `downspout_parts(..., head=True)` when Patina (>= 0.34.0) orders a downspout
`head`: a scupper's lip at the roof's surface, a conductor head hung under it, the leader ending in the head's foot.

Proven: tests/test_scupper.py fails on 1.146.1 (fails_on_old.out.txt); the clone's suite, 7,073 passed, 546 skipped,
1 xfailed, and its whole Blender set, 3,150 passed (suite_clone.out.txt, suite_bpy_clone.out.txt); the slice rebuilt
and priced (the factory's docs/findings/slice_look/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'zoo'
PINS = {'CHANGELOG.md': '3a4062e09cb34c02', 'VERSION': '3df2dfe5aad0eacb', 'zoo_keeper/core/dressing.py': '8887624d20d3088d', 'zoo_keeper/recipes/dress_cover.py': 'd73f7c9139fe6be0'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [1.146.1] - fourteen Blender tests that pinned the wrong thing\n', "## [1.147.0] - a scupper and a conductor head\n\nThe factory's roadmap 324. Patina (>= 0.34.0) orders a downspout `head` on a side a parapet stands over, its run from\nthe ground to the roof's surface: a flat roof behind a parapet drains through it, not into an eave gutter.\n\n### Added\n- **`core.dressing.scupper_parts`**, built by `downspout_parts(..., head=True)`: a scupper's lip standing out of the\n  parapet face with its top at the roof's surface, a conductor head hung under it, 4 mm up into the lip so the two\n  share no face, and the head's foot around the leader, which ends inside it. Every part stands 1 mm or more off the\n  wall. A downspout without `head` is built as it was. `dress_plan` carries `head`. Slice 2's bank: 10 headed\n  downspouts where 64 gutters hung (the factory's `docs/findings/slice_look/`). Tests: tests/test_scupper.py (fails\n  on 1.146.1).\n\n## [1.146.1] - fourteen Blender tests that pinned the wrong thing\n")], 'VERSION': [('lines 1-1', '1.146.1', '1.147.0')], 'zoo_keeper/core/dressing.py': [('lines 129-130', 'BOOT_H, BOOT_W, BOOT_D = 0.35, 0.12, 0.10\n\n', "BOOT_H, BOOT_W, BOOT_D = 0.35, 0.12, 0.10\n#: A ROOF THAT DRAINS THROUGH ITS PARAPET (1.147.0; Patina >= 0.34.0 orders the downspout `head`, the factory's\n#: roadmap 324). Its water leaves by a scupper -- a lipped spout through the parapet at the roof's surface -- into a\n#: conductor head, a flared box on the wall that the leader hangs from. The run's top is the roof's surface: the\n#: scupper's lip stands on it, the head hangs just under the lip, and the leader enters the head's foot. Sized from\n#: a 1990s commercial roof's 4 in scupper and a 10 x 8 in head, drawn a little large to hold at street distance.\nSCUPPER_W, SCUPPER_OUT, SCUPPER_H = 0.24, 0.16, 0.10\nHEAD_W, HEAD_D, HEAD_H = 0.30, 0.22, 0.26\nHEAD_FOOT_W, HEAD_FOOT_H = 0.16, 0.08\n\n"), ('lines 327-328', '            "frame_width": float(order.get("frame_width", 0.12)),\n        },\n', '            "frame_width": float(order.get("frame_width", 0.12)),\n            "head": bool(order.get("head", False)),\n        },\n'), ('lines 435-435', 'def downspout_parts(length: float, cross: float):\n', 'def downspout_parts(length: float, cross: float, head: bool = False):\n'), ('lines 440-441', '    the run between the two).\n    """\n', '    the run between the two).\n\n    ``head`` (1.147.0): the top is the roof\'s surface instead, and the run\n    ends in a scupper and a conductor head (`scupper_parts`) with the leader\n    entering the head\'s foot.\n    """\n'), ('lines 446-447', '    pipe = ((0.0, y0 + DOWNSPOUT_DEPTH / 2.0, (pipe_z0 + L / 2.0) / 2.0),\n            (cross, DOWNSPOUT_DEPTH, L / 2.0 - pipe_z0))\n', "    top = L / 2.0\n    extra = []\n    if head:\n        extra = scupper_parts(top)\n        top = top - SCUPPER_H - HEAD_H - HEAD_FOOT_H + 0.02   # into the head's foot\n    pipe = ((0.0, y0 + DOWNSPOUT_DEPTH / 2.0, (pipe_z0 + top) / 2.0),\n            (cross, DOWNSPOUT_DEPTH, top - pipe_z0))\n"), ('lines 452-452', '    return [pipe, boot] + straps\n', '    return [pipe, boot] + straps + extra\n\n\ndef scupper_parts(roof_z: float):\n    """A scupper and its conductor head (1.147.0), as (center, size) boxes in a\n    downspout\'s cover-local space, ``roof_z`` the roof\'s surface: the scupper\'s\n    lip standing on it out of the parapet face, the head hung just under the\n    lip and standing off the wall, and the head\'s narrower foot where the\n    leader enters. Every part stands 1 mm or more off the wall face."""\n    z = float(roof_z)\n    lip = ((0.0, 0.001 + SCUPPER_OUT / 2.0, z + SCUPPER_H / 2.0 - SCUPPER_H),\n           (SCUPPER_W, SCUPPER_OUT, SCUPPER_H))\n    hz1 = z - SCUPPER_H + 0.004                       # 4 mm up into the lip: no shared face\n    head = ((0.0, 0.003 + HEAD_D / 2.0, hz1 - HEAD_H / 2.0), (HEAD_W, HEAD_D, HEAD_H))\n    fy = 0.001 + (DOWNSPOUT_DEPTH + 0.04) / 2.0           # 1 mm off the wall, around the leader\n    foot = ((0.0, fy, hz1 - HEAD_H - HEAD_FOOT_H / 2.0 + 0.005),\n            (HEAD_FOOT_W, DOWNSPOUT_DEPTH + 0.04, HEAD_FOOT_H + 0.01))\n    return [lip, head, foot]\n')], 'zoo_keeper/recipes/dress_cover.py': [('lines 105-105', '        for center, size in downspout_parts(h, w):\n', '        for center, size in downspout_parts(h, w, head=bool(order.get("head"))):\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_scupper.py': '"""A roof that drains through its parapet (1.147.0; Patina >= 0.34.0, the factory\'s roadmap 324).\n\nPatina orders a downspout `head` on a side a parapet stands over, its run from the ground to the roof\'s surface; Zoo\nends it in a scupper\'s lip at the roof and a conductor head hung under it, with the leader entering the head\'s foot.\nA downspout without `head` is built as it always was.\n"""\nimport pytest\n\nfrom zoo_keeper import TOOL_VERSION\nfrom zoo_keeper.core import dressing as D\nfrom zoo_keeper.core import genome\n\nL, CROSS = 7.2, 0.076\n\n\ndef _span(part):\n    (cx, cy, cz), (sx, sy, sz) = part\n    return (cy - sy / 2, cy + sy / 2), (cz - sz / 2, cz + sz / 2)\n\n\ndef test_a_headed_run_ends_in_a_scupper_and_a_head_at_the_roof():\n    """FAILS ON 1.146.1: no scupper, no head, and the leader ran to the top."""\n    parts = D.downspout_parts(L, CROSS, head=True)\n    pipe, lip, head, foot = parts[0], parts[-3], parts[-2], parts[-1]\n    (_ly, (lz0, lz1)), ((hy0, hy1), (hz0, hz1)) = _span(lip), _span(head)\n    _fy, (fz0, fz1) = _span(foot)\n    _py, (pz0, pz1) = _span(pipe)\n    assert lz1 == pytest.approx(L / 2)                    # the lip\'s top is the roof\'s surface\n    assert hz1 > lz0 and hz1 - lz0 < 0.01                 # the head hangs under the lip, into it, no shared face\n    assert hy1 > _ly[1]                                   # and stands out past it, to catch what it spills\n    assert fz1 > hz0 and fz0 < pz1 < fz1                  # the leader enters the head\'s foot\n    assert all(_span(p)[0][0] >= 0.001 for p in parts[-3:])   # nothing in the wall\n\n\ndef test_an_unheaded_run_is_built_as_it_was():\n    assert D.downspout_parts(L, CROSS) == D.downspout_parts(L, CROSS, head=False)\n    assert len(D.downspout_parts(L, CROSS)) == 4\n\n\ndef test_the_plan_carries_head():\n    order = {"cover": "downspout", "pos": [0, 11.15, 3.6], "normal": [0, 1, 0], "size": L, "head": True,\n             "collision": "none", "seed_offset": 1}\n    g = genome.load_species("dress_cover")\n    plan = D.dress_plan(order, g, "delco_1997", "spec/Blender Z-up raw coords", TOOL_VERSION)\n    assert plan["order"]["head"] is True and plan["material"] == "metal_painted"\n    assert D.dress_plan(dict(order, head=False), g, "delco_1997", "spec/Blender Z-up raw coords",\n                        TOOL_VERSION)["order"]["head"] is False\n'}


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
