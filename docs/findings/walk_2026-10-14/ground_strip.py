"""Make a COPY of a package's backdrop scene without its ground, or with the ground unshaded (roadmap 252's arms).

    python docs/findings/walk_2026-10-14/ground_strip.py none      <copy>/site_backdrop.tscn
    python docs/findings/walk_2026-10-14/ground_strip.py unshaded  <copy>/site_backdrop.tscn

Level Factory 0.211.0's `backdrop_layer.with_ground` writes a `PlaneMesh` sub-resource `BackdropGround_mesh`, a
`StandardMaterial3D` sub-resource `BackdropGround_mat`, and a `BackdropGround` MeshInstance3D node, and raises
`load_steps` by 2.
- `none` removes all three and lowers `load_steps` by 2: the control, the level as 0.210.0 shipped it.
- `unshaded` adds `shading_mode = 0` to the material, so the plane draws its albedo with no light: the cheaper
  alternative 252 names, as a second arm.

Each block must be found exactly once, the file's line endings are kept, and nothing is written on a miss. Run it on
a COPY (`ground_price.sh` makes them under `_scratch/price_ground/`); it refuses a path under `workspaces/` or
`_runs/walk_export_`. Proven 2026-10-14: `none` on 9308's backdrop gives 9305's, byte for byte.
"""
import re
import sys
from pathlib import Path

MESH = re.compile(r'\[sub_resource type="PlaneMesh" id="BackdropGround_mesh"\]\n(?:[^\[\n][^\n]*\n)*\n')
MAT = re.compile(r'\[sub_resource type="StandardMaterial3D" id="BackdropGround_mat"\]\n(?:[^\[\n][^\n]*\n)*\n?')
NODE = re.compile(r'\n\[node name="BackdropGround" type="MeshInstance3D" parent="\."\]\n(?:[^\[\n][^\n]*\n)*')
HEAD = re.compile(r'\A\[gd_scene load_steps=(\d+) format=3\]')


def main(mode, path):
    p = Path(path)
    norm = str(p.resolve()).replace("\\", "/")
    if "/workspaces/" in norm or "/_runs/walk_export_" in norm:
        raise SystemExit("refusing %s: run this on a copy, never a package or a walk copy" % p)
    raw = p.read_bytes()
    crlf = raw.count(b"\r\n")
    if crlf not in (0, raw.count(b"\n")):
        raise SystemExit("mixed line endings in %s" % p)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for name, pat in (("mesh", MESH), ("material", MAT), ("node", NODE), ("head", HEAD)):
        n = len(pat.findall(text))
        if n != 1:
            raise SystemExit("%s: the ground's %s found %d times, not once; nothing written" % (p, name, n))
    if mode == "none":
        steps = int(HEAD.match(text).group(1))
        text = MESH.sub("", text, count=1)
        text = MAT.sub("", text, count=1)
        text = NODE.sub("\n", text, count=1)
        text = HEAD.sub("[gd_scene load_steps=%d format=3]" % (steps - 2), text, count=1)
        assert "BackdropGround" not in text
    elif mode == "unshaded":
        block = MAT.search(text).group(0)
        if "shading_mode" in block:
            raise SystemExit("%s: the ground's material already sets shading_mode" % p)
        text = text.replace(block, block.replace("roughness", "shading_mode = 0\nroughness", 1), 1)
        assert text.count("shading_mode = 0") == 1
    else:
        raise SystemExit("mode is none or unshaded, not %r" % mode)
    if crlf:
        text = text.replace("\n", "\r\n")
    p.write_bytes(text.encode("utf-8"))
    print("%s: ground %s" % (p, "removed, load_steps -2" if mode == "none" else "unshaded"))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
