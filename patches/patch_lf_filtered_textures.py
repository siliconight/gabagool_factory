"""Level Factory 0.128.0: a filtered texture ships compressed; the register's
display loses its flicker.

TWO CHANGES, both from pricing Zoo 1.46.0's real look.

1. THE EXPORT PINS `compress/mode=0` (lossless) on every shared texture under
   `_tex/`, for a measured reason: VRAM compression changes every pixel, and
   the pixel art is sampled Closest, so every changed pixel is on screen at
   its own size. Zoo 1.46.0's painted atlases are sampled with FILTERING, at
   three times the density, and lossless they are the largest textures a
   store holds. Measured in a scratch project, the new ATM, video poker and
   cash register together (Godot 4.7, GL Compatibility, the renderer's own
   texture-memory figure with the props loaded):

       lossless, mip chain (what the export ships)    7,304,813 B
       VRAM compressed, mip chain                     1,374,528 B

   So a shared texture that EVERY sampler reaching it filters is pinned to
   `compress/mode=2`. Which textures those are is read off the GLBs
   themselves -- a glTF sampler's `magFilter` is 9729 for LINEAR -- so there
   is no naming contract with Zoo to drift. A texture any GLB samples
   Closest, or with no sampler at all, stays lossless.

2. `_vfd_motion` (0.127.0) is removed. It gave `M_Register_*_Face` a
   two-rate flicker. Measured since: the swing is 5.3 % of the display's
   green and it costs the register one more draw; and it never reached the
   tills on store and bar counters, whose material is `M_Counter_VFD_*_Face`.
   The walker's call, 2026-10-02: leave it off the counters and take it off
   the register.

    python patch_lf_filtered_textures.py
    LF_ROOT=<copy> python patch_lf_filtered_textures.py

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")


def _edit(rel, pairs, cuts=()):
    p = LF / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.replace(b"\r\n", b"\n").decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:70]!r}"
        s = s.replace(old, new)
    for start, end in cuts:
        assert s.count(start) == 1 and s.count(end) == 1, f"{rel}: cut anchors: {start[:50]!r}"
        a, b = s.index(start), s.index(end) + len(end)
        assert a < b
        s = s[:a] + s[b:]
    out = s.encode("utf-8")
    p.write_bytes(out.replace(b"\n", b"\r\n") if crlf else out)
    print("edited", rel)


EXPORT = [
    ('''#: Import parameters pinned on every `.png.import` under `SHARED_TEX_DIR`.
#: The measurement behind each is in `_write_import_sidecars`'s docstring.
SHARED_TEX_PINS = {
    "compress/mode": "0",
    "process/fix_alpha_border": "false",
    "mipmaps/generate": "true",
}
''', '''#: Import parameters pinned on every `.png.import` under `SHARED_TEX_DIR`.
#: The measurement behind each is in `_write_import_sidecars`'s docstring.
SHARED_TEX_PINS = {
    "compress/mode": "0",
    "process/fix_alpha_border": "false",
    "mipmaps/generate": "true",
}

#: And on the ones every sampler FILTERS (0.128.0): VRAM compression. The
#: lossless pin above protects pixel art, which is sampled Closest -- every
#: changed pixel is on screen at its own size. A filtered texture is already
#: an average of its neighbours on screen, and Zoo 1.46.0's painted atlases
#: are filtered, three times as dense, and the largest textures a store
#: holds. Measured (see `_write_import_sidecars`): 7,304,813 B lossless,
#: 1,374,528 B compressed, for the same three props.
FILTERED_TEX_PINS = {"compress/mode": "2"}
#: glTF's `magFilter` for LINEAR. 9728 is NEAREST.
GLTF_LINEAR = 9729


def _glb_json(path: Path):
    """The JSON chunk of a binary glTF, or None when the file is not one."""
    import json as _json
    import struct as _struct
    try:
        with open(path, "rb") as fh:
            head = fh.read(20)
            if len(head) < 20 or head[:4] != b"glTF" or head[16:20] != b"JSON":
                return None
            return _json.loads(fh.read(_struct.unpack("<I", head[12:16])[0]))
    except (OSError, ValueError):
        return None


def _filtered_shared_textures(export_dir: Path) -> set:
    """Every shared texture that EVERY sampler reaching it filters.

    Read off the GLBs: a texture names an image and a sampler, and a sampler
    whose `magFilter` is `GLTF_LINEAR` filters. One Closest use anywhere in
    the package -- or a use with no sampler, or no `magFilter`, which is the
    importer's default and not a statement -- keeps the texture lossless,
    because that use shows its pixels at their own size.

    A GLB this cannot read contributes nothing either way; its textures stay
    at the lossless pin unless another GLB names them.
    """
    filtered, other = set(), set()
    for glb in export_dir.rglob("*.glb"):
        doc = _glb_json(glb)
        if not isinstance(doc, dict):
            continue
        images = doc.get("images") or []
        samplers = doc.get("samplers") or []
        for tex in doc.get("textures") or []:
            src = tex.get("source")
            if not isinstance(src, int) or not 0 <= src < len(images):
                continue
            uri = images[src].get("uri")
            if not uri:
                continue
            png = (glb.parent / uri).resolve()
            if png.parent.name != SHARED_TEX_DIR:
                continue
            si = tex.get("sampler")
            linear = (isinstance(si, int) and 0 <= si < len(samplers)
                      and samplers[si].get("magFilter") == GLTF_LINEAR)
            (filtered if linear else other).add(png)
    return filtered - other
'''),
    ('''    A sidecar missing a key is not written to. The key set is Godot's, read
    off what Godot wrote on the first pass; a file that does not carry one is
    a file this function has not been shown, and adding the line would be
    guessing at a schema.
    """
    changed = 0
    for sidecar in export_dir.rglob("*.png.import"):
        if sidecar.parent.name != SHARED_TEX_DIR:
            continue
        try:
            lines = sidecar.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        out, hit = [], False
        for ln in lines:
            key = ln.split("=", 1)[0]
            want = SHARED_TEX_PINS.get(key)
