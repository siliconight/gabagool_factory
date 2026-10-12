"""Roadmap 239: the shared textures' compression, decided by the walker (compressed everywhere) and
done by Level Factory 0.190.0. Two anchors, each asserted once, nothing written on a miss. Run
`python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_compressed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "and two calls for the walker -- the grader's step (4x against the game's 1/60 s) and the "
     "shared textures' compression, which no editor leaves lossless.*",
     "and the grader's step (4x against the game's 1/60 s), the walker's call. The shared "
     "textures' compression was the walker's call too, made 2026-10-12 -- compressed everywhere: "
     "Level Factory 0.190.0 pins what an editor decides, and the bake's editor now changes none of "
     "the package's 572 texture sidecars where it changed 426.*"),
    ("item 1's texture call",
     "or VRAM everywhere (what editors have shown, roadmap 89's reason set aside): a look and memory "
     "trade, not changed. Left: the editor's bake.",
     "or VRAM everywhere (what editors have shown, roadmap 89's reason set aside): a look and memory "
     "trade, not changed. **DECIDED, the walker, 2026-10-12: \"go with compressed everywhere\" -- "
     "Level Factory 0.190.0.** `docs/findings/grader_speed/editor_texture_probe.py` keeps the bake's "
     "work copy and compares its texture sidecars with the package's, key by key: the editor changed "
     "426 (VRAM and mips on what it finds in use; on the 22 normal maps -- exactly the glTF's "
     "`normalTexture`s -- red-green compression and a roughness limiter pointed at the map itself). "
     "0.190.0 pins those decisions before any import, on the shared textures, the site skins and "
     "every sign; re-exported, the editor detected nothing and left all 572 as they ship, and opened "
     "the scene in 14.7 s against 20.3. Left: the editor's bake."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "Level Factory 0.190.0.**" not in text, "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's texture compression decided and done; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
