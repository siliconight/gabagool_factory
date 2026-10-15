"""Add the work light to a walk copy assembled before it existed (2026-10-14).

    python tools/walk_add_work_light.py _runs/walk_export_<mission> [...]

`walk_export.py` puts the work light (`walk_work_light.gd`, toggled with L) in
every walk copy it assembles from 2026-10-14. A copy assembled before carries
none, and assembling it again costs a fresh import. This adds the node and its
script to the copy's `_walk.tscn` in place, beside the flashlight, the way
`cold_drive/wire_sky.py` adds the sky cycle, and counts `load_steps` off the
scene. A copy that already carries it is left as it is. It touches only
`_walk.tscn` and `_walk_work_light.gd`; the package inside is never read.
"""
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "walk_work_light.gd"
EXT = '[ext_resource type="Script" path="res://_walk_work_light.gd" id="walk_work_light"]'
FLASHLIGHT_EXT = '[ext_resource type="Script" path="res://_walk_flashlight.gd" id="walk_flashlight"]'
NODE = '[node name="WalkWorkLight" type="Node" parent="."]'


def add(walk_dir):
    """Add the work light to one walk copy. Returns what it did."""
    w = pathlib.Path(walk_dir)
    t = w / "_walk.tscn"
    d = t.read_bytes()
    eol = "\r\n" if b"\r\n" in d else "\n"
    s = d.decode("utf-8")
    if EXT in s:
        return "already carries the work light; left as it is"
    head = re.match(r"\[gd_scene load_steps=\d+ format=3\]", s)
    if not head:
        raise SystemExit("%s: not a walk scene: %r" % (t, s[:60]))
    flashlight_node = ('[node name="WalkFlashlight" type="Node" parent="."]' + eol
                       + 'script = ExtResource("walk_flashlight")' + eol)
    if s.count(FLASHLIGHT_EXT) != 1 or s.count(flashlight_node) != 1:
        raise SystemExit("%s: no single flashlight to stand the work light beside" % t)
    s = s.replace(FLASHLIGHT_EXT, FLASHLIGHT_EXT + eol + EXT, 1)
    s = s.replace(flashlight_node, flashlight_node + eol + NODE + eol
                  + 'script = ExtResource("walk_work_light")' + eol, 1)
    loads = len(re.findall(r"^\[(?:ext|sub)_resource ", s, flags=re.M))
    s = "[gd_scene load_steps=%d format=3]" % (loads + 1) + s[head.end():]
    shutil.copy2(SRC, w / "_walk_work_light.gd")
    t.write_bytes(s.encode("utf-8"))
    got = t.read_bytes().decode("utf-8").replace("\r\n", "\n")
    if got.count(NODE) != 1 or got.count(EXT) != 1 or (w / "_walk_work_light.gd").read_bytes() != SRC.read_bytes():
        raise SystemExit("%s: the work light did not land as written" % t)
    return "added: the WalkWorkLight node and _walk_work_light.gd (L toggles it); load_steps %d" % (loads + 1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for arg in sys.argv[1:]:
        print("%s: %s" % (arg, add(arg)))
