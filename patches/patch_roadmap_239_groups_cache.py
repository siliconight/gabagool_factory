"""Roadmap 239: cold run 9256 (Level Factory 0.190.0 in a drive) and Level Factory 0.191.0, the
bake's editor given the scene groups cache it would build first. Two anchors, each asserted once,
nothing written on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_groups_cache.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "the drive 7.8 minutes. Open: the editor's bake (96 s of the export), the Lux job's staging "
     "and the work done for a cache hit before the cache is asked, the Blender builds' "
     "reproducibility, and the grader's step (4x against the game's 1/60 s), the walker's call. "
     "The shared textures' compression was the walker's call too, made 2026-10-12 -- compressed "
     "everywhere: Level Factory 0.190.0 pins what an editor decides, and the bake's editor now "
     "changes none of the package's 572 texture sidecars where it changed 426.*",
     "the drive 7.8 minutes. The shared textures' compression was the walker's call, made "
     "2026-10-12 -- compressed everywhere: Level Factory 0.190.0 pins what an editor decides, and "
     "the bake's editor now changes none of the package's 572 texture sidecars where it changed "
     "426; cold run 9256: the export 217 -> 204 s, the drive 7.5 minutes. Then the bake's editor, "
     "timed step by step: for its first 20 s it loaded every model to read the scenes' groups, a "
     "cache the export's headless imports never wrote; Level Factory 0.191.0 writes it from the "
     "scenes' own text, and re-exported, change and control alternated, the editor took 69.3 and "
     "67.5 s against 87.6 and 92.6, the lightmap within what two exports differ by. Open: the "
     "editor's scene opening and bake (about 56 s of its 68), the Lux job's staging and the work "
     "done for a cache hit before the cache is asked, the Blender builds' reproducibility, and the "
     "grader's step (4x against the game's 1/60 s), the walker's call.*"),
    ("item 1's editor",
     "opened the scene in 14.7 s against 20.3. Left: the editor's bake.",
     "opened the scene in 14.7 s against 20.3; cold run 9256: the export 217 -> 204 s, the drive "
     "7.5 minutes. **THE EDITOR'S FIRST TWENTY SECONDS: Level Factory 0.191.0.** "
     "`docs/findings/grader_speed/bake_phases_probe.py` swaps the bake's plugin for a copy that "
     "prints the engine's clock at each step: on 9256's workspace the plugin waited 27.5 s before "
     "it asked for the scene, and under `--verbose` the editor's log shows that wait loading every "
     "one of the package's 482 models and their textures, its file system scanning throughout -- "
     "a Godot 4.7 editor whose project has no `.godot/scene_groups_cache.cfg` reads every scene's "
     "groups first, and the export's headless imports never write one. 0.191.0 writes the cache "
     "from the scenes' own `[node ...]` headers (on 9256's 22 scenes exactly the editor's own, 3 "
     "scenes) before the work copy is made. Four re-exports, change and control alternated: the "
     "scene asked for at 13.6 and 13.1 s against 32.5 and 33.8, the editor 69.3 and 67.5 s "
     "against 87.6 and 92.6, every package differing from 9256's own in the same 21 files the "
     "control's does, and the lightmap, texel by texel (`lightmap_compare.py`), nearer the "
     "control's than two exports of 0.190.0 are to each other. **Found on the way:** 0.190.0 "
     "moved the baked light -- 9256's lightmap against 9255's differs by 2 % of its mean on "
     "average, four times what two exports differ by; whether that shows is a question for "
     "frames. Left: the scene's opening (about 19 s: the level loaded again and its shaders "
     "compiled into an empty shader cache) and the bake (35 s)."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "Level Factory 0.191.0.**" not in text, "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's cold run 9256 and Level Factory 0.191.0 recorded; now roadmap_status.py "
          "--write / --check")


if __name__ == "__main__":
    sys.exit(main())
