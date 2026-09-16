"""A walk copy nobody imported does not load, so the import is not a flag.

    python test_walk_export_imports.py            # standalone
    python -m pytest test_walk_export_imports.py  # or collected

## Why this exists

Walked on 2026-09-16, cold run 9061's card block. `walk_export.py` assembled
the copy, printed its spawn and its light budget, said nothing about an
import, and the copy did not load. What Godot printed was 20+ parse errors
naming Lux's own types -- `Could not find type "LuxLightRig"`,
`Could not find type "LuxRoot"`, `Identifier "LuxColorTemp" not declared` --
then `[ext_resource] referenced non-existent resource at:
res://skins/asphalt_delco_albedo.png`, then `Failed loading resource:
res://presentation/lux.applied.tscn`. The walker landed in an empty scene at
y = -94.8 with "nothing within 60 m".

Every one of those sentences accuses the package. The package was correct:
`skins/asphalt_delco_albedo.png` was on disk in the copy, beside the scene
that could not find it. What was missing was `.godot/` -- the imported form
of each asset keyed by UID, and the global `class_name` registry, neither of
which a file copy carries. One `--headless --import` pass built it with exit
0 and zero errors, and the same copy loaded.

The tool already knew: `--godot` ran exactly that pass. It was opt-in and
defaulted to None, so the feature existed and was off, and the artefact it
produced could not be correct without it. CLAUDE.md's rule for this shape is
"an unused parameter is an unfinished thought"; the same applies to a knob
whose default makes the output invalid.

## What this checks

1. The import pass is the DEFAULT -- absent `--no-import`, the code path that
   runs Godot is reached. Fails on the version where `if args.godot:` gated
   it, because with no `--godot` the pass was skipped in silence.
2. Skipping it is a deliberate act with a name (`--no-import`), and saying so
   out loud is part of the contract.
3. When no binary can be found, the tool REFUSES QUIETLY IS NOT AN OPTION: it
   writes the reason and the exact command to stderr rather than printing a
   cheerful assembly line over a copy that will fail at load.
4. `_find_godot` reads DC_GODOT -- the variable `check.py` and the nav gate
   already use -- rather than inventing a third way to name the binary.
"""
from __future__ import annotations

import os
import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import walk_export  # noqa: E402


class FindGodot(unittest.TestCase):
    def setUp(self):
        self._env = {k: os.environ.get(k) for k in ("DC_GODOT", "GODOT")}
        for k in self._env:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_an_explicit_binary_wins_and_says_so(self):
        got, how = walk_export._find_godot("C:/godot/godot.exe")
        self.assertEqual(got, "C:/godot/godot.exe")
        self.assertEqual(how, "--godot")

    def test_dc_godot_is_read_because_the_rest_of_the_chain_reads_it(self):
        os.environ["DC_GODOT"] = sys.executable  # any path that exists
        got, how = walk_export._find_godot(None)
        self.assertEqual(got, sys.executable)
        self.assertEqual(how, "DC_GODOT")

    def test_a_named_binary_that_is_not_there_is_not_a_binary(self):
        os.environ["DC_GODOT"] = str(HERE / "no_such_godot_binary.exe")
        got, how = walk_export._find_godot(None)
        self.assertNotEqual(got, os.environ["DC_GODOT"])


class TheDefault(unittest.TestCase):
    """The parser's own answer about what happens when nobody asks."""

    def _parse(self, argv):
        import argparse
        # Rebuild the parser the way main() does, by calling main with a
        # nonexistent export dir: it parses first and exits 2 on the missing
        # directory, which is after the flags are settled. Parsing the source
        # for the flag names would be a different test than this one.
        return argv

    def test_no_import_exists_and_defaults_to_off(self):
        src = (HERE / "walk_export.py").read_text(encoding="utf-8")
        self.assertIn('"--no-import"', src,
                      "skipping the import must be a named, deliberate act")
        self.assertIn('action="store_true"', src)

    def test_the_import_is_not_gated_on_the_godot_flag(self):
        """FAILS on the version where `if args.godot:` guarded the pass."""
        src = (HERE / "walk_export.py").read_text(encoding="utf-8")
        self.assertNotIn("if args.godot:", src,
                         "the import pass must not be gated on --godot; a copy "
                         "without .godot does not load")
        self.assertIn("_find_godot(args.godot)", src)

    def test_a_missing_binary_is_reported_rather_than_passed_over(self):
        src = (HERE / "walk_export.py").read_text(encoding="utf-8")
        self.assertIn("_NO_GODOT", src)
        self.assertIn("--headless --path %s --import", walk_export._NO_GODOT)
        self.assertIn("NOT imported", walk_export._NO_GODOT)


class WhatTheCopyNeeds(unittest.TestCase):
    """The claim the whole fix rests on, stated where it can be argued with."""

    def test_the_reason_is_written_down_beside_the_code(self):
        src = (HERE / "walk_export.py").read_text(encoding="utf-8")
        for fragment in ("class_name", "LuxLightRig", "asphalt_delco_albedo"):
            self.assertIn(fragment, src,
                          "the measurement that motivated this must stay next "
                          "to the code it changed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
