"""Patina 0.32.0 -- the Godot half is gone, and the version the outputs carry is the release's.

Factory roadmap 20 (filed 2026-08) asked for `ps1.gdshader` and the Patina plugin to be retired so the
vertex-colour channel means one thing everywhere. Re-read 2026-10-15 (`docs/findings/open_items_remeasure/`):
`patina/godot/` (8 files) is consumed by nothing in any tool repo, shipped in no package (cold run 9314: no
`addons/`, 0 `res://addons` references), its README still says it was never walked in the engine, and the channel
has one reader in a package -- Level Factory's `zoo_worldskin.gd`, albedo on objects. Nothing is left for the
folder to do. Found on the way: `patina/version.py` said 0.30.0 while `VERSION` said 0.31.0, so every manifest
and GLB of 0.31.0 carries `generator: "Patina 0.30.0"` (9314's `deli_a01.patina.json` does); a test now pins
the two together.

What this does, in the Patina repo:
  - `git rm -r godot/` (8 files, 27 KB).
  - Rewords the six places that described the Godot half as alive (README, docs/DESIGN.md, the package
    docstring, the manifest's shader comment, smoke_offline's last line).
  - VERSION and `patina/version.py` -> 0.32.0; a CHANGELOG entry.
  - Adds `tests/test_version_file.py`: `patina.__version__` equals the number in VERSION. It FAILS on 0.31.0's
    tree (0.30.0 against 0.31.0) and passes after this patch.

Every anchor is asserted once and every touched file is pinned by sha16; a miss refuses the whole patch.

    python patches/patch_patina_godot_half_gone.py
    (cd patina && python -m pytest -q)
"""
import hashlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATINA = ROOT / "patina"

SHA = {
    "README.md": "3838bbab7c52696c",
    "docs/DESIGN.md": "b9b004ab42d60bdd",
    "patina/__init__.py": "3fd31b15ada428bd",
    "patina/manifest.py": "36b65139117a2270",
    "smoke_offline.py": "9058406a1662cb6a",
    "VERSION": "8675831c6be7af3d",
    "patina/version.py": "0dd2a415fb4fc62b",
    "CHANGELOG.md": "9e5a171dce075fec",
}

DASH = "—"

