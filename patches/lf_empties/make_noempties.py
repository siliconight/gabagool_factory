"""Make an experiment copy of a package with every Empty hidden.

    python make_noempties.py <package_dir> <dest_dir>

Copies the package (without its .godot cache) and adds `visible = false`
under every `[node name="blocker_<n>" ...]` in `presentation/lux.applied.tscn`
-- the scene `bake.tscn` instances as `/root/Mission/Bake/Site`, read off cold
run 9160's package -- whose instance is a `lot/gs_empty_*/site.tscn`. The
nodes stay, so the lightmap's user paths still resolve; hidden, nothing under
them is submitted. The ceiling on what any merge of the Empties could save.
A measurement copy only -- never a package.

Refuses if a blocker node instances anything but an Empty, if one is already
hidden, or if it hides none.
"""
import pathlib
import re
import shutil
import sys

src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".godot"))
scene = dst / "presentation" / "lux.applied.tscn"
b = scene.read_bytes()
nl = "\r\n" if b"\r\n" in b else "\n"
lines = b.decode("utf-8").split(nl)
res = {}
for ln in lines:
    if ln.startswith("[ext_resource ") and 'type="PackedScene"' in ln:
        p, i = re.search(r' path="([^"]+)"', ln), re.search(r' id="([^"]+)"', ln)
        if not (p and i):
            raise SystemExit(f"{scene}: an ext_resource this does not read: {ln}")
        res[i.group(1)] = p.group(1)
out, hidden, designs = [], 0, set()
for i, ln in enumerate(lines):
    out.append(ln)
    m = re.match(r'^\[node name="blocker_\d+" .*instance=ExtResource\("([^"]+)"\)\]$', ln)
    if not m:
        continue
    path = res.get(m.group(1), "")
    if "lot/gs_empty_" not in path:
        raise SystemExit(f"{scene}: {ln} instances {path!r}, not an Empty")
    if i + 1 < len(lines) and lines[i + 1].strip() == "visible = false":
        raise SystemExit(f"{scene}: {ln} already hidden")
    out.append("visible = false")
    hidden += 1
    designs.add(path)
if hidden == 0:
    raise SystemExit("nothing hidden")
scene.write_bytes(nl.join(out).encode("utf-8"))
print(f"hid {hidden} Empties ({len(designs)} designs) in {scene.relative_to(dst)}")
