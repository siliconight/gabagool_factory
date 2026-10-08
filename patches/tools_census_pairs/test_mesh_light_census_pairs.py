"""mesh_light_census counts what the engine pairs, beside what reaches (2026-10-08).

Godot 4.7's culler never binds a light whose cull mask misses a mesh's
layers, nor a BAKE_STATIC light to a mesh that has a lightmap
(`servers/rendering/renderer_scene_cull.cpp`, `_scene_cull`). The census
counted reach alone, so on a package Level Factory had baked it over-reported
exactly on the lightmapped meshes. Level Factory 0.159.0's perf census got
the same rule (`patches/patch_lf_census_pairs.py`).

THE PAYLOAD RUNS HERE FOR REAL. A headless Godot builds two meshes, a
LightmapGI whose LightmapGIData lists one of them, and three visible lights
that reach both -- plus a hidden one, which the census has always left out --
and the payload counts them as it counts a level:
  Baked     BAKE_STATIC   paired with B, not with A (A has a lightmap)
  Live      BAKE_DYNAMIC  paired with both
  LayerOne  cull mask 1   paired with A, not with B (B is on layer 2)
Skipped where no Godot is installed.

    python -m pytest tools/test_mesh_light_census_pairs.py -q
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PAYLOAD = HERE / "mesh_light_census.gd"
MARK_BEGIN, MARK_END = "<<<MESH_LIGHT_CENSUS_JSON", "MESH_LIGHT_CENSUS_JSON>>>"

BUILD = """extends SceneTree


func _initialize() -> void:
\t# A WATCHDOG: a payload that errors never reaches its own quit().
\tcreate_timer(20.0).timeout.connect(_watchdog)
\t_run()


func _watchdog() -> void:
\tprint("CENSUS_WATCHDOG")
\tquit(3)


## A frame before the payload enters, so the site is inside the tree: during
## `_initialize` nothing added to the root is yet.
func _run() -> void:
\tvar site := Node3D.new()
\tsite.name = "Site"
\troot.add_child(site)
\tvar a := MeshInstance3D.new()
\ta.name = "A"
\ta.mesh = BoxMesh.new()
\ta.layers = 1
\tsite.add_child(a)
\tvar b := MeshInstance3D.new()
\tb.name = "B"
\tb.mesh = BoxMesh.new()
\tb.layers = 2
\tb.position = Vector3(3.0, 0.0, 0.0)
\tsite.add_child(b)
\tvar data := LightmapGIData.new()
\tdata.add_user(NodePath("../A"), Rect2(0.0, 0.0, 1.0, 1.0), 0, -1)
\tvar bake := LightmapGI.new()
\tbake.name = "Bake"
\tbake.light_data = data
\tsite.add_child(bake)
\t_lamp(site, "Baked", Light3D.BAKE_STATIC, 0xFFFFFFFF, true)
\t_lamp(site, "Live", Light3D.BAKE_DYNAMIC, 0xFFFFFFFF, true)
\t_lamp(site, "LayerOne", Light3D.BAKE_DYNAMIC, 1, true)
\t_lamp(site, "Hidden", Light3D.BAKE_DYNAMIC, 0xFFFFFFFF, false)
\tawait process_frame
\tcurrent_scene = site
\tvar census: Node = load("res://mesh_light_census.gd").new()
\troot.add_child(census)


func _lamp(parent: Node3D, lamp: String, mode: int, mask: int, shown: bool) -> void:
\tvar l := OmniLight3D.new()
\tl.name = lamp
\tl.omni_range = 20.0
\tl.light_bake_mode = mode
\tl.light_cull_mask = mask
\tl.visible = shown
\tl.position = Vector3(1.5, 2.0, 0.0)
\tparent.add_child(l)
"""


def _godot():
    for env in ("LF_GODOT", "DC_GODOT", "LOT_GODOT"):
        p = os.environ.get(env)
        if p and Path(p).is_file():
            return p
    usual = Path("C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe")
    if usual.is_file():
        return str(usual)
    return shutil.which("godot")


godot_required = pytest.mark.skipif(_godot() is None, reason="no Godot binary")


def _census(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "project.godot").write_text('config_version=5\n\n[application]\n\nconfig/name="census"\n',
                                        encoding="utf-8")
    (proj / "mesh_light_census.gd").write_bytes(PAYLOAD.read_bytes())
    (proj / "build.gd").write_text(BUILD, encoding="utf-8")
    out = subprocess.run([_godot(), "--headless", "--path", str(proj), "--script", "res://build.gd"],
                         capture_output=True, text=True, timeout=90)
    log = out.stdout + out.stderr
    # No block is a census that never ran, not one that counted nothing.
    assert MARK_BEGIN in log and MARK_END in log, log
    return json.loads(log.split(MARK_BEGIN, 1)[1].split(MARK_END, 1)[0])


@godot_required
def test_the_reach_count_is_unchanged(tmp_path):
    """The three visible lights reach both meshes; the hidden one is left out,
    as the census always left it out."""
    c = _census(tmp_path)
    assert c["meshes"] == 2 and c["positional_lights"] == 3, c
    assert c["histogram"] == {"3": 2} and c["worst"] == 3, c


@godot_required
def test_the_paired_count_applies_both_rules(tmp_path):
    """FAILS BEFORE THIS CHANGE: the payload carries no paired count.

    A pairs Live and LayerOne (Baked is in its lightmap): 3 if the lightmap
    rule were missing. B pairs Baked and Live (LayerOne misses layer 2): 3 if
    the cull rule were missing."""
    c = _census(tmp_path)
    assert "paired_histogram" in c, "the payload carries no paired count"
    assert c["paired_histogram"] == {"2": 2}, c
    assert c["paired_worst"] == 2 and c["paired_over_8"] == 0, c
    assert c["lightmap_users"] == 1, c
