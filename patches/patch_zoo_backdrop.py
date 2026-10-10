"""Zoo 1.95.0: the backdrop beyond the plate's edge, a rowhome and a water tower (roadmap 228,
step C). See `zoo_backdrop/CHANGELOG_1.95.0.md`.

New files from `zoo_backdrop/`, and the four species registries replaced whole:
  zoo_keeper/core/backdrop_forms.py            the plan and the facade's paint, no bpy
  zoo_keeper/recipes/backdrop_rowhome.py       one painted box with a roofline, one surface
  zoo_keeper/recipes/water_tower.py            a tank on braced legs with a beacon
  zoo_keeper/genome/species/backdrop_rowhome.json, water_tower.json
  tests/test_backdrop.py
CHANGELOG and VERSION from `CHANGELOG_1.95.0.md`. Nothing is written until every check passed.

    python patch_zoo_backdrop.py --results-pending
    python patch_zoo_backdrop.py --fill            fill the results from result_build.txt, result_suite.txt
    ZOO_ROOT=<copy> python patch_zoo_backdrop.py --draft
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_backdrop"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILD": "result_build.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"1.94.0", b"1.95.0"
CHANGELOG_HEAD = ("## [1.94.0] - a door box wears its business's band as the pack asks, at the "
                  "art's own shape\n")
NEW = {
    "zoo_keeper/core/backdrop_forms.py": "backdrop_forms.py",
    "zoo_keeper/recipes/backdrop_rowhome.py": "backdrop_rowhome.py",
    "zoo_keeper/recipes/water_tower.py": "water_tower.py",
    "zoo_keeper/genome/species/backdrop_rowhome.json": "backdrop_rowhome.json",
    "zoo_keeper/genome/species/water_tower.json": "water_tower.json",
    "tests/test_backdrop.py": "test_backdrop.py",
}
#: The registries that audit every species by hand (a count that updates itself audits
#: nothing), each replaced whole and pinned by the hash its content had when this patch was
#: written: the hand-authored species set, the painted-metal list, the delco_1997 count, and
#: the coincident-face census' build count with its record.
REPLACED = {
    "tests/test_genome.py": ("test_genome.py", "e10444af0d4e5c5d"),
    "tests/test_material_options_closed.py": ("test_material_options_closed.py", "09b0df962be62818"),
    "tests/test_theme_style_resolution.py": ("test_theme_style_resolution.py", "36dc7795814a1c11"),
    "tests/test_coincident_faces.py": ("test_coincident_faces.py", "00314f10b5fcf4c8"),
}


def _sha(raw):
    import hashlib
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


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
    for path, rel in ((ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.95.0.md", "the entry")):
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        path.write_bytes(text.encode("utf-8").replace(b"\n", eol))
    print("Zoo 1.95.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.95.0.md").decode("utf-8")
    assert entry.startswith("## [1.95.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (ZOO / rel).exists(), (rel, "already exists")
    writes = {}
    for rel, (name, sha) in REPLACED.items():
        raw = (ZOO / rel).read_bytes()
        assert _sha(raw) == sha, (rel, "is not the file this patch read", _sha(raw))
        writes[ZOO / rel] = _src(name).replace(b"\n", _eol(raw, rel))
    cl = ZOO / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    head = text.index(CHANGELOG_HEAD)
    assert text.count(CHANGELOG_HEAD) == 1 and head < 200, (head, text[:120])
    # every check passed: now write
    for rel, name in NEW.items():
        (ZOO / rel).parent.mkdir(parents=True, exist_ok=True)
        (ZOO / rel).write_bytes(_src(name))
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((text[:head] + entry.rstrip("\n") + "\n\n" + text[head:])
                   .encode("utf-8").replace(b"\n", eol))
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.94.0 -> 1.95.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
