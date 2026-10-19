"""Roadmap 24 CLOSED, 2026-10-19: the rule the item asked for is written into Lux 0.78.0 (1f9ff78) and proven by the
item's own test -- a shipped `lux.applied.tscn` loaded in the editor, saved and diffed: 7 nodes added on Lux 0.77.0,
none on 0.78.0 (the factory's `docs/findings/lux_owner_24/`). The status line is replaced whole, the OPEN
2026-10-15 status kept after it verbatim. Anchored on that line's sha256 and on the item heading two lines below
it. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_24_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
SHA = "5a39677961f5f06f5ca04a441325a636fa7f52a3dd4e855425d3860f7384e638"
HEADING = "**24. Lux gives runtime scaffolding an `owner`, which is what bakes it into a"
OLD_PREFIX = "*STATUS: OPEN 2026-10-15 -- "
NEW = ("*STATUS: CLOSED 2026-10-19 -- the rule is written, and proven by the test this item named. MEASURED "
       "(`docs/findings/lux_owner_24/owner_probe.py`, Godot's headless editor on cold run 9323's package): opening "
       "the shipped `presentation/lux.applied.tscn` and saving it ADDED 7 nodes on Lux 0.77.0 -- `LuxRoot/LuxSun`, "
       "`LuxRoot/LuxWorldEnvironment`, and the post stack's CanvasLayer (auto-named, its `LuxPostFX` name taken by "
       "the module) with its BackBufferCopy, LuxPostRect, LuxCRTBackBuffer and LuxCRTRect -- each owned to "
       "`edited_scene_root` under `if Engine.is_editor_hint()`; a second save kept the same 7, not 14, because "
       "`_build_modules` clears its own scaffolding first. THE RULE, a call made 2026-10-19 and meant to be "
       "changed: Lux 0.78.0 (1f9ff78, `patches/patch_lux_scaffold_ownerless.py`) keeps runtime scaffolding "
       "ownerless in the editor too -- drawn, never saved -- and a LuxRoot that wants it kept sets "
       "`persist_scaffolding_in_editor` (default off), which the four editor-time owner sites ask; the light "
       "loader and fixture spawner, which own what the apply step persists, are unchanged. PROVEN: the same "
       "package with the 0.78.0 runtime overlaid saves 964 -> 964 nodes, +0, on both cycles, the editor still "
       "holding one WorldEnvironment, one sun and one post stack; `tools/scaffold_owner_selftest.gd` fails on "
       "0.77.0 and passes; all 26 of Lux's self-tests exit 0. The item's four suns stay unisolated, and can no "
       "longer reach a saved scene: nothing an editor reload builds is owned. Earlier status kept: OPEN "
       "2026-10-15 -- ")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if hashlib.sha256(l.encode("utf-8")).hexdigest() == SHA]
    assert len(hits) == 1, f"the OPEN 2026-10-15 status line found {len(hits)} times"
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2] == HEADING, "the status no longer adjoins item 24's heading"
    old = lines[i]
    assert old.startswith(OLD_PREFIX) and old.endswith("*")
    lines[i] = NEW + old[len(OLD_PREFIX):]
    assert lines[i].startswith("*STATUS: CLOSED 2026-10-19 -- ") and lines[i].endswith("*")
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 24 CLOSED (Lux 0.78.0, proven by the editor save probe); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
