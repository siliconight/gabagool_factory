"""Lux 0.68.1: the room fills are owned by the scene, so the lightmapper
takes them.

    python patch_lux_bake_fill_owned.py

0.68.0 left the fill unowned "so even a save that forgot to free it cannot
keep it". Godot's LightmapGI skips any child with no owner when it collects
lights (lightmap_gi.cpp, `_find_meshes_and_lights`: "maybe a helper"), so
the first real bake -- Level Factory 0.151.0's plugin on cold run 9190's
level, 267 fills laid -- baked none of them: every room read the control's
number. The fills are now owned by the scene's owner (the edited root in a
bake), and the bake frees them before it saves.

Anchored on `lux/addons/lux/runtime/lux_light_loader.gd` as 0.68.0 left it
(94,887 bytes, LF). Every anchor must match once.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOADER = ROOT / "lux" / "addons" / "lux" / "runtime" / "lux_light_loader.gd"

EDITS = [
    ("## bake lays before it bakes and frees before it saves. The container has no\n"
     "## owner, so even a save that forgot to free it cannot keep it, and a level\n"
     "## carries no fill at runtime: nothing to draw, nothing to price. Dynamic\n"
     "## objects see it through the lightmap's own probes.\n",
     "## bake lays before it bakes and frees before it saves, so a level carries no\n"
     "## fill at runtime: nothing to draw, nothing to price. Dynamic objects see it\n"
     "## through the lightmap's own probes.\n"
     "##\n"
     "## OWNED, AND THE BAKE MUST FREE IT (0.68.1). 0.68.0 left the fill unowned \"so\n"
     "## even a save that forgot to free it cannot keep it\". LightmapGI skips any\n"
     "## child with no owner when it collects lights (\"maybe a helper\", Godot's\n"
     "## `_find_meshes_and_lights`), so the first real bake -- Level Factory\n"
     "## 0.151.0's, 267 fills laid on cold run 9190's level -- baked none: every\n"
     "## room read the control's number. The experiments that chose the layout\n"
     "## had written their fills into the bake scene, owned, which is why they lit.\n"
     "## Every fill is owned by the scene's owner now, and freeing it before the\n"
     "## save is the bake's job.\n"),
    ("\t\t\tcontainer.name = BAKE_FILL_CONTAINER\n\t\t\tscene_root.add_child(container)\n",
     "\t\t\tcontainer.name = BAKE_FILL_CONTAINER\n\t\t\tscene_root.add_child(container)\n"
     "\t\t\tcontainer.owner = owner_node\n"),
    ("\t\t\t\tcontainer.add_child(omni)\n",
     "\t\t\t\tcontainer.add_child(omni)\n"
     "\t\t\t\tomni.owner = owner_node\n"),
    ("\tvar container: Node3D = null\n\tfor n in scene_root.find_children(\"*\", \"ReflectionProbe\", true, false):\n",
     "\t# owned, or LightmapGI passes the fill by as a helper (0.68.1)\n"
     "\tvar owner_node: Node = scene_root if scene_root.owner == null else scene_root.owner\n"
     "\tvar container: Node3D = null\n\tfor n in scene_root.find_children(\"*\", \"ReflectionProbe\", true, false):\n"),
]


def main():
    data = LOADER.read_bytes()
    assert len(data) == 94887, "loader is %d bytes, read at 94,887" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old, new in EDITS:
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:60])
        text = text.replace(old, new)
    LOADER.write_bytes(text.encode("utf-8"))
    print("lux_light_loader.gd: %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
