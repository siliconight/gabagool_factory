"""Zoo 1.96.0: the backdrop's tree and warehouse (roadmap 228). See
`zoo_backdrop_2/CHANGELOG_1.96.0.md`.

Whole files from `zoo_backdrop_2/`, each replaced file pinned by the hash its content had when
this patch was written, with its line endings made LF:
  replaced  zoo_keeper/core/backdrop_forms.py   tree_parts, warehouse_parts, paint_warehouse,
                                                warehouse_uv_for and their constants
  replaced  tests/test_genome.py, test_theme_style_resolution.py,
            test_coincident_faces.py            the registries that audit every species by hand
  new       zoo_keeper/recipes/backdrop_tree.py, backdrop_warehouse.py
  new       zoo_keeper/genome/species/backdrop_tree.json, backdrop_warehouse.json
  new       tests/test_backdrop_2.py
CHANGELOG and VERSION from `CHANGELOG_1.96.0.md`. Nothing is written until every pin matched.

    python patch_zoo_backdrop_2.py --results-pending
    python patch_zoo_backdrop_2.py --fill        fill the results from result_*.txt
    ZOO_ROOT=<copy> python patch_zoo_backdrop_2.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_backdrop_2"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILD": "result_build.txt", "RESULT_CENSUS": "result_census.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"1.95.0", b"1.96.0"
CHANGELOG_HEAD = "## [1.95.0] - the backdrop beyond the plate's edge: a rowhome and a water tower\n"
REPLACED = {
    "zoo_keeper/core/backdrop_forms.py": ("backdrop_forms.py", "393a63ffd9303703"),
    "tests/test_genome.py": ("test_genome.py", "0379caf8f1082fff"),
    "tests/test_theme_style_resolution.py": ("test_theme_style_resolution.py", "6e3b486872ad8bd1"),
    "tests/test_coincident_faces.py": ("test_coincident_faces.py", "b0bd4f0b22a7769b"),
}
NEW = {
    "zoo_keeper/recipes/backdrop_tree.py": "backdrop_tree.py",
    "zoo_keeper/recipes/backdrop_warehouse.py": "backdrop_warehouse.py",
    "zoo_keeper/genome/species/backdrop_tree.json": "backdrop_tree.json",
    "zoo_keeper/genome/species/backdrop_warehouse.json": "backdrop_warehouse.json",
    "tests/test_backdrop_2.py": "test_backdrop_2.py",
}


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _sha(raw):
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]


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
        assert value and "RESULT_" not in value, (name, value)
        results[key] = value
    for path, rel in ((ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.96.0.md", "the entry")):
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        path.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    print("Zoo 1.96.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.96.0.md").decode("utf-8")
    assert entry.startswith("## [1.96.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, (name, sha) in REPLACED.items():
        raw = (ZOO / rel).read_bytes()
        assert _sha(raw) == sha, (rel, "is not the file this patch read", _sha(raw))
        writes[ZOO / rel] = _src(name).replace(b"\n", _eol(raw, rel))
    for rel in NEW:
        assert not (ZOO / rel).exists(), (rel, "already exists")
    cl = ZOO / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    head = text.index(CHANGELOG_HEAD)
    assert text.count(CHANGELOG_HEAD) == 1 and head < 200, (head, text[:120])
    for rel, name in NEW.items():
        (ZOO / rel).write_bytes(_src(name))
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((text[:head] + entry.rstrip("\n") + "\n\n" + text[head:])
                   .encode("utf-8").replace(b"\n", eol))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.95.0 -> 1.96.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
