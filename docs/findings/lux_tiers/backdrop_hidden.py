"""An arm for `backdrop_split.sh`: the backdrop not drawn at all, so the frame shows where it stands.

    python docs/findings/lux_tiers/backdrop_hidden.py <a copy of a package>

Writes `visible = false` under the root node of the copy's `site_backdrop.tscn`. Refuses before writing
if the root node is not found exactly once or already sets `visible`. Never run it on a package itself.
"""
import pathlib
import sys

ROOT = '[node name="site_backdrop" type="Node3D"]\n'


def main():
    project = pathlib.Path(sys.argv[1])
    if "_scratch" not in project.resolve().parts:
        sys.exit("refusing: %s is not a copy under _scratch" % project)
    path = project / "site_backdrop.tscn"
    raw = path.read_bytes()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if text.count(ROOT) != 1:
        sys.exit("UNKNOWN SHAPE: the root node %d times in %s" % (text.count(ROOT), path))
    after = text.split(ROOT, 1)[1]
    if after.split("\n\n", 1)[0].count("visible ="):
        sys.exit("UNKNOWN SHAPE: the root node already sets visible")
    path.write_bytes(text.replace(ROOT, ROOT + "visible = false\n").encode("utf-8").replace(b"\n", eol))
    print("site_backdrop.tscn: the root hidden")


if __name__ == "__main__":
    main()