EDITS = [
    ("README.md",
     "then hands the result to Godot ready to render in a PS1 style.",
     "then hands the result on as a styled `.glb` plus a manifest. The engine look is Lux's."),
    ("README.md",
     f"labor. Patina automates the mechanical steps that bracket that labor {DASH} vertex\n"
     f"nuance, box-projection UVs, procedural/posterized textures, and the PS1 render\n"
     f"setup {DASH} and marks the seams where a modeler or texture artist takes over.",
     f"labor. Patina automates the mechanical steps that bracket that labor {DASH} vertex\n"
     f"nuance, box-projection UVs and procedural/posterized textures {DASH} and marks the\n"
     f"seams where a modeler or texture artist takes over."),
    ("README.md",
     f"* `shell.patina.json` {DASH} style manifest the Godot addon reads (shader params,\n"
     f"  per-surface specs, kit-bash hooks).",
     f"* `shell.patina.json` {DASH} style manifest (per-surface specs, kit-bash hooks, and\n"
     f"  the shader params kept for the schema; nothing in-engine reads them since 0.32.0)."),
    ("README.md",
     f"Then in Godot: see [`godot/README.md`](godot/README.md) {DASH} enable the addon,\n"
     f"import the `.glb`, click **Apply PS1 style**.",
     f"Then in the engine: the `.glb` imports as any glTF does, and the look is Lux's. There\n"
     f"is no Patina addon since 0.32.0 {DASH} Level Factory's art pass runs this step for you."),
    ("docs/DESIGN.md",
     f"5. PS1 render look (Godot shader) {DASH} **Patina (YES).**",
     f"5. Engine render look {DASH} **Lux, not Patina** (the Godot half was retired in 0.32.0)."),
    ("docs/DESIGN.md",
     f"* **Godot addon (GDScript)** {DASH} `godot/addon/patina/`. Imports the styled `.glb`,\n"
     f"  reads the manifest, assigns the PS1 shader + material params per surface, sets\n"
     f"  white ambient + fog. First-run-in-engine.\n",
     f"* **Godot addon (GDScript)** {DASH} retired in 0.32.0. It was never walked in the engine, no\n"
     f"  tool consumed it and no package shipped it; the vertex-colour channel it read as lighting\n"
     f"  is read as albedo by Level Factory's `zoo_worldskin.gd`, and the engine look is Lux's.\n"),
    ("patina/__init__.py",
     "Public, stable surface for the offline asset pass. The Godot side lives under\n"
     "``godot/`` and is wired up in-engine, not imported here.",
     "Public, stable surface for the offline asset pass. There is no Godot side since\n"
     "0.32.0: the engine look is Lux's, and the styled ``.glb`` imports as any glTF does."),
    ("patina/manifest.py",
     "# Default PS1 shader parameters (the in-engine half reads these). Tuned to the\n"
     "# \"minimal / readability-first\" principle, not maximal grunge.",
     "# Default PS1 shader parameters, kept for the manifest's schema. Nothing in-engine\n"
     "# reads them since 0.32.0 retired the Godot half; they record the look the pass was\n"
     "# tuned to -- \"minimal / readability-first\", not maximal grunge."),
    ("smoke_offline.py",
     '    print("Next: the Blender/Godot walk (smoke_walk.ps1) for the in-engine half.")',
     '    print("Next: the Blender/Godot walk (smoke_walk.ps1), which opens Lux on the result.")'),
    ("VERSION", "Patina 0.31.0", "Patina 0.32.0"),
    ("patina/version.py", '__version__ = "0.30.0"', '__version__ = "0.32.0"'),
    ("CHANGELOG.md",
     "versioning follows [SemVer](https://semver.org/).\n\n## [0.31.0] - a prop is not the building",
     "versioning follows [SemVer](https://semver.org/).\n\n"
     "## [0.32.0] - the Godot half is gone\n\n"
     "Factory roadmap 20, filed 2026-08 and re-read 2026-10-15 against cold run 9314's package.\n\n"
     "### Removed\n"
     "- **`godot/`** -- the editor plugin, its dock, `patina_apply.gd` and both copies of `ps1.gdshader`\n"
     "  (8 files). Measured before deleting: no tool repo referenced any of them, no package shipped them\n"
     "  (9314: no `addons/` directory, 0 `res://addons` references), and their own README still said the\n"
     "  half had never been walked in the editor. The shader was the one reader of the vertex-colour\n"
     "  channel that took it as lighting; the one reader a package has, Level Factory's\n"
     "  `zoo_worldskin.gd`, takes it as albedo on objects and leaves it off on tiles (factory roadmap\n"
     "  84). The engine look is Lux's. The offline pass -- vertex nuance, banding, mottle, per-slot\n"
     "  variation, auto-UV, anchors, dressing -- is untouched, and `shell.patina.json` keeps its\n"
     "  `shader` block for the schema's sake (0.2.0 unchanged); nothing in-engine reads it.\n\n"
     "### Fixed\n"
     "- **The version the outputs carried was not the release's.** `patina/version.py` said 0.30.0\n"
     "  while `VERSION` said 0.31.0, so every 0.31.0 manifest and GLB wrote `generator: \"Patina\n"
     "  0.30.0\"` (cold run 9314's `deli_a01.patina.json` does). Both read 0.32.0 now and\n"
     "  `tests/test_version_file.py` pins them together; it fails on 0.31.0's tree.\n\n"
     "## [0.31.0] - a prop is not the building"),
]

TEST = '''"""`patina.__version__` is the number in VERSION (0.32.0).

The two had drifted: 0.31.0 bumped `VERSION` and not `patina/version.py`, so every manifest and GLB of that
release wrote `generator: "Patina 0.30.0"`. The version is what makes an output traceable to the code that
made it, and a wrong one is worse than none. This fails on 0.31.0's tree.
"""
import pathlib

import patina

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_module_version_is_the_version_file():
    text = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert text.startswith("Patina "), text
    assert patina.__version__ == text.split()[1]
'''


def sha16(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main():
    for rel, want in SHA.items():
        p = PATINA / rel
        got = sha16(p)
        assert got == want, f"{rel}: sha16 {got}, patch written against {want} -- re-ground before applying"
        assert b"\r\n" not in p.read_bytes(), f"{rel} is CRLF; the patch assumes LF"
    assert (PATINA / "godot").is_dir(), "godot/ already gone"
    assert not (PATINA / "tests" / "test_version_file.py").exists(), "the test already exists"
    texts = {}
    for rel, old, new in EDITS:
        text = texts.get(rel) or (PATINA / rel).read_text(encoding="utf-8")
        assert text.count(old) == 1, (rel, old[:60])
        texts[rel] = text.replace(old, new)
    # Every anchor held: now write.
    for rel, text in texts.items():
        (PATINA / rel).write_text(text, encoding="utf-8", newline="\n")
    (PATINA / "tests" / "test_version_file.py").write_text(TEST, encoding="utf-8", newline="\n")
    subprocess.run(["git", "rm", "-r", "-q", "godot"], cwd=PATINA, check=True)
    assert not (PATINA / "godot").exists()
    print("Patina 0.32.0 applied: godot/ removed, 6 texts reworded, versions 0.32.0, test added; now the suite")


if __name__ == "__main__":
    sys.exit(main())