''', '''    A sidecar missing a key is not written to. The key set is Godot's, read
    off what Godot wrote on the first pass; a file that does not carry one is
    a file this function has not been shown, and adding the line would be
    guessing at a schema.

    A texture every sampler filters takes `FILTERED_TEX_PINS` over these
    (0.128.0, `_filtered_shared_textures`).
    """
    changed = 0
    filtered = _filtered_shared_textures(export_dir)
    for sidecar in export_dir.rglob("*.png.import"):
        if sidecar.parent.name != SHARED_TEX_DIR:
            continue
        try:
            lines = sidecar.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        pins = dict(SHARED_TEX_PINS)
        if sidecar.with_name(sidecar.name[:-len(".import")]).resolve() in filtered:
            pins.update(FILTERED_TEX_PINS)
        out, hit = [], False
        for ln in lines:
            key = ln.split("=", 1)[0]
            want = pins.get(key)
'''),
    ('''                                   twenty-GLB control against an empty-scene
                                   baseline -- the renderer allocates the chain
                                   either way.
''', '''                                   twenty-GLB control against an empty-scene
                                   baseline -- the renderer allocates the chain
                                   either way.

    AND ONE EXCEPTION TO THE FIRST PIN (0.128.0): a shared texture that every
    sampler reaching it FILTERS is pinned to `compress/mode=2`. Zoo 1.46.0
    paints its machines' atlases at three times the density and samples them
    Linear; the lossless pin's reason is pixels shown at their own size, and a
    filtered texture's are not. Measured in a scratch project on Zoo 1.46.0's
    ATM, video poker and cash register together, Godot 4.7, GL Compatibility,
    the renderer's texture-memory figure with the three loaded less the
    figure before them:

        compress/mode=0, mip chain     7,304,813 B
        compress/mode=2, mip chain     1,374,528 B

    Mean difference between the two in a frame, 8-bit codes: 5.6 at arm's
    length on the ATM's head, 2.6 at nine metres. NOT MEASURED: any target
    other than desktop -- mode 2 imports S3TC here, and a platform without it
    needs its own import flag before this pin means anything there.
'''),
]

WORLDSKIN = [
    ('''## THE REGISTER'S DISPLAY (0.127.0). Zoo's cash register lights its customer
## display on a material of its own, `M_Register_<art>_Face`, and its picture
## is a price -- which does not animate. A vacuum-fluorescent display does
## shimmer, so it takes the CRT pass's overlay with a display's numbers: a
## two-rate flicker, no sync bar, no snow. Darkening only, for the CRT pass's
## reason.
const VFD_FACE_MARK: String = "Register_"
const VFD_FLICKER_DEPTH: float = 0.07
const VFD_FLICKER_HZ_A: float = 3.1
const VFD_FLICKER_HZ_B: float = 4.7
''', '''## THE REGISTER'S DISPLAY HAD A FLICKER (0.127.0) AND DOES NOT (0.128.0).
## It was the CRT pass's overlay under `M_Register_<art>_Face` with no roll
## and no snow, depth 0.07. Kept here because it is cheaper to keep than to
## rediscover: measured, the display's green swung 5.3 % between its
## brightest and dimmest frame, the pass cost the register one more draw, and
## it never reached the tills on store and bar counters, whose material is
## `M_Counter_VFD_<art>_Face`. The walker's call: off, everywhere.
'''),
    ('''	var vfd: int = _vfd_motion(scene, {})
	if vfd > 0:
		print("[worldskin] %s  %d register display(s) given a flicker" % [base, vfd])
''', ''''''),
]
WORLDSKIN_CUTS = [
    ("## The register's lit display: the CRT pass's shape exactly",
     "\treturn nm.begins_with(CRT_FACE_PREFIX + VFD_FACE_MARK) and nm.ends_with(CRT_FACE_SUFFIX)\n\n\n"),
]

TEST_SHUTTERS = [
    ('''"""Zoo's shutters get their clock at import, and the register's display a flicker (0.127.0).
