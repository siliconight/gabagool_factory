"""Lot 0.123.0: an urban street plants a city block's trees -- one every 30 ft (factory roadmap 241).

Lot planted a tree halfway between lamps 25 m apart, a Delco strip's spacing; Philadelphia's own siting guidelines
(PHS / TreeVitalize, 2010; `docs/reference/STREET_TREES.md`) say 15 to 30 ft between trees and 30 ft from a corner.

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  site_furniture.py   `URBAN_TREE_SPACING`, `URBAN_TREE_CORNER`; `urban_tree_stations`; `plan_furniture(...,
                      urban=False)` plants by them when asked, the strip's lamp stations collected exactly as the
                      loop computed them
  lot.py              `assemble` asks `site_spec["streetscape"] == "urban"`
  site_spawns.py      LOT_DESTINATION_ABOVE_FLOOR's message: the refuted "Laser Tag cannot path to it either way"
                      (the factory's roadmap 245) gives way to the walk test answering it (carried, the walker's
                      call of 2026-10-13 for such fixes: no release of its own)
  tests/test_urban_street_trees.py   NEW (`lot_urban_street_trees/test_urban_street_trees.py.txt`)
CHANGELOG and VERSION from `lot_urban_street_trees/CHANGELOG_0.123.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`.

Read before it was written, in this session: `site_furniture.py`'s header, the spacing constants, `SPECIES` and
`FOOTPRINT` (a tree's grate, 1.2 m, is what `_free` reads), `_piece` (t to 3 places), `_bus_stop`, `plan_furniture`
(the species per road, the controls, the per-kerb tree loop, the per-cut pieces, the bus stop, the pole line);
`site_poles` (`POLE_INSET`, `POLE_SPAN`, `POLE_STEPS`, `_room` reading a tree's crown, `stations`, `plan_line`,
`_pole`); `site_streets.Cut` (t, span, kind road/path/driveway); `lot.py`'s one `plan_furniture` call;
`site_spawns.seat_destinations`' two messages (LOT_DESTINATION_ON_PROP's claim stands under Laser Tag 0.32.0, so
it is left); `tests/test_lane_lamps.py`'s block, reused. Every file LF.

    python patches/patch_lot_urban_street_trees.py --results-pending
    (python -m pytest -q in lot; lot_replay.py replay lot0123 + diff lot0122 lot0123)
    python patches/patch_lot_urban_street_trees.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_urban_street_trees"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_COUNTS": "result_counts.txt", "RESULT_REPLAY": "result_replay.txt",
           "RESULT_FAILING": "result_failing.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Lot 0.122.0", b"Lot 0.123.0"
CHANGELOG_HEAD = ("## 0.122.0 - a row the fences leave open shuts nothing: enemies may stand behind the urban "
                  "street's near side")
SHA = {"site_furniture.py": "810945760dc15704", "lot.py": "cffe9871d2762a29", "site_spawns.py": "05739c655a2b48f9"}
NEW = {"tests/test_urban_street_trees.py": "test_urban_street_trees.py.txt"}

CONST_OLD = "TREE_OFFSET = LAMP_SPACING / 2.0    # a tree halfway between two lamps\n"
CONST_NEW = (CONST_OLD +
             "#: AN URBAN STREET'S TREES (0.123.0, factory roadmap 241): Philadelphia's own\n"
             "#: siting guidelines -- PHS / TreeVitalize, \"Property Owner Request to Plant a\n"
             "#: Street Tree in Philadelphia\", 2010, read at source in the factory root's\n"
             "#: `docs/reference/STREET_TREES.md` -- say 15 to 30 ft between trees by mature\n"
             "#: size, and the five species here are shade trees, so 30 ft; and 30 ft from a\n"
             "#: street corner. A strip keeps the lamps' stations (`TREE_OFFSET`).\n"
             "URBAN_TREE_SPACING = 30 * 0.3048\n"
             "URBAN_TREE_CORNER = 30 * 0.3048\n")

SIG_OLD = ("def plan_furniture(roads_list, buildings=(), markers=(), findings=None,\n"
           "                   sign_bands=(), keep_out=()) -> list:\n")
SIG_NEW = (
    "def urban_tree_stations(road, kerb) -> list:\n"
    "    \"\"\"An urban street's tree stations along one band, metres along the road\n"
    "    (0.123.0, factory roadmap 241).\n"
    "\n"
    "    The band is split at its ROAD crossings; each run is kept `URBAN_TREE_CORNER`\n"
    "    clear of a crossing's dropped kerb and `LAMP_START` of the road's ends, then\n"
    "    planted every `URBAN_TREE_SPACING` with the row centred in the run, so a\n"
    "    block's trees stand evenly from corner to corner. A run shorter than the\n"
    "    spacing holds one tree at its middle. Paths and driveways do not split a run:\n"
    "    a tree steps clear of them where it stands (`_nudged`). Pure.\"\"\"\n"
    "    lo, hi = LAMP_START, road.length - LAMP_START\n"
    "    corners = sorted((c.t - c.span / 2.0, c.t + c.span / 2.0) for c in kerb.cuts if c.kind == \"road\")\n"
    "    runs, a = [], lo\n"
    "    for c0, c1 in corners:\n"
    "        if c0 - URBAN_TREE_CORNER > a:\n"
    "            runs.append((a, c0 - URBAN_TREE_CORNER))\n"
    "        a = max(a, c1 + URBAN_TREE_CORNER)\n"
    "    if hi > a:\n"
    "        runs.append((a, hi))\n"
    "    out = []\n"
    "    for a, b in runs:\n"
    "        k = int(math.floor((b - a) / URBAN_TREE_SPACING + 1e-9))\n"
    "        start = a + ((b - a) - k * URBAN_TREE_SPACING) / 2.0\n"
    "        out += [start + i * URBAN_TREE_SPACING for i in range(k + 1)]\n"
    "    return out\n"
    "\n"
    "\n"
    "def plan_furniture(roads_list, buildings=(), markers=(), findings=None,\n"
    "                   sign_bands=(), keep_out=(), urban=False) -> list:\n")

DOC_OLD = ("    a lane's lamp keeps clear of (`plan_lane_lamps`). Returns the list; the\n"
           "    caller extends the spec and the slots.\"\"\"\n")
DOC_NEW = ("    a lane's lamp keeps clear of (`plan_lane_lamps`). ``urban`` (0.123.0) plants\n"
           "    a city block's trees (`urban_tree_stations`) in place of the lamps'\n"
           "    stations. Returns the list; the caller extends the spec and the slots.\"\"\"\n")

LOOP_OLD = ("            # a tree halfway between two of the lamps' stations, skipping the\n"
            "            # cuts and kept out of the shop bands facing this kerb (0.106.0)\n"
            "            spans = _sign_spans(road, kerb, sign_bands, roads_list)\n"
            "            t = LAMP_START\n"
            "            while t < road.length - LAMP_START:\n"
            "                tt = t + TREE_OFFSET\n"
            "                gw, gd = FOOTPRINT[species_tree]\n"
            "                if tt < road.length - LAMP_START:\n"
            "                    tree = _nudged(lambda s: _piece(f\"Tree_{n}\", species_tree, road, kerb, s, tree_off),\n"
            "                                   tt, gw / 2.0, kerb, placed, markers, avoid=spans)\n"
            "                    if spans and not _clear_of_spans(tt, gw / 2.0, spans) and _clear_of_cuts(tt, gw / 2.0, kerb):\n"
            "                        kept_clear.append((f\"Tree_{n}\", tt, tree[\"t\"] if tree else None))\n"
            "                    if tree:\n"
            "                        placed.append(tree)\n"
            "                        n += 1\n"
            "                t += LAMP_SPACING\n")
LOOP_NEW = ("            # a tree halfway between two of the lamps' stations, skipping the\n"
            "            # cuts and kept out of the shop bands facing this kerb (0.106.0);\n"
            "            # AN URBAN STREET plants a city block's (0.123.0, factory roadmap\n"
            "            # 241): every `URBAN_TREE_SPACING`, 30 ft clear of a corner\n"
            "            # (`urban_tree_stations`), each stepping clear as a strip's does\n"
            "            spans = _sign_spans(road, kerb, sign_bands, roads_list)\n"
            "            gw, gd = FOOTPRINT[species_tree]\n"
            "            if urban:\n"
            "                stations = urban_tree_stations(road, kerb)\n"
            "            else:\n"
            "                stations = []\n"
            "                t = LAMP_START\n"
            "                while t < road.length - LAMP_START:\n"
            "                    if t + TREE_OFFSET < road.length - LAMP_START:\n"
            "                        stations.append(t + TREE_OFFSET)\n"
            "                    t += LAMP_SPACING\n"
            "            for tt in stations:\n"
            "                tree = _nudged(lambda s: _piece(f\"Tree_{n}\", species_tree, road, kerb, s, tree_off),\n"
            "                               tt, gw / 2.0, kerb, placed, markers, avoid=spans)\n"
            "                if spans and not _clear_of_spans(tt, gw / 2.0, spans) and _clear_of_cuts(tt, gw / 2.0, kerb):\n"
            "                    kept_clear.append((f\"Tree_{n}\", tt, tree[\"t\"] if tree else None))\n"
            "                if tree:\n"
            "                    placed.append(tree)\n"
            "                    n += 1\n")

CALL_OLD = ("                                              + _field_rects)\n"
            "    site_spec.setdefault(\"cover\", []).extend(furniture)\n")
CALL_NEW = ("                                              + _field_rects,\n"
            "                                              urban=site_spec.get(\"streetscape\") == \"urban\")\n"
            "    site_spec.setdefault(\"cover\", []).extend(furniture)\n")

MSG_OLD = ("                    f\"reaches it; if it is a prop, the marker's z is wrong. \"\n"
           "                    f\"Laser Tag cannot path to it either way and reports \"\n"
           "                    f\"TRAVERSAL with 0% completion.\"),\n")
MSG_NEW = ("                    f\"reaches it; if it is a prop, the marker's z is wrong. \"\n"
           "                    f\"Lot cannot tell which offline; the walk test answers \"\n"
           "                    f\"it, walking a crew body to the objective (the factory's \"\n"
           "                    f\"roadmap 245: walked to on 95 of the 96 candidates \"\n"
           "                    f\"that carried this).\"),\n")

EDITS = {
    "site_furniture.py": [(CONST_OLD, CONST_NEW), (SIG_OLD, SIG_NEW), (DOC_OLD, DOC_NEW), (LOOP_OLD, LOOP_NEW)],
    "lot.py": [(CALL_OLD, CALL_NEW)],
    "site_spawns.py": [(MSG_OLD, MSG_NEW)],
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
    for path, rel in [(LOT / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.123.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lot 0.123.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.123.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## 0.123.0 - "), entry[:40]
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
    print("Lot 0.122.0 -> 0.123.0")


if __name__ == "__main__":
    main()
