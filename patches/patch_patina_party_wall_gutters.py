"""Patina 0.29.1: no gutter on an Empty's party wall (roadmap 184). See
`patina_party_wall_gutters/CHANGELOG_0.29.1.md`.

Anchored edits (every anchor once; refuses on a miss):
  patina/framing.py   gutter_orders skips a face with no opening on an Empty
  patina/version.py   0.29.1
Copies the test; CHANGELOG and VERSION.

    python patch_patina_party_wall_gutters.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PA = HERE.parent / "patina"
SRC = HERE / "patina_party_wall_gutters"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


GUTTER_OLD = '''def gutter_orders(manifest: SlotManifest, regions: list, *, seed: int,
                  drop: float = 0.08) -> list[dict]:
    """One ``gutter_run`` per top-storey exterior wall slot, under the roofline."""
    uv = _uv(regions, "flashing")
    orders = []
    center = footprint_center(manifest)
    thick_m = modal_thickness(manifest)
    for s in roofline_slots(manifest):
        _w, _d, h = s.size()
'''
GUTTER_NEW = '''def gutter_orders(manifest: SlotManifest, regions: list, *, seed: int,
                  drop: float = 0.08) -> list[dict]:
    """One ``gutter_run`` per top-storey exterior wall slot, under the roofline.

    NOT ON AN EMPTY'S PARTY WALL (0.29.1). On an Empty -- a shell any of whose
    slots carries `glazing: "facade"` -- a face with no window, door or breach
    on any storey is a party wall, and a rowhouse roof drains front and back:
    the downspouts already keep to faces with openings. Between two houses of
    one height the party-wall gutter was hidden; beside a lower neighbour it
    stood exposed and, lit against an unlit wall, read as lines floating in
    the sky (roadmap 184, cold runs 9160 and 9161). A free-standing building
    keeps a gutter on every face, as before.
    """
    uv = _uv(regions, "flashing")
    orders = []
    center = footprint_center(manifest)
    thick_m = modal_thickness(manifest)
    empty = any(s.glazing == "facade" for s in manifest.slots)
    faced = {_side(wall_frame(s, center, thick_m)) for s in manifest.slots
             if s.role in _FACE_ROLES and str(s.slot_id).startswith("ext_")}
    for s in roofline_slots(manifest):
        if empty and _side(wall_frame(s, center, thick_m)) not in faced:
            continue
        _w, _d, h = s.size()
'''

VER_OLD = '__version__ = "0.29.0"\n'
VER_NEW = '__version__ = "0.29.1"\n'


def main():
    assert (PA / "VERSION").read_text(encoding="utf-8").strip() == "Patina 0.29.0"
    _edit(PA / "patina" / "framing.py", [(GUTTER_OLD, GUTTER_NEW)])
    _edit(PA / "patina" / "version.py", [(VER_OLD, VER_NEW)])
    shutil.copyfile(SRC / "test_party_wall_gutters.py", PA / "tests" / "test_party_wall_gutters.py")
    ch = PA / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    head = "## [0.29.0]"
    assert s.count(head) == 1
    ch.write_text(s.replace(head, (SRC / "CHANGELOG_0.29.1.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + head), encoding="utf-8", newline="\n")
    (PA / "VERSION").write_text("Patina 0.29.1", encoding="utf-8", newline="\n")
    print("applied Patina 0.29.1")


if __name__ == "__main__":
    main()
