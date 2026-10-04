"""Patina 0.24.0: which way is up is read off the file, not guessed.

`slots.detect_up_axis` took the smallest-extent axis as up; the rowhome
Empties are narrower than they are tall, so up read X and their dressing was
built on its side (cold run 9147, the walker: "x, y, z axis mismatch on some
of the patina pieces"). See `patina_up_axis/CHANGELOG_0.24.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  patina/mesh.py     Scene.up_axis_hint
  patina/gltf_io.py  load reads the declaration; save carries it forward
  patina/slots.py    detect_up_axis returns the hint before guessing
  patina/cli.py      the result names the source of the axis
  patina/version.py  0.22.0 -> 0.24.0 (it missed 0.23.0)
Copies the test; CHANGELOG and VERSION.

    python patch_patina_up_axis.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PA = HERE.parent / "patina"
SRC = HERE / "patina_up_axis"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


MESH_OLD = '''    lights: Optional[dict] = None      # parsed <name>.lights.json (DC light anchors), if present
'''
MESH_NEW = '''    lights: Optional[dict] = None      # parsed <name>.lights.json (DC light anchors), if present
    #: The up axis (0=X 1=Y 2=Z) the FILE declares, or None when it says
    #: nothing -- set by `gltf_io.load_glb`, read first by
    #: `slots.detect_up_axis` (0.24.0).
    up_axis_hint: Optional[int] = None
'''

LOAD_OLD = '''    scene.lights = _load_lights(path)
    return scene
'''
LOAD_NEW = '''    scene.lights = _load_lights(path)
    scene.up_axis_hint = _declared_up(g)
    return scene


#: Blender's glTF exporter writes +Y up unless `export_yup=False`, and Deli
#: Counter exports with the default (`deli_counter.py`,
#: `bpy.ops.export_scene.gltf`). A file that says Blender wrote it is Y-up.
_BLENDER_GENERATOR = "Khronos glTF Blender I/O"
#: Where Patina's own output records the axis it was given: Patina replaces
#: the generator string, so without this a second pass over its output would
#: be back to guessing.
_UP_EXTRA = "patina_up_axis"


def _declared_up(g) -> Optional[int]:
    """The up axis a file declares (0.24.0), or None when it declares none.

    THE GUESS IT REPLACES, kept above it: `slots.detect_up_axis` took the
    smallest-extent axis as up because "a building is wide and shallow". The
    rowhome Empties are 6.3 m wide and up to 10.1 m tall, so up read X and
    every height-dependent pass ran on its side (cold run 9147).
    """
    asset = g.asset
    extras = getattr(asset, "extras", None) or {}
    if isinstance(extras, dict) and extras.get(_UP_EXTRA) in ("X", "Y", "Z"):
        return "XYZ".index(extras[_UP_EXTRA])
    if (getattr(asset, "generator", None) or "").startswith(_BLENDER_GENERATOR):
        return 1
    return None
'''

SAVE_OLD = '''    g.asset = gl.Asset(version="2.0", generator=f"Patina {version.__version__}")
'''
SAVE_NEW = '''    g.asset = gl.Asset(version="2.0", generator=f"Patina {version.__version__}")
    if scene.up_axis_hint is not None:          # carried forward, never guessed into
        g.asset.extras = {_UP_EXTRA: "XYZ"[scene.up_axis_hint]}
'''

DETECT_OLD = '''    A building is wide and shallow: the vertical extent (wall height, a few
    metres) is the *smallest* of the three axis ranges. Detecting up as the
    min-range axis makes the height-dependent passes correct for both DC's
    Y-up exports and legacy Z-up shells, with no per-file configuration.
    """
    lo = np.full(3, np.inf)
'''
DETECT_NEW = '''    THE FILE IS ASKED FIRST (0.24.0): `Scene.up_axis_hint`, which
    `gltf_io.load_glb` reads off the file's own declaration -- Patina's
    `asset.extras`, else Blender's exporter as the generator, which writes
    +Y up. Only a file that declares nothing falls through to the guess below.

    RETRACTED AS THE RULE, kept as the fallback: "A building is wide and
    shallow: the vertical extent (wall height, a few metres) is the
    *smallest* of the three axis ranges." Deli Counter 0.174.0's rowhome
    Empties are 6.3 m wide and 6.8-10.1 m tall; up read X for all six, and
    their grime, banding and dressing anchors ran on their side -- curbs and
    gutters standing out of the walls in cold run 9147's frames. Still the
    right answer for the legacy Z-up fixture, which says nothing about
    itself and is wide.
    """
    hint = getattr(scene, "up_axis_hint", None)
    if hint is not None:
        return int(hint)
    lo = np.full(3, np.inf)
'''

CLI_OLD = '''    up_axis = slots.detect_up_axis(scene)
    if up_axis != 2:
        result["up_axis"] = "XYZ"[up_axis]
'''
CLI_NEW = '''    up_axis = slots.detect_up_axis(scene)
    if up_axis != 2:
        result["up_axis"] = "XYZ"[up_axis]
    # Which kind of answer it was (0.24.0): a guess from extents put a
    # building on its side once, so a reader can tell the two apart.
    result["up_axis_source"] = ("declared by the file" if scene.up_axis_hint is not None
                                else "guessed from extents")
'''

VER_OLD = '__version__ = "0.22.0"\n'
VER_NEW = '__version__ = "0.24.0"\n'


def main():
    assert (PA / "VERSION").read_text(encoding="utf-8").strip() == "Patina 0.23.0"
    _edit(PA / "patina" / "mesh.py", [(MESH_OLD, MESH_NEW)])
    _edit(PA / "patina" / "gltf_io.py", [(LOAD_OLD, LOAD_NEW), (SAVE_OLD, SAVE_NEW)])
    _edit(PA / "patina" / "slots.py", [(DETECT_OLD, DETECT_NEW)])
    _edit(PA / "patina" / "cli.py", [(CLI_OLD, CLI_NEW)])
    _edit(PA / "patina" / "version.py", [(VER_OLD, VER_NEW)])
    shutil.copyfile(SRC / "test_up_axis_declared.py", PA / "tests" / "test_up_axis_declared.py")
    ch = PA / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    head = "## [0.23.0]"
    assert s.count(head) == 1
    s = s.replace(head, (SRC / "CHANGELOG_0.24.0.md").read_text(encoding="utf-8").rstrip("\n")
                  + "\n\n" + head)
    ch.write_text(s, encoding="utf-8", newline="\n")
    (PA / "VERSION").write_text("Patina 0.24.0", encoding="utf-8", newline="\n")
    print("applied Patina 0.24.0")


if __name__ == "__main__":
    main()
