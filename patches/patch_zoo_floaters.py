"""Zoo 1.106.0: floaters, one rule for a detail laid on a surface (factory roadmap 234; the README's "Floaters").

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all matched:
  zoo_keeper/core/floaters.py           NEW (`zoo_floaters/core_floaters.py.txt`)
  zoo_keeper/bpylayer/geometry.py       imports `core.floaters`; `FLOATER_SKIRT`, `FLOATER_PROUD`,
                                        `add_floater`, `add_flat_floater` before `solidify`
  README.md                             the section's note and its helper paragraph: built, with signatures
  tests/test_floaters.py                NEW (`zoo_floaters/test_floaters.py.txt`)
CHANGELOG and VERSION from `zoo_floaters/CHANGELOG_1.106.0.md`; `--results-pending` leaves the RESULT_ keys
to `--fill`.

Read before it was written, in this session: the README's "Floaters" section whole; `bpylayer/geometry.py`'s
imports, `add_box`, `add_cylinder`, `place` and `solidify`; `core/normals.py`'s header (the pure-core pattern);
`tests/test_hemisphere.py`'s two halves and its Blender command; `tests/test_coincident_faces.py`'s `PROBE_TOL`,
`DEPTH_K` and `fight_distance_m`; and every species constant the README names (`grep` of JOIN, PROUD,
STAND_BURY, RING_PROUD, ART_PROUD). Every file LF.

    python patches/patch_zoo_floaters.py --results-pending
    (python -m pytest -q in zoo; the Blender half: the command in tests/test_floaters.py)
    python patches/patch_zoo_floaters.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_floaters"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_BLENDER": "result_blender.txt"}
VERSION_WAS, VERSION = b"1.105.0", b"1.106.0"
CHANGELOG_HEAD = "## [1.105.0] - a stoop's iron railing: a level section along the landing, a flight down the steps"
GEO = "zoo_keeper/bpylayer/geometry.py"
SHA = {GEO: "83c6cd5d49932b49", "README.md": "b48107b55a6ef816"}
NEW = {"zoo_keeper/core/floaters.py": "core_floaters.py.txt", "tests/test_floaters.py": "test_floaters.py.txt"}

EDITS = {
    GEO: [
        ("from ..core import normals as core_normals\n",
         "from ..core import floaters as core_floaters\n"
         "from ..core import normals as core_normals\n"),
        ("def solidify(bm, thickness):\n",
         "# --- floaters (1.106.0, roadmap 234; the README's \"Floaters\") -------------\n"
         "\n"
         "#: a solid floater's skirt below its host, and a flat one's stand off it\n"
         "#: (`core.floaters`, where each is derived)\n"
         "FLOATER_SKIRT = core_floaters.FLOATER_SKIRT\n"
         "FLOATER_PROUD = core_floaters.FLOATER_PROUD\n"
         "\n"
         "\n"
         "def add_floater(bm, point, normal, build, spin=0.0, skirt=FLOATER_SKIRT):\n"
         "    \"\"\"A SOLID floater. `build(bm)` makes it in its own frame -- Z up, its\n"
         "    base at z = 0, open at the bottom -- and returns its verts; they are\n"
         "    carried onto the host so +Z lies along `normal`, turned `spin` radians\n"
         "    about it, the base on `point` lowered `skirt` into the host. Returns\n"
         "    the verts. A recipe gives `point` and `normal` from its own\n"
         "    construction -- it knows where its faces are -- so placement stays\n"
         "    deterministic, and the coplanar census stays the judge of the result.\"\"\"\n"
         "    verts = build(bm)\n"
         "    m = Matrix(core_floaters.solid_frame(point, normal, spin, skirt))\n"
         "    for v in verts:\n"
         "        v.co = m @ v.co\n"
         "    return verts\n"
         "\n"
         "\n"
         "def add_flat_floater(bm, point, normal, w, h, spin=0.0, proud=FLOATER_PROUD):\n"
         "    \"\"\"A FLAT floater: a one-sided `w` x `h` quad standing `proud` off its\n"
         "    host, centred on `point` and facing along `normal`, its width along the\n"
         "    axis turned `spin` radians about it. Returns its face.\"\"\"\n"
         "    verts = [bm.verts.new(c) for c in core_floaters.flat_quad(\n"
         "        point, normal, w, h, spin, proud)]\n"
         "    return bm.faces.new(verts)\n"
         "\n"
         "\n"
         "def solidify(bm, thickness):\n"),
    ],
    "README.md": [
        ("2011). Roadmap 234. The concept is written down first; the helper below is not\n"
         "built yet.*\n",
         "2011). Roadmap 234. The concept was written down first; the helper below was\n"
         "built in 1.106.0, and no species uses it yet.*\n"),
        ("**The helper (to build, roadmap 234).**\n"
         "`geometry.add_floater(bm, point, normal, build, spin=0.0, skirt=FLOATER_SKIRT)`:\n"
         "`build(bm)` makes the floater in its own frame (Z up, its base at z = 0, open at\n"
         "the bottom); the helper turns +Z onto the host's normal, spins it about that\n"
         "normal, and lowers it into the host by the skirt.\n"
         "`geometry.add_flat_floater(bm, point, normal, w, h, proud=FLOATER_PROUD)` lays\n"
         "a one-sided quad. A recipe takes `point` and `normal` from its own construction\n"
         "-- it knows where its faces are -- rather than by ray-casting, so placement\n"
         "stays deterministic, and the coplanar census stays the judge of every result",
         "**The helper (1.106.0, roadmap 234).** The arithmetic is `core.floaters`, pure\n"
         "Python: `FLOATER_SKIRT` 4 mm, `FLOATER_PROUD` 3 mm, and the frame that carries\n"
         "a floater onto its host.\n"
         "`geometry.add_floater(bm, point, normal, build, spin=0.0, skirt=FLOATER_SKIRT)`:\n"
         "`build(bm)` makes the floater in its own frame (Z up, its base at z = 0, open at\n"
         "the bottom) and returns its verts; the helper turns +Z onto the host's normal,\n"
         "spins it about that normal, and lowers it into the host by the skirt.\n"
         "`geometry.add_flat_floater(bm, point, normal, w, h, spin=0.0, proud=FLOATER_PROUD)`\n"
         "lays a one-sided quad, its width along the spun axis. A recipe takes `point` and\n"
         "`normal` from its own construction -- it knows where its faces are -- rather\n"
         "than by ray-casting, so placement stays deterministic, and the coplanar census\n"
         "stays the judge of every result. No species uses them yet: each built its\n"
         "floaters before the rule had a name, and moving one is a change to that\n"
         "species' mesh, priced and censused as any other"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION, (ZOO / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.106.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.106.0: results filled")


def main():
    if FILL:
        return fill()
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_1.106.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [1.106.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (ZOO / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, pairs in EDITS.items():
        p = ZOO / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    news = {rel: (SRC / src).read_bytes().replace(b"\r\n", b"\n") for rel, src in NEW.items()}
    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    for rel, data in news.items():
        (ZOO / rel).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.105.0 -> 1.106.0")


if __name__ == "__main__":
    main()