''', '''"""Zoo's shutters get their clock at import (0.127.0); the register's flicker is gone (0.128.0).
'''),
    ('''    for call in ("_shutters(scene", "_vfd_motion(scene"):
''', '''    for call in ("_shutters(scene",):
'''),
    ('''def test_the_register_keeps_its_own_material_and_gets_no_roll_and_no_snow():
    vfd = _func(_src(), "_vfd_motion")
    assigns = re.findall(r"\\bbm\\.(\\w+)\\s*=[^=]", vfd)
    assert assigns == ["next_pass"], assigns
    assert "surface_set_material" not in vfd and "emission" not in vfd
    assert "if bm.next_pass != null:" in vfd
    assert 'set_shader_parameter("roll_depth", 0.0)' in vfd
    assert 'set_shader_parameter("noise_depth", 0.0)' in vfd
    face = _func(_src(), "_is_vfd_face")
    assert "CRT_FACE_PREFIX + VFD_FACE_MARK" in face and "CRT_FACE_SUFFIX" in face
    assert 'const VFD_FACE_MARK: String = "Register_"' in _src()
    # and it does not catch the CRTs, which have their own pass
    assert "CRT_Screen" not in "M_Register_x_Face"
''', '''def test_the_register_s_display_is_given_no_pass_of_its_own():
    """0.127.0 gave `M_Register_*_Face` a flicker; 0.128.0 took it away: a
    5.3 % swing for one more draw a register, and it never reached a
    counter's tills. The reason is kept in the source where the constants
    were; the pass, its mark and its call are gone."""
    src = _src()
    assert "func _vfd_motion" not in src and "func _is_vfd_face" not in src
    assert "_vfd_motion(" not in src
    assert not re.search(r"^const VFD_", src, re.M)
    assert "THE REGISTER'S DISPLAY HAD A FLICKER (0.127.0) AND DOES NOT (0.128.0)" in src
'''),
]

TEST_PINS_TAIL = '''

# --- 0.128.0: a texture every sampler filters ships compressed -----------------------


def _glb(path, images, samplers, textures):
    """A binary glTF holding only the JSON chunk this reads."""
    import json
    import struct
    body = json.dumps({"asset": {"version": "2.0"}, "images": images, "samplers": samplers,
                       "textures": textures}).encode("utf-8")
    body += b" " * (-len(body) % 4)
    path.write_bytes(b"glTF" + struct.pack("<II", 2, 20 + len(body))
                     + struct.pack("<I", len(body)) + b"JSON" + body)


def _two_textures(tmp_path):
    d = _tex(tmp_path)
    (d / "smooth.png").write_bytes(b"\\x89PNG\\r\\n\\x1a\\n" + b"y" * 64)
    (d / "smooth.png.import").write_text(REAL_SIDECAR, encoding="utf-8")
    return d


def _mode(sidecar):
    return _params(sidecar.read_text(encoding="utf-8"))["compress/mode"]


def test_a_texture_every_sampler_filters_is_pinned_to_vram_compression(tmp_path):
    """Read off a real GLB's records (cold run 9135's ATM): images carry a
    `uri` under `_tex/`, a texture names a sampler and a source, and a
    filtering sampler's `magFilter` is 9729."""
    d = _two_textures(tmp_path)
    zoo = d.parent
    _glb(zoo / "prop_atm.glb",
         [{"name": "ATM", "uri": "_tex/smooth.png"}],
         [{"magFilter": 9729, "minFilter": 9987, "wrapS": 33071, "wrapT": 33071}],
         [{"sampler": 0, "source": 0}])
    _glb(zoo / "prop_shelving.glb",
         [{"name": "paper", "uri": "_tex/t.png"}],
         [{"magFilter": 9728, "minFilter": 9984}],
         [{"sampler": 0, "source": 0}])
    assert export._filtered_shared_textures(tmp_path) == {(d / "smooth.png").resolve()}
    export._pin_shared_texture_imports(tmp_path)
    assert _mode(d / "smooth.png.import") == "2"
    assert _mode(d / "t.png.import") == "0"
    # the other two pins hold on both
    for name in ("smooth.png.import", "t.png.import"):
        got = _params((d / name).read_text(encoding="utf-8"))
        assert got["mipmaps/generate"] == "true" and got["process/fix_alpha_border"] == "false"
    assert export._pin_shared_texture_imports(tmp_path) == 0


