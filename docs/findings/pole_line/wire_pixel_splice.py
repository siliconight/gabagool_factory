"""The look at Lot 0.119.1's wires before the release: a COPY of cold run 9263's package with a
drafted Lot's wire files and material spliced in, so the shader is seen compiling and drawing.

    LOT_ROOT=<drafted Lot copy> python docs/findings/pole_line/wire_pixel_splice.py \
        <package copy under _scratch/> <the run's themed site.site.drawn.json>

Writes the draft's `site_poles.wire_meshes` output for the run's own cover over the copy's
`site_wires_*.obj`, and replaces the `Mat_site_wires` block -- its header to the next blank line --
in every scene that carries one with the draft's material (the Shader and the ShaderMaterial);
`site.tscn`'s `load_steps` counts the one more sub_resource. Refuses unless the draft writes exactly
the files the copy has and each scene's block is found once; nothing is written until both hold.
This is not the generator's output in a run -- that is the cold run after the release -- and it
says so in what it prints.
"""
import json
import os
import pathlib
import re
import sys

HEADER = '[sub_resource type="StandardMaterial3D" id="Mat_site_wires"]'


def main():
    lot_root = os.environ.get("LOT_ROOT")
    if not lot_root:
        sys.exit("refusing: set LOT_ROOT to the drafted Lot copy")
    sys.path.insert(0, lot_root)
    import lot          # noqa: E402
    import site_poles   # noqa: E402
    if not hasattr(site_poles, "WIRE_SHADER"):
        sys.exit("refusing: %s has no WIRE_SHADER; it is not the draft" % site_poles.__file__)
    copy = pathlib.Path(sys.argv[1]).resolve()
    if "_scratch" not in copy.parts:
        sys.exit("refusing: %s is not a copy under _scratch/" % copy)
    spec = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
    _body, sub, files = site_poles.wire_meshes(spec.get("cover") or [], lot.SIDEWALK_H)
    have = sorted(p.name for p in copy.glob("site_wires_*.obj"))
    if sorted(files) != have:
        sys.exit("MISMATCH: the draft writes %s, the copy has %s" % (sorted(files), have))
    block = "\n".join(sub).rstrip("\n") + "\n"
    plans = []
    for scene in sorted(copy.rglob("*.tscn")):
        raw = scene.read_bytes()
        if HEADER.encode() not in raw:
            continue
        eol = b"\r\n" if b"\r\n" in raw else b"\n"
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if text.count(HEADER) != 1:
            sys.exit("UNKNOWN SHAPE: %d material blocks in %s" % (text.count(HEADER), scene))
        start = text.index(HEADER)
        end = text.index("\n\n", start) + 1
        text = text[:start] + block + text[end:]
        m = re.match(r"\[gd_scene load_steps=(\d+) ", text)
        if m:
            text = text.replace(m.group(0), "[gd_scene load_steps=%d " % (int(m.group(1)) + 1), 1)
        plans.append((scene, text.encode("utf-8").replace(b"\n", eol)))
    if not plans:
        sys.exit("NOTHING TO SPLICE: no scene in %s carries %s" % (copy, HEADER))
    # every check passed: now write
    for name, text in files.items():
        (copy / name).write_bytes(text.encode("utf-8"))
    for scene, data in plans:
        scene.write_bytes(data)
        print("spliced the draft's wire material into %s" % scene.relative_to(copy).as_posix())
    print("wrote the draft's %d wire OBJs (Lot %s, DRAFT -- not a run's output)"
          % (len(files), (pathlib.Path(lot_root) / "VERSION").read_text().strip()))


if __name__ == "__main__":
    main()
