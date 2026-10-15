"""The walk copy's work light is wired in, and the walk scene counts what it loads.

    python test_walk_export_work_light.py            # standalone
    python -m pytest test_walk_export_work_light.py  # or collected

The walker, 2026-10-14: "a tool to make the area brighter for checking things
so its not too dark and you get mistaken... just for visual checks".
`walk_work_light.gd` is that light, L toggles it, and
`walk_work_light_selftest.gd` proves what it does headless. This proves
`walk_export.py` puts it in every walk copy.

The scene's `load_steps` was typed by hand and had already gone stale once --
a comment said "4 ext + 1 sub" while the scene loaded five -- so it is now
counted off the scene by `_walk_scene`, and the counts are pinned here.
"""
from __future__ import annotations

import os
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import walk_export  # noqa: E402


def _steps(text):
    return int(re.search(r"load_steps=(\d+)", text).group(1))


def _count(kind, text):
    return len(re.findall(r"^\[%s_resource " % kind, text, flags=re.M))


class WorkLight(unittest.TestCase):
    def test_the_walk_scene_carries_the_work_light(self):
        text = walk_export._walk_scene((0.0, 0.0, 0.0))
        self.assertIn('[ext_resource type="Script" path="res://_walk_work_light.gd" '
                      'id="walk_work_light"]', text)
        self.assertIn('[node name="WalkWorkLight" type="Node" parent="."]\n'
                      'script = ExtResource("walk_work_light")', text)

    def test_the_script_it_copies_is_there(self):
        self.assertTrue(os.path.isfile(walk_export._WORK_LIGHT_SRC), walk_export._WORK_LIGHT_SRC)
        src = Path(walk_export._WORK_LIGHT_SRC).read_text(encoding="utf-8")
        self.assertIn("KEY_L", src)
        self.assertIn("OS.is_debug_build()", src)

    def test_every_resource_a_node_names_is_declared(self):
        for drip in (False, True):
            text = walk_export._walk_scene((0.0, 0.0, 0.0), drip=drip, headlamp=True)
            declared = set(re.findall(r'^\[ext_resource [^\]]* id="([^"]+)"\]', text, flags=re.M))
            used = set(re.findall(r'ExtResource\("([^"]+)"\)', text))
            self.assertEqual(used - declared, set(), "drip=%s" % drip)


class LoadSteps(unittest.TestCase):
    def test_load_steps_counts_what_the_scene_loads(self):
        for drip in (False, True):
            for headlamp in (False, True):
                text = walk_export._walk_scene((1.0, 2.0, 3.0), drip=drip, headlamp=headlamp)
                self.assertEqual(_steps(text), _count("ext", text) + _count("sub", text) + 1,
                                 "drip=%s headlamp=%s" % (drip, headlamp))

    def test_the_counts_today(self):
        # the mission and five scripts, one capsule, and the scene itself: 8;
        # the drip's script makes 9
        self.assertEqual(_steps(walk_export._walk_scene((0.0, 0.0, 0.0))), 8)
        self.assertEqual(_steps(walk_export._walk_scene((0.0, 0.0, 0.0), drip=True)), 9)

    def test_the_spawn_lands_on_the_player(self):
        text = walk_export._walk_scene((1.5, 2.25, -3.0))
        self.assertIn("transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 1.5, 2.25, -3.0)", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
