"""Lot 0.120.2: the cover fallback is the contract's cell, and the pinch message states the threshold its
check used (factory roadmap 197; found in docs/findings/door_widths/README.md, "Lot carries the refuted
cell").

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of
them matched:
  site_cover.py                 FALLBACK: `_NAV_BAKE_FALLBACK` cell_size_m 0.15 -> 0.1, its comment;
                                `min_passable_gap`'s docstring at the contract's cell
                                MESSAGE: `CoverPlan.passable_gap`; `plan_cover` sets it from the bake
                                it gives `pinches`; `findings` states it, and refuses pinches without it
  tests/test_lot.py             FALLBACK: the pinned gap 1.2 -> 1.0, its docstring; a comment's 1.2 m
  tests/test_site_cover_slots.py  the too-tight lane derived from the clearance the plan uses, not a
                                literal sized at the fallback's 2.7 (the one suite failure the fallback
                                caused); applied with either half, since it holds under both
  tests/test_cover_fallback.py  new, from `lot_cover_fallback/test_cover_fallback.py`
CHANGELOG and VERSION from `lot_cover_fallback/CHANGELOG_0.120.2.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`. `--without=fallback`, `--without=message` or both (with LOT_ROOT, a copy)
withhold that half of the source change, so each new test can be run against the defect it owns.

Read before it was written, in this session: site_cover.py whole (0.120.1); tests/test_lot.py's cover
tests (1276-1425); tests/test_site_cover_slots.py (1-95); lot.py's `_AGENT_DEFAULTS` and `_agent` (46-108) and its `plan_cover` and `findings`
calls (3981-4028); site_surfaces.py's `_agent_radius` (189-201: the radius only, unchanged) and
site_fences.py's docstring (18-22: true at 1.0 m, unchanged); every importer of `site_cover` and what
each reads; deli_counter/agent_contract.json whole and deli_counter/test_agent_contract.py whole;
level_factory/packages/validation/lasertag_contract.py's checks (none reads `nav_bake`). Every file LF.

    python patches/patch_lot_cover_fallback.py --results-pending
    (python -m pytest -q in lot)
    python patches/patch_lot_cover_fallback.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_cover_fallback"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
WITHOUT = set()
for _arg in sys.argv[1:]:
    if _arg.startswith("--without="):
        WITHOUT |= set(_arg.split("=", 1)[1].split(","))
RESULTS = {"RESULT_REPLAY": "result_replay.txt", "RESULT_PLANS": "result_plans.txt",
           "RESULT_FAILS": "result_fails.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.120.1", b"Lot 0.120.2"
CHANGELOG_HEAD = "## 0.120.1 - a storm inlet keeps clear of the paint: none stands in a crosswalk\n"
SHA = {"site_cover.py": "4e441513822161b7", "tests/test_lot.py": "e36cab364ec13ab8",
       "tests/test_site_cover_slots.py": "ec664cdd39aadd89"}
NEW_TEST = "tests/test_cover_fallback.py"

FALLBACK = [
    # the value, and what its comment claimed
    ("#: Ratified fallbacks, equal to `deli_counter/agent_contract.json`'s\n"
     "#: ``nav_bake``. Same rule as every other consumer of that contract: carry the\n"
     "#: values so a missing file degrades instead of breaking, and let Level\n"
     "#: Factory's `lasertag_contract` report drift.\n"
     "_NAV_BAKE_FALLBACK = {\"agent_radius_m\": 0.4, \"cell_size_m\": 0.15}\n",
     "#: Ratified fallbacks, equal to `deli_counter/agent_contract.json`'s\n"
     "#: ``nav_bake``. Same rule as every other consumer of that contract: carry the\n"
     "#: values so a missing file degrades instead of breaking.\n"
     "#:\n"
     "#: WAS cell_size_m 0.15 (to Lot 0.120.1). That was the contract's cell on the\n"
     "#: day this was written, 2026-07-27; on 2026-07-29 the contract moved to 0.1\n"
     "#: and its own ``cell_size_derivation`` records why -- 0.15 capped the\n"
     "#: connected slope at 45 deg against a stated 55, and eight path proofs failed\n"
     "#: as disjoint islands. `lot._AGENT_DEFAULTS` was refreshed the next day and\n"
     "#: this copy was not. This comment said Level Factory's `lasertag_contract`\n"
     "#: would \"report drift\"; it checks the opening range and the sight heights\n"
     "#: and never reads ``nav_bake``, so nothing compared the two.\n"
     "#: `tests/test_cover_fallback.py` does now.\n"
     "_NAV_BAKE_FALLBACK = {\"agent_radius_m\": 0.4, \"cell_size_m\": 0.1}\n"),
    # the derivation, at the contract's cell
    ("    Navmesh erosion removes whole voxels per side, `ceil(radius/cell)` of them,\n"
     "    so a gap is either wide enough after erosion or it is not there at all.\n"
     "    At the ratified 0.4 m radius and 0.15 m cells that is 1.2 m, which is why\n"
     "    the ratified door is 1.25.\n",
     "    Navmesh erosion removes whole voxels per side, `ceil(radius/cell)` of them,\n"
     "    so a gap is either wide enough after erosion or it is not there at all.\n"
     "    At the contract's 0.4 m radius and 0.1 m cells that is 1.0 m.\n"
     "\n"
     "    THIS SAID \"0.15 m cells ... 1.2 m, which is why the ratified door is 1.25\"\n"
     "    to Lot 0.120.1. 0.15 is the cell the contract refuted (see\n"
     "    `_NAV_BAKE_FALLBACK`). Its ``clearances.derivation`` still evaluates the\n"
     "    formula there, and whether the door follows the bake is a question for\n"
     "    the factory's roadmap 197, not for this module.\n"),
]

MESSAGE = [
    # the threshold, carried on the plan
    ("    pinches: list = field(default_factory=list)\n"
     "    #: Stretches of the crew's route left inside an enemy's reach with nothing\n",
     "    pinches: list = field(default_factory=list)\n"
     "    #: The width those gaps were measured against: `min_passable_gap` of the\n"
     "    #: bake `plan_cover` gave `pinches`, so `findings` states the number the\n"
     "    #: read-back used (0.120.2). It stated `min_passable_gap()` -- no bake --\n"
     "    #: and said 1.2 m above a check made at the contract's 1.0 m. None on a\n"
     "    #: plan `plan_cover` did not make, which has no measurement to state.\n"
     "    passable_gap: float = None\n"
     "    #: Stretches of the crew's route left inside an enemy's reach with nothing\n"),
    # derived once, from the bake the read-back is given
    ("    plan = CoverPlan()\n"
     "    # Derived from the agent contract unless a caller overrides it, so the room\n",
     "    plan = CoverPlan()\n"
     "    # The narrowest lane, from the bake `pinches` is given at the end: the\n"
     "    # number `findings` states is the one the read-back measured against.\n"
     "    plan.passable_gap = min_passable_gap(nav_bake)\n"
     "    # Derived from the agent contract unless a caller overrides it, so the room\n"),
    # stated, never the fallback's
    ("    if plan.pinches:\n"
     "        worst = min(gap for _n, _w, gap in plan.pinches)\n",
     "    if plan.pinches:\n"
     "        # THE NUMBER THE CHECK USED (0.120.2), never the fallback's: a plan\n"
     "        # that does not carry it has no measurement to state.\n"
     "        if plan.passable_gap is None:\n"
     "            raise ValueError(\"CoverPlan.pinches without the passable_gap they were \"\n"
     "                             \"measured against; plan_cover sets both\")\n"
     "        worst = min(gap for _n, _w, gap in plan.pinches)\n"),
    ("                f\"cover to less than the {min_passable_gap():g} m an agent can \"\n",
     "                f\"cover to less than the {plan.passable_gap:g} m an agent can \"\n"),
]

TEST_LOT = [
    ("def test_passable_gap_is_the_agent_contracts_own_derivation():\n"
     "    \"\"\"Not a chosen number. `AGENT_CONTRACT.md` derives min door width as\n"
     "    `2*ceil(agent_radius/cell_size)*cell_size + 2*cell_size` because navmesh\n"
     "    erosion removes whole voxels per side — at the ratified 0.4 m radius and\n"
     "    0.15 m cells that is 1.2 m, which is why the ratified door is 1.25. A cover\n"
     "    piece beside a wall is a doorway made of street furniture and nothing was\n"
     "    applying the rule to it.\"\"\"\n"
     "    import site_cover as sc\n"
     "    assert abs(sc.min_passable_gap() - 1.2) < 1e-9\n",
     "def test_passable_gap_is_the_agent_contracts_own_derivation():\n"
     "    \"\"\"Not a chosen number. `AGENT_CONTRACT.md` derives min door width as\n"
     "    `2*ceil(agent_radius/cell_size)*cell_size + 2*cell_size` because navmesh\n"
     "    erosion removes whole voxels per side — at the contract's 0.4 m radius and\n"
     "    0.1 m cells that is 1.0 m. A cover piece beside a wall is a doorway made of\n"
     "    street furniture and nothing was applying the rule to it.\n"
     "\n"
     "    This pinned 1.2 to Lot 0.120.1 -- \"0.15 m cells ... which is why the\n"
     "    ratified door is 1.25\" -- the fallback's cell, which the contract refuted\n"
     "    on 2026-07-29 (`tests/test_cover_fallback.py`).\"\"\"\n"
     "    import site_cover as sc\n"
     "    assert abs(sc.min_passable_gap() - 1.0) < 1e-9\n"),
    ("    # 0.8 m of lane to the east wall — under the 1.2 m the bake can carry.\n",
     "    # 0.8 m of lane to the east wall — under the 1.0 m the bake can carry.\n"),
]

TEST_SLOTS = [
    ("def test_a_lane_too_tight_for_a_truck_gets_a_car():\n"
     "    \"\"\"Two building footprints leave a 9 m lane across the line: a 6 m truck\n"
     "    turned across it needs its footprint plus clearance either side and is\n"
     "    refused; the 4.3 m car fits.\"\"\"\n"
     "    clear = site_cover.building_clearance(3.0)\n"
     "    lane = 11.0        # 4.3 + 2 x 2.7 fits; 6.0 + 2 x 2.7 does not\n",
     "def test_a_lane_too_tight_for_a_truck_gets_a_car():\n"
     "    \"\"\"Two building footprints leave a lane across the line: a 6 m truck\n"
     "    turned across it needs its length plus the clearance either side and is\n"
     "    refused; the 4.3 m car fits.\n"
     "\n"
     "    The lane is derived from the clearance the plan uses. It was a literal\n"
     "    11.0, \"4.3 + 2 x 2.7 fits; 6.0 + 2 x 2.7 does not\", sized at the\n"
     "    fallback's refuted 0.15 m cell: at the contract's 2.5 (Lot 0.120.2) a\n"
     "    truck needs exactly 11.0, and stood in it.\"\"\"\n"
     "    clear = site_cover.building_clearance(3.0)\n"
     "    need = {name: depth for name, _w, depth, _h in site_cover.COVER_SPECIES}\n"
     "    # midway between what the car needs across the lane and what the truck does\n"
     "    lane = (need[\"simple_car\"] + need[\"box_truck\"]) / 2.0 + 2.0 * clear\n"),
]


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (LOT / "VERSION").read_bytes().strip() == VERSION, (LOT / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.120.2.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.120.2: results filled")


def main():
    if FILL:
        return fill()
    if WITHOUT - {"fallback", "message"}:
        sys.exit(f"refusing: --without takes fallback and message, not {sorted(WITHOUT)}")
    if WITHOUT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --without is for a LOT_ROOT copy, never the repo")
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.120.2.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## 0.120.2 - "), entry[:40]
    left = entry
    for key in RESULTS if (PENDING or WITHOUT) else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    edits = {"site_cover.py": ([] if "fallback" in WITHOUT else FALLBACK)
                              + ([] if "message" in WITHOUT else MESSAGE),
             "tests/test_lot.py": [] if "fallback" in WITHOUT else TEST_LOT,
             "tests/test_site_cover_slots.py": TEST_SLOTS}
    writes = {}
    for rel, pairs in edits.items():
        p = LOT / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    new_test = LOT / NEW_TEST
    assert not new_test.exists(), (NEW_TEST, "exists")
    test_raw = (SRC / "test_cover_fallback.py").read_bytes()
    assert b"\r\n" not in test_raw, "the new test is CRLF"
    writes[new_test] = test_raw
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.120.1 -> 0.120.2" + (f" (WITHOUT {','.join(sorted(WITHOUT))}, a copy)" if WITHOUT else ""))


if __name__ == "__main__":
    main()
