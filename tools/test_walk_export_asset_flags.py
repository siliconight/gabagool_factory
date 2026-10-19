"""Walk copies carry the asset flags (G looks good, P needs love), and the ledger reads them (roadmap 253).

    python test_walk_export_asset_flags.py            # standalone
    python -m pytest test_walk_export_asset_flags.py  # or collected

The walker, 2026-10-14: "I want a way to flag assets that look good and assets that need more polish/love".
`walk_asset_flags.gd` is the key handler and `walk_asset_flags_selftest.gd` proves what it does headless; this
proves `walk_export.py` puts it in every walk copy, and that `asset_flags.py`'s ledger holds.
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import asset_flags  # noqa: E402
import walk_export  # noqa: E402


class AssetFlags(unittest.TestCase):
    def test_the_walk_scene_carries_the_handler(self):
        text = walk_export._walk_scene((0.0, 0.0, 0.0))
        self.assertIn('[ext_resource type="Script" path="res://_walk_asset_flags.gd" '
                      'id="walk_asset_flags"]', text)
        self.assertIn('[node name="WalkAssetFlags" type="Node" parent="."]\n'
                      'script = ExtResource("walk_asset_flags")', text)

    def test_the_script_it_copies_is_there_and_debug_only(self):
        self.assertTrue(os.path.isfile(walk_export._ASSET_FLAGS_SRC), walk_export._ASSET_FLAGS_SRC)
        src = Path(walk_export._ASSET_FLAGS_SRC).read_text(encoding="utf-8")
        self.assertIn("KEY_G", src)
        self.assertIn("KEY_P", src)
        self.assertIn("OS.is_debug_build()", src)

    def test_the_selftest_is_a_scene_tree(self):
        st = HERE / "walk_asset_flags_selftest.gd"
        self.assertTrue(st.is_file())
        self.assertTrue(st.read_text(encoding="utf-8").startswith("extends SceneTree"))

    def test_the_ledger_holds(self):
        self.assertEqual(asset_flags.selftest(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
