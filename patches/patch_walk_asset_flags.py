"""Walk copies carry asset flags: G marks what the crosshair rests on as looking good, P as needing love (roadmap 253).

The walker, 2026-10-14, after the demo: "I want a way to flag assets that look good and assets that need more
polish/love". `tools/walk_asset_flags.gd` (new) is the key handler -- debug builds only, like F3 and the work light --
and picks by RENDER first, because in these levels collision is Deli Counter's greybox and the asset the eye sees is
a Zoo module instanced over it; `tools/walk_asset_flags_selftest.gd` (new) proves it headless (14 checks, output in
`docs/findings/asset_flags_253/selftest.out.txt`); `tools/asset_flags.py` (new) gathers the copies' flags into one
ledger per asset, needs-love first, with each flag's frame copied beside it so the ledger outlives the walk copy.
This patch is the wiring: `tools/walk_export.py` puts the handler in every walk copy, as it puts the work light.

What it changes (anchored; each file pinned by hash; nothing written on a miss):
  * tools/walk_export.py -- `_ASSET_FLAGS_SRC`; the walk scene's ext_resource and `WalkAssetFlags` node; the copy
    as `_walk_asset_flags.gd`; one summary line.
  * tools/test_walk_export_work_light.py -- the walk scene's pinned load count: six scripts now, 9 (10 with the drip).
  * tools/test_walk_export_asset_flags.py (new): the scene carries the handler, the script it copies is there and
    debug-only, the selftest is a SceneTree, and the ledger's own selftest holds.

    python patches/patch_walk_asset_flags.py --tests   # the new test only (prove it fails first)
    python patches/patch_walk_asset_flags.py           # everything
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
WE = ROOT / "tools" / "walk_export.py"
WL_TEST = ROOT / "tools" / "test_walk_export_work_light.py"
SHA = {WE: "366641a1b56a1d31", WL_TEST: "537916fdc0feb43b"}

RES_OLD = '[ext_resource type="Script" path="res://_walk_work_light.gd" id="walk_work_light"]\n'
RES_NEW = (RES_OLD + '[ext_resource type="Script" path="res://_walk_asset_flags.gd" id="walk_asset_flags"]\n')

NODE_OLD = '[node name="WalkWorkLight" type="Node" parent="."]\nscript = ExtResource("walk_work_light")\n'
NODE_NEW = (NODE_OLD + '\n[node name="WalkAssetFlags" type="Node" parent="."]\n'
            'script = ExtResource("walk_asset_flags")\n')

SRC_OLD = '''_WORK_LIGHT_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "walk_work_light.gd")
'''
SRC_NEW = SRC_OLD + '''
#: ASSET FLAGS, G and P (2026-10-19, factory roadmap 253). The walker: "I want a
#: way to flag assets that look good and assets that need more polish/love". G
#: marks what the crosshair rests on as looking good, P as needing love; each
#: press appends a record and a small frame beside the copy (`asset_flags.jsonl`,
#: `asset_flags/`), and `tools/asset_flags.py` gathers them into a ledger. The
#: pick is by render first -- collision here is the greybox, the asset is the
#: module over it. `tools/walk_asset_flags_selftest.gd` proves it headless.
#: Always in the walk copy, never in the package; debug builds only.
_ASSET_FLAGS_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "walk_asset_flags.gd")
'''

COPY_OLD = '    shutil.copy2(_WORK_LIGHT_SRC, os.path.join(out, "_walk_work_light.gd"))\n'
COPY_NEW = COPY_OLD + '    shutil.copy2(_ASSET_FLAGS_SRC, os.path.join(out, "_walk_asset_flags.gd"))\n'

PRINT_OLD = '''    print("  work light: L toggles one, OFF at start -- the whole view lit "
          "flat for checking what is there; a banner says it is not the look")
'''
PRINT_NEW = PRINT_OLD + '''    print("  flags    : G looks good, P needs love -- what the crosshair rests on, "
          "to asset_flags.jsonl beside the copy (tools/asset_flags.py gathers)")
'''

COUNT_OLD = '''        # the mission and five scripts, one capsule, and the scene itself: 8;
        # the drip's script makes 9
        self.assertEqual(_steps(walk_export._walk_scene((0.0, 0.0, 0.0))), 8)
        self.assertEqual(_steps(walk_export._walk_scene((0.0, 0.0, 0.0), drip=True)), 9)
'''
COUNT_NEW = '''        # the mission and six scripts (the asset flags joined on 2026-10-19), one
        # capsule, and the scene itself: 9; the drip's script makes 10
        self.assertEqual(_steps(walk_export._walk_scene((0.0, 0.0, 0.0))), 9)
        self.assertEqual(_steps(walk_export._walk_scene((0.0, 0.0, 0.0), drip=True)), 10)
'''

TEST = '''"""Walk copies carry the asset flags (G looks good, P needs love), and the ledger reads them (roadmap 253).

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
        self.assertIn('[node name="WalkAssetFlags" type="Node" parent="."]\\n'
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
'''


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(path):
    raw = path.read_bytes()
    assert b"\r\n" not in raw, f"{path.name} is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA[path], (f"{path.name} is not the file this patch read", got)
    return raw.decode("utf-8")


def write_tests():
    p = ROOT / "tools" / "test_walk_export_asset_flags.py"
    assert not p.exists(), f"{p.name} exists"
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote tools/test_walk_export_asset_flags.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    we = _read(WE)
    assert "_ASSET_FLAGS_SRC" not in we, "already applied"
    we = _once(we, RES_OLD, RES_NEW, "the work light's ext_resource")
    we = _once(we, NODE_OLD, NODE_NEW, "the work light's node")
    we = _once(we, SRC_OLD, SRC_NEW, "the work light's source")
    we = _once(we, COPY_OLD, COPY_NEW, "the work light's copy")
    we = _once(we, PRINT_OLD, PRINT_NEW, "the work light's summary line")
    wl = _once(_read(WL_TEST), COUNT_OLD, COUNT_NEW, "the pinned load count")
    WE.write_bytes(we.encode("utf-8"))
    WL_TEST.write_bytes(wl.encode("utf-8"))
    write_tests()
    print("walk copies carry the asset flags; the load count says six scripts")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
