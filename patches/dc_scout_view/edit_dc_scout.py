"""Deli Counter 0.258.0, the scout view (the factory's roadmap 296), applied to a CLONE: <repo>. The renderer's
`scout=` was made first, in the clone, by `edit_axo_scout_first.py` beside this and then by hand after its first
frames (one leader a flight, one line a hole, thicker doors: README.md); the clone's diff is the patch. This adds the package's `scout.svg`, the tests, VERSION
and the changelog. Anchored; refuses on a miss; keeps each file's line endings."""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("portable_building.py", [
    ("""    first; none in the library has two, read 2026-10-21) -- each with a ``.import`` that keeps it as the file it is
    (`KEEP_IMPORT`), and ``drawings.json`` naming them.""",
     """    first; none in the library has two, read 2026-10-21) -- and since 0.258.0 its scout view, ``scout.svg``
    (`render_axonometric(scout=True)`: only what a body finds its way by, the walker's "simpler but carry all of the
    signals needed") -- each with a ``.import`` that keeps it as the file it is (`KEEP_IMPORT`), and
    ``drawings.json`` naming them."""),
    ("""    record = {"schema": "deli_counter.drawings.v1", "spec": spec.name, "axonometric": None, "plans": []}""",
     """    record = {"schema": "deli_counter.drawings.v1", "spec": spec.name, "axonometric": None, "scout": None,
              "plans": []}"""),
    ("""        files["axonometric.svg"] = axonometric.render_axonometric(spec)
        record["axonometric"] = "axonometric.svg"
""",
     """        files["axonometric.svg"] = axonometric.render_axonometric(spec)
        record["axonometric"] = "axonometric.svg"
        files["scout.svg"] = axonometric.render_axonometric(spec, scout=True)
        record["scout"] = "scout.svg"
"""),
])

edit("test_package_drawings.py", [
    ("""    rec = PB.package_drawings(_spec("deli_a03"), str(tmp_path))
    spec = spec_loader.load_spec(_spec("deli_a03"))
    d = tmp_path / "drawings"
    assert rec["spec"] == spec.name and rec["axonometric"] == "axonometric.svg"
""",
     """    rec = PB.package_drawings(_spec("deli_a03"), str(tmp_path))
    spec = spec_loader.load_spec(_spec("deli_a03"))
    d = tmp_path / "drawings"
    assert rec["spec"] == spec.name and rec["axonometric"] == "axonometric.svg" and rec["scout"] == "scout.svg"
"""),
    ("""    assert (d / "axonometric.svg").read_text(encoding="utf-8") == AX.render_axonometric(spec)
""",
     """    assert (d / "axonometric.svg").read_text(encoding="utf-8") == AX.render_axonometric(spec)
    assert (d / "scout.svg").read_text(encoding="utf-8") == AX.render_axonometric(spec, scout=True)
"""),
    ("""    assert svgs == sorted(["axonometric.svg"] + [p["file"] for p in rec["plans"]])""",
     """    assert svgs == sorted(["axonometric.svg", "scout.svg"] + [p["file"] for p in rec["plans"]])"""),
    ("""    assert rec["axonometric"] is None and rec["plans"] == [] and "facade" in rec["none_because"]""",
     """    assert rec["axonometric"] is None and rec["scout"] is None and rec["plans"] == []
    assert "facade" in rec["none_because"]"""),
])

