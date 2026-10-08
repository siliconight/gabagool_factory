"""Lux 0.69.0's test, written first: a cycling stage lamp bakes no bounce, and
the stage outshines the room.

    python patch_lux_stage_live_tests.py

Roadmap 213, decided 2026-10-08: the club's stage lights stay LIVE so their
colour cycle runs, and they are brighter. Adds case M to
`lux/tools/club_light_selftest.gd` (as 0.68.2 left it, 23,412 bytes, LF):

- **A cycling stage rig's lamps carry no indirect energy.** LightmapGI bakes
  a live (BAKE_DYNAMIC) lamp's bounce at the colour it shows at bake time, so
  a cycling stage would ship a bounce frozen on one colour under a lamp that
  keeps changing.
- **A still rig, and a cycling rig whose resource is baked, keep their
  bounce** -- the controls; neither cycles at runtime.
- **The stage outshines the room's wash** (`CLUB_STAGE_LEVEL` over
  `CLUB_WASH_LEVEL`): the rule the new level was chosen by, not its digits.

On 0.68.2 it must FAIL: the cycling lamps carry indirect energy 1.0, and the
stage level (3) is a quarter of the wash's (12).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "lux" / "tools" / "club_light_selftest.gd"

OLD = "\t\tn.free()\n\n\tprint(\"\")\n\tif _fails == 0:\n"
NEW = (
    "\t\tn.free()\n"
    "\n"
    "\tprint(\"case M -- a cycling stage lamp bakes no bounce; the stage outshines the room (0.69.0)\")\n"
    "\t# A baked bounce cannot cycle: LightmapGI bakes a live (BAKE_DYNAMIC) lamp's\n"
    "\t# indirect light at the colour it shows at bake time, so a cycling stage\n"
    "\t# would ship a bounce frozen on one colour under a lamp that keeps\n"
    "\t# changing. Its lamps carry no indirect energy; a still rig, and a\n"
    "\t# cycling rig whose resource is baked, keep theirs -- neither cycles.\n"
    "\tvar cyc_live: Node3D = Loader.rig_for_anchor({\"type\": \"stage_light\", \"id\": \"cyc_live\",\n"
    "\t\t\"color\": \"red\", \"pos\": [0, 0, 3.0], \"target\": [0, 0, 0.9], \"cycle_s\": 4.0,\n"
    "\t\t\"row\": {\"count\": 2, \"spacing\": 0.6}})\n"
    "\tvar still: Node3D = Loader.rig_for_anchor({\"type\": \"stage_light\", \"id\": \"still\",\n"
    "\t\t\"color\": \"red\", \"pos\": [0, 0, 3.0], \"target\": [0, 0, 0.9]})\n"
    "\tvar cyc_baked: Node3D = Loader.rig_for_anchor({\"type\": \"stage_light\", \"id\": \"cyc_baked\",\n"
    "\t\t\"color\": \"red\", \"pos\": [0, 0, 3.0], \"target\": [0, 0, 0.9], \"cycle_s\": 4.0})\n"
    "\tcyc_baked.get(\"rig\").bake_mode = 1\n"
    "\tfor n in [cyc_live, still, cyc_baked]:\n"
    "\t\troot.add_child(n)\n"
    "\tawait process_frame\n"
    "\tvar lamps_live: Array = _lights_of(cyc_live)\n"
    "\t_check(\"a cycling rig builds its two lamps\", lamps_live.size(), 2)\n"
    "\tfor l in lamps_live:\n"
    "\t\t_near(\"...and neither bakes a bounce\", (l as Light3D).light_indirect_energy, 0.0, 1e-6)\n"
    "\t_near(\"a still rig keeps its bounce\",\n"
    "\t\t(_lights_of(still)[0] as Light3D).light_indirect_energy, 1.0, 1e-6)\n"
    "\t_near(\"a baked cycling rig keeps its bounce\",\n"
    "\t\t(_lights_of(cyc_baked)[0] as Light3D).light_indirect_energy, 1.0, 1e-6)\n"
    "\t_check(\"the stage outshines the room's wash\", stage_level > wash_level, true)\n"
    "\tfor n in [cyc_live, still, cyc_baked]:\n"
    "\t\tn.free()\n"
    "\n"
    "\tprint(\"\")\n"
    "\tif _fails == 0:\n")


def main():
    data = TEST.read_bytes()
    assert len(data) == 23412, "club_light_selftest.gd is %d bytes, read at 23,412" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(OLD) == 1, "anchor found %d times" % text.count(OLD)
    TEST.write_bytes(text.replace(OLD, NEW).encode("utf-8"))
    print("case M added: %d -> %d bytes" % (len(data), len(text.replace(OLD, NEW).encode("utf-8"))))


if __name__ == "__main__":
    main()
