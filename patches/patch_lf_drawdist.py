"""Level Factory 0.272.0: a draw distance from each part's own size.

`zoo_worldskin.gd` `_draw_distance`: each part of an object's GLB is dropped where its bounding sphere spans 3 px of a
1080-line screen through the game's 75 degree camera, about 235 x its radius; a lit part, a range already set, kit
tiles, dressing and building bases are left alone.

Proven: tests/unit/test_worldskin_draw_distance.py fails on 0.271.0 (fails_on_old.out.txt); the clone's suite, exit 0
(suite_clone.out.txt); the slice rebuilt and priced (the factory's docs/findings/size_cull/ and
docs/findings/slice_look/, slice 19: no heading gains a draw, the long views lose 36-100, the worst view's p95 11.31 ->
10.92 ms).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'level_factory'
PINS = {'CHANGELOG.md': '0ea674119b5ea61a', 'VERSION': '4a28af11ecf4503e', 'assets/godot/zoo_worldskin.gd': 'ac4869b1f6a6d6f3'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [0.271.0] - a stain drawn over its wall, not lit beside it\n', '## [0.272.0] - a draw distance from each part\'s own size\n\nThe walker, 2026-10-30: 60 FPS is the floor, and the level is not the whole frame -- guns, AI, sound and networking\nneed theirs -- "so smart LOD, culling techniques now will go a long way". No mesh in a package had a draw distance\n(every one `visibility_range_end = 0`). Measured first (the factory\'s `docs/findings/size_cull/`, a headless probe at\nthe price harness\'s own views): at the slice\'s worst views 479-563 surfaces in the frustum spanned under 3 px at\n1080p, most of them small parts of props kept as their own meshes -- a parking meter\'s window and body, cars\'\nstickers, newspaper boxes\' windows.\n\n### Added\n- **`zoo_worldskin.gd` `_draw_distance`**: each part of an object\'s GLB is dropped where its own bounding sphere spans\n  `DRAW_PX` (3) pixels of a `DRAW_SCREEN_H` (1080) screen through a `DRAW_FOV_DEG` (75) camera -- Godot\'s default,\n  which the walk player\'s camera keeps -- about 235 x its radius, with `DRAW_HYSTERESIS` (10 %) of it as the end\n  margin so a part at its threshold does not flicker. Each part by its own size, so a meter\'s window goes at about\n  35 m and its body at about 140 m: the small details of a thing go first. A part that lights (an emissive surface or\n  any shader material) keeps every distance; a range already set is kept; a kit tile, a dressing and a building\'s\n  base are never given one.\n\nOn the slice (slice 19 against slice 18b, nothing else different; a quiet price, the controls 0.93 ms apart): no\nheading gains a draw, the long views lose 36-100 and the close ones nothing; the worst view, longest_sightline yaw 90,\n2,443 -> 2,343 draws and p95 11.31 -> 10.92 ms. 1,386 parts of 302 object GLBs given a range, 191 lit parts kept.\nNo visible change in the frames but the trees\' leaves. The probe predicted up to 502 at that view: occlusion was\nalready removing some of it, and the meshes the export merges (`merge_buildings.gd`, `merge_empties.gd`) are not\ncovered -- the next step. Tests: tests/unit/test_worldskin_draw_distance.py.\n\n## [0.271.0] - a stain drawn over its wall, not lit beside it\n')], 'VERSION': [('lines 1-1', '0.271.0', '0.272.0')], 'assets/godot/zoo_worldskin.gd': [('lines 1033-1034', '\t\t\t\t% [base, int(vc[0]), int(vc[1]), int(vc[2])])\n\tif not is_kit:\n', '\t\t\t\t% [base, int(vc[0]), int(vc[1]), int(vc[2])])\n\t\t# and a draw distance from each part\'s own size (0.272.0), never on a building\'s base\n\t\tif not base.begins_with(BASE_PREFIX):\n\t\t\tvar dd: Array = _draw_distance(scene)\n\t\t\tif int(dd[0]) + int(dd[1]) > 0:\n\t\t\t\tprint("[worldskin] %s  %d part(s) given a draw distance, %d lit part(s) kept to any distance"\n\t\t\t\t\t% [base, int(dd[0]), int(dd[1])])\n\tif not is_kit:\n'), ('lines 1778-1779', "\n## Texels per metre, read off the surface's own vertices and UVs.\n", '\n## A DRAW DISTANCE FROM A PART\'S OWN SIZE (0.272.0). Nothing in a package had one: every mesh reported\n## `visibility_range_end = 0`, so a parking meter\'s window 200 m down the avenue cost a draw as one at your feet.\n## The walker, 2026-10-30: 60 FPS is the floor, and the level is not the whole frame -- guns, AI, sound and networking\n## need theirs -- "so smart LOD, culling techniques now will go a long way". An object\'s part is dropped where its\n## bounding sphere spans fewer than `DRAW_PX` pixels of a `DRAW_SCREEN_H` screen through the game\'s camera\n## (`DRAW_FOV_DEG`: the walk player\'s Camera3D sets none, so Godot\'s default; the price harness uses the same):\n##\n##     end = radius * (DRAW_SCREEN_H / 2) / tan(DRAW_FOV_DEG / 2) / DRAW_PX      -- about 235 x the radius\n##\n## Each PART by its own size, so a meter\'s window goes at about 35 m and its body at about 140 m: the small details\n## of a thing go first, which is the LOD a hand-made chain would give, from the model it already has. Measured\n## before it was written (the factory\'s `docs/findings/size_cull/`): at the slice\'s worst views 479-563 surfaces in\n## the frustum spanned under 3 px, most of them parts of props. A part that lights -- an emissive surface or any\n## shader material, which may be a lit screen or a swaying crown -- keeps every distance: a lamp\'s lens at night is\n## seen far past 3 px. A range something set already is kept. `DRAW_HYSTERESIS` of the range, as the end margin, so\n## a part at its threshold does not flicker. Only an object\'s GLB: a kit tile, a dressing and a building\'s base are\n## never given one. Returns [parts given a range, lit parts kept].\nconst DRAW_PX: float = 3.0\nconst DRAW_SCREEN_H: float = 1080.0\nconst DRAW_FOV_DEG: float = 75.0\nconst DRAW_HYSTERESIS: float = 0.1\n\n\nfunc _draw_distance(scene: Node) -> Array:\n\tvar k: float = (DRAW_SCREEN_H / 2.0) / tan(deg_to_rad(DRAW_FOV_DEG) / 2.0)\n\tvar found: Array = []\n\t_find_meshes(scene, found)\n\tvar set_n: int = 0\n\tvar lit_n: int = 0\n\tfor f in found:\n\t\tvar mi: MeshInstance3D = f as MeshInstance3D\n\t\tif mi.visibility_range_end > 0.0:\n\t\t\tcontinue\n\t\tvar lit: bool = false\n\t\tfor i in range(mi.mesh.get_surface_count()):\n\t\t\tvar m: Material = mi.get_active_material(i)\n\t\t\tvar bm: BaseMaterial3D = m as BaseMaterial3D\n\t\t\tif m is ShaderMaterial or (bm != null and bm.emission_enabled):\n\t\t\t\tlit = true\n\t\tif lit:\n\t\t\tlit_n += 1\n\t\t\tcontinue\n\t\tvar box: AABB = _stain_to_root(mi, scene) * mi.mesh.get_aabb()\n\t\tvar radius: float = box.size.length() / 2.0\n\t\tif radius <= 0.0:\n\t\t\tcontinue\n\t\tvar end: float = radius * k / DRAW_PX\n\t\tmi.visibility_range_end = end\n\t\tmi.visibility_range_end_margin = end * DRAW_HYSTERESIS\n\t\tset_n += 1\n\treturn [set_n, lit_n]\n\n\nfunc _find_meshes(n: Node, found: Array) -> void:\n\tvar mi: MeshInstance3D = n as MeshInstance3D\n\tif mi != null and mi.mesh != null and mi.mesh.get_surface_count() > 0:\n\t\tfound.append(mi)\n\tfor c in n.get_children():\n\t\t_find_meshes(c, found)\n\n\n## Texels per metre, read off the surface\'s own vertices and UVs.\n')]}
WHOLE = {}
NEW_FILES = {'tests/unit/test_worldskin_draw_distance.py': '"""A draw distance from each part\'s own size (0.272.0).\n\nNo mesh in a package had a draw distance. `_draw_distance` gives each part of an object\'s GLB the distance at which\nits bounding sphere spans `DRAW_PX` pixels of a `DRAW_SCREEN_H` screen through a `DRAW_FOV_DEG` camera, keeps any part\nthat lights to every distance, keeps a range already set, and runs on no kit tile, dressing or building base. Read\nas source, as the other worldskin tests are; the derivation is checked in numbers here.\n"""\nimport math\nimport re\nfrom pathlib import Path\n\nSCRIPT = Path(__file__).resolve().parents[2] / "assets" / "godot" / "zoo_worldskin.gd"\n\n\ndef _src() -> str:\n    return SCRIPT.read_text(encoding="utf-8")\n\n\ndef _func(src: str, name: str) -> str:\n    m = re.search(r"^func %s\\(.*?(?=^func |^## |\\Z)" % re.escape(name), src, re.S | re.M)\n    assert m, f"no func {name} in {SCRIPT.name}"\n    return m.group(0)\n\n\ndef _const(src: str, name: str) -> float:\n    m = re.search(r"^const %s: float = ([0-9.]+)$" % name, src, re.M)\n    assert m, name\n    return float(m.group(1))\n\n\ndef test_the_distance_is_derived_from_the_games_camera_and_a_pixel_threshold():\n    """FAILS ON 0.271.0: no draw distance."""\n    src = _src()\n    px, h, fov = _const(src, "DRAW_PX"), _const(src, "DRAW_SCREEN_H"), _const(src, "DRAW_FOV_DEG")\n    assert (px, h, fov) == (3.0, 1080.0, 75.0)\n    body = _func(src, "_draw_distance")\n    assert "var k: float = (DRAW_SCREEN_H / 2.0) / tan(deg_to_rad(DRAW_FOV_DEG) / 2.0)" in body\n    assert "var end: float = radius * k / DRAW_PX" in body\n    # about 235 x the radius: a meter\'s 0.15 m window at about 35 m, its 0.6 m body at about 140 m\n    k = (h / 2.0) / math.tan(math.radians(fov) / 2.0)\n    assert 234.0 < k / px < 235.0\n    assert 30.0 < 0.15 * k / px < 40.0 and 130.0 < 0.6 * k / px < 150.0\n\n\ndef test_the_walk_camera_is_the_one_derived_from():\n    """`DRAW_FOV_DEG` is Godot\'s default because the walk player\'s Camera3D sets none; one that set a FOV would make\n    this constant wrong."""\n    player = (SCRIPT.parent / "player_walk.tscn").read_text(encoding="utf-8")\n    assert "fov" not in player\n\n\ndef test_a_lit_part_and_a_range_already_set_are_kept():\n    body = _func(_src(), "_draw_distance")\n    assert "if mi.visibility_range_end > 0.0:" in body\n    assert "m is ShaderMaterial or (bm != null and bm.emission_enabled)" in body\n    assert "mi.visibility_range_end_margin = end * DRAW_HYSTERESIS" in body\n    # the part\'s own size, in the GLB\'s space\n    assert "var box: AABB = _stain_to_root(mi, scene) * mi.mesh.get_aabb()" in body\n\n\ndef test_only_an_objects_glb_never_a_kit_tile_dressing_or_base():\n    post = _func(_src(), "_post_import")\n    call = post.index("_draw_distance(scene)")\n    branch = post.rfind("if not is_kit and not _is_tiled(base):", 0, call)\n    assert branch != -1 and post.rfind("\\n\\tif ", branch + 1, call) == -1\n    assert "if not base.begins_with(BASE_PREFIX):" in post[branch:call]\n'}


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
