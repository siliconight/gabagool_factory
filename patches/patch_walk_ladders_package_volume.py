"""The walk copy climbs the package's own ladder volume (the walker's walk of cold run 9383, finding 2:
`docs/findings/walk_2026-10-23_deli/`). "im stuck trying to get up the ladder to the roof": `tools/walk_ladders.gd` sized
every climb volume from a `hatch` marker over the ladder, which Deli Counter emits only for a hatch link and never for a
ladder, else 3.0 m -- deli_a03's roof ladder got 4.0 m against a 6.6 m climb -- while the package's own Area3D, 7.6 m,
groups `ladder_area3d`/`dc_ladder` (`deli_counter/portable_building.py:54-66`), stood unused because the walk player
climbs group `ladder`. This adopts every package volume into `ladder` and builds the fallback only for a marker with
none at its base; the header says so. Adds `tools/test_walk_ladders.py`, which runs the script in Godot headless and
fails on the version before this on behaviour.

    python patches/patch_walk_ladders_package_volume.py && python tools/test_walk_ladders.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GD = ROOT / "tools" / "walk_ladders.gd"
TEST = ROOT / "tools" / "test_walk_ladders.py"

EDITS = [
    ("""## This does Lot's half at runtime, in the walk copy only: for every ladder
## MARKER (a Node3D in group "ladder" that is not already an Area3D) it adds a
## climb Area3D. The height runs from the marker, which sits at the ladder's
## base, up to the nearest "hatch" marker directly above it -- Deli Counter
## emits one at the top of every roof and slab ladder -- or 3.0 m when there is
## none. Sizing mirrors `lot._ladder_volume_nodes`: a 1.3 m square footprint so
## a building's rotation cannot turn the volume edge-on, and a 1 m dismount lip
## over the top. Never in the package; the package is content.
""",
     """## This does Lot's half at runtime, in the walk copy only.
##
## THE PACKAGE'S OWN VOLUME FIRST (2026-10-23). Deli Counter's packages carry a
## climb Area3D for every ladder -- `Ladders/Ladder_<id>`, groups
## "ladder_area3d"/"dc_ladder", at the ladder's base, spanning the full climb
## plus a metre (`deli_counter/portable_building.py`) -- and the walk player
## climbs group "ladder", so it stood unused. Each is put in "ladder" here, and
## a marker with one at its base gets nothing more. The walker, cold run 9383:
## "im stuck trying to get up the ladder to the roof" -- deli_a03's roof ladder
## climbs 6.6 m and the volume this file built for it was 4.0 m tall; 17 roof
## ladders in the library could not be climbed in a walk copy
## (`docs/findings/walk_2026-10-23_deli/`).
##
## The fallback, for a ladder MARKER (a Node3D in group "ladder" that is not an
## Area3D) with no package volume at its base: a climb Area3D from the marker up
## to the nearest "hatch" marker directly above it, or 3.0 m when there is
## none. (This header said Deli Counter emits a hatch marker atop every roof and
## slab ladder; it emits one only for a hatch link -- which is why the fallback
## ran on a roof ladder at 3.0 m.) Sizing mirrors `lot._ladder_volume_nodes`: a
## 1.3 m square footprint so a building's rotation cannot turn the volume
## edge-on, and a 1 m dismount lip over the top. Never in the package; the
## package is content.
"""),
    ("""const HATCH_XZ_TOLERANCE := 1.0
""",
     """const HATCH_XZ_TOLERANCE := 1.0
## How near a package volume's origin must stand to a marker, across and up, to be that marker's ladder: both sit at
## the ladder's base anchor, so they coincide; a metre across and half a metre up allow for rounding.
const PACKAGE_XZ_TOLERANCE := 1.0
const PACKAGE_Y_TOLERANCE := 0.5
"""),
    ("""	var hatches: Array[Node3D] = []
	for h in get_tree().get_nodes_in_group("hatch"):
		if h is Node3D:
			hatches.append(h as Node3D)
	var made := 0
	for n in get_tree().get_nodes_in_group("ladder"):
		if n is Area3D or not (n is Node3D):
			continue
		var base: Vector3 = (n as Node3D).global_position
		var climb := _climb_height(base, hatches)""",
     """	var hatches: Array[Node3D] = []
	for h in get_tree().get_nodes_in_group("hatch"):
		if h is Node3D:
			hatches.append(h as Node3D)
	# the package's own volumes: climbable as they are
	var package_bases: Array[Vector3] = []
	var adopted := 0
	for v in get_tree().get_nodes_in_group("ladder_area3d"):
		if not (v is Area3D):
			continue
		package_bases.append((v as Area3D).global_position)
		if not v.is_in_group("ladder"):
			v.add_to_group("ladder")
			adopted += 1
	var made := 0
	for n in get_tree().get_nodes_in_group("ladder"):
		if n is Area3D or not (n is Node3D):
			continue
		var base: Vector3 = (n as Node3D).global_position
		if _has_package_volume(base, package_bases):
			continue
		var climb := _climb_height(base, hatches)"""),
    ("""	print("[walk_ladders] %d ladder climb volume(s)" % made)
""",
     """	print("[walk_ladders] %d package ladder volume(s) adopted, %d fallback volume(s) built" % [adopted, made])


func _has_package_volume(base: Vector3, package_bases: Array[Vector3]) -> bool:
	for p in package_bases:
		var dx: float = p.x - base.x
		var dz: float = p.z - base.z
		if sqrt(dx * dx + dz * dz) <= PACKAGE_XZ_TOLERANCE and absf(p.y - base.y) <= PACKAGE_Y_TOLERANCE:
			return true
	return false
"""),
]

TEST_TEXT = '''"""The walk copy climbs the package's own ladder volume, and builds one only where a package carries none.

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
        (self.tmp / "project.godot").write_text('config_version=5\\n\\n[application]\\n\\nconfig/name="t"\\n',
                                               encoding="utf-8")
        shutil.copyfile(HERE / "walk_ladders.gd", self.tmp / "walk_ladders.gd")
        (self.tmp / "driver.gd").write_text(DRIVER, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _report(self):
        out = subprocess.run([str(self.godot), "--headless", "--path", str(self.tmp), "--script", "res://driver.gd"],
                             capture_output=True, text=True, timeout=120)
        lines = [ln for ln in (out.stdout + out.stderr).splitlines() if ln.startswith("REPORT ")]
        self.assertTrue(lines, "the driver reported nothing:\\n" + out.stdout + out.stderr)
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
'''


def main():
    raw = GD.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if "_has_package_volume" in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    if TEST.exists():
        raise SystemExit("REFUSED: tools/test_walk_ladders.py exists; nothing written")
    for old, new in EDITS:
        if text.count(old) != 1:
            raise SystemExit("REFUSED: an anchor in tools/walk_ladders.gd is there %d times; nothing written"
                             % text.count(old))
        text = text.replace(old, new)
    GD.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    TEST.write_text(TEST_TEXT, encoding="utf-8", newline="\n")
    print("tools/walk_ladders.gd adopts the package's ladder volumes; tools/test_walk_ladders.py written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
