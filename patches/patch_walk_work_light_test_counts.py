"""tools/test_walk_add_work_light.py counts the walk scene's resources off the scene, not from numbers. Four of its tests
had failed since 2026-10-19 (f7e7a76, walk copies carry asset flags): they pinned a copy from before the work light at
six resources and `load_steps` 7, and the results at 8 and 9 -- and the asset flags added one resource and one node
to every fresh walk scene, so the pinned old copy carried seven. The tools were right; the test was pinned to a scene
that no longer existed. Each count is now the fresh scene's own, less or plus what the step under test removes or adds,
so the next node a walk copy gains moves them with it. Found while shipping the walk-ladder fix
(`patches/walk_ladders_package_volume/walk_tests_before_after.out.txt`). Anchored; refuses on a miss.

    python patches/patch_walk_work_light_test_counts.py && python tools/test_walk_add_work_light.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
T = ROOT / "tools" / "test_walk_add_work_light.py"

EDITS = [
    ('''def _old_copy_scene():
    """A walk scene as walk_export.py wrote it before the work light: five ext, one sub, load_steps 7."""
    s = walk_export._walk_scene((1.0, 0.0, 2.0))
    s = s.replace(walk_add_work_light.EXT + "\\n", "")
    s = s.replace("\\n" + walk_add_work_light.NODE + '\\nscript = ExtResource("walk_work_light")\\n', "")
    s = re.sub(r"load_steps=\\d+", "load_steps=7", s, count=1)
    assert "walk_work_light" not in s and _loads(s) == 6
    return s
''',
     '''def _fresh():
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
    s = s.replace(walk_add_work_light.EXT + "\\n", "")
    s = s.replace("\\n" + walk_add_work_light.NODE + '\\nscript = ExtResource("walk_work_light")\\n', "")
    s = re.sub(r"load_steps=\\d+", "load_steps=%d" % FRESH_LOADS, s, count=1)
    assert "walk_work_light" not in s and _loads(s) == FRESH_LOADS - 1
    return s
'''),
    ('''            self.assertEqual(_steps(got), _loads(got) + 1)
            self.assertEqual(_steps(got), 8)
            self.assertEqual(got.count("\\r\\n") == got.count("\\n"), eol == "\\r\\n", "line endings kept")''',
     '''            self.assertEqual(_steps(got), _loads(got) + 1)
            self.assertEqual(_steps(got), FRESH_STEPS)
            self.assertEqual(got.count("\\r\\n") == got.count("\\n"), eol == "\\r\\n", "line endings kept")'''),
    ('''            self.assertEqual(_steps(got), _loads(got) + 1)
            self.assertEqual(_steps(got), 9)''',
     '''            self.assertEqual(_steps(got), _loads(got) + 1)
            self.assertEqual(_steps(got), FRESH_STEPS + 1)   # the sky's script'''),
    ('''        self.assertEqual(_steps((self.dir / "_walk.tscn").read_text(encoding="utf-8")), 8)''',
     '''        self.assertEqual(_steps((self.dir / "_walk.tscn").read_text(encoding="utf-8")), FRESH_STEPS)'''),
    ('''        self.assertEqual(_steps(got), _loads(got) + 1)
        self.assertEqual(_steps(got), 9)''',
     '''        self.assertEqual(_steps(got), _loads(got) + 1)
        self.assertEqual(_steps(got), FRESH_STEPS + 1)   # the sky's script and the work light, on the old copy'''),
]


def main():
    raw = T.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if "FRESH_LOADS" in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    for old, new in EDITS:
        if text.count(old) != 1:
            raise SystemExit("REFUSED: an anchor is there %d times; nothing written" % text.count(old))
        text = text.replace(old, new)
    T.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print("tools/test_walk_add_work_light.py counts off the scene")
    return 0


if __name__ == "__main__":
    sys.exit(main())
