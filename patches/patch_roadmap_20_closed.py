"""Roadmap 20 CLOSED, 2026-10-15: Patina 0.32.0 deleted the Godot half (`patches/patch_patina_godot_half_gone.py`,
proof in `patches/patina_godot_half_gone/`). Replaces the NARROWED status written earlier the same day (asserted
once, from its first line to the line ending the block's `*`). The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_20_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: NARROWED 2026-10-15 -- the ambiguity is gone from every package and the files are still "
                   "in the repo")
HEADING = "\n\n**20. Patina's Godot half is a renderer from before Lux was one.**"
STATUS_NEW = (
    "*STATUS: CLOSED 2026-10-15 -- Patina 0.32.0 deleted the Godot half (`godot/`: the plugin, its dock, the "
    "apply script, both `ps1.gdshader` copies -- 8 files), measured dead first "
    "(`docs/findings/open_items_remeasure/`): consumed by nothing in any tool repo, shipped in no package (cold "
    "run 9314: no `addons/`, 0 `res://addons` references), never walked in the editor by its own README's "
    "account. The vertex-colour channel now has one reader anywhere, Level Factory's `zoo_worldskin.gd` -- "
    "albedo on objects, off on tiles (84). The open question had settled itself before this: `art_mode` is "
    "`vertex-color` on both branches (76), Patina's texture half never runs, Pixelcoat is the skin; the "
    "PS1-preset half of the migration was overtaken by the walker's realism call. Found on the way and fixed in "
    "the same release: `patina/version.py` said 0.30.0 against VERSION 0.31.0, so every 0.31.0 manifest and GLB "
    "carried `generator: \"Patina 0.30.0\"`; `tests/test_version_file.py` pins the two (it fails on 0.31.0's "
    "tree). Suite 402 passed, 1 skipped (`patches/patina_godot_half_gone/prove_tests.out.txt`).*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "20's status block not found once"
    j = i
    while True:
        k = text.find("\n", j)
        assert k > 0
        if text[i:k].endswith("*"):
            break
        j = k + 1
    old = text[i:k]
    assert old.count("*STATUS:") == 1 and old.endswith("*"), old[-80:]
    assert text[k:].startswith(HEADING), ("the block does not end just above its heading", text[k:k + 80])
    text = text[:i] + STATUS_NEW + text[k:]
    m = text.find(STATUS_NEW)
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "20's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 20 CLOSED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
