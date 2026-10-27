"""Edit a Level Factory clone's merge tests for 0.258.0 (after edit_lf_opening_merge.py). Run from the clone's root."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


edit("tests/unit/test_merge_buildings.py", [
("""         "unwrapped": 560, "colliders": 485, "units": {"ext": 24, "int": 7, "roof": 5, "room": 434},
         "lit_surfaces": 132, "lit_meshes": 90,""",
"""         "unwrapped": 590, "colliders": 485, "units": {"ext": 24, "int": 7, "roof": 5, "room": 434},
         "lit_surfaces": 132, "lit_meshes": 90, "glass_surfaces": 41, "glass_meshes": 30,"""),
("""    _report([_row(ASKED[0]), _row(ASKED[1], unwrapped=470)]),    # the lit meshes not unwrapped""",
"""    _report([_row(ASKED[0]), _row(ASKED[1], unwrapped=470)]),    # the lit meshes not unwrapped
    _report([_row(ASKED[0]), _row(ASKED[1], unwrapped=560)]),    # the glass meshes not unwrapped (0.258.0)
    _report([_row(ASKED[0]), _row(ASKED[1], glass_meshes=0)]),   # glass surfaces in no mesh
    # a merge before 0.258.0, which kept every opening whole and counted no glass
    _report([_row(ASKED[0]), {k: v for k, v in _row(ASKED[1]).items() if k != "glass_surfaces"}]),"""),
('''    """Held to the Godot half's source: an interactive slot, an opening, anything animated, scripted or
    shader-driven, the collision base and the covers are never taken apart."""
    text = M.MERGE_SCRIPT.read_text(encoding="utf-8")
    keep = _func(text, "_mergeable")
    for needle in ('"GreyboxBase"', '"Dressing"', 'has_meta("interactive_id")', 'name.find("_open") >= 0',
                   "AnimationPlayer", "get_script() != null", "is ShaderMaterial", "_fixture(m)"):
        assert needle in keep, needle''',
'''    """Held to the Godot half's source: an interactive slot, anything animated, scripted or shader-driven, the
    collision base and the covers are never taken apart. An OPENING is, since 0.258.0 (`test_an_openings_glass_...`)."""
    text = M.MERGE_SCRIPT.read_text(encoding="utf-8")
    keep = _func(text, "_mergeable")
    for needle in ('"GreyboxBase"', '"Dressing"', 'has_meta("interactive_id")',
                   "AnimationPlayer", "get_script() != null", "is ShaderMaterial", "_fixture(m)"):
        assert needle in keep, needle
    assert "_open" not in keep'''),
('''def test_a_room_unit_is_cut_into_cells():''',
'''def test_an_openings_glass_stays_its_own_instances_mesh():
    """0.258.0: an opening's surround merges with its wall -- the walker's seams round doors, breach panels and
    windows (the factory's docs/findings/walk_2026-10-26_panel/, L5-L7) -- and a transparent surface goes into one
    mesh of its own where its instance stood (`GlassR_<n>`), sorted as it always was."""
    text = M.MERGE_SCRIPT.read_text(encoding="utf-8")
    glass = _func(text, "_glass")
    assert "transparency != BaseMaterial3D.TRANSPARENCY_DISABLED" in glass
    merge = _func(text, "_merge_scene")
    pane_at = merge.index("if _glass(mat):")
    assert merge.index("continue", pane_at) < merge.index("var key: String = _key(unit, mat, fmt)")
    assert 'gout.name = "GlassR_%d" % gi' in merge


def test_a_room_unit_is_cut_into_cells():'''),
])

edit("tests/unit/test_merge_buildings_godot.py", [
('''[sub_resource type="BoxShape3D" id="Shape_box"]

[node name="Building" type="Node3D"]''',
'''[sub_resource type="BoxShape3D" id="Shape_box"]

[sub_resource type="StandardMaterial3D" id="Mat_glass"]
resource_name = "M_glass"
transparency = 1

[node name="Building" type="Node3D"]'''),
('''[node name="lamp_r1_0" type="Node3D" parent="."]''',
'''[node name="ext_0_N_open1" type="Node3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 4, 0, 0)

[node name="Mesh" type="MeshInstance3D" parent="ext_0_N_open1"]
mesh = SubResource("BoxMesh_box")
surface_material_override/0 = SubResource("Mat_wall")

[node name="Pane" type="MeshInstance3D" parent="ext_0_N_open1"]
mesh = SubResource("BoxMesh_box")
surface_material_override/0 = SubResource("Mat_glass")

[node name="lamp_r1_0" type="Node3D" parent="."]'''),
('''    # the two wall modules, one storey's side, into one mesh; the lamp's prop, the ladders and the markers left whole
    assert (row["slots_merged"], row["surfaces_in"], row["merged"], row["colliders"]) == (2, 2, 1, 1), row''',
'''    # the two wall modules and the window's surround, one storey's side, into one mesh; the pane its own (0.258.0);
    # the lamp's prop, the ladders and the markers left whole
    assert (row["slots_merged"], row["surfaces_in"], row["merged"], row["colliders"]) == (3, 3, 1, 1), row
    assert (row["glass_surfaces"], row["glass_meshes"]) == (1, 1), row'''),
('''def test_a_bare_socket_does_not_keep_its_module_whole(merged):''',
'''def test_an_openings_surround_merges_and_its_pane_stands_alone(merged):
    """0.258.0: the window slot is gone, its wall surface in `MergedR_0`, its glass in `GlassR_0`. FAILS ON 0.257.0,
    which kept `ext_0_N_open1` whole."""
    _rep, scene, _log = merged
    nodes = _nodes(scene)
    assert not [k for k in nodes if "ext_0_N_open1" in k], sorted(nodes)
    assert nodes.get((".", "GlassR_0"), (None,))[0] == "MeshInstance3D"


def test_a_bare_socket_does_not_keep_its_module_whole(merged):'''),
])
