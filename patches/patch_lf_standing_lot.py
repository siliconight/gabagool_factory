"""Level Factory 0.207.0: a package carries the buildings its scene stands, and no others.

The compose stage themes every Empty the brief was given, and an urban brief is given every corner block and
mid-rise; a candidate stands some. The export copied the composed root whole, so every composed `lot/<id>/` shipped.
Cold run 9297's package carried sixteen `lot/` packages while its assembly scene named thirteen: `gs_cornershop_a`,
`gs_cornershop_b` and `gs_midrise_g` -- 12.2 MB of 210, and 95 of the 711 model imports the light bake sets to
Static Lightmaps, each unwrapped for a lightmap at import -- shipped and imported for scenes nothing instanced
(measured on the package: `du`, `light_bake.json`'s `imports.baked`, and a grep of every `.tscn` for the three ids,
which only their own scenes name).

Anchored edits, each asserted exactly once and the file's sha16 pinned, nothing written until all matched:
  packages/exporting/export.py   `_standing_lot_ids` (the `lot/<id>/` the assembly names, or None where it cannot
                                 say); `_copy_tree(..., skip_lot=...)`, matched on a relative path's first two
                                 parts; the composed copy leaves out the composed packages no scene stands, and
                                 says which
  tests/unit/test_export_standing_lot.py   NEW (`lf_standing_lot/test_export_standing_lot.py.txt`)
CHANGELOG and VERSION from `lf_standing_lot/CHANGELOG_0.207.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`.

Read before it was written, in this session: `_copy_tree` whole (its `skip` matches basenames anywhere, the
reason `skip_rel` exists, and the measured failure that took every building out of a package by name);
`_LOT_SITE_REF` and `_assembly_building_dir` (a single-shell mission's root moves under `lot/<id>/`); the composed
copy and its comments; step 2.5, which copies the assembly scene and its sibling directories and no `lot/`
package; a real assembly scene's references (`path="lot/<id>/site.tscn"`, thirteen in 9297's); and
`tests/unit/test_orphan_root_base.py`, whose fixture the new test follows. Every file LF.

    python patches/patch_lf_standing_lot.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_standing_lot.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_standing_lot"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_FAILING": "result_failing.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.206.1", b"0.207.0"
CHANGELOG_HEAD = ("## [0.206.1] - A spent bag is not a closed run: the corner wall's fill deals afresh before it "
                  "stops\n")
SHA = {"packages/exporting/export.py": "2dc62e8d6131c7c9"}
NEW = {"tests/unit/test_export_standing_lot.py": "test_export_standing_lot.py.txt"}

STANDING = '''

def _standing_lot_ids(themed_site_dir):
    """The `lot/<id>/` packages the ASSEMBLY scene stands (0.207.0): every
    `lot/<id>/site.tscn` it names (`_LOT_SITE_REF`), as a set -- or None where
    there is no assembly scene to ask, or it names none, and then every
    composed package ships, as before. Absence of evidence decides toward
    including.

    WHY. The compose stage themes every Empty the brief was given, and an
    urban brief is given every corner block and mid-rise; a candidate stands
    some. Cold run 9297's package carried sixteen `lot/` packages and its
    assembly named thirteen: `gs_cornershop_a`, `_b` and `gs_midrise_g` --
    12.2 MB, and 95 of the 711 model imports `light_bake.mark_imports` sets
    to Static Lightmaps, each unwrapped for a lightmap at import -- shipped
    and imported for scenes nothing instanced."""
    if not themed_site_dir:
        return None
    scene = Path(themed_site_dir) / "site.tscn"
    try:
        text = scene.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    ids = {m.group(2) for m in _LOT_SITE_REF.finditer(text)}
    return ids or None
'''

EDITS = [
    ("_LOT_SITE_REF = re.compile(r'path=\"(lot/([^\"/]+)/site\\.tscn)\"')\n",
     "_LOT_SITE_REF = re.compile(r'path=\"(lot/([^\"/]+)/site\\.tscn)\"')\n" + STANDING),
    ("def _copy_tree(src: Path, dst: Path, *, skip: set[str] = frozenset(),\n"
     "               skip_dirs: set[str] = frozenset(),\n"
     "               skip_rel: set[str] = frozenset()) -> None:\n"
     "    dst.mkdir(parents=True, exist_ok=True)\n"
     "    for item in src.rglob(\"*\"):\n"
     "        if item.is_dir():\n"
     "            continue\n"
     "        if item.name in skip or item.name.endswith(\".provenance.json\"):\n"
     "            continue\n"
     "        rel = item.relative_to(src)\n",
     "def _copy_tree(src: Path, dst: Path, *, skip: set[str] = frozenset(),\n"
     "               skip_dirs: set[str] = frozenset(),\n"
     "               skip_rel: set[str] = frozenset(),\n"
     "               skip_lot: set[str] = frozenset()) -> None:\n"
     "    dst.mkdir(parents=True, exist_ok=True)\n"
     "    for item in src.rglob(\"*\"):\n"
     "        if item.is_dir():\n"
     "            continue\n"
     "        if item.name in skip or item.name.endswith(\".provenance.json\"):\n"
     "            continue\n"
     "        rel = item.relative_to(src)\n"
     "        # `skip_lot` (0.207.0) names `lot/<id>/` packages no scene stands\n"
     "        # (`_standing_lot_ids`): by a relative path's first two parts, never\n"
     "        # by a name, which would match anywhere in the tree\n"
     "        if skip_lot and len(rel.parts) > 2 and rel.parts[0] == \"lot\" and rel.parts[1] in skip_lot:\n"
     "            continue\n"),
    ("        _copy_tree(composed_root, dest,\n"
     "                   skip={\"project.godot\", \"HANDOFF.md\",\n"
     "                         \"portable_resource_manifest.json\",\n"
     "                         \"compose.summary.json\",\n"
     "                         \"site_main.tscn\"},\n"
     "                   skip_rel=(set() if (wanted or building_rel)\n"
     "                             else set(_COMPOSED_ROOT_PAIR)),\n"
     "                   skip_dirs={\".godot\", \"addons\"})\n",
     "        # ONLY THE PACKAGES A SCENE STANDS (0.207.0, `_standing_lot_ids`): a\n"
     "        # varied lot's composed root holds a `lot/<id>/` for every building\n"
     "        # the brief was given, and the assembly names the ones this candidate\n"
     "        # stands. A single-shell mission moves the root itself under\n"
     "        # `lot/<id>/` and has no packages of its own to leave out.\n"
     "        standing = None if building_rel else _standing_lot_ids(themed_site_dir)\n"
     "        lot_root = Path(composed_root) / \"lot\"\n"
     "        idle = (sorted({d.name for d in lot_root.iterdir() if d.is_dir()} - standing)\n"
     "                if standing is not None and lot_root.is_dir() else [])\n"
     "        if idle:\n"
     "            print(\"[export] %d composed building(s) no scene stands, left out: %s\"\n"
     "                  % (len(idle), \", \".join(idle)))\n"
     "        _copy_tree(composed_root, dest,\n"
     "                   skip={\"project.godot\", \"HANDOFF.md\",\n"
     "                         \"portable_resource_manifest.json\",\n"
     "                         \"compose.summary.json\",\n"
     "                         \"site_main.tscn\"},\n"
     "                   skip_rel=(set() if (wanted or building_rel)\n"
     "                             else set(_COMPOSED_ROOT_PAIR)),\n"
     "                   skip_dirs={\".godot\", \"addons\"},\n"
     "                   skip_lot=set(idle))\n"),
]


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.207.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.207.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.207.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.207.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    rel = "packages/exporting/export.py"
    raw = (LF / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    eol = _eol(raw, rel)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in EDITS:
        assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
        text = text.replace(old, new)
    compile(text, rel, "exec")
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    for r, data in news.items():
        compile(data.decode("utf-8"), r, "exec")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    (LF / rel).write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for r, data in news.items():
        (LF / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.206.1 -> 0.207.0")


if __name__ == "__main__":
    main()
