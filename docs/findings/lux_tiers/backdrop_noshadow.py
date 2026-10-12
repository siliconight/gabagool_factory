"""An arm for `sun_occluders.sh`: the backdrop drawn as built but casting no shadow.

    python docs/findings/lux_tiers/backdrop_noshadow.py <a copy of a package>

Writes `cast_shadow = 0` under every MultiMeshInstance3D node of the copy's `site_backdrop.tscn` (Lot's
backdrop rowhomes, one MultiMesh a species a side; none sets `cast_shadow`, so each casts). Refuses
before writing if the file holds no such node, if any node already sets it, or if the count written
differs from the count found. Never run it on a package itself.
"""
import pathlib
import re
import sys

NODE = re.compile(r'^\[node name="[^"]+" type="MultiMeshInstance3D" parent="\."\]$', re.M)


def main():
    project = pathlib.Path(sys.argv[1])
    if "_scratch" not in project.resolve().parts:
        sys.exit("refusing: %s is not a copy under _scratch" % project)
    path = project / "site_backdrop.tscn"
    raw = path.read_bytes()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if "cast_shadow" in text:
        sys.exit("UNKNOWN SHAPE: %s already sets cast_shadow" % path)
    found = len(NODE.findall(text))
    if found == 0:
        sys.exit("UNKNOWN SHAPE: no MultiMeshInstance3D node in %s" % path)
    new, made = NODE.subn(lambda m: m.group(0) + "\ncast_shadow = 0", text)
    if made != found or new.count("\ncast_shadow = 0\n") != found:
        sys.exit("MISMATCH: %d nodes, %d written" % (found, made))
    path.write_bytes(new.encode("utf-8").replace(b"\n", eol))
    print("site_backdrop.tscn: cast_shadow = 0 on %d MultiMeshInstance3D nodes" % made)


if __name__ == "__main__":
    main()
