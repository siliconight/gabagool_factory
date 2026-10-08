"""Lux 0.69.0's release: VERSION and the CHANGELOG entry.

    python patch_lux_0690_release.py

Anchored on VERSION (b'Lux 0.68.2', no newline) and on CHANGELOG.md's head
as Lux 0.68.2 left it (LF).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LUX = ROOT / "lux"

HEAD = "# Changelog\n\n## [0.68.2]"
ENTRY = """# Changelog

## [0.69.0] - the stage is the brightest light in the club, and a cycling stage bakes no bounce

Roadmap 213, decided 2026-10-08. The walker: "Stage can be brighter, im ok
with live or baked, whatever you think is the best". The call: live, so the
colour cycle runs, and brighter. Level Factory 0.160.0 is the other half --
its bake keeps a cycling rig live.

**`CLUB_STAGE_LEVEL` 3 -> 24** (`lux_light_loader.gd`).
- **Why 3 had to move.** It read on the grand-lounge tuning frames. In cold
  run 9204's club it read as a dim platform, baked or live
  (`docs/findings/club_stage_live_price/` at the factory root): a stage lit
  at a quarter of the room's own wash pools (`CLUB_WASH_LEVEL` 12).
- **The frames.** Live frames of that stage at the old level's 4x, 8x and
  10x:
  - 4x is lit but no brighter than the room;
  - 8x is the brightest thing in it, the pole lit, nothing clipped;
  - 10x is hardly different from 8x, at the tonemapper's shoulder.
- **So 24, twice the wash:** chosen against frames, not derived.
- **The cost does not move.** Pairing reads range, not energy, so the
  light census reads the same.

**A cycling stage rig bakes no bounce** (`lux_stage_light_rig.gd`,
`_rebuild`).
- **The defect.** LightmapGI bakes a live lamp's indirect light
  (BAKE_DYNAMIC, the default a Realtime rig leaves) at the colour the lamp
  shows at bake time. A cycling stage would ship a bounce frozen on one
  colour under a lamp that keeps changing.
- **The fix.** A rig that cycles sets `light_indirect_energy` 0 on its
  lamps.
- **Unchanged.** A still rig, and a cycling rig whose resource is baked,
  keep their bounce; neither cycles at runtime.

**Tests.** `tools/club_light_selftest.gd`, case M.
- **On 0.68.2, 3 checks fail:** both cycling lamps' bounce, and the stage
  level against the wash. The controls pass on both versions.
- **All 18 selftests pass** -- 17 headless, and
  `streetlight_shadow_selftest.gd` windowed, as it documents.

**Not shown yet:** the stage in a cold run, lit live at 24 with no baked
wash under it. The frames above kept the old bake's wash, so the stage
top will read a little darker than they do.

## [0.68.2]"""


def main():
    v = (LUX / "VERSION").read_bytes()
    assert v == b"Lux 0.68.2", repr(v)
    c = (LUX / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.count(HEAD) == 1, text.count(HEAD)
    (LUX / "VERSION").write_bytes(b"Lux 0.69.0")
    (LUX / "CHANGELOG.md").write_bytes(text.replace(HEAD, ENTRY, 1).encode("utf-8"))
    print("Lux 0.69.0: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