def test_one_closest_use_anywhere_keeps_a_texture_lossless(tmp_path):
    """A texture shown at its own pixel size by ANY module is pixel art
    there, whatever another module does with it."""
    d = _two_textures(tmp_path)
    zoo = d.parent
    _glb(zoo / "a.glb", [{"uri": "_tex/smooth.png"}], [{"magFilter": 9729}],
         [{"sampler": 0, "source": 0}])
    _glb(zoo / "b.glb", [{"uri": "_tex/smooth.png"}], [{"magFilter": 9728}],
         [{"sampler": 0, "source": 0}])
    assert export._filtered_shared_textures(tmp_path) == set()
    export._pin_shared_texture_imports(tmp_path)
    assert _mode(d / "smooth.png.import") == "0"


@pytest.mark.parametrize("samplers,texture", [
    ([], {"source": 0}),                                   # no sampler named
    ([{"minFilter": 9987}], {"sampler": 0, "source": 0}),   # no magFilter stated
    ([{"magFilter": 9729}], {"sampler": 3, "source": 0}),   # a sampler that is not there
])
def test_a_use_that_does_not_say_it_filters_is_not_taken_to(tmp_path, samplers, texture):
    d = _two_textures(tmp_path)
    _glb(d.parent / "a.glb", [{"uri": "_tex/smooth.png"}], samplers, [texture])
    assert export._filtered_shared_textures(tmp_path) == set()


def test_a_file_that_is_not_a_glb_and_an_image_outside_the_shared_folder_are_ignored(tmp_path):
    d = _two_textures(tmp_path)
    zoo = d.parent
    (zoo / "broken.glb").write_bytes(b"not a gltf at all")
    _glb(zoo / "a.glb", [{"uri": "loose.png"}, {"name": "embedded"}], [{"magFilter": 9729}],
         [{"sampler": 0, "source": 0}, {"sampler": 0, "source": 1}, {"sampler": 0, "source": 9}])
    assert export._filtered_shared_textures(tmp_path) == set()
    export._pin_shared_texture_imports(tmp_path)
    assert _mode(d / "smooth.png.import") == "0"
