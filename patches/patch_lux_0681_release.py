"""Lux 0.68.1's release: VERSION and the CHANGELOG entry.

    python patch_lux_0681_release.py

Anchored on VERSION (b'Lux 0.68.0', no newline) and on CHANGELOG.md's head
as Lux 0.68.0 left it (LF).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LUX = ROOT / "lux"

HEAD = "# Changelog\n\n## [0.68.0]"
ENTRY = """# Changelog

## [0.68.1] - the room fills are owned, so the lightmapper takes them

0.68.0 left `add_bake_fills`' container unowned, "so even a save that forgot
to free it cannot keep it". **LightmapGI skips any child with no owner when it
collects lights** ("maybe a helper", Godot's `_find_meshes_and_lights`). So
the first real bake baked none of it: Level Factory 0.151.0's plugin, on a
copy of cold run 9190's level with 0.68.0 vendored in, laid 267 fills
(`light_bake.json`: `room_fills` 267), and every room read the plain
re-bake's number, 16 fluorescent rooms 15.5 and 8 bulb-lit 3.8. The
experiments that chose the layout had written their fills into the bake
scene's text, owned, which is why they lit.

**Every fill is owned by the scene's owner now** (the edited root, in a
bake), and freeing it before the save is the bake's job. Level Factory
0.151.0's plugin does it, and its test holds the order. The same copy,
re-vendored with this release and baked through that plugin:

    rooms                  no fill    0.68.1
    16 fluorescent rows      15.5      39.0    (the scripted layout: 39.1)
    saved bake.tscn          --        no fill
    bake time in the editor  85 s      92 s

The bulb-lit rooms read 14.3 there, not the scripted 22.8. That copy's
presentation scene was built before 0.67.0, so its bulbs still hang inside
their glass. A fresh build carries both.

`tools/bake_fill_selftest.gd`: the check that held the defect -- "the
container has no owner" -- is replaced by "the fills are owned by the
scene", the refutation kept in its comment. On 0.68.0 it fails 1.

## [0.68.0]"""


def main():
    v = (LUX / "VERSION").read_bytes()
    assert v == b"Lux 0.68.0", repr(v)
    c = (LUX / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.count(HEAD) == 1, text.count(HEAD)
    (LUX / "VERSION").write_bytes(b"Lux 0.68.1")
    (LUX / "CHANGELOG.md").write_bytes(text.replace(HEAD, ENTRY, 1).encode("utf-8"))
    print("Lux 0.68.1: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
