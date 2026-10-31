"""Pixelcoat 0.67.0: Delco's road paint, worn.

road_paint_delco dirtier, 80 % coverage at a 1 m wear field; the art baseline re-snapshotted.

Proven: tests/test_road_paint_worn.py fails on 0.66.0 (fails_on_old.out.txt); the clone's suite, 684 passed
(suite_clone.out.txt); the map re-baked on the slice (the factory's docs/findings/sodium_pools/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'pixelcoat'
PINS = {'CHANGELOG.md': 'e13cfe71bcb6fec7', 'VERSION': '1d10f67e6b45cf45', 'pixelcoat/version.py': 'a1b523560fced743', 'profiles/materials/road_paint_delco.json': 'be2dd615d349a9f9', 'tools/art_standard_baseline.json': 'bd79b4334e0d9473'}
EDITS = {'CHANGELOG.md': [('lines 1-2', '# Changelog\n\n', '# Changelog\n\n## [0.67.0] - Delco\'s road paint, worn\n\nThe walker, of the game\'s vertical slice: "keep getting us closer to that amazing vertical slice look".\n\n### Changed\n- **`road_paint_delco`**: the avenue\'s lines read crisp and new -- 90 % coverage, an off-white at 0.87 -- on a street\n  meant to be 1999\'s. Dirt-grey base colours (#cfcac0 / #c2bdb2 / #d8d3c9, the map 0.75), `detail_strength` 0.2,\n  `cutout.coverage` 0.8 with its field at 8 cells (1 m) instead of 4, so the loss is ragged nicks along a line.\n  **Refused on the way, kept in the grammar\'s notes:** 70 % at 4 cells cut the edge lines into random dashes that read\n  as a broken lane line. Re-baked on the slice\'s walk copy with each map swapped in (the factory\'s\n  `docs/findings/sodium_pools/`); a map, so no draw moves.\n- **`tools/art_standard_baseline.json` re-snapshotted**: worn paint is wider-ranged by construction -- value_range\n  0.167 -> 0.305, hf_energy 0.077 -> 0.090 -- inside the environment budget (value_range 0.500).\n\nTests: tests/test_road_paint_worn.py (fails on 0.66.0).\n\n')], 'VERSION': [('lines 1-1', 'Pixelcoat 0.66.0', 'Pixelcoat 0.67.0')], 'pixelcoat/version.py': [('lines 33-33', '_FALLBACK = "0.66.0"\n', '_FALLBACK = "0.67.0"\n')], 'profiles/materials/road_paint_delco.json': [('lines 5-7', '    "#e6e3dc",\n    "#d8d4ca",\n    "#efece5"\n', '    "#cfcac0",\n    "#c2bdb2",\n    "#d8d3c9"\n'), ('lines 29-29', '  "detail_strength": 0.15,\n', '  "detail_strength": 0.2,\n'), ('lines 39-39', '      "cells": 4,\n', '      "cells": 8,\n'), ('lines 42-42', '    "coverage": 0.9\n', '    "coverage": 0.8\n'), ('lines 52-52', '  "notes": "An 8 m tile, not 0.5 m, because Lot projects this pack in WORLD space (uv1_world_triplanar at 1/meters_per_tile) and a crosswalk bar is 0.5 m wide on a 1.0 m pitch: at 0.5 m every bar of a crosswalk sampled the same phase of the tile, and every bar repeated the same holes every 0.5 m down its 9.4 m length -- measured on cold run 9044\'s themed build, 36 of 36 bar pairs within a crosswalk and 84 of 210 across the site pixel-identical. The walker\'s question was why the paint wore in identical blotches. The colour bands keep their size in metres (every cell count x16). The wear is fbm from 4 cells (2 m) down six octaves to 6 cm, so a whole stretch of paint is worn or intact and the nicks inside it are ragged; `coverage` 0.9 keeps nine tenths of the tile at the field\'s own quantile, because the fixed 0.40 threshold this carried would have kept 70% at these octaves. RESIDUE THIS CANNOT REMOVE: any world-space period repeats wherever two bars stand a multiple of it apart (5 of 210 pairs on 9044 still match within 24 cm of shift at 8 m; a 7.7 m tile only moved which pairs); a per-marking uv offset in Lot is what ends that. 1024 px at 8 m is the library\'s 128 px/m. WET VARIANT: a paint film is not porous, so it responds like painted metal -- the least darkening of the four presets (0.30). Its cavity bias is low because a flat film has almost no recesses to pool in; the water is on it, not in it.",\n', '  "notes": "WORN, 1999 (0.67.0): the paint read crisp and new on the vertical slice\'s avenue -- 90 % coverage, an off-white at 0.87. A 1999 Delco street\'s lines are dirty and chipped: dirt-grey colours (0.75), 80 % coverage, the wear field at 8 cells (1 m) not 4, so the loss is ragged nicks along a line, not missing stretches. 70 % at 4 cells was tried first and refused from its frames: it cut the edge lines into random dashes that read as a broken lane line (the factory\'s docs/findings/sodium_pools/). PREVIOUSLY: An 8 m tile, not 0.5 m, because Lot projects this pack in WORLD space (uv1_world_triplanar at 1/meters_per_tile) and a crosswalk bar is 0.5 m wide on a 1.0 m pitch: at 0.5 m every bar of a crosswalk sampled the same phase of the tile, and every bar repeated the same holes every 0.5 m down its 9.4 m length -- measured on cold run 9044\'s themed build, 36 of 36 bar pairs within a crosswalk and 84 of 210 across the site pixel-identical. The walker\'s question was why the paint wore in identical blotches. The colour bands keep their size in metres (every cell count x16). The wear is fbm from 4 cells (2 m) down six octaves to 6 cm, so a whole stretch of paint is worn or intact and the nicks inside it are ragged; `coverage` 0.9 keeps nine tenths of the tile at the field\'s own quantile, because the fixed 0.40 threshold this carried would have kept 70% at these octaves. RESIDUE THIS CANNOT REMOVE: any world-space period repeats wherever two bars stand a multiple of it apart (5 of 210 pairs on 9044 still match within 24 cm of shift at 8 m; a 7.7 m tile only moved which pairs); a per-marking uv offset in Lot is what ends that. 1024 px at 8 m is the library\'s 128 px/m. WET VARIANT: a paint film is not porous, so it responds like painted metal -- the least darkening of the four presets (0.30). Its cavity bias is low because a flat film has almost no recesses to pool in; the water is on it, not in it.",\n')], 'tools/art_standard_baseline.json': [('lines 808-809', '      "blown_frac": 0.30645751953125,\n      "chroma_mean": 0.017186821239022765,\n', '      "blown_frac": 0.0753326416015625,\n      "chroma_mean": 0.019050014629965625,\n'), ('lines 813-813', '      "hf_energy": 0.07663848427755691,\n', '      "hf_energy": 0.0899714206529233,\n'), ('lines 817-817', '      "value_range": 0.1673910786845857\n', '      "value_range": 0.3045595735924407\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_road_paint_worn.py': '"""Delco\'s road paint is a 1999 street\'s: dirty and chipped (0.67.0).\n\nIt read crisp and new on the vertical slice\'s avenue: 90 % coverage, an off-white at 0.87. The map is minted here as the\ntheme library mints it; its gaps and its brightness are held to a worn line\'s.\n\nFAILS ON 0.66.0: a tenth gone and 0.87 bright.\n"""\nimport os\nimport subprocess\nimport sys\n\nimport numpy as np\nfrom PIL import Image\n\nROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))\n\n\ndef test_the_delco_road_paint_is_worn(tmp_path):\n    out = tmp_path / "p"\n    r = subprocess.run([sys.executable, "-m", "pixelcoat.cli.main", "proc-pack",\n                        os.path.join(ROOT, "profiles", "materials", "road_paint_delco.json"),\n                        "--out", str(out), "--asset-id", "road_paint_delco", "--size", "512"],\n                       cwd=ROOT, capture_output=True, text=True)\n    assert r.returncode == 0, r.stdout + r.stderr\n    a = np.asarray(Image.open(out / "road_paint_delco_albedo.png").convert("RGBA"), dtype=float) / 255.0\n    gone = float((a[..., 3] < 0.5).mean())\n    assert 0.15 <= gone <= 0.25, gone\n    assert float(a[..., :3][a[..., 3] >= 0.5].mean()) <= 0.8\n'}


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
