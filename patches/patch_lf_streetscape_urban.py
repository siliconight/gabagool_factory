"""Level Factory 0.200.0: an urban street -- the brief asks (`streetscape: "urban"`), and the far side stands a
continuous mid-rise wall (factory roadmap 241, steps 2 and 3, the first cut).

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  packages/core/models.py               STREETSCAPE_URBAN, `streetscape_effective`, the `streetscape` field, and
                                        the signature key only when it takes effect
  packages/pipeline/building_library.py MIDRISE_PREFIX; `empty_rows(build_dir, prefix)`; `empties_for_brief`
                                        draws the mid-rise family for an urban brief
  packages/pipeline/empties.py          `terrace(..., continuous=False)`: no alleys when continuous
  apps/cli/commands/__init__.py         the compose stage passes `continuous` for an urban brief, and says so --
                                        or says URBAN_WITHOUT_MIDRISES when the library holds none
  adapters/deli_counter/__init__.py     `_VALID_PRESETS` learns Deli Counter 0.213.0's `empty_midrise`:
                                        `test_dc_preset_registry` has failed since that release, unseen,
                                        because nothing ran this suite after it
  tests/unit/test_streetscape_urban.py  NEW (`lf_streetscape_urban/test_streetscape_urban.py.txt`)
CHANGELOG and VERSION from `lf_streetscape_urban/CHANGELOG_0.200.0.md`; `--results-pending` leaves RESULT_ keys
to `--fill`.

Read before it was written, in this session: `models.MissionBrief` (its fields, `functional_signature` and the
conditional-key rule), `empties_effective`; `building_library.empty_rows`, `empties_for_brief` and their
callers (the planner's art jobs at `commands` 1450, the compose rows at 2285); `empties.terrace` whole and its
tests; the compose stage's terrace block; `_brief_model` (unknown keys are dropped, so the field must be
declared); the factory's `docs/reference/URBAN_MIDRISE_COMPS.md` and roadmap 241. Every file LF.

    python patches/patch_lf_streetscape_urban.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_streetscape_urban.py --fill
    (commit; then a cold run of an urban brief, recorded in the factory root)
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_streetscape_urban"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.199.0", b"0.200.0"
CHANGELOG_HEAD = "## [0.199.0] - The price reports what the package holds in memory"
SHA = {"packages/core/models.py": "b068fe170e8d13f9",
       "packages/pipeline/building_library.py": "7a1eac847463eeed",
       "packages/pipeline/empties.py": "8229553232cf7c36",
       "apps/cli/commands/__init__.py": "38d8ec6d9ef19ba4",
       "adapters/deli_counter/__init__.py": "69ca600bbdd504eb"}
NEW = {"tests/unit/test_streetscape_urban.py": "test_streetscape_urban.py.txt"}

EDITS = {
    "adapters/deli_counter/__init__.py": [
        ("    \"corner_deli\", \"empty_rowhome\", \"facade_industrial\", \"facade_rowhome\",\n",
         "    \"corner_deli\", \"empty_midrise\", \"empty_rowhome\", \"facade_industrial\",\n"
         "    \"facade_rowhome\",\n"),
    ],
    "packages/core/models.py": [
        ("EMPTIES_ACROSS = \"across\"\n\n",
         "EMPTIES_ACROSS = \"across\"\n"
         "\n"
         "#: THE URBAN STREET (0.200.0, factory roadmap 241): the brief's word for mid-rise\n"
         "#: street walls. Any other word, the empty string included, is today's strip.\n"
         "STREETSCAPE_URBAN = \"urban\"\n"
         "\n"
         "\n"
         "def streetscape_effective(streetscape, empties) -> str:\n"
         "    \"\"\"What a brief GETS: `STREETSCAPE_URBAN` when it asks for it and a terrace\n"
         "    stands (`empties`, `empties_effective`'s answer) -- the urban street's\n"
         "    first cut is the terrace's family and its continuity, so with no terrace\n"
         "    there is nothing for it to change -- and `\"\"` otherwise. One rule, read by\n"
         "    `MissionBrief.functional_signature` and `building_library`.\"\"\"\n"
         "    if str(streetscape or \"\").strip().lower() != STREETSCAPE_URBAN:\n"
         "        return \"\"\n"
         "    return STREETSCAPE_URBAN if empties else \"\"\n"
         "\n"),
        ("    empties: str = EMPTIES_ACROSS\n",
         "    empties: str = EMPTIES_ACROSS\n"
         "    #: THE STREETSCAPE (0.200.0, factory roadmap 241): `\"urban\"` stands the far\n"
         "    #: side as a continuous wall of Deli Counter's mid-rise Empties\n"
         "    #: (`gs_midrise_*`), the walker's urban level type of 2026-10-11. Empty, or\n"
         "    #: any other word, is today's strip: the rowhome terrace with its alleys.\n"
         "    #: `streetscape_effective` is the one rule for what a brief gets.\n"
         "    streetscape: str = \"\"\n"),
        ("        if empties:\n"
         "            sig[\"empties\"] = empties\n"
         "        return sig\n",
         "        if empties:\n"
         "            sig[\"empties\"] = empties\n"
         "        # the same care for the streetscape (0.200.0): keyed only where it\n"
         "        # changes the site, so every strip brief keeps the lock it has.\n"
         "        streetscape = streetscape_effective(self.streetscape, empties)\n"
         "        if streetscape:\n"
         "            sig[\"streetscape\"] = streetscape\n"
         "        return sig\n"),
    ],
    "packages/pipeline/building_library.py": [
        ("from packages.core.models import EMPTIES_ACROSS, empties_effective\n",
         "from packages.core.models import EMPTIES_ACROSS, empties_effective, streetscape_effective\n"),
        ("EMPTY_PREFIX = \"gs_empty_\"\n",
         "EMPTY_PREFIX = \"gs_empty_\"\n"
         "#: THE MID-RISE EMPTIES (0.200.0, factory roadmap 241): Deli Counter 0.213.0's\n"
         "#: family, named out of `EMPTY_PREFIX` so no strip terrace draws them; an\n"
         "#: urban brief draws them instead of the rowhomes.\n"
         "MIDRISE_PREFIX = \"gs_midrise_\"\n"),
        ("def empty_rows(build_dir) -> list[dict]:\n",
         "def empty_rows(build_dir, prefix=EMPTY_PREFIX) -> list[dict]:\n"),
        ("    for glb in sorted(d.glob(EMPTY_PREFIX + \"*.glb\")):\n",
         "    for glb in sorted(d.glob(prefix + \"*.glb\")):\n"),
        ("    return empty_rows(library)\n",
         "    empties = empties_effective(getattr(model, \"empties\", EMPTIES_ACROSS), library,\n"
         "                                getattr(model, \"building_count\", 1))\n"
         "    if streetscape_effective(getattr(model, \"streetscape\", \"\"), empties):\n"
         "        return empty_rows(library, MIDRISE_PREFIX)\n"
         "    return empty_rows(library)\n"),
    ],
    "packages/pipeline/empties.py": [
        ("def terrace(rows, extents, stream, roads, span_x):\n",
         "def terrace(rows, extents, stream, roads, span_x, continuous=False):\n"),
        ("    the through road first.\"\"\"\n",
         "    the through road first.\n"
         "\n"
         "    ``continuous`` (0.200.0, factory roadmap 241): the urban street's wall,\n"
         "    with no alley between runs -- one row broken only where a road crosses\n"
         "    the far side. Off, the terrace draws exactly as it did.\"\"\"\n"),
        ("        if in_run >= run_len:\n"
         "            x += ALLEY\n",
         "        if not continuous and in_run >= run_len:\n"
         "            x += ALLEY\n"),
    ],
    "apps/cli/commands/__init__.py": [
        ("    _empty_rows = _bl.empties_for_brief(model) if library else []\n",
         "    _empty_rows = _bl.empties_for_brief(model) if library else []\n"
         "    # THE URBAN STREET (0.200.0, roadmap 241): the mid-rise wall, no alleys.\n"
         "    # Asked with the rule `empties_for_brief` asks, so the rows it drew and the\n"
         "    # wall they stand as cannot disagree.\n"
         "    from packages.core.models import empties_effective as _ee, streetscape_effective as _se\n"
         "    _urban = bool(library) and bool(_se(getattr(model, \"streetscape\", \"\"),\n"
         "                                       _ee(getattr(model, \"empties\", \"across\"), library,\n"
         "                                           getattr(model, \"building_count\", 1))))\n"
         "    if _urban and not _empty_rows:\n"
         "        print(\"  URBAN_WITHOUT_MIDRISES: the brief asks for an urban street and the lot \"\n"
         "              \"library holds no gs_midrise_* Empty -- no wall stands across the street\",\n"
         "              file=sys.stderr)\n"),
        ("        placed_e, need_half = _empties.terrace(\n"
         "            _empty_rows, _ext, site_variation.stream(int(seed) ^ 0x5E3A11),\n"
         "            roads, spec[\"ground\"][\"size_x\"])\n",
         "        placed_e, need_half = _empties.terrace(\n"
         "            _empty_rows, _ext, site_variation.stream(int(seed) ^ 0x5E3A11),\n"
         "            roads, spec[\"ground\"][\"size_x\"], continuous=_urban)\n"),
        ("                  f\"across the street, {len({b['archetype'] for b in blockers})} \"\n"
         "                  f\"shell(s), {'themed' if themed_map else 'greybox'}\")\n",
         "                  f\"across the street{' (an urban wall)' if _urban else ''}, \"\n"
         "                  f\"{len({b['archetype'] for b in blockers})} \"\n"
         "                  f\"shell(s), {'themed' if themed_map else 'greybox'}\")\n"),
    ],
}


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.200.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.200.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.200.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.200.0] - "), entry[:40]
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
    (LF / "VERSION").write_bytes(VERSION + b"\n" if (LF / "VERSION").read_bytes().endswith(b"\n") else VERSION)
    print("Level Factory 0.199.0 -> 0.200.0")


if __name__ == "__main__":
    main()
