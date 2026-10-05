"""Zoo 1.66.0: a painted pane shows its picture on BOTH faces.

Cold run 9151 shipped the painted windows (1.64.0/1.65.0) with the picture on
the wrong face. Measured by `patches/lf_empties/pane_face_probe.gd` on the
walk copy: the face carrying the atlas cell has world normal (0, 0, +1), INTO
the house; the street-side face carries the frame point, so from the street
every pane read as flat beige and none glowed. `_arch.build_slab` mapped the
cell to the local +Y face on the assumption "+Y is outdoors", which holds for
a wall module through its placement and not for these windows as placed.

Both big faces now carry the cell, each mapped to read unmirrored from its own
side, so the result does not depend on a module's orientation at all. The
mapping is a pure function, `window_panes.face_uv`, tested without Blender.
See `zoo_pane_faces/CHANGELOG_1.66.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/window_panes.py  `face_uv`, `frame_uv`
  zoo_keeper/recipes/_arch.py      the pane's UVs come from `face_uv`
  tests/test_window_panes.py       both faces, each side's right, the frame point
CHANGELOG and VERSION.

    python patch_zoo_pane_faces.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_pane_faces"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


UV_OLD = '''def _room(c, e, x0, y0, x1, y1, light):'''
UV_NEW = '''def frame_uv():
    """A UV point inside frame paint: the faces of a pane nobody looks at
    straight on (its thin edges) take the frame colour from here."""
    f = uv_rect(STATES[0])[0] * 0.25
    return (f, f)


def face_uv(state, normal_y, x, z, cx, cz, hx, hz):
    """The UV of one corner of a pane's face (1.66.0).

    ``normal_y`` is the face normal's Y in the module's own frame; ``x``, ``z``
    the corner; ``cx``, ``cz``, ``hx``, ``hz`` the pane's centre and half size.

    BOTH BIG FACES CARRY THE CELL. 1.64.0 painted only the +Y face, on the
    assumption that +Y is outdoors, and cold run 9151 measured the painted
    face pointing INTO the houses: the street saw frame paint. Painting both
    faces makes the answer independent of how a module is turned.

    EACH READS UNMIRRORED FROM ITS OWN SIDE. Looking along the view direction
    ``d`` with up +Z, the viewer's right is ``d x up``: -X for a viewer on
    the +Y side, +X on the -Y side. ``u`` runs toward that right on both.
    The thin faces take `frame_uv`.
    """
    if abs(normal_y) < 0.9:
        return frame_uv()
    u0, v0, u1, v1 = uv_rect(state)
    t = ((cx + hx) - x) / (2 * hx) if normal_y > 0 else (x - (cx - hx)) / (2 * hx)
    return (u0 + (u1 - u0) * t, v0 + (v1 - v0) * (z - (cz - hz)) / (2 * hz))


def _room(c, e, x0, y0, x1, y1, light):'''

ARCH_OLD = '''            # A PAINTED PANE (1.64.0): the street face (+Y, outdoors) shows
            # its state's cell of the shared atlas; every other face takes a
            # point of the frame paint. Own UVs, so `finish=False` -- the
            # cube projection would overwrite them -- and a white COLOR_0,
            # which Level Factory's import multiplies by.
            u0, v0, u1, v1 = window_panes.uv_rect(state)
            frame = window_panes.uv_rect("lit")[0] * 0.25
            uv = bm.loops.layers.uv.new("UVMap")
            hx, hz = pane_w * 0.49, pane_h * 0.49
            bm.normal_update()
            for face in bm.faces:
                for loop in face.loops:
                    if face.normal.y > 0.9:
                        co = loop.vert.co
                        # seen from +Y looking at -Y, +X is the viewer's
                        # LEFT: u runs from the +X edge, or the cell mirrors
                        loop[uv].uv = (u0 + (u1 - u0) * ((cx + hx) - co.x) / (2 * hx),
                                       v0 + (v1 - v0) * (co.z - (cz - hz)) / (2 * hz))
                    else:
                        loop[uv].uv = (frame, frame)
'''
ARCH_NEW = '''            # A PAINTED PANE (1.64.0): both big faces show the state's cell
            # of the shared atlas, each unmirrored from its own side, and the
            # thin edges take frame paint (`window_panes.face_uv`, 1.66.0 --
            # 1.64.0 painted only +Y, and cold run 9151 measured that face
            # pointing into the house). Own UVs, so `finish=False` -- the
            # cube projection would overwrite them -- and a white COLOR_0,
            # which Level Factory's import multiplies by.
            uv = bm.loops.layers.uv.new("UVMap")
            hx, hz = pane_w * 0.49, pane_h * 0.49
            bm.normal_update()
            for face in bm.faces:
                for loop in face.loops:
                    co = loop.vert.co
                    loop[uv].uv = window_panes.face_uv(
                        state, face.normal.y, co.x, co.z, cx, cz, hx, hz)
'''

TEST_ANCHOR = '''def _window(pane=None, glazing="facade"):'''
TEST_NEW = '''def _inside(uv, state):
    u0, v0, u1, v1 = P.uv_rect(state)
    return u0 - 1e-9 <= uv[0] <= u1 + 1e-9 and v0 - 1e-9 <= uv[1] <= v1 + 1e-9


def test_both_big_faces_carry_the_cell_and_the_edges_the_frame():
    """FAILS ON 1.65.0: only the +Y face was painted, and cold run 9151
    measured that face pointing INTO the house -- the street saw frame paint."""
    box = (0.0, 1.55, 0.475, 0.8)          # cx, cz, hx, hz
    for ny in (1.0, -1.0):
        for x in (-0.475, 0.475):
            for z in (0.75, 2.35):
                assert _inside(P.face_uv("lit_amber", ny, x, z, *box), "lit_amber")
    assert P.face_uv("lit_amber", 0.0, 0.475, 1.5, *box) == P.frame_uv()
    a, _ = P.atlas()
    w, h = P.COLS * P.CELL_W, P.ROWS * P.CELL_H
    fu, fv = P.frame_uv()
    assert a.get(int(fu * w), min(h - 1, int((1 - fv) * h))) == P.FRAME_RGB


def test_each_face_reads_unmirrored_from_its_own_side():
    """Seen from +Y the viewer's right is -X; seen from -Y it is +X. On both,
    u must grow toward the viewer's right, or one side shows the cell
    mirrored."""
    box = (0.0, 1.55, 0.475, 0.8)
    left_from_plus = P.face_uv("lit", 1.0, 0.4, 1.5, *box)[0]
    right_from_plus = P.face_uv("lit", 1.0, -0.4, 1.5, *box)[0]
    assert right_from_plus > left_from_plus
    left_from_minus = P.face_uv("lit", -1.0, -0.4, 1.5, *box)[0]
    right_from_minus = P.face_uv("lit", -1.0, 0.4, 1.5, *box)[0]
    assert right_from_minus > left_from_minus
    # and up is up on both: v grows with z
    assert P.face_uv("lit", 1.0, 0.0, 2.3, *box)[1] > P.face_uv("lit", 1.0, 0.0, 0.8, *box)[1]
    assert P.face_uv("lit", -1.0, 0.0, 2.3, *box)[1] > P.face_uv("lit", -1.0, 0.0, 0.8, *box)[1]


def _window(pane=None, glazing="facade"):'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.65.0"
    _edit(ZOO / "zoo_keeper" / "core" / "window_panes.py", [(UV_OLD, UV_NEW)])
    _edit(ZOO / "zoo_keeper" / "recipes" / "_arch.py", [(ARCH_OLD, ARCH_NEW)])
    _edit(ZOO / "tests" / "test_window_panes.py", [(TEST_ANCHOR, TEST_NEW)])
    (SRC / "test_window_panes.py").write_bytes((ZOO / "tests" / "test_window_panes.py").read_bytes())
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.66.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.66.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.66.0")


if __name__ == "__main__":
    main()
