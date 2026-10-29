"""Zoo 1.146.1: fourteen Blender tests that pinned the wrong thing.

test_club_bpy and test_interior_bpy hash meshes order-free and are re-pinned to the shapes their old pins described
(equal at 0.90.0, 1.102.0, 1.103.0 and 1.146.0); test_shut_door and test_front_doors pass over 1.124.0's knob. No
code changes.

Proven: the fourteen fail on 1.146.0 and pass with the change (fails_on_old.out.txt, which also shows the club pins
failing on 0.89.0, whose TV stands differ); the clone's whole Blender set (suite_bpy_clone.out.txt).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'zoo'
PINS = {'CHANGELOG.md': '55ce9f01421fb250', 'VERSION': '28b173c9e2e18b9d', 'tests/test_club_bpy.py': '4743daabf04659e3', 'tests/test_front_doors.py': 'eed795c9d9978ffa', 'tests/test_interior_bpy.py': 'fc6f73f8926308f7', 'tests/test_shut_door.py': 'ac29ce938906667b'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [1.146.0] - a parapet has a coping\n', "## [1.146.1] - fourteen Blender tests that pinned the wrong thing\n\nFound by running every Blender test for 1.146.0, where earlier releases had run a set of them: fourteen failed on\n1.144.0, 1.145.0 and 1.146.0 alike. Each was bisected and measured; none was a defect in what Zoo builds.\n\n### Fixed\n- **`test_club_bpy` (5) and `test_interior_bpy` (7) pinned a vertex ORDER as well as a shape.** Their digests hashed\n  each object's vertices in stored order. 1.103.0 sorts every mesh's faces so two builds write the same bytes, and a\n  later release moved the order again; neither moved a vertex. Measured in Blender 5.1.1 on 0.90.0, 1.102.0, 1.103.0\n  and 1.146.0: an order-free digest -- each object's vertex and wear lines sorted, objects by name -- is the same at\n  all four for all twelve keys, and the ordered one equals each old pin through 1.102.0. The digests are order-free\n  now and re-pinned to those values, the old pins kept beside them; run on 0.89.0 the club's two TVs, whose stands\n  0.90.0 rebuilt, still fail.\n- **`test_shut_door` and `test_front_doors` read 1.124.0's knob as a leaf.** Both took every mesh with `Leaf` in its\n  name as the door leaf and wanted the door's material on it; 1.124.0 added the knob as `_LeafHardware`, in iron.\n  They pass the hardware over now; `test_door_hardware.py` pins it.\n\n## [1.146.0] - a parapet has a coping\n")], 'VERSION': [('lines 1-1', '1.146.0', '1.146.1')], 'tests/test_club_bpy.py': [('lines 37-39', '#: materials: object names, vertices to 0.1 mm, Wear to 1e-4, material names\nMAIN_DIGESTS = {\n    # 0.86.0 - 0.89.0, the stand set that failed `fit_depth`:\n', "#: materials: object names, vertices to 0.1 mm, Wear to 1e-4, material names\n#: THE DIGEST IS ORDER-FREE (1.147.0). It hashed each object's vertices in the\n#: order Blender stored them, so it pinned an ORDER as well as a shape, and two\n#: deliberate releases moved the order and nothing else: 1.103.0 sorts every\n#: mesh's faces so two builds write the same bytes (the factory's\n#: docs/findings/grader_speed/), and a later one moved it again. Measured in\n#: Blender 5.1.1 on 0.90.0 (82d23b1), 1.102.0, 1.103.0 and 1.146.0: the ordered\n#: digest is each old pin until 1.102.0 and differs from 1.103.0 on, while the\n#: digest below -- each object's vertex and wear lines sorted, objects sorted\n#: by name -- is the same at all four for every key. So the pins are re-taken\n#: in that form and still describe the shapes main built; the old ordered pins\n#: are kept beside them.\nMAIN_DIGESTS = {\n    # 0.86.0 - 0.89.0, the stand set that failed `fit_depth` (ordered):\n"), ('lines 42-47', '    # 0.90.0, measured on the first build of `crt_forms.stand_layout`:\n    ("crt_tv", (0.55, 0.5, 0.42), ()): "ea931596f371006cdda67be9e6f4f6a1bde869f6",\n    ("crt_tv", (0.9, 0.62, 0.7), ()): "13598510af7123b6ce3b4d87fb04d93036c8ecbd",\n    ("booth_seat", (2.0, 0.9, 0.85), (("form", "sofa"),)): "13cba2a4abf87dbfe4be1dc10e75cbefeefe8438",\n    ("pool_table", (2.0, 1.14, 0.79), ()): "c904dc4002de72713a3111dd26b0787d8c18dbb1",\n    ("table", (1.2, 0.8, 0.74), (("stock", "bar"), ("variant", 1))): "1a8cc276ae4b5d5ccb2c4bcde9bf008c05d128a6",\n', '    # 0.90.0, measured on the first build of `crt_forms.stand_layout`\n    # (ordered, held to 1.102.0): crt_tv 0.55 ea931596f371..., crt_tv 0.9\n    # 13598510af71..., booth_seat 13cba2a4abf8..., pool_table c904dc4002de...,\n    # table 1a8cc276ae4b...; order-free, the same shapes:\n    ("crt_tv", (0.55, 0.5, 0.42), ()): "6007319d5cf33aabd96ccb3eaa00e359f5dfbff3",\n    ("crt_tv", (0.9, 0.62, 0.7), ()): "df7127bb77d08a7af8fdb7d3713a90e9335b0a44",\n    ("booth_seat", (2.0, 0.9, 0.85), (("form", "sofa"),)): "7bdf16436eb2f65c3164c2c7cbb4806f1db07c1f",\n    ("pool_table", (2.0, 1.14, 0.79), ()): "214d7f936295514391a4405b78a8907c3de637e3",\n    ("table", (1.2, 0.8, 0.74), (("stock", "bar"), ("variant", 1))): "1b72f9b7777ff8387cf56b2401af30ca80c3104d",\n'), ('lines 80-85', 'def _digest(objs):\n    h = hashlib.sha1()\n    for o in objs:\n        h.update(o.name.encode())\n        for v in o.data.vertices:\n            h.update(("%.4f,%.4f,%.4f;" % tuple(v.co)).encode())\n', 'def _digest(objs, materials=True):\n    """Every object\'s name, vertices, wear and materials, in no stored order\n    (see `MAIN_DIGESTS`)."""\n    rows = []\n    for o in sorted(objs, key=lambda o: o.name):\n        vs = sorted("%.4f,%.4f,%.4f" % tuple(v.co) for v in o.data.vertices)\n'), ('lines 87-92', '        if ca:\n            for c in ca.data:\n                h.update(("%.4f" % c.color[0]).encode())\n        for s in o.material_slots:\n            h.update((s.material.name if s.material else "-").encode())\n    return h.hexdigest()\n', '        ws = sorted("%.4f" % c.color[0] for c in ca.data) if ca else []\n        ms = [s.material.name if s.material else "-" for s in o.material_slots] if materials else []\n        rows.append("%s|%s|%s|%s" % (o.name, ";".join(vs), ",".join(ws), ",".join(ms)))\n    return hashlib.sha1("\\n".join(rows).encode()).hexdigest()\n')], 'tests/test_front_doors.py': [('lines 89-91', '                   theme="delco_1997", style=1, options={"save_blend": False})\n    leaves = {o.name: o.data.materials[0].name for o in bpy.data.objects\n              if o.type == "MESH" and "Leaf" in o.name}\n', '                   theme="delco_1997", style=1, options={"save_blend": False})\n    # the leaf and its panels; 1.124.0\'s knob (`_LeafHardware`) is iron and\n    # pinned by test_door_hardware.py\n    leaves = {o.name: o.data.materials[0].name for o in bpy.data.objects\n              if o.type == "MESH" and "Leaf" in o.name and "Hardware" not in o.name}\n')], 'tests/test_interior_bpy.py': [('lines 24-24', '#: measured on Zoo 0.80.0 (main at 295a3fe), kit path, theme delco_1997\n', "#: THE DIGEST IS ORDER-FREE (1.147.0). It hashed each object's vertices in the\n#: order Blender stored them, so it pinned an ORDER as well as a shape, and two\n#: deliberate releases moved the order and nothing else: 1.103.0 sorts every\n#: mesh's faces so two builds write the same bytes (the factory's\n#: docs/findings/grader_speed/), and a later one moved it again. Measured in\n#: Blender 5.1.1 on 0.90.0 (82d23b1, the ordered pins taken on 0.80.0 still held there), 1.102.0, 1.103.0 and 1.146.0: the ordered\n#: digest is each old pin until 1.102.0 and differs from 1.103.0 on, while the\n#: digest below -- each object's vertex and wear lines sorted, objects sorted\n#: by name -- is the same at all four for every key. So the pins are re-taken\n#: in that form and still describe the shapes main built; the old ordered pins\n#: are kept beside them.\n#: measured on Zoo 0.80.0 (main at 295a3fe), kit path, theme delco_1997, ordered\n#: (held to 1.102.0): desk 1.6 2374d64849a5..., desk 4.4 8de4dc3118a1..., table\n#: 0.5 dac69cddbefb..., table 0.9 105412ce2b31..., counter 817d0c443e4f...,\n#: filing_cabinet 0.9 1b2b032391e9..., filing_cabinet 2.0 64963084df6f...;\n#: order-free, the same shapes:\n"), ('lines 26-32', '    ("desk", (1.6, 0.8, 0.75)): "2374d64849a50ccc5af4f67b5966d0db5f2db068",\n    ("desk", (4.4, 1.5, 1.2)): "8de4dc3118a10d4b9c73b0d14819e9acbda5310d",\n    ("table", (1.2, 0.8, 0.5)): "dac69cddbefb1db72ac64a9fdfebd218c17160f0",\n    ("table", (4.0, 1.2, 0.9)): "105412ce2b312521d295db00efd2a63abb8c8e52",\n    ("counter", (2.2, 0.8, 1.05)): "817d0c443e4fe6016b5183ed613862e636bc7f80",\n    ("filing_cabinet", (0.9, 0.5, 1.4)): "1b2b032391e9ec8b04846377d188033395123dd4",\n    ("filing_cabinet", (2.0, 0.6, 1.8)): "64963084df6f9a0957b8bc20d19141336c6e39c5",\n', '    ("desk", (1.6, 0.8, 0.75)): "2ecb5b5ac26a68dd6599c4357406992c2ea1c94a",\n    ("desk", (4.4, 1.5, 1.2)): "6fc0cf392e6764087830682a09f14ad70e427507",\n    ("table", (1.2, 0.8, 0.5)): "8518291f11d684ed549d7a90817ca87f36aeda15",\n    ("table", (4.0, 1.2, 0.9)): "bf1667ab1d115e509a9821612ed1caa1cc0f01ee",\n    ("counter", (2.2, 0.8, 1.05)): "88132078c3d946c86d55cf79c700460cec033a21",\n    ("filing_cabinet", (0.9, 0.5, 1.4)): "cf5bf04ea92a0f31ef4ae0e8e02a6f2457f96746",\n    ("filing_cabinet", (2.0, 0.6, 1.8)): "b9e11d1a23b7fd3110785623ce59278b509168ab",\n'), ('lines 53-57', '    h = hashlib.sha1()\n    for o in objs:\n        h.update(o.name.encode())\n        for v in o.data.vertices:\n            h.update(("%.4f,%.4f,%.4f;" % tuple(v.co)).encode())\n', '    """Every object\'s name, vertices and wear, in no stored order (see\n    `MAIN_DIGESTS`)."""\n    rows = []\n    for o in sorted(objs, key=lambda o: o.name):\n        vs = sorted("%.4f,%.4f,%.4f" % tuple(v.co) for v in o.data.vertices)\n'), ('lines 59-62', '        if ca:\n            for c in ca.data:\n                h.update(("%.4f" % c.color[0]).encode())\n    return h.hexdigest()\n', '        ws = sorted("%.4f" % c.color[0] for c in ca.data) if ca else []\n        rows.append("%s|%s|%s|" % (o.name, ";".join(vs), ",".join(ws)))\n    return hashlib.sha1("\\n".join(rows).encode()).hexdigest()\n')], 'tests/test_shut_door.py': [('lines 53-53', '    leaves = {n: m for n, m in shut.items() if "Leaf" in n}\n', '    # the leaf and its panels; 1.124.0\'s knob (`_LeafHardware`) is iron and\n    # pinned by test_door_hardware.py\n    leaves = {n: m for n, m in shut.items() if "Leaf" in n and "Hardware" not in n}\n')]}
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
