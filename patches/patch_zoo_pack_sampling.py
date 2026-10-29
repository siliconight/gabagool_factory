"""Zoo 1.144.0: a pack material samples its textures as the pack asks (the factory's roadmap 324).

`materials._textured` hardcoded Closest while `skins.load_pack` read the pack's `interpolation` hint; it now asks the
pack, as the sign path has since 1.94.0. Every Pixelcoat pack says `nearest` today, so nothing built changes until
Pixelcoat asks for `linear`.

Proven: tests/test_pack_sampling.py fails on 1.143.0 in Blender (fails_on_old.out.txt); the clone's suite, 7060
passed, 544 skipped (bpy), 1 xfailed; the new tests pass in Blender 5.1.
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'zoo'
PINS = {'CHANGELOG.md': 'e13ae808b54658e8', 'VERSION': '81127854aade1468', 'zoo_keeper/bpylayer/materials.py': 'bfc71f980a752126'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [1.143.0] - a vault rack is blue painted steel, its bricks pale\n', '## [1.144.0] - a pack material samples its textures as the pack asks\n\nThe factory\'s roadmap 324; the walker, 2026-10-28: "how would we make our assets look more realistic?", and the\ntarget, "the look of Xbox 360 Games like Halo 3 and Gears of War". `skins.load_pack` has read a pack\'s\n`interpolation` hint since 1.94.0, and the sign path honoured it; the pack material (`materials._textured`) hardcoded\nClosest -- "pixel art stays pixel art" -- so a pack asking for `linear` was sampled nearest anyway, the retro look\'s\nsampling kept after realism replaced it. It now asks the pack, as a sign does. A pack that does not say keeps Closest,\nand every Pixelcoat pack says `nearest` today, so nothing built changes until Pixelcoat asks for `linear`: this is the\ndial, turned there. Tests: tests/test_pack_sampling.py, run in Blender (fails on 1.143.0).\n\n## [1.143.0] - a vault rack is blue painted steel, its bricks pale\n')], 'VERSION': [('lines 1-1', '1.143.0', '1.144.0')], 'zoo_keeper/bpylayer/materials.py': [('lines 739-742', '    bsdf.inputs["Metallic"].default_value = METALLIC.get(material_kind, 0.0)\n    maps = pack["maps"]\n\n    def tex_node(path, non_color=False):\n', '    bsdf.inputs["Metallic"].default_value = METALLIC.get(material_kind, 0.0)\n    maps = pack["maps"]\n    # AS THE PACK ASKS (1.144.0, the factory\'s roadmap 324), as a sign\'s has\n    # since 1.94.0: `skins.load_pack` reads the pack\'s `interpolation` hint,\n    # and this hardcoded Closest -- "pixel art stays pixel art" -- so a pack\n    # asking for `linear` was sampled nearest anyway, and a 128 px tile read\n    # as blocky up close. A pack that does not say keeps Closest.\n    filt = "Linear" if pack.get("interpolation") == "linear" else "Closest"\n\n    def tex_node(path, non_color=False):\n'), ('lines 745-745', '        node.interpolation = "Closest"       # pixel art stays pixel art\n', '        node.interpolation = filt\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_pack_sampling.py': '"""A pack material samples its textures as the pack asks (1.144.0, the factory\'s roadmap 324).\n\n`skins.load_pack` has read a pack\'s `interpolation` hint since 1.94.0 and the sign path honoured it; the pack material\n(`materials._textured`) hardcoded Closest, so a pack asking for `linear` was sampled nearest anyway -- the retro look\'s\nsampling, kept after realism replaced it. A pack that does not say keeps Closest. FAILS ON 1.143.0.\n\n    blender -b --factory-startup --python-expr "import sys, pytest; sys.path.insert(0, \'.\'); print(\'rc\', int(pytest.main([\'-q\', \'-p\', \'no:cacheprovider\', \'tests/test_pack_sampling.py\'])))"\n"""\nfrom __future__ import annotations\n\nimport struct\nimport zlib\n\nimport pytest\n\n\ndef _png(path, rgb=(128, 96, 64)):\n    """A 2 x 2 RGB PNG, written by hand so the test needs no imaging library."""\n    def chunk(tag, data):\n        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)\n    rows = b"".join(b"\\x00" + bytes(rgb) * 2 for _ in range(2))\n    path.write_bytes(b"\\x89PNG\\r\\n\\x1a\\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))\n                     + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))\n    return str(path)\n\n\ndef _filters(tmp_path, name, interpolation):\n    from zoo_keeper.bpylayer import materials\n    maps = {k: _png(tmp_path / ("%s_%s.png" % (name, k))) for k in ("albedo", "roughness", "normal")}\n    pack = {"maps": maps, "meters_per_tile": 1.0}\n    if interpolation is not None:\n        pack["interpolation"] = interpolation\n    mat = materials._textured(name, pack, "metal")\n    return {n.interpolation for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}\n\n\ndef test_bpy_a_pack_asking_for_linear_is_sampled_linear(tmp_path):\n    pytest.importorskip("bpy")\n    assert _filters(tmp_path, "zoo_t_linear", "linear") == {"Linear"}\n\n\ndef test_bpy_a_pack_that_does_not_say_keeps_closest(tmp_path):\n    pytest.importorskip("bpy")\n    assert _filters(tmp_path, "zoo_t_unsaid", None) == {"Closest"}\n    assert _filters(tmp_path, "zoo_t_nearest", "nearest") == {"Closest"}\n'}


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