'''

CHANGELOG = '''## [0.128.0] - a filtered texture ships compressed; the register's flicker is gone

Both from pricing Zoo 1.46.0's real look (smooth type, painted shading and
chamfered bodies on the video poker, the ATM and the registers).

### Changed
- **A shared texture that every sampler filters is exported VRAM-compressed.**
  The export pins `compress/mode=0` on every texture under `_tex/` because
  compression changes every pixel and pixel art is shown at its own pixel
  size. Zoo 1.46.0's painted atlases are sampled Linear, at three times the
  density. `_filtered_shared_textures` reads which textures those are off the
  GLBs themselves (a sampler's `magFilter` 9729), so there is no naming
  contract with Zoo; one Closest use anywhere, or a use that names no
  sampler, keeps a texture lossless. The mip chain and the alpha-border pin
  are unchanged.

### Removed
- **`_vfd_motion`**, 0.127.0's flicker on `M_Register_*_Face`. Measured: a
  5.3 % swing in the display's green for one more draw a register, and it
  never reached the tills on store and bar counters (`M_Counter_VFD_*_Face`),
  which are the ones a level stands. The walker's call, 2026-10-02: off
  everywhere. The reason is kept in `zoo_worldskin.gd` where the constants
  were.

### Measured
A scratch project, Godot 4.7, GL Compatibility; Zoo 1.46.0's ATM, video poker
and cash register loaded together; the renderer's texture-memory figure less
its figure before they loaded:

| import | texture memory |
|---|---|
| `compress/mode=0`, mip chain (0.127.0's export) | 7,304,813 B |
| `compress/mode=2`, mip chain (this export) | 1,374,528 B |

Mean difference between the two frames, 8-bit codes: 5.6 at arm's length on
the ATM's head, 2.6 at nine metres. Up close the type is slightly softer and
a flat red sign shows faint banding.

And in a level -- cold run 9135's package (gas_block_001), the pin applied to
a copy of it, both imported fresh and loaded to `mission.tscn` with the
warm-up finished. Eight shared textures are filtered by every sampler that
reaches them (the ATMs', the video poker's and the counter tills' atlases);
149 stay lossless.

| package | texture memory |
|---|---|
| as 0.127.0 exported it | 344,910,446 B |
| with the eight compressed | 336,561,431 B |

8,349,015 B back, 2.4 % of the level's textures. The other 97.6 % is not
this change's and nobody has attributed it.

### Not measured
- A target other than desktop. Mode 2 imports S3TC here.
- Frame time. Texture memory is what moved; nothing here changes a draw
  except the register's, which loses one.

'''


def main():
    assert (LF / "VERSION").read_text(encoding="utf-8").strip() == "0.127.0", "not 0.127.0"
    _edit("packages/exporting/export.py", EXPORT)
    _edit("assets/godot/zoo_worldskin.gd", WORLDSKIN, WORLDSKIN_CUTS)
    _edit("tests/unit/test_worldskin_shutters.py", TEST_SHUTTERS)
    p = LF / "tests" / "unit" / "test_shared_texture_imports.py"
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.replace(b"\r\n", b"\n").decode("utf-8")
    assert "_filtered_shared_textures" not in s and "import pytest" in s
    out = (s.rstrip("\n") + "\n" + TEST_PINS_TAIL).encode("utf-8")
    p.write_bytes(out.replace(b"\n", b"\r\n") if crlf else out)
    print("appended tests/unit/test_shared_texture_imports.py")
    p = LF / "CHANGELOG.md"
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.replace(b"\r\n", b"\n").decode("utf-8")
    assert s.startswith("## [0.127.0]")
    out = (CHANGELOG + s).encode("utf-8")
    p.write_bytes(out.replace(b"\n", b"\r\n") if crlf else out)
    (LF / "VERSION").write_text("0.128.0", encoding="utf-8")
    print("0.127.0 -> 0.128.0")


if __name__ == "__main__":
    main()
