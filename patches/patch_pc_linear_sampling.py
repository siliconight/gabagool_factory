"""Pixelcoat 0.64.0: a material pack asks to be sampled linear (the factory's roadmap 324).

`build_material_pack` asked every consumer for `nearest` sampling, the retro look's; it now asks for `linear`, with the
mip chain every pack already asked for. Zoo 1.144.0 honours the hint. Signs' pixel lettering and decals unchanged.

Proven: tests/test_material_grammar.py's new test fails on 0.63.0 (fails_on_old.out.txt); the clone's suite, 678
passed, 1 skipped.
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'pixelcoat'
PINS = {'CHANGELOG.md': '45e492cfd26f65b3', 'VERSION': '134ab23e816f6181', 'pixelcoat/core/material_grammar.py': 'f74d5f76d2319522', 'pixelcoat/version.py': '57bd8291c4525c7d', 'tests/test_material_grammar.py': '1158d2f1c5a625c9'}
EDITS = {'CHANGELOG.md': [('lines 1-2', '# Changelog\n\n', '# Changelog\n\n## [0.64.0] - a material pack asks to be sampled linear\n\nThe factory\'s roadmap 324. The walker, 2026-10-28: "how would we make our assets look more realistic?", and the target,\n"the look of Xbox 360 Games like Halo 3 and Gears of War ... we don\'t have to make it look like Runescape either". Every\ngrammar pack asked its consumer for `nearest` sampling -- the retro look\'s, kept after realism replaced it -- and with\n53 of the 118 shipped packs at 128 px that is what read as blocky up close. `build_material_pack` now asks for\n`linear`, with the mip chain every pack already asked for. Zoo 1.144.0 honours the hint (it hardcoded Closest before).\nA sign\'s pixel lettering still asks for itself (`signage`), and decals are unchanged. The hint is in the manifest, so\na consumer hashing it sees the change. Tests: tests/test_material_grammar.py, a material pack asks to be sampled\nlinear (fails on 0.63.0).\n\n')], 'VERSION': [('lines 1-1', 'Pixelcoat 0.63.0', 'Pixelcoat 0.64.0')], 'pixelcoat/core/material_grammar.py': [('lines 886-886', '            "interpolation": "nearest",\n', '            # LINEAR (0.64.0, the factory\'s roadmap 324): a surface sampled\n            # with filtering and its mip chain, as the factory\'s art target\n            # asks -- "the look of Xbox 360 Games like Halo 3 and Gears of\n            # War" (the walker, 2026-10-28). `nearest` was the retro look\'s,\n            # and kept a 128 px tile blocky up close after realism replaced\n            # it. A sign\'s pixel lettering asks for itself (`signage`).\n            "interpolation": "linear",\n')], 'pixelcoat/version.py': [('lines 33-33', '_FALLBACK = "0.63.0"\n', '_FALLBACK = "0.64.0"\n')], 'tests/test_material_grammar.py': [('lines 238-238', '    assert slab.masonry["offset"] == 0.0                       # a grid, not a bond\n', '    assert slab.masonry["offset"] == 0.0                       # a grid, not a bond\n\n\ndef test_a_material_pack_asks_to_be_sampled_linear(tmp_path):\n    """0.64.0 (the factory\'s roadmap 324): every grammar pack asks its consumer for filtered sampling with mips, the\n    art target\'s; Zoo 1.144.0 honours the hint. FAILS ON 0.63.0, which asked for `nearest`."""\n    for name in ("painted_metal_industrial",):\n        manifest = mg.build_material_pack(os.path.join(_PROFILES, name + ".json"), str(tmp_path / name), size=48)\n        hints = manifest["import_hints"]\n        assert hints["interpolation"] == "linear" and hints["generate_mipmaps"] is True\n')]}
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
