"""Level Factory 0.151.0's release: VERSION and the CHANGELOG entry.

    python patch_lf_0151_release.py

Anchored on VERSION (b'0.150.0') and on CHANGELOG.md's head (625,046 bytes,
LF, as read 2026-10-07).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

HEAD = "## [0.150.0] - A brief that asks for a deli gets the corner deli\n"
ENTRY = """## [0.151.0] - The light bake lays the rooms' floor, and frees it before it saves

**What the bake took away.** A lightmapped surface takes its light from the
lightmap alone. Since 0.131.0's bake (on by default since 0.144.0), the
floor Lux puts under a room's fixtures, a room probe's flat ambient, has
reached no wall and no floor. Raised five-fold on cold run 9190's baked
level, it moved no surface. A corner no lamp reaches baked to black.

Measured against the same level lit live (`docs/findings/night_interiors/`
at the factory root), mean luma of 255:

| rooms | baked | live |
|---|---|---|
| 16 fluorescent rows | 15.5 | 24.3 |
| 8 bulb-lit rooms | 3.8 | 17.5 |

The walker had seen it: "a lot of our interiors are quite dark when the
sun isn't up".

**What the plugin does now** (`assets/godot/light_bake_plugin.gd`):
- after the scene opens and before Bake is pressed, it asks the level's Lux
  (>= 0.68.1, `LuxLightLoader.add_bake_fills`) to lay bake-only fills over
  its room probes;
- it frees them before the save.

The lightmap keeps their light; the package carries no fill.

It finds the loader beside the scene's LuxRoot script, so the same call works
in a package (`res://runtime/lux/runtime/`) and in Lux's repo.

**What is recorded.** `room_fills` in `light_bake.json` and the export log say
how many fills were laid; -1 or "no room floor" means the level's Lux lays
none.

**Re-baked through this plugin,** on a copy of cold run 9190's level with
Lux 0.68.1 vendored:
- **Fluorescent rooms:** 15.5 -> 39.0.
- **The fills:** 267 laid, and none in the saved `bake.tscn`.
- **Bake time:** 85 -> 92 s in the editor.

**Refuted, kept.** The first proof bake, with Lux 0.68.0's unowned fill, laid
the same 267 and baked none of them: every room read the control's number.
LightmapGI skips a child with no owner. Lux 0.68.1 owns the fill, and this
plugin's free-before-save is what keeps it out of the package. The test reads
that order off the plugin's source.

**Not priced: nothing ships.** The lightmap keeps its size. The scene the
level loads holds the same nodes, lights and materials as before.

**Tests:** `tests/unit/test_light_bake.py` +2, both failing on 0.150.0:
- the plugin lays the fill before Bake and frees it before the save;
- the count reaches the report and the log.

Suite: 1,971 passed, 14 skipped, 1 xfailed (exit 0).

"""


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.150.0", repr(v)
    c = (LF / "CHANGELOG.md").read_bytes()
    assert len(c) == 625046 and b"\r\n" not in c, len(c)
    text = c.decode("utf-8")
    assert text.startswith(HEAD) and text.count(HEAD) == 1
    (LF / "VERSION").write_bytes(b"0.151.0")
    (LF / "CHANGELOG.md").write_bytes((ENTRY + text).encode("utf-8"))
    print("Level Factory 0.151.0: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
