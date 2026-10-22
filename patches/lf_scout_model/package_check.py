"""Copied from `patches/lf_scout_view/package_check.py` with the scout model added (Deli Counter 0.259.0, Level Factory
0.234.0): each entry's `scout_model` counted with the drawings it names, and each shipped `scout.glb` compared with
what Deli Counter's `scout_model.build_glb` builds from the spec today.

Does a cold run's package carry its buildings' drawings, as roadmap 296 asks? (argv: the cold run's number; the
previous run's, for the file counts.) Reads the run's portable-godot package and prints, measured:

- `buildings.json`: each instance -- node, package id, kind, spec, its axonometric and plan count, or why none;
- every `res://` drawing the index names, present or not, and every drawing's `.import` the keep file
  (`importer="keep"`) or not;
- `lot/<id>/drawings/` in each package: its files and bytes;
- the import cache the export keeps beside the package (`occluders.kept_cache_dir`): any `.ctex` made of a drawing
  (an SVG imported as a texture), which the keep file exists to prevent;
- the closure verdict (`export_closure_scan.json`): ok, issues, and any issue naming `buildings.json` or `drawings/`;
- the package's file count against the previous run's, and the files only this one has, by kind.

Prints measurements only; writes package_check_<N>.out.txt beside this file.

    python patches/lf_scout_model/package_check.py 9381 9379
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[1]
run, prev = sys.argv[1], sys.argv[2]
NAME = "LF_restaurant_row_001.portable-godot"
pkg = F / "workspaces" / ("cold-%s-ws" % run) / ".level_factory" / "exports" / NAME
old = F / "workspaces" / ("cold-%s-ws" % prev) / ".level_factory" / "exports" / NAME
assert pkg.is_dir() and old.is_dir(), (pkg, old)
KEEP = '[remap]\n\nimporter="keep"\n'
lines = ["== cold run %s's package (%s)" % (run, NAME)]
idx_path = pkg / "buildings.json"
if not idx_path.is_file():
    lines.append("buildings.json: ABSENT")
    index = {"buildings": []}
else:
    index = json.loads(idx_path.read_text(encoding="utf-8"))
    lines.append("buildings.json: %d instance(s); schema %s; frame: %s"
                 % (len(index["buildings"]), index.get("schema"), index.get("frame")))
named = []
for e in index["buildings"]:
    named += ([e["axonometric"]] if e.get("axonometric") else []) + ([e["scout"]] if e.get("scout") else []) + (
        [e["scout_model"]] if e.get("scout_model") else []) + [
        p["file"] for p in e.get("plans") or []]
    lines.append("  %-10s %-22s %-8s spec %-22s %s" % (
        e["node"], e["id"], e["kind"], e.get("spec"),
        ("axonometric + %s + %s + %d plan(s)" % ("scout" if e.get("scout") else "NO SCOUT",
                                                 "scout model" if e.get("scout_model") else "NO SCOUT MODEL",
                                                 len(e.get("plans") or [])))
        if e.get("axonometric") else "none: " + str(e.get("none_because"))[:60] + "; scout %s" % e.get("scout")))
missing = [r for r in named if not (pkg / r[len("res://"):]).is_file()]
lines.append("drawings the index names: %d; present: %d; missing: %s" % (len(named), len(named) - len(missing), missing))
not_keep = [r for r in named if (pkg / (r[len("res://"):] + ".import")).read_text(encoding="utf-8")
            != KEEP] if not missing else ["(not asked: drawings missing)"]
lines.append("their .import files the keep file: %d of %d; not: %s" % (len(named) - len(not_keep), len(named), not_keep))
total = 0
for d in sorted((pkg / "lot").glob("*/drawings")):
    files = sorted(f for f in d.iterdir() if f.is_file())
    size = sum(f.stat().st_size for f in files)
    total += size
    lines.append("  lot/%s/drawings/: %d file(s), %d bytes" % (d.parent.name, len(files), size))
lines.append("drawings folders in all: %d bytes" % total)
# THE CACHE IS NOT ALWAYS BESIDE THE PACKAGE: the export keeps it there (`occluders.KEPT_CACHE_SUFFIX`), and the walk
# copy the drive makes next starts from it and takes it -- its `.godot/imported/`. The first run of this looked
# beside the package alone, found nothing, and printed "0 .ctex": a check with nothing to read, reported as a pass.
# It now says which caches it read, how many entries, and NOT CHECKED when it read none.
caches = [c for c in (pkg.parent / (pkg.name + ".import_cache"),
                      F / "_runs" / ("walk_%s_restaurant_row_001" % run) / ".godot" / "imported") if c.is_dir()]
drawn = {pathlib.PurePosixPath(r).name for r in named}
entries, svg_ctex = 0, []
for c in caches:
    for p in c.rglob("*"):
        if p.is_file():
            entries += 1
            if p.suffix == ".ctex" and p.name.split("-")[0].endswith(".svg"):
                svg_ctex.append(p.name.split("-")[0])
if not caches:
    lines.append("import cache: NOT CHECKED -- none beside the package and no walk copy %s" % run)
else:
    lines.append("import caches read: %s, %d entries; textures made of an .svg: %s; of a drawing: %s"
                 % ([str(c.relative_to(F)) for c in caches], entries, sorted(set(svg_ctex)),
                    sorted(set(svg_ctex) & drawn)))
# each shipped scout view against what Deli Counter draws from the spec today
sys.path.insert(0, str(F / "deli_counter"))
import axonometric  # noqa: E402
import scout_model  # noqa: E402
import spec_loader  # noqa: E402
for e in index["buildings"]:
    if e.get("scout") and not missing:
        shipped = (pkg / e["scout"][len("res://"):]).read_text(encoding="utf-8")
        drawn_now = axonometric.render_axonometric(
            spec_loader.load_spec(str(F / "deli_counter" / "specs" / (e["spec"] + ".json"))), scout=True)
        lines.append("  %s's scout.svg: %d bytes, data-view scout %s, the same as Deli Counter draws it today: %s"
                     % (e["id"], len(shipped.encode("utf-8")), 'data-view="scout"' in shipped, shipped == drawn_now))
    if e.get("scout_model") and not missing:
        glb = (pkg / e["scout_model"][len("res://"):]).read_bytes()
        spec = spec_loader.load_spec(str(F / "deli_counter" / "specs" / (e["spec"] + ".json")))
        lines.append("  %s's scout.glb: %d bytes, the same as Deli Counter builds it today: %s; triangles a storey %s"
                     % (e["id"], len(glb), glb == scout_model.build_glb(spec), scout_model.model_stats(spec)))
scan = json.loads((pkg / "export_closure_scan.json").read_text(encoding="utf-8"))
issues = scan.get("issues") or []
lines.append("closure verdict: ok=%s, %d issue(s); naming buildings.json or drawings/: %s" % (
    scan.get("ok"), len(issues), [i for i in issues if "buildings.json" in i or "/drawings/" in i][:6]))
mine = {p.relative_to(pkg).as_posix() for p in pkg.rglob("*") if p.is_file()}
theirs = {p.relative_to(old).as_posix() for p in old.rglob("*") if p.is_file()}
only = sorted(mine - theirs)
kinds = collections.Counter("buildings.json" if n == "buildings.json" else
                            ("drawings/" + n.rsplit(".", 1)[-1] if "/drawings/" in n else "other") for n in only)
lines.append("package files: %d against %s's %d; only in %s: %d %s; only in %s: %d"
             % (len(mine), prev, len(theirs), run, len(only), dict(kinds), prev, len(theirs - mine)))
lines += ["  only %s, other: %s" % (run, n) for n in only if "/drawings/" not in n and n != "buildings.json"][:12]
txt = "\n".join(lines) + "\n"
(HERE / ("package_check_%s.out.txt" % run)).write_text(txt, encoding="utf-8", newline="\n")
print(txt)
