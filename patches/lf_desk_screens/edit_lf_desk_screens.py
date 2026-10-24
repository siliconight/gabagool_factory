"""Level Factory 0.239.0 on a CLONE (<repo>): a desk's monitor gets the club TVs' motion (the walker's walk of cold run
9386, finding 5: "screens should have the same effect as the tvs in the strip club that give them that little
movement/"shimmer" to show "life""). Anchored; refuses on a miss.

    python edit_lf_desk_screens.py <repo>
"""
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


edit("assets/godot/zoo_worldskin.gd", [
    ('''const CRT_FACE_MARK: String = "CRT_Screen"
const CRT_FACE_SUFFIX: String = "_Face"
const CRT_FACE_PREFIX: String = "M_"''',
     '''const CRT_FACE_MARK: String = "CRT_Screen"
const CRT_FACE_SUFFIX: String = "_Face"
const CRT_FACE_PREFIX: String = "M_"
## A DESK'S MONITOR IS A CRT TOO (0.239.0). Zoo 1.115.0 lights a desk's screen
## on a backlit `M_StockScreen_<atlas>_Face` (`prim_mesh.build_stock`), and
## this pass took only `CRT_Screen`, so every office monitor was a still
## picture. The walker, walking cold run 9386: "screens should have the same
## effect as the tvs in the strip club". Same pass, same numbers: a 1997
## office's monitors are tubes. They live in the export's MERGED lit meshes
## (`merge_buildings.gd`, `LitR_*`, one a desk where it stood), whose
## `duplicate(true)` carries the next_pass this hangs at import. PRICED before
## it shipped: the factory's `patches/lf_desk_screens/` (three arms, one
## session).
const DESK_SCREEN_MARK: String = "StockScreen"'''),
    ('''func _is_crt_face(nm: String) -> bool:
	return nm.begins_with(CRT_FACE_PREFIX) and nm.ends_with(CRT_FACE_SUFFIX) \\
		and nm.contains(CRT_FACE_MARK)''',
     '''func _is_crt_face(nm: String) -> bool:
	return nm.begins_with(CRT_FACE_PREFIX) and nm.ends_with(CRT_FACE_SUFFIX) \\
		and (nm.contains(CRT_FACE_MARK) or nm.contains(DESK_SCREEN_MARK))'''),
])
edit("tests/unit/test_worldskin_crt_motion.py", [
    ('''    # and the pass itself asks that question before doing anything
    crt = _func(src, "_crt_motion")
    assert "if not _is_crt_face(" in crt''',
     '''    # and the pass itself asks that question before doing anything
    crt = _func(src, "_crt_motion")
    assert "if not _is_crt_face(" in crt


def test_a_desk_monitor_s_lit_screen_gets_the_motion_too():
    """0.239.0, the walker walking cold run 9386: "screens should have the same
    effect as the tvs in the strip club". Zoo names a desk's lit screen
    `M_StockScreen_<atlas>_Face`; the pass takes it beside `CRT_Screen`, with
    the prefix and suffix still asked of both. FAILS ON 0.238.0."""
    src = _src()
    assert 'DESK_SCREEN_MARK: String = "StockScreen"' in src
    body = _func(src, "_is_crt_face")
    assert "nm.contains(CRT_FACE_MARK) or nm.contains(DESK_SCREEN_MARK)" in body
    assert "begins_with(CRT_FACE_PREFIX)" in body and "ends_with(CRT_FACE_SUFFIX)" in body


def test_the_merge_carries_the_overlay_onto_the_merged_lit_faces():
    """The desk screens live in the export's merged lit meshes; the merge gives
    each a DEEP copy of its material, which keeps the next_pass hung here."""
    merge = (SCRIPT.parent / "merge_buildings.gd").read_text(encoding="utf-8")
    assert "(pair[1] as Material).duplicate(true)" in merge'''),
])
print("zoo_worldskin: desk screens take the CRT motion; tests")
