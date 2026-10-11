"""Zoo 1.102.0: what a roof carries follows what the building is, and fewer (the walker, 2026-10-11).

Anchored edits in `zoo_keeper/core/roofprops.py`: `ROOF_PROFILES` (a building id's words -> kitchen,
shop, office, big_box, home or none; first row whose word is a token of the id wins, a name no row
claims is a shop), `PROFILE_COUNTS` (per profile, each species' count drawn per roof in [lo, hi],
seeded by the building, so no two roofs match), `profile_of`; `scatter` reads them where it read the
area formula, a `none` roof carries nothing, the water tank keeps its formula and its 12 m rule, and
the plan records its `profile`. `tests/test_roofprops.py` replaced from
`zoo_roof_profiles/test_roofprops.py.txt` (run against 1.101.0 first). Each file pinned by hash and
each anchor asserted once, nothing written on a miss; the files' own line endings kept. Applies on
Zoo 1.101.0. CHANGELOG and VERSION from `zoo_roof_profiles/CHANGELOG_1.102.0.md`;
`--results-pending` leaves the RESULT_ keys to `--fill`.

    python patches/patch_zoo_roof_profiles.py --results-pending && cd zoo && python -m pytest -q
    python patches/patch_zoo_roof_profiles.py --fill
    ZOO_ROOT=<copy> python patches/patch_zoo_roof_profiles.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_roof_profiles"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt", "RESULT_LIBRARY": "result_library.txt"}
VERSION_WAS, VERSION = b"1.101.0", b"1.102.0"
CHANGELOG_HEAD = ("## [1.101.0] - a roof's props keep off its hatches and landings, stand in the box "
                  "they occupy, and draw as one roof\n")
ROOF = "zoo_keeper/core/roofprops.py"
TEST = "tests/test_roofprops.py"
SHA = {ROOF: "b9e796523487fd07", TEST: "4b2df7fb92856a3e"}

R_DOC_OLD = ("one-storey roof is on street pressure, so one is planned only on a roof\n"
             "``TANK_MIN_ROOF_M`` or more above the plan.\n"
             "\"\"\"\n")
R_DOC_NEW = ("one-storey roof is on street pressure, so one is planned only on a roof\n"
             "``TANK_MIN_ROOF_M`` or more above the plan.\n"
             "\n"
             "WHAT A ROOF CARRIES FOLLOWS THE BUILDING (1.102.0). The walker, on cold run\n"
             "9245's roofs -- every one carrying the same 17 props, because the area\n"
             "formula saturated every cap on any roof over about 300 m2 -- chose \"by\n"
             "building, fewer\": a deli or a shop gets a unit or two, a vent and a fan,\n"
             "warehouses and markets get more and the skylights, seeded so no two roofs\n"
             "match. `ROOF_PROFILES` reads the building's use off its id's words (first\n"
             "row whose word is a TOKEN of the id wins -- `barber` is not `bar`), and\n"
             "`PROFILE_COUNTS` draws each species' count per roof inside its range. The\n"
             "water tank keeps its formula and its height rule, which the walker kept.\n"
             "\"\"\"\n")
R_IMP_OLD = "import math\n\nfrom . import genome as genome_mod\n"
R_IMP_NEW = "import math\nimport re\n\nfrom . import genome as genome_mod\n"
R_TAB_OLD = ("_CLEARANCE = 0.35     # metres between prop AABBs\n"
             "_ATTEMPTS = 24        # rejection-sampling tries per prop\n")
R_TAB_NEW = ("_CLEARANCE = 0.35     # metres between prop AABBs\n"
             "_ATTEMPTS = 24        # rejection-sampling tries per prop\n"
             "\n"
             "#: A building's use, read off its id's words (1.102.0): the first row with a\n"
             "#: word that is a TOKEN of the id wins, so the specific stands before the\n"
             "#: general and `barber` never reads as `bar`; a name no row claims is a shop.\n"
             "#: Checked against every id in Deli Counter's library on 2026-10-11: 12\n"
             "#: kitchens, 35 shops, 28 offices, 43 big boxes, 21 homes, 6 with nothing.\n"
             "ROOF_PROFILES = (\n"
             "    # a parking deck is parked on, and a construction site is not finished\n"
             "    ((\"parking\", \"construction\"), \"none\"),\n"
             "    ((\"warehouse\", \"market\", \"supermarket\", \"depot\", \"freight\", \"factory\",\n"
             "      \"foundry\", \"storage\", \"terminal\", \"yard\", \"brewery\", \"arena\",\n"
             "      \"stadium\", \"airport\", \"rail\", \"hall\"), \"big_box\"),\n"
             "    ((\"deli\", \"diner\", \"pizza\", \"restaurant\", \"tavern\", \"bar\", \"club\",\n"
             "      \"cafe\"), \"kitchen\"),\n"
             "    ((\"office\", \"bank\", \"credit\", \"courthouse\", \"clinic\", \"hospital\",\n"
             "      \"museum\", \"police\", \"funeral\", \"casino\", \"hotel\", \"school\"), \"office\"),\n"
             "    ((\"rowhouse\", \"rowhome\", \"twin\", \"apartment\", \"walkup\", \"home\",\n"
             "      \"house\", \"mansion\"), \"home\"),\n"
             ")\n"
             "DEFAULT_PROFILE = \"shop\"\n"
             "\n"
             "#: Per profile, each species' count is drawn per roof in [lo, hi] -- seeded\n"
             "#: by the building, so no two roofs match -- then placed as before; a species\n"
             "#: the roof is too small for is still skipped. A kitchen's fan is its hood's.\n"
             "#: About a third of 1.101.0's 17 on a small commercial roof.\n"
             "PROFILE_COUNTS = {\n"
             "    \"kitchen\": {\"hvac_unit\": (1, 2), \"vent_stack\": (1, 1),\n"
             "                \"exhaust_fan\": (1, 2), \"satellite_dish\": (0, 1)},\n"
             "    \"shop\":    {\"hvac_unit\": (1, 2), \"vent_stack\": (1, 1),\n"
             "                \"exhaust_fan\": (0, 1), \"satellite_dish\": (0, 1)},\n"
             "    \"office\":  {\"hvac_unit\": (2, 3), \"vent_stack\": (1, 2),\n"
             "                \"exhaust_fan\": (0, 1), \"satellite_dish\": (0, 1)},\n"
             "    \"big_box\": {\"hvac_unit\": (2, 4), \"vent_stack\": (2, 4),\n"
             "                \"exhaust_fan\": (1, 2), \"skylight\": (2, 4),\n"
             "                \"satellite_dish\": (0, 1)},\n"
             "    \"home\":    {\"vent_stack\": (1, 2), \"satellite_dish\": (0, 1)},\n"
             "    \"none\":    {},\n"
             "}\n"
             "\n"
             "\n"
             "def profile_of(building_id) -> str:\n"
             "    \"\"\"The roof profile of a building, by its id's words (`ROOF_PROFILES`).\"\"\"\n"
             "    tokens = {t for t in re.split(r\"[^a-z]+\", str(building_id or \"\").lower()) if t}\n"
             "    for words, profile in ROOF_PROFILES:\n"
             "        if tokens & set(words):\n"
             "            return profile\n"
             "    return DEFAULT_PROFILE\n")
R_SDOC_OLD = ("    coords (1.101.0) -- and ``seed_offset``. ``forbidden`` counts the rects\n"
              "    each roof kept its props off.\n"
              "    \"\"\"\n")
R_SDOC_NEW = ("    coords (1.101.0) -- and ``seed_offset``. ``forbidden`` counts the rects\n"
              "    each roof kept its props off; ``profile`` is the building's\n"
              "    (`profile_of`, 1.102.0), which decides each species' count.\n"
              "    \"\"\"\n")
R_INIT_OLD = ("    building = manifest.get(\"building_id\", \"building\")\n"
              "    allowed = set(species) if species else {r[0] for r in _RULES}\n")
R_INIT_NEW = ("    building = manifest.get(\"building_id\", \"building\")\n"
              "    allowed = set(species) if species else {r[0] for r in _RULES}\n"
              "    profile = profile_of(building)\n"
              "    ranges = PROFILE_COUNTS[profile]\n")
R_WANT_OLD = "            want = min(cap, int(round((base + area * per_m2) * density)))\n"
R_WANT_NEW = ("            if profile == \"none\":\n"
              "                continue   # a deck or a site: nothing stands on it\n"
              "            if name == \"water_tank\":\n"
              "                # the tank keeps its formula and its height rule above\n"
              "                want = min(cap, int(round((base + area * per_m2) * density)))\n"
              "            else:\n"
              "                lo, hi = ranges.get(name, (0, 0))\n"
              "                if hi < 1:\n"
              "                    continue\n"
              "                count_rng = seeding.RNGStreams(seeding.root_key(\n"
              "                    building, name, seed, slot[\"slot_id\"])).stream(\"count\")\n"
              "                want = int(round(count_rng.randint(lo, hi) * density))\n")
R_RET_OLD = ("            # how many rects each roof kept its props off (1.101.0)\n"
             "            \"forbidden\": forbidden_by_slot}\n")
R_RET_NEW = ("            # how many rects each roof kept its props off (1.101.0)\n"
             "            \"forbidden\": forbidden_by_slot,\n"
             "            # what the building is, which decided the counts (1.102.0)\n"
             "            \"profile\": profile}\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = ZOO / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION, (ZOO / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(ZOO / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_1.102.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Zoo 1.102.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    assert (ZOO / "VERSION").read_bytes().strip() == VERSION_WAS, (ZOO / "VERSION").read_bytes()
    entry = _src("CHANGELOG_1.102.0.md")
    assert entry.startswith("## [1.102.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    test_text = _src("test_roofprops.py.txt")
    assert "test_the_profile_follows_the_building_s_words" in test_text

    rp, r_eol, roof = _read(ROOF)
    assert "ROOF_PROFILES" not in roof, "already applied"
    roof = _once(roof, R_DOC_OLD, R_DOC_NEW, "the module docstring")
    roof = _once(roof, R_IMP_OLD, R_IMP_NEW, "the imports")
    roof = _once(roof, R_TAB_OLD, R_TAB_NEW, "the tables after _ATTEMPTS")
    roof = _once(roof, R_SDOC_OLD, R_SDOC_NEW, "scatter's docstring")
    roof = _once(roof, R_INIT_OLD, R_INIT_NEW, "scatter's head")
    roof = _once(roof, R_WANT_OLD, R_WANT_NEW, "the count")
    roof = _once(roof, R_RET_OLD, R_RET_NEW, "the return")
    tp, t_eol, _old_tests = _read(TEST)

    cl = ZOO / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:120]
    # every anchor matched: now write
    _write(rp, r_eol, roof)
    _write(tp, t_eol, test_text)
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (ZOO / "VERSION").write_bytes(VERSION)
    print("Zoo 1.101.0 -> 1.102.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
