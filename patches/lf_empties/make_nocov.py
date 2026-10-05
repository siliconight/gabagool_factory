"""Make an experiment copy of a package with every building's covers hidden.

    python make_nocov.py <package_dir> <dest_dir>

Copies the package (without its .godot cache) and adds `visible = false`
under each `[node name="Dressing" ... instance=ExtResource("L_Dressing")]`
in `lot/*/site.tscn`. The nodes stay, so the lightmap's user paths still
resolve; hidden, nothing under them is submitted. The ceiling on what any
merge of the covers could save. A measurement copy only -- never a package.
Refuses unless every building scene carries exactly one such node.
"""
import pathlib
import shutil
import sys

src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
NODE = '[node name="Dressing" parent="." instance=ExtResource("L_Dressing")]'
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".godot"))
scenes = sorted(dst.glob("lot/*/site.tscn"))
done = 0
for p in scenes:
    b = p.read_bytes()
    eol = b"\r\n" if b"\r\n" in b else b"\n"
    s = b.decode("utf-8")
    n = s.count(NODE)
    if n == 0 and "_dressing.glb" not in s:
        continue
    if n != 1:
        raise SystemExit(f"{p}: {n} Dressing nodes")
    nl = eol.decode()
    if NODE + nl + "visible = false" in s:
        raise SystemExit(f"{p}: already hidden")
    s = s.replace(NODE + nl, NODE + nl + "visible = false" + nl)
    p.write_bytes(s.encode("utf-8"))
    done += 1
print(f"hid the covers in {done} of {len(scenes)} building scene(s)")
if done == 0:
    raise SystemExit("nothing hidden")
