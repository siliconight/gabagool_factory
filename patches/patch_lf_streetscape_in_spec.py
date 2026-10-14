"""Level Factory 0.205.0: the site says what its street is -- an urban brief's spec carries `streetscape: "urban"`
(factory roadmap 241), so Lot 0.123.0 plants a city block's trees on it.

One anchored edit to `apps/cli/commands/__init__.py`, asserted exactly once and the file's sha16 pinned: right after
the compose stage decides `_urban`, `spec["streetscape"] = "urban"` when it is; a strip writes nothing.
`tests/unit/test_streetscape_in_site_spec.py` NEW (`lf_streetscape_in_spec/...py.txt`). CHANGELOG and VERSION from
`lf_streetscape_in_spec/CHANGELOG_0.205.0.md`; `--results-pending` leaves RESULT_ keys to `--fill`.

Read before it was written, in this session: `_write_site_spec`'s urban block (`_urban` from `library`,
`streetscape_effective` and `empties_effective`; `spec` built before it and given `blockers` after); Lot 0.123.0's
`assemble`, which asks `site_spec.get("streetscape") == "urban"`. Every file LF.

    python patches/patch_lf_streetscape_in_spec.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_streetscape_in_spec.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_streetscape_in_spec"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_FAILING": "result_failing.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.204.0", b"0.205.0"
CHANGELOG_HEAD = ("## [0.204.0] - Heights by cause: the urban wall stands its lowest blocks across from the action "
                  "and rises away from it")
SHA = {"apps/cli/commands/__init__.py": "eec8062ea651a2c4"}
NEW = {"tests/unit/test_streetscape_in_site_spec.py": "test_streetscape_in_site_spec.py.txt"}

URBAN_OLD = ("    _urban = bool(library) and bool(_se(getattr(model, \"streetscape\", \"\"),\n"
             "                                       _ee(getattr(model, \"empties\", \"across\"), library,\n"
             "                                           getattr(model, \"building_count\", 1))))\n")
URBAN_NEW = (URBAN_OLD +
             "    # THE SITE SAYS WHAT ITS STREET IS (0.205.0, roadmap 241): Lot 0.123.0\n"
             "    # plants a city block's trees on an urban street, one every 30 ft\n"
             "    # (`site_furniture.urban_tree_stations`); a strip writes nothing, so its\n"
             "    # spec is byte for byte what it was.\n"
             "    if _urban:\n"
             "        spec[\"streetscape\"] = \"urban\"\n")

EDITS = {"apps/cli/commands/__init__.py": [(URBAN_OLD, URBAN_NEW)]}


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.205.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.205.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.205.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.205.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in EDITS.items():
        raw = (LF / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:70])
            text = text.replace(old, new)
        compile(text, rel, "exec")
        writes[rel] = (text, eol)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, (body, e) in writes.items():
        (LF / rel).write_bytes(body.encode("utf-8").replace(b"\n", e))
    for r, data in news.items():
        (LF / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.204.0 -> 0.205.0")


if __name__ == "__main__":
    main()
