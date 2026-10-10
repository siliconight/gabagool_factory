"""Zoo 1.97.0: the backdrop tree with a silhouette (roadmap 228, step F). See
`zoo_backdrop_3/CHANGELOG_1.97.0.md`.

The walker, on cold run 9227's parkland: "those trees in the distance are a little lazy imo
(giant lolipops vs. trees)". A trunk that flares and forks into three limbs under seven lobes,
the form by the slot's proportions, the sum fitted to the slot.

Whole files from `zoo_backdrop_3/`, each replaced file pinned by the hash its content had when
this patch was written, with its line endings made LF:
  replaced  zoo_keeper/core/backdrop_forms.py        tree_form, tree_plan, tree_plan_bounds,
                                                     TREE_FORM_ROWS and the tree's new constants;
                                                     tree_parts kept for the record
  replaced  zoo_keeper/recipes/backdrop_tree.py      the cones and the lobes, fitted
  replaced  zoo_keeper/genome/species/backdrop_tree.json   version 2, budget 800
  new       tests/test_backdrop_3.py
No registry changes: the species, its theme styles and its census builds are as 1.96.0 listed
them. CHANGELOG and VERSION from `CHANGELOG_1.97.0.md`. Nothing is written until every pin matched.

    python patches/patch_zoo_backdrop_3.py --results-pending
    python patches/patch_zoo_backdrop_3.py --fill        fill the results from result_*.txt
    ZOO_ROOT=<copy> python patches/patch_zoo_backdrop_3.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_backdrop_3"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILD": "result_build.txt", "RESULT_CENSUS": "result_census.txt",
           "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"1.96.0", b"1.97.0"
CHANGELOG_HEAD = "## [1.96.0] - the backdrop's tree and warehouse\n"
REPLACED = {
    "zoo_keeper/core/backdrop_forms.py": ("backdrop_forms.py", "195d949d6ed56d8a"),
    "zoo_keeper/recipes/backdrop_tree.py": ("backdrop_tree.py", "4c0acd5d61cedd87"),
    "zoo_keeper/genome/species/backdrop_tree.json": ("backdrop_tree.json", "1f98bc10f9672b88"),
}
NEW = {
    "tests/test_backdrop_3.py": "test_backdrop_3.py",
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
    for path, rel in ((ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.97.0.md", "the entry")):
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        path.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    print("Zoo 1.97.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.97.0.md").decode("utf-8")
    assert entry.startswith("## [1.97.0] - "), entry[:40]
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
    print("Zoo 1.96.0 -> 1.97.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
