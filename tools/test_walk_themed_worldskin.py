"""The themed walk imports with LEVEL FACTORY's world-skin script, not a fork.

    python test_walk_themed_worldskin.py            # standalone
    python -m pytest test_walk_themed_worldskin.py  # or collected

## Why this exists

`tools/zoo_worldskin.gd` -- 6,664 bytes, 147 lines, never committed to any
branch -- sat beside `walk_themed.py` and was read by it at module import.
Every themed walk since level_factory 0.57.0 ran it, because `--worldskin`
defaults on. It was last touched 2026-09-06 and had drifted five releases
behind the copy the export runs and the package ships: no stair pass (LF
0.72.0), no mip chains or vertex-colour albedo (0.86.0), no glass shadow pass,
no CRT motion pass (0.89.0).

MEASURED 2026-09-16, cold run 9061's `card_block_001`, the same assembled tree
imported twice with only the source of this one file different, 173 GLBs, exit
0 and no push_error either way: 173 `[worldskin]` lines against 298, 21 blended
materials moved out of the shadow pass against 0, 342 materials on 102 GLBs
drawing vertex colour against 0, 18 stair flight surfaces skinned against 0.
Kit world-projection was identical at 53 materials, which is why nobody saw it:
the pass the walk was LOOKING at was the one pass the fork still did correctly.

Nothing announced the substitution. `walk_themed` printed `worldskin=True`,
which is a treatment flag and not a provenance -- CLAUDE.md's first
verification rule, "name what produced an artefact before concluding anything
from it", with no name available to give.

## What this checks

1. `_WORLDSKIN_SRC` resolves into the level_factory checkout, the way
   `_OVERLAY_SRC` beside it already did. FAILS on the previous version: there
   was no such constant, only `_WORLDSKIN_GD` holding text read at import.
2. Nothing is read at module import. FAILS on the previous version, which ran
   `open(...).read()` at class-body level, so importing this module on a
   machine without the fork raised FileNotFoundError before any argument was
   parsed.
3. No `zoo_worldskin.gd` sits beside `walk_themed.py`. FAILS on the previous
   version, where the fork was the point. This is the guard against somebody
   re-adding one: an untracked file cannot be kept out by git history.
4. The text actually handed to the walk project carries the passes the fork
   lacked. FAILS on the previous version: `grep -c stair` over the fork
   returned 0. Checked by NAME of the function rather than by byte count, so
   the test still means something after LF's next release.
5. A missing source REFUSES, and the refusal names the path it wanted. FAILS
   on the previous version in the worst way available: the constant was read
   at import, so a missing file was an ImportError from a module nobody had
   called yet, and the alternative anybody would have reached for -- a default
   of `""` -- assembles a project that builds, imports, opens, and shows
   untextured kit.
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import walk_themed  # noqa: E402


class SourceIsLevelFactorys(unittest.TestCase):
    def test_constant_points_into_level_factory(self):
        src = Path(walk_themed._WORLDSKIN_SRC)
        self.assertEqual(src.name, "zoo_worldskin.gd")
        # The same three path parts `_OVERLAY_SRC` uses, from the same root.
        self.assertEqual(src.parts[-4:-1],
                         ("level_factory", "assets", "godot"))
        self.assertEqual(src.parent.parent.parent.parent,
                         Path(walk_themed._OVERLAY_SRC).parent.parent.parent
                         .parent,
                         "the two scripts must be read from ONE checkout; two "
                         "roots is the drift this replaces")

    def test_nothing_is_read_at_module_import(self):
        self.assertFalse(
            hasattr(walk_themed, "_WORLDSKIN_GD"),
            "_WORLDSKIN_GD held the script's TEXT, read at import. A path "
            "constant resolves without touching the disk, so the tool is "
            "importable -- and testable -- on a tree that has no such file")

    def test_no_fork_beside_the_tool(self):
        fork = HERE / "zoo_worldskin.gd"
        self.assertFalse(
            fork.is_file(),
            "a copy of LF's import script is back at %s. Whatever put it "
            "there, `walk_themed` no longer reads it, so it is a file that "
            "will drift with nothing reading it -- delete it" % fork)


class SourceCarriesTheLaterPasses(unittest.TestCase):
    """Read the real file. A checker against a guessed shape has learned
    nothing (CLAUDE.md, rule 3), so this fails loudly when LF's copy is not
    where the constant says."""

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(walk_themed._WORLDSKIN_SRC):
            raise unittest.SkipTest(
                "no level_factory checkout beside this tools/ directory: %s"
                % walk_themed._WORLDSKIN_SRC)
        cls.text = walk_themed.worldskin_source()

    def test_has_the_passes_the_fork_lacked(self):
        for func in ("_skin_stairs", "_mip_chains", "_glass_casts_no_shadow",
                     "_crt_motion", "_vertex_colour_albedo"):
            with self.subTest(func=func):
                self.assertIn(
                    "func %s(" % func, self.text,
                    "%s is one of the passes the 2026-09-06 fork predated; a "
                    "source without it is a fork again" % func)

    def test_still_does_the_pass_the_fork_did(self):
        self.assertIn("func _apply(", self.text)
        self.assertIn("uv1_world_triplanar", self.text)


class MissingSourceRefuses(unittest.TestCase):
    def test_raises_failed_and_names_the_path(self):
        missing = str(HERE / "no_such_zoo_worldskin.gd")
        with self.assertRaises(walk_themed.Failed) as caught:
            walk_themed.worldskin_source(missing)
        msg = str(caught.exception)
        self.assertIn(missing, msg,
                      "a refusal that does not name the path it wanted sends "
                      "the reader back to the source to find out")
        self.assertIn("--no-worldskin", msg,
                      "name the deliberate way to build without it, or the "
                      "next person edits the tool to get past this")

    def test_does_not_fall_back_to_empty(self):
        """The failure this replaces one level along.

        An empty script is a valid `import_script/path`: Godot loads it,
        imports every GLB unchanged, and prints nothing. That is the same
        silent-no-op shape the caller's own comment warns about for a path
        that does not exist yet.
        """
        try:
            walk_themed.worldskin_source(str(HERE / "no_such_file.gd"))
        except walk_themed.Failed:
            return
        self.fail("worldskin_source returned instead of refusing")


if __name__ == "__main__":
    unittest.main(verbosity=2)
