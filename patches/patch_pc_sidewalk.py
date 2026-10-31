"""Pixelcoat 0.68.0: Delco's sidewalk, flecked with gum.

sidewalk_delco gains grime and gum wear layers; the art baseline re-snapshotted.

Proven: tests/test_sidewalk_gum.py fails on 0.67.0 (fails_on_old.out.txt); the clone's suite, 685 passed
(suite_clone.out.txt); the map re-baked on the slice (the factory's docs/findings/sodium_pools/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'pixelcoat'
PINS = {'CHANGELOG.md': '18b2c4acec11fb71', 'VERSION': '399e8ac70b6c8ed3', 'pixelcoat/version.py': '12a34677fd1d25ec', 'profiles/materials/sidewalk_delco.json': '8af3c429c4e998e5', 'tools/art_standard_baseline.json': '2caa63b5bc3f44d3'}
EDITS = {'CHANGELOG.md': [('lines 1-2', '# Changelog\n\n', '# Changelog\n\n## [0.68.0] - Delco\'s sidewalk, flecked with gum\n\nThe walker, of the game\'s vertical slice: "keep getting us closer to that amazing vertical slice look".\n\n### Changed\n- **`sidewalk_delco` gains two `wear` layers**: a 1999 Philly sidewalk is flecked with flattened gum and patched with\n  grime, and the slice\'s slabs were clean. Broad soft grime (fbm 3 cells, 14 % of the tile, feathered, #5a5751 at\n  0.3) and gum (fbm 64 cells on the 2.5 m tile, 1.8 %, hard-edged, #2b2927 at 0.8, 0.25 glossier). Re-baked on the\n  slice\'s walk copy with the map swapped in (the factory\'s `docs/findings/sodium_pools/`): flecks across the near slabs,\n  no repeat seen at 2.5 m. A map: no draw moves.\n- **`tools/art_standard_baseline.json` re-snapshotted**: hf_energy 0.062 -> 0.069, rough_mean 0.930 -> 0.927, both\n  the gum, both inside the environment budget (rough_mean_min 0.45).\n\nTests: tests/test_sidewalk_gum.py (fails on 0.67.0).\n\n')], 'VERSION': [('lines 1-1', 'Pixelcoat 0.67.0', 'Pixelcoat 0.68.0')], 'pixelcoat/version.py': [('lines 33-33', '_FALLBACK = "0.67.0"\n', '_FALLBACK = "0.68.0"\n')], 'profiles/materials/sidewalk_delco.json': [('lines 42-43', '  },\n  "detail_strength": 0.2,\n', '  },\n  "wear": [\n    {\n      "generator": {\n        "generator": "fbm",\n        "cells": 3,\n        "octaves": 3\n      },\n      "coverage": 0.14,\n      "feather": 0.7,\n      "color": "#5a5751",\n      "strength": 0.3\n    },\n    {\n      "generator": {\n        "generator": "fbm",\n        "cells": 64,\n        "octaves": 2\n      },\n      "coverage": 0.018,\n      "feather": 0.05,\n      "color": "#2b2927",\n      "strength": 0.8,\n      "roughness": -0.25\n    }\n  ],\n  "detail_strength": 0.2,\n'), ('lines 72-72', '  "notes": "A concrete walk is SLABS: a 2x2 grid of scored joints on a 2.5 m tile is 1.25 m squares, which is what a Delco sidewalk is poured in. REFUTED ON THE WAY: the white mosaic on the frames was read as the meso Worley and it was the `edges` crack network (5 cells at 0.35 strength) -- adding slabs without fixing that gave a sidewalk wearing both. Edges are now hairlines and nearly nothing (0.07 at a 0.985 threshold): at 0.16 the crack web still read over the slabs, so the walk wore both; the joints are the masonry grid and the face is fine sand. CORRECTED after cold run 9041: the crack layer is a closed tessellation, so the \'few long cracks\' the retune claimed were a honeycomb at every threshold. sparsity 0.28 breaks it. WET VARIANT: a sidewalk is under awnings and trees for part of its run and its slabs drain to their joints, so it reads slightly less uniformly wet than the road beside it.",\n', '  "notes": "GUM AND GRIME (0.68.0): a 1999 Philly sidewalk is flecked with flattened gum and patched with grime, and the vertical slice\'s slabs were clean. Two `wear` layers: broad soft grime (fbm 3 cells, 14 %, feathered) and gum -- fbm at 64 cells on the 2.5 m tile, 1.8 %, hard-edged, near black and a little glossier. Re-baked on the slice with the map swapped in (the factory\'s docs/findings/sodium_pools/): flecks read across the near slabs and no repeat shows. A concrete walk is SLABS: a 2x2 grid of scored joints on a 2.5 m tile is 1.25 m squares, which is what a Delco sidewalk is poured in. REFUTED ON THE WAY: the white mosaic on the frames was read as the meso Worley and it was the `edges` crack network (5 cells at 0.35 strength) -- adding slabs without fixing that gave a sidewalk wearing both. Edges are now hairlines and nearly nothing (0.07 at a 0.985 threshold): at 0.16 the crack web still read over the slabs, so the walk wore both; the joints are the masonry grid and the face is fine sand. CORRECTED after cold run 9041: the crack layer is a closed tessellation, so the \'few long cracks\' the retune claimed were a honeycomb at every threshold. sparsity 0.28 breaks it. WET VARIANT: a sidewalk is under awnings and trees for part of its run and its slabs drain to their joints, so it reads slightly less uniformly wet than the road beside it.",\n')], 'tools/art_standard_baseline.json': [('lines 845-845', '      "chroma_mean": 0.011550065078511923,\n', '      "chroma_mean": 0.011334354380193656,\n'), ('lines 849-849', '      "hf_energy": 0.0623945826392481,\n', '      "hf_energy": 0.06889202965181884,\n'), ('lines 851-851', '      "rough_mean": 0.9298452339920343,\n', '      "rough_mean": 0.9265450271905638,\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_sidewalk_gum.py': '"""Delco\'s sidewalk is flecked with gum and patched with grime (0.68.0).\n\nA 1999 Philly sidewalk; the vertical slice\'s slabs were clean. The map is minted here as the theme library mints it\nand its near-black flecks counted.\n\nFAILS ON 0.67.0: 0.1 % of the tile under the cut, the mortar\'s corners; with the gum 1.7 %.\n"""\nimport os\nimport subprocess\nimport sys\n\nimport numpy as np\nfrom PIL import Image\n\nROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))\n\n\ndef test_the_delco_sidewalk_is_flecked_with_gum(tmp_path):\n    out = tmp_path / "s"\n    r = subprocess.run([sys.executable, "-m", "pixelcoat.cli.main", "proc-pack",\n                        os.path.join(ROOT, "profiles", "materials", "sidewalk_delco.json"),\n                        "--out", str(out), "--asset-id", "sidewalk_delco", "--size", "256"],\n                       cwd=ROOT, capture_output=True, text=True)\n    assert r.returncode == 0, r.stdout + r.stderr\n    luma = np.asarray(Image.open(out / "sidewalk_delco_albedo.png").convert("L"), dtype=float) / 255.0\n    flecks = float((luma < 0.28).mean())\n    assert 0.01 <= flecks <= 0.04, flecks\n'}


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
