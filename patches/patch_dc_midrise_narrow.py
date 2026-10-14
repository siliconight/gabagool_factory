"""Deli Counter 0.217.0: three narrow mid-rises, the blocks that fit between the mission's buildings (factory roadmap
241, the near side).

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  presets.py              `empty_midrise`'s bays floor at two, not three; `EMPTY_MIDRISE_NARROW` (gs_midrise_g, _h,
                          _i) after `EMPTY_MIDRISES`
  navgate_baseline.json   three UNJUDGED entries after `gs_midrise_f`; `counts.unjudged` 27 -> 30
  specs/gs_midrise_g/h/i.json   NEW, written from the patched presets (indent=2, no closing newline, as the six
                          are); `specs/CATALOG.md` regenerated (`catalog.py`)
  test_empty_midrise_narrow.py  NEW (`dc_midrise_narrow/test_empty_midrise_narrow.py.txt`)
CHANGELOG and VERSION from `dc_midrise_narrow/CHANGELOG_0.217.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`. The three shells are built after (`build.py --all`, since `presets.py` moves).

Read before it was written, in this session: `presets.empty_midrise` (the bay arithmetic, `max(3, ...)`, the
door bay) and `EMPTY_MIDRISES`; `test_empty_midrise.py` (five to twelve storeys, no two the same height --
why the narrow three are a separate table); a mid-rise spec's form; `navgate_baseline.json`'s last Empty entry
and its counts; the three narrow blocks generated in memory and linted (0 FAIL, 0 WARN each); the near rooms
measured on cold run 9288 (`docs/findings/urban_street/near_room.py`). Every file LF.

    python patches/patch_dc_midrise_narrow.py --results-pending
    (build.py --all; python -m pytest -q in deli_counter)
    python patches/patch_dc_midrise_narrow.py --fill
"""
import hashlib
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_midrise_narrow"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILT": "result_built.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.216.0", b"Deli Counter 0.217.0"
CHANGELOG_HEAD = ("## [0.216.0] - the census's body-sized literals read the agent contract, and combat_audit "
                  "reads the builder's openings")
SHA = {"presets.py": "f993079b37279378", "navgate_baseline.json": "d9a6a9e3fc48ba70"}
NEW = {"test_empty_midrise_narrow.py": "test_empty_midrise_narrow.py.txt"}
NAMES = ["gs_midrise_g", "gs_midrise_h", "gs_midrise_i"]

PRESETS = [
    ("    bays = max(3, int(round(float(width) / MIDRISE_BAY)))\n",
     "    # Two bays at the least (0.217.0): a 6.3 m front holds two windows in the\n"
     "    # family's rhythm, where a floor of three stood them 2.1 m apart. The six\n"
     "    # have five bays or more, so the floor never bound them.\n"
     "    bays = max(2, int(round(float(width) / MIDRISE_BAY)))\n"),
    ("    \"gs_midrise_f\": dict(width=19.5, floors=12, wall=\"brick\", lobby=-0.25, cornice=1.5,\n"
     "                         seed=1936, door_finish=\"white\"),\n"
     "}\n",
     "    \"gs_midrise_f\": dict(width=19.5, floors=12, wall=\"brick\", lobby=-0.25, cornice=1.5,\n"
     "                         seed=1936, door_finish=\"white\"),\n"
     "}\n"
     "\n"
     "#: THE NARROW MID-RISES (0.217.0, roadmap 241): two- and three-bay blocks for\n"
     "#: the rooms an urban street's near side leaves between the mission's own\n"
     "#: buildings -- on urban_row_001 (cold run 9288) 12.67, 11.35, 7.33 and 6.70\n"
     "#: m, where the six's narrowest measures 15.3. 12.0, 10.0 and 6.3 m wide\n"
     "#: (12.3, 10.3 and 6.6 as built), lower than the six, under the family's\n"
     "#: prefix so the urban street draws them with the rest. A table of their own,\n"
     "#: so the six keep theirs: five to twelve storeys, no two the same height.\n"
     "EMPTY_MIDRISE_NARROW = {\n"
     "    \"gs_midrise_g\": dict(width=12.0, floors=6, wall=\"brick\", lobby=0.0, cornice=1.0,\n"
     "                         seed=1937, door_finish=\"black\"),\n"
     "    \"gs_midrise_h\": dict(width=10.0, floors=5, wall=\"brick_orange\", lobby=0.0, cornice=1.0,\n"
     "                         seed=1938, door_finish=\"stained\"),\n"
     "    \"gs_midrise_i\": dict(width=6.3, floors=4, wall=\"brick_brown\", lobby=0.0, cornice=0.8,\n"
     "                         seed=1939, door_finish=\"green\"),\n"
     "}\n"),
]

