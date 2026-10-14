"""Lot 0.122.0: a row the fences leave open shuts nothing -- enemies may stand behind the urban street's near side
(factory roadmap 241).

`plan_fences` leaves an Empty row open when a mission marker stands in the band behind it; `place_enemies` kept out
of every row's band all the same. On cold run 9289 the near side's rows (one Empty between the mission's buildings,
a band across the plate's whole width) starved seed_9205 of all six enemies and put seed_9104's six in the street
(`docs/findings/urban_street/spawn_filters.py`, its rerun reproducing each job's enemies).

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  site_fences.py   `markers_behind(band, members, markers)`, the one question; `shut_bands(..., markers=())` leaves
                   out a row with any; `plan_fences` asks it in place of its own copy
  site_spawns.py   `shut_band_rects(..., markers=())` passes them; `place_enemies` passes its spawn, objective and
                   extraction
  site_cover.py    `min_passable_gap`'s docstring: the contract's derivation works at 0.1 m since Deli Counter
                   0.214.0 (carried, the walker's call: "leave it for the next Lot change")
  tests/test_open_rows_are_not_shut.py               NEW (`lot_open_rows/test_open_rows_are_not_shut.py.txt`)
  tests/fixtures/urban_row_001_seed_9205.place_enemies.json   NEW (the probe's dump at the call)
CHANGELOG and VERSION from `lot_open_rows/CHANGELOG_0.122.0.md`; `--results-pending` leaves RESULT_ keys to `--fill`.

Read before it was written, in this session: `site_fences` (`empties`, `rows`, `front_line`, `shut_band`,
`shut_bands`, `plan_fences`, `_say`); `site_spawns` (`solid_rects`, `blocker_rects`, `footprints`,
`footprint_rect`, `shut_band_rects`, `ground_rect`, `outdoors`, `_candidates`, `place_enemies`); `lot.assemble`'s
calls of both (`cover_points`: the three mission points and the placed enemies, handed to `plan_fences`);
`tests/test_spawns_keep_out_of_empties.py`, whose source check still holds; `site_cover.py` 108-122; the agent
contract's `clearances.derivation`. Every file LF.

    python patches/patch_lot_open_rows.py --results-pending
    (python -m pytest -q in lot; lot_replay.py replay lot0122 + diff after lot0122; spawn_filters.py on 9289)
    python patches/patch_lot_open_rows.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_open_rows"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_PROBE": "result_probe.txt", "RESULT_REPLAY": "result_replay.txt",
           "RESULT_FAILING": "result_failing.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.121.0", b"Lot 0.122.0"
CHANGELOG_HEAD = "## 0.121.0 - every planner that keeps clear of what stands keeps clear of the Empties"
SHA = {"site_fences.py": "8856122d67eccc00", "site_spawns.py": "698562f431790261",
       "site_cover.py": "8a792099555329f0"}
NEW = {"tests/test_open_rows_are_not_shut.py": "test_open_rows_are_not_shut.py.txt",
       "tests/fixtures/urban_row_001_seed_9205.place_enemies.json": "urban_row_001_seed_9205.place_enemies.json"}

SHUT_BANDS_OLD = (
    "def shut_bands(site_spec, roads_list, ground) -> list:\n"
    "    \"\"\"`shut_band` for every Empty row on the site; none without a plate.\"\"\"\n"
    "    if not ground:\n"
    "        return []\n"
    "    out = []\n"
    "    for axis, members in rows(site_spec):\n"
    "        front, sign = front_line(axis, members, roads_list, ground)\n"
    "        out.append(shut_band(axis, front, sign, ground))\n"
    "    return out\n")
SHUT_BANDS_NEW = (
    "def markers_behind(band, members, markers) -> list:\n"
    "    \"\"\"The mission markers a row's band would shut off: inside the band and in\n"
    "    none of the row's own houses.\n"
    "\n"
    "    A row with any is LEFT OPEN. `plan_fences` will not fence it rather than\n"
    "    strand a spawn, objective or enemy nobody can reach, and a row left open\n"
    "    shuts nothing, so `shut_bands` leaves its band out (0.122.0). One\n"
    "    question, asked by both.\n"
    "    \"\"\"\n"
    "    houses = [r for _e, r in members]\n"
    "    return [m for m in markers\n"
    "            if band[0] < m[0] < band[2] and band[1] < m[1] < band[3]\n"
    "            and not any(h[0] <= m[0] <= h[2] and h[1] <= m[1] <= h[3] for h in houses)]\n"
    "\n"
    "\n"
    "def shut_bands(site_spec, roads_list, ground, markers=()) -> list:\n"
    "    \"\"\"`shut_band` for every Empty row on the site the fences shut; none\n"
    "    without a plate.\n"
    "\n"
    "    A ROW LEFT OPEN SHUTS NOTHING (0.122.0). `plan_fences` leaves a row open\n"
    "    when a mission marker stands behind it (`markers_behind`), and until\n"
    "    0.122.0 this returned that row's band anyway, so `site_spawns.place_enemies`\n"
    "    kept every enemy out of ground no fence closed. On a strip level that\n"
    "    never happened: of the factory's 276 `lot_assemble` job logs, a row was\n"
    "    left open in 3, all on the urban street's near side, where an Empty\n"
    "    stands between the mission's buildings as a row of its own and its band\n"
    "    runs from its front line to the plate's edge across the plate's whole\n"
    "    width. Cold run 9289 (the factory's\n"
    "    `docs/findings/urban_street/spawn_filters.py`): on seed_9205 that band and\n"
    "    the far row's left only the street, open and inside the opening range,\n"
    "    and all six enemies were dropped; on seed_9104 all six stood in the\n"
    "    street; on seed_9003, whose near row's front was its far side, the band\n"
    "    covered the street and the crew's whole route.\n"
    "\n"
    "    ``markers`` are the mission's points: `place_enemies` passes its spawn,\n"
    "    objective and extraction, and `plan_fences` is handed those and the\n"
    "    enemies placed among them -- which never stand in a band those three\n"
    "    leave shut, so the two answer alike. Without them every row is shut, as\n"
    "    before.\n"
    "    \"\"\"\n"
    "    if not ground:\n"
    "        return []\n"
    "    out = []\n"
    "    for axis, members in rows(site_spec):\n"
    "        front, sign = front_line(axis, members, roads_list, ground)\n"
    "        band = shut_band(axis, front, sign, ground)\n"
    "        if markers_behind(band, members, markers):\n"
    "            continue\n"
    "        out.append(band)\n"
    "    return out\n")

FENCES_OLD = ("            band = shut_band(axis, front, sign, ground)\n"
              "            houses = [r for _e, r in members]\n"
              "            stranded = [m for m in markers\n"
              "                        if band[0] < m[0] < band[2] and band[1] < m[1] < band[3]\n"
              "                        and not any(h[0] <= m[0] <= h[2] and h[1] <= m[1] <= h[3]\n"
              "                                    for h in houses)]\n"
              "            if stranded:\n")
FENCES_NEW = ("            band = shut_band(axis, front, sign, ground)\n"
              "            stranded = markers_behind(band, members, markers)\n"
              "            if stranded:\n")

RECTS_FN_OLD = (
    "def shut_band_rects(site_spec, margin: float = WALL_MARGIN) -> list:\n"
    "    \"\"\"The ground behind every Empty row's front line, grown by ``margin``:\n"
    "    what the row's fences shut off from the street, by the function\n"
    "    `plan_fences` asks (`site_fences.shut_bands`).\"\"\"\n"
    "    import site_extent\n"
    "    import site_fences\n"
    "    import site_streets\n"
    "    ground = site_extent.resolve(site_spec).rect\n"
    "    return [site_extent.grow(b, margin) if margin else b\n"
    "            for b in site_fences.shut_bands(site_spec, site_streets.roads(site_spec), ground)]\n")
RECTS_FN_NEW = (
    "def shut_band_rects(site_spec, margin: float = WALL_MARGIN, markers=()) -> list:\n"
    "    \"\"\"The ground behind every Empty row's front line, grown by ``margin``:\n"
    "    what the row's fences shut off from the street, by the function\n"
    "    `plan_fences` asks (`site_fences.shut_bands`). A row the fences leave\n"
    "    open -- one of ``markers`` behind it -- shuts nothing and is not here\n"
    "    (0.122.0).\"\"\"\n"
    "    import site_extent\n"
    "    import site_fences\n"
    "    import site_streets\n"
    "    ground = site_extent.resolve(site_spec).rect\n"
    "    return [site_extent.grow(b, margin) if margin else b\n"
    "            for b in site_fences.shut_bands(site_spec, site_streets.roads(site_spec), ground,\n"
    "                                            markers=markers)]\n")

PLACE_OLD = "    rects = solid_rects(site_spec) + shut_band_rects(site_spec)\n"
PLACE_NEW = (
    "    #\n"
    "    # NOT BEHIND A ROW THE FENCES SHUT, AND ONLY THEN (0.122.0). The band is\n"
    "    # shut where `plan_fences` fences it, and it leaves a row open when one of\n"
    "    # the mission's points stands behind it -- these three, the points it is\n"
    "    # handed besides the enemies placed here. An urban street's near-side\n"
    "    # Empty is such a row, and its band was the mission's own half of the\n"
    "    # plate or the street: cold run 9289's seed_9205 dropped all six enemies.\n"
    "    mission_points = [tuple(positions[k][:2]) for k in (\"spawn\", \"objective\", \"extraction\")]\n"
    "    rects = solid_rects(site_spec) + shut_band_rects(site_spec, markers=mission_points)\n")

COVER_OLD = ("    `_NAV_BAKE_FALLBACK`). Its ``clearances.derivation`` still evaluates the\n"
             "    formula there, and whether the door follows the bake is a question for\n"
             "    the factory's roadmap 197, not for this module.\n")
COVER_NEW = ("    `_NAV_BAKE_FALLBACK`). The contract's ``clearances.derivation`` was first\n"
             "    worked there; since Deli Counter 0.214.0 it works the formula at the\n"
             "    contract's 0.1 m cell (1.00 m), and the walker kept the door at 1.25 as\n"
             "    the width a walkable door is built to (the factory's roadmap 197).\n")

EDITS = {
    "site_fences.py": [(SHUT_BANDS_OLD, SHUT_BANDS_NEW), (FENCES_OLD, FENCES_NEW)],
    "site_spawns.py": [(RECTS_FN_OLD, RECTS_FN_NEW), (PLACE_OLD, PLACE_NEW)],
    "site_cover.py": [(COVER_OLD, COVER_NEW)],
}


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
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.122.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.122.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.122.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## 0.122.0 - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LOT / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in EDITS.items():
        raw = (LOT / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
            text = text.replace(old, new)
        compile(text, rel, "exec")
        writes[rel] = (text, eol)
    news = {r: (SRC / s).read_bytes().replace(b"\r\n", b"\n") for r, s in NEW.items()}
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, (body, e) in writes.items():
        (LOT / rel).write_bytes(body.encode("utf-8").replace(b"\n", e))
    for r, data in news.items():
        (LOT / r).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.121.0 -> 0.122.0")


if __name__ == "__main__":
    main()
