"""The walk copy starts from the export's own import cache (Level Factory 0.188.0).

    python test_walk_export_cache.py            # standalone
    python -m pytest test_walk_export_cache.py  # or collected

## Why this exists

Cold run 9252's step stamps put the walk step at 91 s of a 615 s drive: `walk_export.py` copied
the package and imported it from scratch, a minute after the export had imported the same files
and deleted the cache. Level Factory 0.188.0 keeps that cache beside the package
(`<package>.import_cache`). Moved into the copy as its `.godot`, the import pass only checks it:
9.6 s against 85.6 and 86.2 s from scratch, every model the copy imports loading the same and the
level the same (docs/findings/grader_speed/walk_cache_probe.py).

## What this checks

1. A kept cache becomes the copy's `.godot`, and is gone from beside the package: moved, not
   copied, so it costs no disk and a second walk copy imports from scratch as before.
2. No kept cache, nothing taken.
3. A copy that already has a `.godot` keeps its own.
4. `main` takes it before the import pass, and not under `--no-import`.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import walk_export  # noqa: E402


class TakeKeptCache(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pkg = self.tmp / "exports" / "LF_x.portable-godot"
        self.pkg.mkdir(parents=True)
        self.out = self.tmp / "walk"
        self.out.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _kept(self):
        kept = Path(str(self.pkg) + ".import_cache")
        (kept / "imported").mkdir(parents=True)
        (kept / "imported" / "wall.glb-1.scn").write_bytes(b"scn")
        return kept

    def test_the_kept_cache_becomes_the_copys_godot_and_leaves_the_export(self):
        kept = self._kept()
        self.assertTrue(walk_export._take_kept_cache(str(self.pkg), str(self.out)))
        self.assertEqual((self.out / ".godot" / "imported" / "wall.glb-1.scn").read_bytes(), b"scn")
        self.assertFalse(kept.exists(), "moved, not copied")

    def test_no_kept_cache_takes_nothing(self):
        self.assertFalse(walk_export._take_kept_cache(str(self.pkg), str(self.out)))
        self.assertFalse((self.out / ".godot").exists())

    def test_a_copy_with_its_own_cache_keeps_it(self):
        kept = self._kept()
        (self.out / ".godot").mkdir()
        self.assertFalse(walk_export._take_kept_cache(str(self.pkg), str(self.out)))
        self.assertTrue(kept.exists())

    def test_a_trailing_separator_on_the_export_dir_finds_the_same_cache(self):
        self._kept()
        self.assertTrue(walk_export._take_kept_cache(str(self.pkg) + os.sep, str(self.out)))


class TheCallInMain(unittest.TestCase):
    def test_main_takes_it_before_the_import_pass_and_not_under_no_import(self):
        src = (HERE / "walk_export.py").read_text(encoding="utf-8")
        body = src[src.index("def main("):]
        take = body.index("_take_kept_cache(export_dir, out)")
        imp = body.index('[godot, "--headless", "--path", out, "--import"]')
        self.assertLess(take, imp, "the cache must be in place before the pass that checks it")
        line = body[body.rfind("\n", 0, take):body.find("\n", take)]
        self.assertIn("not args.no_import", line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
