"""The walk copy climbs the package's own ladder volume, and builds one only where a package carries none.

    python test_walk_ladders.py            # standalone
    python -m pytest test_walk_ladders.py  # or collected

The walker, cold run 9383: "im stuck trying to get up the ladder to the roof". `walk_ladders.gd` built deli_a03's
roof ladder a 4.0 m climb volume against a 6.6 m climb, from a hatch marker Deli Counter does not emit for ladders,
and left the package's own 7.6 m volume (group `ladder_area3d`) out of the group the walk player climbs
(`docs/findings/walk_2026-10-23_deli/`). This runs the real script in Godot, headless, in a scratch project: a marker
with a package volume at its base, and a marker with none. FAILS on the version before 2026-10-23 on behaviour: the
package volume is not in `ladder`, and the first marker gets a 4.0 m volume of its own.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import walk_export  # noqa: E402

DRIVER = """extends SceneTree
# A package ladder (marker + its Area3D, 7.6 m) at x 5 and a bare marker at x 20; walk_ladders.gd added; reports.

func _initialize() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var m0 := Node3D.new()
	m0.name = "LADDER_0"
	m0.add_to_group("ladder")
	world.add_child(m0)
	m0.global_position = Vector3(5.0, 0.0, 0.0)
	var v := Area3D.new()
	v.name = "Ladder_ladder_0"
	v.add_to_group("ladder_area3d")
	v.add_to_group("dc_ladder")
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(1.3, 7.6, 0.8)
	cs.shape = box
	cs.position = Vector3(0.0, 3.3, 0.45)
	v.add_child(cs)
	world.add_child(v)
	v.global_position = Vector3(5.0, 0.0, 0.0)
	var m1 := Node3D.new()
	m1.name = "LADDER_1"
	m1.add_to_group("ladder")
	world.add_child(m1)
	m1.global_position = Vector3(20.0, 0.0, 0.0)
	var wl: Node = (load("res://walk_ladders.gd") as GDScript).new()
	world.add_child(wl)
	_report.call_deferred(wl, v)


func _report(wl: Node, v: Area3D) -> void:
	await process_frame
	await process_frame
	var climbs := {}
	for c in wl.get_children():
		if c is Area3D:
			var b: BoxShape3D = ((c as Area3D).get_child(0) as CollisionShape3D).shape as BoxShape3D
			climbs[String(c.name)] = b.size.y
	print("REPORT " + JSON.stringify({"package_in_ladder": v.is_in_group("ladder"), "climbs": climbs}))
	quit(0)
"""


class WalkLaddersTest(unittest.TestCase):
    def setUp(self):
        self.godot, _how = walk_export._find_godot(None)
        if not self.godot:
            self.skipTest("no Godot to run the script with")
        self.tmp = Path(tempfile.mkdtemp(prefix="walk_ladders_"))
        (self.tmp / "project.godot").write_text('config_version=5\n\n[application]\n\nconfig/name="t"\n',
                                               encoding="utf-8")
        shutil.copyfile(HERE / "walk_ladders.gd", self.tmp / "walk_ladders.gd")
        (self.tmp / "driver.gd").write_text(DRIVER, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _report(self):
        out = subprocess.run([str(self.godot), "--headless", "--path", str(self.tmp), "--script", "res://driver.gd"],
                             capture_output=True, text=True, timeout=120)
        lines = [ln for ln in (out.stdout + out.stderr).splitlines() if ln.startswith("REPORT ")]
        self.assertTrue(lines, "the driver reported nothing:\n" + out.stdout + out.stderr)
        return json.loads(lines[-1][len("REPORT "):])

    def test_the_package_volume_is_climbed_and_a_bare_marker_gets_the_fallback(self):
        r = self._report()
        self.assertTrue(r["package_in_ladder"], "the package's own ladder volume is not climbable")
        self.assertNotIn("LADDER_0_climb", r["climbs"],
                         "a marker with the package's volume at its base got a volume of its own: %s" % r["climbs"])
        # the bare marker: no hatch over it, the 3.0 m fallback plus the 1 m lip
        self.assertEqual(r["climbs"], {"LADDER_1_climb": 4.0})


if __name__ == "__main__":
    unittest.main()
