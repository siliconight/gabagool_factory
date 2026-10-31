"""Lot 0.140.0: a utility cut has an age.

site_patches: a seeded age a patch, PATCH_TINT fresh to OLDEST_TINT old, in its vertex colour on the one material.

Proven: tests/test_patch_age.py fails on 0.139.0 (fails_on_old.out.txt); the clone suite fails only the 12
location-only tests an untouched Lot does (suite_clone.out.txt); built as slice 28 (the factory's
docs/findings/slice_look/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'lot'
PINS = {'CHANGELOG.md': '8b901574aa50d873', 'VERSION': '60d9b53589aea625', 'site_patches.py': '320025df2f96cf31', 'tests/test_site_patches.py': 'f0d24e01bb45d1c7'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## 0.139.0 - where tyres wear the paint\n', "## 0.140.0 - a utility cut has an age\n\nThe factory's roadmap 324 (the vertical slice). Every patch `site_patches` cuts wore one tint, `PATCH_TINT` (0.42 of\nthe road's pack), so every cut on a 1999 avenue read as laid last week; in the slice's sodium pools, once Pixelcoat\n0.66.0 lifted the road to a weathered albedo, each was a near-black bar across the lane, read as a painted shadow\n(the factory's docs/findings/slice_look/, slices 27 and 28). A street's cuts are of every age, and a cap weathers\ntoward the road round it: each patch now draws a seeded `age` in [0, 1) (by its building and lateral) and wears\n`PATCH_TINT` fresh to `OLDEST_TINT` (0.84, 0.84, 0.85) old, linearly (`tint_of`). The age rides in the mesh's vertex\ncolour (`v x y z r g b`, which Godot 4.7's OBJ importer keeps -- probed) on the one material, whose tint is\n`OLDEST_TINT`, with `vertex_color_use_as_albedo` and `vertex_color_is_srgb`: colour-only variation is never a new\nmaterial, so no draw is added. On the slice (seed 9205): 8 patches, ages 0.03 to 0.98; draws +0 median, +0.5 largest\nagainst slice 27.\n\nTests: tests/test_patch_age.py (fails on 0.139.0); tests/test_site_patches.py reads the oldest tint and the vertex\ncolour flags.\n\n## 0.139.0 - where tyres wear the paint\n")], 'VERSION': [('lines 1-1', 'Lot 0.139.0', 'Lot 0.140.0')], 'site_patches.py': [('lines 69-70', 'PATCH_TINT = (0.42, 0.42, 0.44)\nPROUD = site_drains.PROUD\n', 'PATCH_TINT = (0.42, 0.42, 0.44)\n#: A CUT HAS AN AGE (0.140.0). Every patch wore `PATCH_TINT`, so every cut on a 1999 avenue read as laid last\n#: week: in the slice\'s sodium pools, once Pixelcoat 0.66.0 lifted the road to a weathered albedo, each was a\n#: near-black bar across the lane, read as a painted shadow (the factory\'s docs/findings/slice_look/, slice 27). A\n#: street\'s cuts are of every age, and a cap weathers toward the road round it. Each patch draws a seeded ``age``\n#: in [0, 1) and wears `PATCH_TINT` at 0 to `OLDEST_TINT` at 1, linearly, so a few stand out fresh and most have\n#: nearly gone back to the road. The age rides in the mesh\'s vertex colour on the one material, whose tint is\n#: `OLDEST_TINT` -- colour-only variation is never a new material (the factory\'s CLAUDE.md, "Draw calls are the\n#: budget"), so the draw count is the one it was.\nOLDEST_TINT = (0.84, 0.84, 0.85)\nPROUD = site_drains.PROUD\n'), ('lines 147-148', '\ndef _drain_poly(d):\n', '\ndef tint_of(age):\n    """The tint a patch of ``age`` (0 fresh, 1 oldest) wears: `PATCH_TINT` to `OLDEST_TINT`, linearly."""\n    a = min(max(float(age), 0.0), 1.0)\n    return tuple(f + (o - f) * a for f, o in zip(PATCH_TINT, OLDEST_TINT))\n\n\ndef _drain_poly(d):\n'), ('lines 160-161', "    patch's ``at`` (plan centre), ``yaw`` (the road's, degrees), ``size`` [along, across] and\n    ``corners`` (plan polygon). ``marks`` is the paint the site draws and ``drains`` its drains\n", "    patch's ``at`` (plan centre), ``yaw`` (the road's, degrees), ``size`` [along, across],\n    ``corners`` (plan polygon) and ``age`` (0 fresh to 1 oldest, seeded by building and lateral; `tint_of`). ``marks`` is the paint the site draws and ``drains`` its drains\n"), ('lines 190-190', '                        "corners": [[round(px, 4), round(py, 4)] for px, py in poly]})\n', '                        "corners": [[round(px, 4), round(py, 4)] for px, py in poly],\n                        "age": round(_unit(f"{bid}|{n}|age"), 3)})\n'), ('lines 196-196', 'def _obj(name, quads, comment, uv):\n', 'def _obj(name, quads, comment, uv, colours=None):\n    """An OBJ of ``quads`` [(plan corners, height)]; ``colours``, one (r, g, b) a quad, rides on its\n    vertices (``v x y z r g b``, which Godot\'s OBJ importer keeps -- probed on 4.7, 2026-10-31)."""\n'), ('lines 198-199', '    vs, vt, fs = [], [], []\n    for quad, y in quads:\n', '    vs, vt, fs, vc = [], [], [], []\n    for i, (quad, y) in enumerate(quads):\n'), ('lines 204-205', '            vt.append(uv(gx, gz))\n        fs.append((k + 1, k + 2, k + 3))\n', '            vt.append(uv(gx, gz))\n            if colours is not None:\n                vc.append(colours[i])\n        fs.append((k + 1, k + 2, k + 3))\n'), ('lines 207-207', '    lines += [f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in vs]\n', '    if colours is None:\n        lines += [f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in vs]\n    else:\n        lines += [f"v {x:.6f} {y:.6f} {z:.6f} {r:.4f} {g:.4f} {b:.4f}"\n                  for (x, y, z), (r, g, b) in zip(vs, vc)]\n'), ('lines 233-234', '        name = f"site_patches_asphalt_{tag}"\n        files[f"{name}.obj"] = _obj(\n', '        name = f"site_patches_asphalt_{tag}"\n        # each patch\'s age as its share of the oldest tint, the material\'s (0.140.0)\n        files[f"{name}.obj"] = _obj(\n'), ('lines 237-237', '            lambda gx, gz: (gz * scale + off[0], -gx * scale + off[2]))\n', '            lambda gx, gz: (gz * scale + off[0], -gx * scale + off[2]),\n            colours=[tuple(t / o for t, o in zip(tint_of(p.get("age", 0.0)), OLDEST_TINT)) for p in group])\n'), ('lines 242-244', '    mat = mat_sub("site_patches_asphalt", None, road_skin, tint=PATCH_TINT, triplanar=False)\n    mat.insert(len(mat) - 1, "cull_mode = 2")\n    sub += mat\n', '    mat = mat_sub("site_patches_asphalt", None, road_skin, tint=OLDEST_TINT, triplanar=False)\n    mat.insert(len(mat) - 1, "cull_mode = 2")\n    # the age: the vertex colour multiplies the tint, read as sRGB as the tint is (0.140.0)\n    mat.insert(len(mat) - 1, "vertex_color_use_as_albedo = true")\n    mat.insert(len(mat) - 1, "vertex_color_is_srgb = true")\n    sub += mat\n')], 'tests/test_site_patches.py': [('lines 108-108', '    assert "albedo_color = Color(0.42, 0.42, 0.44, 1)" in text\n', '    # the material wears the oldest tint; each patch\'s age darkens it in its vertex colour (0.140.0)\n    assert "albedo_color = Color(0.84, 0.84, 0.85, 1)" in text\n    assert "vertex_color_use_as_albedo = true" in text and "vertex_color_is_srgb = true" in text\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_patch_age.py': '"""A utility cut has an age (Lot 0.140.0).\n\nEvery patch wore one tint, 0.42 of the road\'s pack, so every cut on the slice\'s 1999 avenue read as laid last week:\nin its sodium pools, a near-black bar across the lane, read as a painted shadow. Each patch now draws a seeded age and\nwears `PATCH_TINT` fresh to `OLDEST_TINT` old, carried in its vertex colour on the one material.\nFAILS ON 0.139.0: a patch record has no age and the meshes carry no colour.\n"""\nimport os\nimport sys\n\nHERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\nsys.path.insert(0, HERE)\nsys.path.insert(0, os.path.join(HERE, "tests"))\n\nimport lot            # noqa: E402\nimport site_patches   # noqa: E402\nfrom test_site_patches import STREET, _bld, _plan   # noqa: E402\n\n\ndef _patches():\n    blds = [_bld("b%d" % i, -70.0 + 20.0 * i, 14.0, 12.0, 10.0) for i in range(8)]\n    return _plan(STREET, blds)[3]\n\n\ndef test_every_patch_has_a_seeded_age_and_the_ages_spread():\n    a, b = _patches(), _patches()\n    assert a == b and len(a) >= 8\n    ages = [p["age"] for p in a]\n    assert all(0.0 <= x < 1.0 for x in ages)\n    assert min(ages) < 0.35 and max(ages) > 0.65            # some fresh, some old, on one street\n\n\ndef test_the_age_runs_from_the_fresh_tint_to_the_oldest():\n    assert site_patches.tint_of(0.0) == site_patches.PATCH_TINT\n    assert site_patches.tint_of(1.0) == site_patches.OLDEST_TINT\n    mid = site_patches.tint_of(0.5)\n    assert all(f < m < o for f, m, o in zip(site_patches.PATCH_TINT, mid, site_patches.OLDEST_TINT))\n\n\ndef test_the_age_rides_in_the_vertex_colour_on_one_material():\n    """Colour-only variation is never a new material: one material, one mesh a cell, as before."""\n    patches = _patches()\n    skin = {"id": "road_pack", "albedo": "a.png", "meters_per_tile": 4.0}\n    body, sub, files = site_patches.meshes(patches, 0.1, skin, lot.paint_offset, lot._mat_sub)\n    assert "\\n".join(sub).count("[sub_resource") == 1\n    assert len(files) == "\\n".join(body).count("MeshInstance3D")\n    want = {}\n    for p in patches:\n        r = round(site_patches.tint_of(p["age"])[0] / site_patches.OLDEST_TINT[0], 4)\n        for c in p["corners"]:\n            want[(round(c[0], 6), round(-c[1], 6))] = r\n    seen = 0\n    for text in files.values():\n        for ln in text.splitlines():\n            if ln.startswith("v "):\n                f = ln.split()\n                assert len(f) == 7, ln\n                assert abs(float(f[4]) - want[(round(float(f[1]), 6), round(float(f[3]), 6))]) < 1e-4\n                seen += 1\n    assert seen == 4 * len(patches)\n'}


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