(R / "test_scout_view.py").write_text('''"""The scout view: a building drawn with only what a body finds its way by (0.258.0, the factory's roadmap 296).

The walker judged the exploded axonometric on a review page (2026-10-22): one storey of pharmacy "Looks right"; deli_a03
and office "Needs work" -- "we need to find a way to be simple and not noisy visually" -- and what players should see,
"simpler but carry all of the signals needed". `render_axonometric(scout=True)` keeps the storeys, the cut and the
offsets, and every wall, opening, tread, ladder and hole; it leaves out furniture, room names and tints, markers, and
the dashed lines that join the storeys, keeping one line for each flight and each hole.

THE TEST THAT MATTERS IS `test_the_scout_view_keeps_every_signal_the_full_drawing_carries`: simpler must not mean
less to find your way by.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import axonometric as AX  # noqa: E402
import spec_loader  # noqa: E402

#: The review page's three buildings, and the library's every vertical link kind among them (stairs both straight and
#: switchback, a ladder, an authored floor hole).
NAMES = ("deli_a03", "office", "pharmacy_a01")
SIGNALS = ("data-wall", "data-opening", "data-tread", "data-landing", "data-ladder", "data-void")


def _load(name):
    return spec_loader.load_spec(os.path.join(HERE, "specs", name + ".json"))


def _attrs(svg, attr):
    """Every value of one attribute, with the attributes that follow it on its element -- an opening's kind and place,
    a tread's height -- so a signal moved or dropped is seen, not only a signal's name."""
    return sorted(re.findall(r'%s="([^"]*)"((?: data-[a-z-]+="[^"]*")*)' % attr, svg))


def test_the_scout_view_keeps_every_signal_the_full_drawing_carries():
    """Every wall piece, door and window (with its kind and place), tread and landing (with its height), ladder and
    hole of the full drawing is in the scout view, the same, and nothing is added."""
    seen = set()
    for name in NAMES:
        spec = _load(name)
        full, scout = AX.render_axonometric(spec), AX.render_axonometric(spec, scout=True)
        for attr in SIGNALS:
            assert _attrs(scout, attr) == _attrs(full, attr), (name, attr)
            if _attrs(full, attr):
                seen.add(attr)
    # the control: across the three, every kind of signal is there to be kept (pharmacy_a01 has one storey, no stair)
    assert seen == set(SIGNALS), seen


def test_the_scout_view_leaves_out_what_a_body_does_not_find_its_way_by():
    """No furniture, no room fills or names, no markers, no dashed line anywhere, and no "furniture" in the legend --
    each of which the full drawing of the same building carries."""
    for name in NAMES:
        spec = _load(name)
        full, scout = AX.render_axonometric(spec), AX.render_axonometric(spec, scout=True)
        for attr in ("data-object", "data-room", "data-marker"):
            assert attr not in scout, (name, attr)
        assert "stroke-dasharray" not in scout and ">furniture<" not in scout, name
        # the control: the full drawing of the same building carries what the scout view leaves out
        assert "data-object" in full and "data-room" in full and ">furniture<" in full, name
        assert 'data-view="scout"' in scout and "scout view" in scout, name


def test_each_flight_and_each_hole_keeps_one_line_to_the_floor_it_reaches():
    """The joins between storeys are a signal: a flight's head carries on to the storey it reaches, a hole down to the
    floor it opens onto. Each pair of storeys a stair serves keeps its group with one leader; each hole that opens onto
    a drawn storey, one line."""
    for name in NAMES:
        spec = _load(name)
        full, scout = AX.render_axonometric(spec), AX.render_axonometric(spec, scout=True)
        joins = re.findall(r'<g data-stair="([^"]+)" data-from="(-?\\d+)" data-to="(-?\\d+)">(.*?)</g>', scout, re.S)
        assert [j[:3] for j in joins] == re.findall(r'<g data-stair="([^"]+)" data-from="(-?\\d+)" '
                                                     r'data-to="(-?\\d+)">', full), name
        for sid, a, b, inner in joins:
            assert inner.count("<line") in (1, 3), (name, sid, a, b)   # a leader, and its two arrowhead strokes
        conn = scout[scout.index('<g id="connections">'):]
        assert conn.count("<line") >= len(joins), name


def test_the_scout_view_is_deterministic_and_holds_its_text():
    for name in NAMES + ("gs_facade_rowhome",):
        spec = _load(name)
        svg = AX.render_axonometric(spec, scout=True)
        assert svg == AX.render_axonometric(spec, scout=True), name
        width = float(re.search(r'<svg [^>]*width="([\\d.]+)"', svg).group(1))
        legend = re.findall(r'<text x="([\\d.]+)" y="[\\d.]+" font-size="9.5" fill="#52606d">([^<]*)</text>', svg)
        x, word = legend[-1]
        assert float(x) + len(word) * 6.0 <= width, (name, word)
        for size, bold, text in re.findall(r'<text x="40" y="(?:24|38|50)" font-size="([\\d.]+)"( font-weight="700")?'
                                           r'[^>]*>([^<]*)</text>', svg):
            em = AX.CHAR_EM_BOLD if bold else AX.CHAR_EM
            assert AX.PADDING + len(text) * float(size) * em <= width + 1e-6, (name, text)
''', encoding="utf-8", newline="\n")

v = (R / "VERSION").read_text(encoding="utf-8")
assert v.strip() == "Deli Counter 0.257.0", v
(R / "VERSION").write_bytes(v.replace("0.257.0", "0.258.0").encode("utf-8"))
print("edited", R)
