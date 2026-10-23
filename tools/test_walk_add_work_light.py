"""A walk copy assembled before the work light gets it, and the sky wiring takes a copy that has it.

    python test_walk_add_work_light.py            # standalone
    python -m pytest test_walk_add_work_light.py  # or collected

`walk_add_work_light.py` adds the work light to a copy assembled before
2026-10-14. `cold_drive/wire_sky.py` runs on every fresh walk copy in the cold
drive, and it asserted the scene's head read `load_steps=7`: the work light made
a fresh copy's 8, and it refused every one, silently, since the drive pipes it
through `tail`. Both now count `load_steps` off the scene, and this holds them
to it in either order, in LF and in CRLF.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import walk_add_work_light  # noqa: E402
import walk_export  # noqa: E402

WIRE_SKY = HERE / "cold_drive" / "wire_sky.py"


def _steps(text):
    return int(re.search(r"load_steps=(\d+)", text).group(1))


def _loads(text):
    return len(re.findall(r"^\[(?:ext|sub)_resource ", text, flags=re.M))


def _fresh():
    """The walk scene walk_export.py writes today."""
    return walk_export._walk_scene((1.0, 0.0, 2.0))


#: The fresh scene's resources and load_steps, counted off it: the numbers below are this, less or plus the one
#: resource the step under test removes or adds. They were pinned as numbers (an old copy at six resources and
#: load_steps 7) and broke when the asset flags (2026-10-19) added a resource to every fresh scene.
FRESH_LOADS = _loads(_fresh())
FRESH_STEPS = _steps(_fresh())


def _old_copy_scene():
    """A walk scene as walk_export.py wrote it before the work light: today's, less the work light's ext and node,
    load_steps one over its resources."""
    s = _fresh()
    s = s.replace(walk_add_work_light.EXT + "\n", "")
    s = s.replace("\n" + walk_add_work_light.NODE + '\nscript = ExtResource("walk_work_light")\n', "")
    s = re.sub(r"load_steps=\d+", "load_steps=%d" % FRESH_LOADS, s, count=1)
    assert "walk_work_light" not in s and _loads(s) == FRESH_LOADS - 1
    return s


class Retrofit(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _write(self, text, eol):
        (self.dir / "_walk.tscn").write_bytes(text.replace("\n", eol).encode("utf-8"))

    def _read(self):
        return (self.dir / "_walk.tscn").read_bytes().decode("utf-8")

    def test_an_old_copy_gets_the_work_light(self):
        for eol in ("\n", "\r\n"):
            self._write(_old_copy_scene(), eol)
            said = walk_add_work_light.add(self.dir)
            self.assertIn("added", said)
            got = self._read()
            self.assertEqual(got.count(walk_add_work_light.NODE), 1)
            self.assertEqual(got.count(walk_add_work_light.EXT), 1)
            self.assertEqual(_steps(got), _loads(got) + 1)
            self.assertEqual(_steps(got), FRESH_STEPS)
            self.assertEqual(got.count("\r\n") == got.count("\n"), eol == "\r\n", "line endings kept")
            self.assertEqual((self.dir / "_walk_work_light.gd").read_bytes(),
                             walk_add_work_light.SRC.read_bytes())

    def test_a_copy_that_has_it_is_left_alone(self):
        self._write(walk_export._walk_scene((1.0, 0.0, 2.0)), "\n")
        before = self._read()
        self.assertIn("already", walk_add_work_light.add(self.dir))
        self.assertEqual(self._read(), before)

    def test_the_result_matches_a_fresh_copy(self):
        self._write(_old_copy_scene(), "\n")
        walk_add_work_light.add(self.dir)
        self.assertEqual(self._read(), walk_export._walk_scene((1.0, 0.0, 2.0)))


class WireSky(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _wire(self):
        return subprocess.run([sys.executable, str(WIRE_SKY), str(self.dir)], capture_output=True, text=True)

    def test_a_fresh_copy_with_the_work_light_takes_the_sky(self):
        for eol in ("\n", "\r\n"):
            (self.dir / "_sky_cycle.gd").unlink(missing_ok=True)
            (self.dir / "_walk.tscn").write_bytes(
                walk_export._walk_scene((1.0, 0.0, 2.0)).replace("\n", eol).encode("utf-8"))
            r = self._wire()
            self.assertEqual(r.returncode, 0, r.stderr[-400:])
            got = (self.dir / "_walk.tscn").read_bytes().decode("utf-8")
            self.assertEqual(got.count('[node name="SkyCycle" type="Node" parent="."]'), 1)
            self.assertEqual(got.count('[node name="WalkWorkLight" type="Node" parent="."]'), 1)
            self.assertEqual(_steps(got), _loads(got) + 1)
            self.assertEqual(_steps(got), FRESH_STEPS + 1)   # the sky's script

    def test_an_old_copy_still_takes_the_sky_and_then_the_work_light(self):
        (self.dir / "_walk.tscn").write_bytes(_old_copy_scene().encode("utf-8"))
        r = self._wire()
        self.assertEqual(r.returncode, 0, r.stderr[-400:])
        self.assertEqual(_steps((self.dir / "_walk.tscn").read_text(encoding="utf-8")), FRESH_STEPS)
        walk_add_work_light.add(self.dir)
        got = (self.dir / "_walk.tscn").read_text(encoding="utf-8")
        self.assertEqual(got.count('[node name="SkyCycle" type="Node" parent="."]'), 1)
        self.assertEqual(got.count('[node name="WalkWorkLight" type="Node" parent="."]'), 1)
        self.assertEqual(_steps(got), _loads(got) + 1)
        self.assertEqual(_steps(got), FRESH_STEPS + 1)   # the sky's script and the work light, on the old copy


if __name__ == "__main__":
    unittest.main(verbosity=2)
