"""tools/draw_census.py: its scene-instance count never counted (noted 2026-10-12, fixed 2026-10-13).

The node pattern was `^\\[node name="..."(?: type="...")?[^\\n]*?(instance=ExtResource)?`: a lazy `[^\\n]*?` and
then an OPTIONAL group, so the engine takes the empty match every time and the group never captures. On
cold run 9272's `site.tscn` the census printed "instances total 0" over a file holding 193
`instance=ExtResource` nodes (`grep -c`). Read off the records that cite the tool
(`docs/findings/street_draws/README.md`, cold runs 9234-9237): each used its meshes, materials and
MeshInstance3D counts, none its instances, so nothing built on the zero.

Each node's whole header line is read now, its type and its instance asked of the line. The node count
is held to what it was: the patch prints both censuses' node counts for every package named on its
command line, and refuses if the MeshInstance3D or MultiMeshInstance3D count moves.

One anchored edit, asserted once, the file's sha16 pinned:

    python patches/patch_draw_census_instances.py <package dir> [...]
"""
import hashlib
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "draw_census.py"
SHA = "be7ac06d8efdc602"
OLD = ("    for name, typ, instance in re.findall(\n"
       "            r'^\\[node name=\"([^\"]+)\"(?: type=\"([^\"]+)\")?[^\\n]*?(instance=ExtResource)?', text, re.M):\n"
       "        if typ in (\"MeshInstance3D\", \"MultiMeshInstance3D\"):\n"
       "            out[\"nodes\"][typ] += 1\n"
       "        elif instance:\n"
       "            out[\"instances\"][re.sub(r\"[_-]?\\d+$\", \"\", name)] += 1\n")
NEW = ("    # Each node's header line whole, its type and its instance asked of the line (2026-10-13).\n"
       "    # RETRACTED, KEPT: the pattern here was a lazy `[^\\n]*?` and an OPTIONAL\n"
       "    # `(instance=ExtResource)?`, which the engine satisfies with the empty match every time --\n"
       "    # \"instances total 0\" on cold run 9272's site.tscn, which holds 193 of them. The records that\n"
       "    # cite this tool (cold runs 9234-9237, docs/findings/street_draws) used its other counts.\n"
       "    for line in re.findall(r'^\\[node [^\\n]*', text, re.M):\n"
       "        named = re.search(r' name=\"([^\"]+)\"', line)\n"
       "        typed = re.search(r' type=\"([^\"]+)\"', line)\n"
       "        typ = typed.group(1) if typed else \"\"\n"
       "        if typ in (\"MeshInstance3D\", \"MultiMeshInstance3D\"):\n"
       "            out[\"nodes\"][typ] += 1\n"
       "        elif \"instance=ExtResource\" in line and named:\n"
       "            out[\"instances\"][re.sub(r\"[_-]?\\d+$\", \"\", named.group(1))] += 1\n")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _scene(arg):
    p = pathlib.Path(arg)
    return p / "site.tscn" if p.is_dir() else p


def main(argv):
    packages = argv[1:]
    assert packages, "name at least one package: the node counts are held to the old census's on it"
    raw = TOOL.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA, ("tools/draw_census.py is not the file this patch read", got)
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    assert crlf in (0, lf), "mixed line endings"
    eol = b"\r\n" if crlf else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.count(OLD) == 1, ("anchor", text.count(OLD))
    old = _load(TOOL, "draw_census_old")
    new_path = ROOT / "_scratch" / "draw_census_new.py"
    new_path.parent.mkdir(exist_ok=True)
    new_path.write_text(text.replace(OLD, NEW), encoding="utf-8")
    new = _load(new_path, "draw_census_new")
    for pkg in packages:
        a, b = old.census(str(_scene(pkg))), new.census(str(_scene(pkg)))
        assert a["nodes"] == b["nodes"], (pkg, "node counts moved", a["nodes"], b["nodes"])
        assert a["meshes"] == b["meshes"] and a["materials"] == b["materials"], pkg
        print("%s: nodes %s as before; instances %d -> %d %s" % (
            pkg, dict(b["nodes"]), sum(a["instances"].values()), sum(b["instances"].values()),
            dict(b["instances"].most_common(6))))
    new_path.unlink()
    TOOL.write_bytes(text.replace(OLD, NEW).encode("utf-8").replace(b"\n", eol))
    print("tools/draw_census.py: its instances counted")


if __name__ == "__main__":
    main(sys.argv)
