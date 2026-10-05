"""Patina 0.25.1: a gutter runs the whole eave, over the top-floor windows too.

Cold run 9153's frames, close up: each rowhome's gutter stopped at every
top-floor window bay. `roofline_slots` returned the top storey's WALL slots
only, and a window is a slot of its own. See
`patina_eave_gaps/CHANGELOG_0.25.1.md`.

Anchored edits (every anchor once; refuses on a miss):
  patina/framing.py   `roofline_slots` adds the top storey's exterior openings
  patina/version.py   0.25.1
Copies the test; CHANGELOG and VERSION.

    python patch_patina_eave_gaps.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PA = HERE.parent / "patina"
SRC = HERE / "patina_eave_gaps"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


OLD = '''    the eave, which is the top of the highest STOREY wall, so parapets are
    left out before the top storey is found.
    """
    walls = [s for s in wall_slots(manifest) if not _is_parapet(s)]
    storeys = [int(s.story) for s in walls if s.story is not None]
    if not storeys:
        return walls
    top = max(storeys)
    return [s for s in walls if s.story is not None and int(s.story) == top]
'''
NEW = '''    the eave, which is the top of the highest STOREY wall, so parapets are
    left out before the top storey is found.

    AND THE TOP STOREY'S OPENINGS ARE PART OF IT (0.25.1). A window is a slot
    of its own, so a roofline of WALL slots stopped at every top-floor window
    bay: cold run 9153's rowhomes showed a pale gutter broken over each one.
    An exterior window, door or breach on the top storey carries its stretch
    of the eave. Its module is the storey's height (Deli Counter >= 0.176.0
    names heights apart), so its gutter hangs at the same line, above the
    opening's head -- clear of the keep-out the dressing filter enforces.
    """
    walls = [s for s in wall_slots(manifest) if not _is_parapet(s)]
    storeys = [int(s.story) for s in walls if s.story is not None]
    if not storeys:
        return walls
    top = max(storeys)
    eave = [s for s in walls if s.story is not None and int(s.story) == top]
    eave += [s for s in manifest.slots
             if s.role in _FACE_ROLES and str(s.slot_id).startswith("ext_")
             and s.story is not None and int(s.story) == top]
    return eave
'''

VER_OLD = '__version__ = "0.25.0"\n'
VER_NEW = '__version__ = "0.25.1"\n'


def main():
    assert (PA / "VERSION").read_text(encoding="utf-8").strip() == "Patina 0.25.0"
    _edit(PA / "patina" / "framing.py", [(OLD, NEW)])
    _edit(PA / "patina" / "version.py", [(VER_OLD, VER_NEW)])
    shutil.copyfile(SRC / "test_gutter_eave_gaps.py", PA / "tests" / "test_gutter_eave_gaps.py")
    ch = PA / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    head = "## [0.25.0]"
    assert s.count(head) == 1
    ch.write_text(s.replace(head, (SRC / "CHANGELOG_0.25.1.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + head), encoding="utf-8", newline="\n")
    (PA / "VERSION").write_text("Patina 0.25.1", encoding="utf-8", newline="\n")
    print("applied Patina 0.25.1")


if __name__ == "__main__":
    main()