REASON = ("a narrow mid-rise Empty (Deli Counter 0.217.0, roadmap 241): facade-only, sealed, no interior for a "
          "spawn marker to stand in, so zero markers checked is the correct outcome -- the same call as every Empty")
BASELINE_OLD = ("      \"reason\": \"a mid-rise Empty (Deli Counter 0.213.0, roadmap 241): facade-only, sealed, no "
                "interior for a spawn marker to stand in, so zero markers checked is the correct outcome -- the "
                "same call as gs_facade_rowhome and the rowhome Empties\"\n"
                "    }\n"
                "  ],\n"
                "  \"stair_failures\": [\n")
BASELINE_NEW = BASELINE_OLD[:-len("    }\n  ],\n  \"stair_failures\": [\n")] + "".join(
    "    },\n"
    "    {\n"
    "      \"shell\": \"%s\",\n"
    "      \"checked\": 0,\n"
    "      \"navigable\": null,\n"
    "      \"stairs_ok\": true,\n"
    "      \"reason\": \"%s\"\n" % (n, REASON) for n in NAMES) + "    }\n  ],\n  \"stair_failures\": [\n"
COUNT_OLD, COUNT_NEW = "    \"unjudged\": 27,\n", "    \"unjudged\": 30,\n"

REGEN = (
    "import json, sys\n"
    "sys.path.insert(0, '.')\n"
    "import presets\n"
    "for n, a in sorted(presets.EMPTY_MIDRISE_NARROW.items()):\n"
    "    p = 'specs/%s.json' % n\n"
    "    open(p, 'wb').write(json.dumps(presets.empty_midrise(name=n, **a), indent=2).encode('utf-8'))\n"
    "for n, a in sorted(presets.EMPTY_MIDRISES.items()):\n"
    "    p = 'specs/%s.json' % n\n"
    "    data = json.dumps(presets.empty_midrise(name=n, **a), indent=2).encode('utf-8')\n"
    "    assert open(p, 'rb').read() == data, ('the six moved', p)\n"
    "print('wrote', len(presets.EMPTY_MIDRISE_NARROW), 'specs; the six unchanged')\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _read(rel):
    raw = (DC / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.217.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.217.0: results filled")


def main():
    if FILL:
        return fill()
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.217.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.217.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in list(NEW) + ["specs/%s.json" % n for n in NAMES]:
        assert not (DC / rel).exists(), ("already applied", rel)
    eol_p, presets_text = _read("presets.py")
    for old, new in PRESETS:
        assert presets_text.count(old) == 1, ("presets.py", "anchor", presets_text.count(old), old[:60])
        presets_text = presets_text.replace(old, new)
    compile(presets_text, "presets.py", "exec")
    eol_b, base = _read("navgate_baseline.json")
    for old, new in ((BASELINE_OLD, BASELINE_NEW), (COUNT_OLD, COUNT_NEW)):
        assert base.count(old) == 1, ("navgate_baseline.json", "anchor", base.count(old), old[:60])
        base = base.replace(old, new)
    import json
    json.loads(base)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    (DC / "presets.py").write_bytes(presets_text.encode("utf-8").replace(b"\n", eol_p))
    (DC / "navgate_baseline.json").write_bytes(base.encode("utf-8").replace(b"\n", eol_b))
    for r, data in news.items():
        (DC / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(VERSION)
    subprocess.run([sys.executable, "-c", REGEN], cwd=DC, check=True)
    subprocess.run([sys.executable, "catalog.py"], cwd=DC, check=True)
    print("Deli Counter 0.216.0 -> 0.217.0")


if __name__ == "__main__":
    main()
