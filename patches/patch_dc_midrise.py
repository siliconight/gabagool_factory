"""Deli Counter 0.213.0: mid-rise Empties, five to twelve storeys of brick, out of today's streets (factory roadmap
241, step 1; the walker's comps in the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`).

Anchored edits, each asserted exactly once and the file's sha16 pinned, nothing written until all matched:
  presets.py                   `MIDRISE_BAY`, `empty_midrise`, `EMPTY_MIDRISES` after the rowhome family's
                               stoop loop (`dc_midrise/presets_midrise.py.txt`); `REGISTRY["empty_midrise"]`
  test_empty_midrise.py        NEW (`dc_midrise/test_empty_midrise.py.txt`)
  specs/gs_midrise_*.json      NEW, written from the patched presets (`json.dumps(indent=2)`, no trailing
                               newline, as the rowhome Empties' are), and `specs/CATALOG.md` regenerated
                               (`catalog.py`)
CHANGELOG and VERSION from `dc_midrise/CHANGELOG_0.213.0.md`; `--results-pending` leaves the RESULT_ keys
to `--fill`. The six shells are built after (`build.py specs/gs_midrise_*.json`).

Read before it was written, in this session: `presets.py`'s `_facade`, `empty_rowhome`, `EMPTY_ROWHOMES` and
its stoop loop, `REGISTRY` and `make`; `deli_counter.py`'s `facade` branches (the shut door, facade glazing,
the roof slab); `empty_panes.py` (window states by storey); `roofs.front_facing`; `test_empties.py` and
`test_more_rowhomes.py`; a rowhome Empty's spec, slots and GLB; `catalog.py`'s usage; and Level Factory's
`building_library.empty_rows` and `non_source`, which decide what a brief is given. Every file LF.

    python patches/patch_dc_midrise.py --results-pending
    (build.py on the six specs; python -m pytest -q in deli_counter)
    python patches/patch_dc_midrise.py --fill
"""
import hashlib
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_midrise"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILT": "result_built.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.212.0", b"Deli Counter 0.213.0"
CHANGELOG_HEAD = "## [0.212.0] - a stoop's iron railings, one each side"
SHA = {"presets.py": "21cc0259284f96b3"}
NEW = {"test_empty_midrise.py": "test_empty_midrise.py.txt"}

LOOP = ("for _args in EMPTY_ROWHOMES.values():\n"
        "    _args.setdefault(\"stoop\", stoop_geom.RISERS)\n")
REG_OLD = "    \"empty_rowhome\": empty_rowhome,\n"
REG_NEW = "    \"empty_rowhome\": empty_rowhome,\n    \"empty_midrise\": empty_midrise,\n"

REGEN = (
    "import json, sys\n"
    "sys.path.insert(0, '.')\n"
    "import presets\n"
    "for n, a in sorted(presets.EMPTY_MIDRISES.items()):\n"
    "    p = 'specs/%s.json' % n\n"
    "    data = json.dumps(presets.empty_midrise(name=n, **a), indent=2).encode('utf-8')\n"
    "    if sys.argv[1] == 'check':\n"
    "        assert open(p, 'rb').read() == data, ('not the presets output', p)\n"
    "    else:\n"
    "        open(p, 'wb').write(data)\n"
    "print(sys.argv[1], len(presets.EMPTY_MIDRISES), 'specs')\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.213.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    subprocess.run([sys.executable, "-c", REGEN, "check"], cwd=DC, check=True)
    print("Deli Counter 0.213.0: results filled")


def main():
    if FILL:
        return fill()
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.213.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.213.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (DC / rel).exists(), ("already applied", rel)
    assert not list((DC / "specs").glob("gs_midrise_*.json")), "already applied: specs"
    rel = "presets.py"
    raw = (DC / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    eol = _eol(raw, rel)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    block = (SRC / "presets_midrise.py.txt").read_bytes().decode("utf-8").replace("\r\n", "\n")
    for old, new in ((LOOP, LOOP + block), (REG_OLD, REG_NEW)):
        assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
        text = text.replace(old, new)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    (DC / rel).write_bytes(text.encode("utf-8").replace(b"\n", eol))
    for r, data in news.items():
        (DC / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(VERSION)
    subprocess.run([sys.executable, "-c", REGEN, "write"], cwd=DC, check=True)
    subprocess.run([sys.executable, "catalog.py"], cwd=DC, check=True)
    print("Deli Counter 0.212.0 -> 0.213.0")


if __name__ == "__main__":
    main()
