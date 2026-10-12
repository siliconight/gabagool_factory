"""Roadmap 239: every model imported once (Level Factory 0.189.0), measured by re-exporting cold
run 9254 and in cold run 9255, and the lossless pins that no editor keeps, found on the way and
left to the walker. Two anchors, each asserted once, nothing written on a miss. Run
`python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_models_once.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "Open: the sidecar step's two passes, the Lux job's staging and the work done for a cache hit "
     "before the cache is asked, the Blender builds' reproducibility, and the grader's step (4x "
     "against the game's 1/60 s, the walker's call).*",
     "Then the sidecar step: Level Factory 0.189.0 imports every model once, in three passes over "
     "three sets; cold run 9255: the export 241 -> 217 s, the drive 7.8 minutes. Open: the editor's "
     "bake (96 s of the export), the Lux job's staging and the work done for a cache hit before the "
     "cache is asked, the Blender builds' reproducibility, and two calls for the walker -- the "
     "grader's step (4x against the game's 1/60 s) and the shared textures' compression, which no "
     "editor leaves lossless.*"),
    ("item 1's left",
     "cold run 9254, the walk step 88 -> 11 s, the drive 9.7 -> 8.4 minutes, 0 interventions. Left: "
     "the sidecar step's two passes.",
     "cold run 9254, the walk step 88 -> 11 s, the drive 9.7 -> 8.4 minutes, 0 interventions. "
     "**The sidecar step's two passes: Level Factory 0.189.0** "
     "(`docs/findings/grader_speed/sidecar_once_probe.py`): every model imported once, with its "
     "final settings -- the textures first (a model imported before them embeds a copy of each, "
     "1,463 surfaces in 461 models with every gate passing, seen only by `import_digest.gd`), the "
     "worldskin bases last, a model with a light baking of its own last from a whole sidecar (a "
     "model imported twice is the pin race; a written sidecar's missing key takes its pre-key "
     "value). Against 0.188.0's own step: 85.8 -> 61.5 s, the export 235.9 -> 212.2 s, 501 of 501 "
     "models loading the same; cold run 9255, the export 241 -> 217 s and the drive 8.4 -> 7.8 "
     "minutes, 0 interventions. **Found on the way, the walker's call:** every shipped `_tex/` "
     "sidecar keeps Godot's 3D detection, so every editor that opens the package -- the bake's, the "
     "walk copy opened to be walked, a recipient's -- re-encodes the textures the export pins "
     "lossless as VRAM compressed (426 in the bake editor's own log); the pins hold only in a "
     "headless import. Lossless everywhere (detection pinned off: about 5 s of the bake, more "
     "texture memory, a look change from what editors have shown) or VRAM everywhere (what editors "
     "have shown, roadmap 89's reason set aside): a look and memory trade, not changed. Left: the "
     "editor's bake."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**The sidecar step's two passes: Level Factory 0.189.0**" not in text, "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's 0.189.0, cold run 9255 and the texture finding recorded; now "
          "roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
