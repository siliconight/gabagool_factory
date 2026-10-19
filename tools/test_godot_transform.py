"""Every factory tool that reads a `.tscn` Transform3D reads it as Godot does (2026-10-19, roadmap 177's class).

`tools/godot_transform.py` is the one reader: the basis's three ROWS, then the origin, pinned here to the numbers
the engine measured -- cold run 9324's `ext_0_E_seg10` (`tools/module_pose_census.py`: x 18.825..19.175, z
-6.300..-5.700) and Lot's 30-degree `str_to_var` (local +X to (0.866, 0, -0.5)). Five tools read the twelve
numbers as columns until this date; each is held to the shared reader on the same numbers, so the next one to
drift fails here rather than in a finding.

Run: python -m pytest -q tools/test_godot_transform.py
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import godot_transform as G  # noqa: E402

# exactly as cold run 9324's lot/deli_a01/site.tscn writes it
SEG10 = [0.0, 0.0, -0.35, 0.0, 3.0, 0.0, 0.6, 0.0, 0.0, 19.0, 1.496, -6.0]
# Lot's measured turn, `Transform3D(c, 0, s, 0, 1, 0, -s, 0, c, ...)` at 30 degrees
THIRTY = [0.866025, 0.0, 0.5, 0.0, 1.0, 0.0, -0.5, 0.0, 0.866025, 0.0, 0.0, 0.0]
TEXT = ", ".join(repr(v) for v in SEG10)


def _close(a, b, tol=1e-6):
    return all(abs(x - y) < tol for x, y in zip(a, b))


def test_the_reader_stands_the_end_piece_where_the_engine_did():
    lo, hi = G.box(SEG10, (-0.5, -0.5, -0.5), (0.5, 0.5, 0.5))
    assert _close(lo, (18.825, -0.004, -6.3)) and _close(hi, (19.175, 2.996, -5.7)), (lo, hi)


def test_the_reader_turns_as_lot_measured():
    assert _close(G.axis(THIRTY, 0), (0.866025, 0.0, -0.5))


def test_scale_is_the_columns_length():
    assert _close(G.scales(SEG10), (0.6, 3.0, 0.35))


def test_floats_reads_the_text_forms():
    assert _close(G.floats("transform = Transform3D(%s)" % TEXT), SEG10)
    assert _close(G.floats(TEXT), SEG10)


def test_site_fights_reads_rows():
    import site_fights
    assert site_fights._m(TEXT) == G.matrix(SEG10)


def test_insert_overhang_reads_rows():
    import insert_overhang
    got = insert_overhang.godot_transform([str(v) for v in SEG10])
    assert [list(r) for r in got] == G.matrix(SEG10)


def test_light_check_reads_rows(tmp_path):
    import light_check
    (tmp_path / "site.tscn").write_text(
        '[ext_resource type="PackedScene" path="res://lot/deli_a01/site.tscn" id="1_b"]\n\n'
        '[node name="b0" parent="." instance=ExtResource("1_b")]\ntransform = Transform3D(%s)\n' % TEXT,
        encoding="utf-8")
    arch, basis, origin = light_check.placements(str(tmp_path))["b0"]
    assert arch == "deli_a01"
    assert [list(r) for r in basis] == [row[:3] for row in G.matrix(SEG10)]
    assert _close(origin, (19.0, 1.496, -6.0))


def test_module_extents_reads_rows():
    import module_extents
    m = module_extents._tscn_matrix(SEG10)          # column-major 4x4
    for k in range(3):
        assert _close(m[4 * k:4 * k + 3], G.axis(SEG10, k)), k
    assert _close(module_extents._scale_of(SEG10), G.scales(SEG10))


def test_repetition_census_scales_by_columns():
    import repetition_census
    text = ('[ext_resource type="PackedScene" path="res://art/zoo/wallEnd.glb" id="1_w"]\n\n'
            '[node name="ext_0_E_seg10" parent="." instance=ExtResource("1_w")]\n'
            'transform = Transform3D(%s)\n' % TEXT)
    (name, stem, scale, origin), = repetition_census.parse_scene(text)
    assert name == "ext_0_E_seg10" and stem == "wallEnd"
    assert _close(scale, (0.6, 3.0, 0.35), 1e-4)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
