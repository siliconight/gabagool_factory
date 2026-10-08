"""Lux 0.69.0: the stage is the brightest light in the club, and a cycling
stage bakes no bounce.

    python patch_lux_stage_live.py

Roadmap 213, decided 2026-10-08. The walker: "Stage can be brighter, im ok
with live or baked, whatever you think is the best". The call: live, so the
colour cycle runs -- Level Factory's bake keeps a cycling rig live -- and
brighter.

Anchored on Lux as 0.68.2 left it (all LF): `lux_light_loader.gd` (96,948
bytes) at the club levels; `rigs/lux_stage_light_rig.gd` (4,676 bytes) where
`_rebuild` applies the bake mode to a lamp. Every anchor must match once;
nothing is written until both files matched.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOADER = ROOT / "lux" / "addons" / "lux" / "runtime" / "lux_light_loader.gd"
RIG = ROOT / "lux" / "addons" / "lux" / "runtime" / "rigs" / "lux_stage_light_rig.gd"

LOADER_OLD = "const CLUB_WASH_LEVEL := 12.0\nconst CLUB_STAGE_LEVEL := 3.0\n"
LOADER_NEW = (
    "const CLUB_WASH_LEVEL := 12.0\n"
    "## THE STAGE IS WHERE A CLUB'S LIGHT GOES (0.69.0, roadmap 213). *As first\n"
    "## set:* 3, which read on the grand-lounge tuning frames above. In cold run\n"
    "## 9204's club it read as a dim platform, baked or live -- a stage lit at a\n"
    "## quarter of the room's own wash pools. The walker, 2026-10-08: \"Stage can\n"
    "## be brighter\". Live frames of that stage at 4x, 8x and 10x the old level\n"
    "## (`docs/findings/club_stage_live_price/` at the factory root):\n"
    "##   4x (12) -- lit, but no brighter than the room;\n"
    "##   8x (24) -- the brightest thing in the room, the pole lit, no clipping;\n"
    "##   10x (30) -- hardly different from 8x, the tonemapper's shoulder.\n"
    "## So 24, twice the wash: chosen against frames, not derived.\n"
    "const CLUB_STAGE_LEVEL := 24.0\n")

RIG_OLD = "\t\tr.apply_bake_mode(spot)\n"
RIG_NEW = (
    "\t\tr.apply_bake_mode(spot)\n"
    "\t\t# A BAKED BOUNCE CANNOT CYCLE (0.69.0). LightmapGI bakes a live lamp's\n"
    "\t\t# indirect light -- BAKE_DYNAMIC, the engine default a Realtime rig\n"
    "\t\t# leaves -- at the colour the lamp shows at bake time, so a cycling\n"
    "\t\t# stage would ship a bounce frozen on one colour under a lamp that keeps\n"
    "\t\t# changing. A cycling rig's lamps put no light into the bake at all.\n"
    "\t\tif _cycles():\n"
    "\t\t\tspot.light_indirect_energy = 0.0\n")


def _stage(path, size, old, new):
    data = path.read_bytes()
    assert len(data) == size, "%s is %d bytes, read at %d" % (path.name, len(data), size)
    assert b"\r\n" not in data, path.name
    text = data.decode("utf-8")
    assert text.count(old) == 1, "%s: anchor found %d times" % (path.name, text.count(old))
    return text.replace(old, new).encode("utf-8")


def main():
    staged = {LOADER: _stage(LOADER, 96948, LOADER_OLD, LOADER_NEW),
              RIG: _stage(RIG, 4676, RIG_OLD, RIG_NEW)}
    for path, raw in staged.items():
        path.write_bytes(raw)
        print("%s: %d bytes" % (path.name, len(raw)))


if __name__ == "__main__":
    main()
