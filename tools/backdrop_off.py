"""Make a copy of a package its own control: the same level with the backdrop scene not loaded.

    python tools/backdrop_off.py <package copy>

Roadmap 228's recipe runs have no earlier run of the same level without the backdrop to price
against, and the next-best control is the package itself with `<site>_backdrop.tscn` left out:
every other draw identical, and the same `bake.tscn` loaded by both copies, so the lightmap is the
same by construction. The entry scene (`localize.write_entry_scene`) loads its content from a
GDScript in `mission.tscn`, three lines a scene:

    var packed_2 := load('res://site_backdrop.tscn') as PackedScene
    if packed_2 != null:
        add_child(packed_2.instantiate())

This removes exactly that block for the one `*_backdrop.tscn`, IN PLACE in the copy given (never a
workspace's package), keeps the file's line endings, and prints what it removed. An entry scene
that loads no backdrop, or loads it some other way, is an error, not a no-op.
"""
import re
import sys
from pathlib import Path

BLOCK = re.compile(
    r"\tvar (packed_\d+) := load\('res://([^']*_backdrop\.tscn)'\) as PackedScene\n"
    r"\tif \1 != null:\n"
    r"\t\tadd_child\(\1\.instantiate\(\)\)\n")


def main(argv):
    if len(argv) != 1:
        raise SystemExit(__doc__)
    entry = Path(argv[0]) / "mission.tscn"
    raw = entry.read_bytes()
    crlf = raw.count(b"\r\n")
    if crlf and crlf != raw.count(b"\n"):
        raise SystemExit("%s has mixed line endings (%d CRLF of %d): refusing" % (entry, crlf, raw.count(b"\n")))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    found = BLOCK.findall(text)
    if len(found) != 1:
        raise SystemExit("%s loads %d *_backdrop.tscn block(s), not 1: %r" % (entry, len(found), found))
    out = BLOCK.sub("", text, count=1)
    assert "_backdrop.tscn" not in out, "the backdrop scene is still named in the entry scene"
    if crlf:
        out = out.replace("\n", "\r\n")
    entry.write_bytes(out.encode("utf-8"))
    print("backdrop off in %s: removed the block loading %s (%s); %d bytes -> %d"
          % (entry, found[0][1], found[0][0], len(raw), len(out.encode("utf-8"))))


if __name__ == "__main__":
    main(sys.argv[1:])
