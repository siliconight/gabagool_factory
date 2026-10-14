"""Level Factory 0.201.0: the urban street's near side -- the mission's buildings stand among mid-rises (factory roadmap
241, the second cut).

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  packages/pipeline/empties.py      NEAR_PASSAGE, building_rect, _near_side, _road_band, _hits, infill -- after
                                    `terrace` (`lf_urban_near_side/empties_near.py.txt`)
  apps/cli/commands/__init__.py     for an urban brief: the near infill after the far terrace, both sides as
                                    blockers, the plate grown for whichever side reaches further, the count said;
                                    a strip brief runs none of it
  tests/unit/test_urban_near_side.py   NEW (`lf_urban_near_side/test_urban_near_side.py.txt`)
CHANGELOG and VERSION from `lf_urban_near_side/CHANGELOG_0.201.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`.

Read before it was written, in this session: `empties.py` as 0.200.0 left it (`_turned`, `_far_side`,
`_blocked`, `_deal`, `terrace`); the compose stage's building entries (`at`, `rot`), `fp_list` in both the
library and the shell branch, `roads_for`, and the terrace block (`_urban`, `placed_e`, the blockers loop, the
plate's `half_y`, the log line); `road_grammar`'s FRONTAGE, the service lane (LANE_WIDTH, no sidewalk) and
roads as `{"a", "b", "width", "sidewalk"}`; `site_variation.CLEARANCE`; Lot 0.121.0, which keeps its planners
clear of every blocker. Every file LF.

    python patches/patch_lf_urban_near_side.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_urban_near_side.py --fill
    (commit; then a cold run of urban_row_001, recorded in the factory root)
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_urban_near_side"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.200.0", b"0.201.0"
CHANGELOG_HEAD = ("## [0.200.0] - An urban street: the brief asks, and the far side stands a continuous "
                  "mid-rise wall")
SHA = {"packages/pipeline/empties.py": "4649f0a543d64243",
       "apps/cli/commands/__init__.py": "9f1b2f1312e46a1b"}
NEW = {"tests/unit/test_urban_near_side.py": "test_urban_near_side.py.txt"}


def _edits():
    near = (SRC / "empties_near.py.txt").read_text(encoding="utf-8").replace("\r\n", "\n")
    return {
        "packages/pipeline/empties.py": [
            ("    return out, need\n\n\ndef stoop_reach(whole, house):\n",
             "    return out, need\n" + near.rstrip("\n") + "\n\n\ndef stoop_reach(whole, house):\n"),
        ],
        "apps/cli/commands/__init__.py": [
            ("        placed_e, need_half = _empties.terrace(\n"
             "            _empty_rows, _ext, site_variation.stream(int(seed) ^ 0x5E3A11),\n"
             "            roads, spec[\"ground\"][\"size_x\"], continuous=_urban)\n",
             "        placed_e, need_half = _empties.terrace(\n"
             "            _empty_rows, _ext, site_variation.stream(int(seed) ^ 0x5E3A11),\n"
             "            roads, spec[\"ground\"][\"size_x\"], continuous=_urban)\n"
             "        # THE NEAR SIDE (0.201.0, roadmap 241): an urban street fills the near\n"
             "        # frontage between the mission's own buildings, a passage kept beside\n"
             "        # each (`empties.infill`). A strip brief places nothing here.\n"
             "        placed_n, need_north = [], 0.0\n"
             "        if _urban:\n"
             "            _rects_n = [_empties.building_rect(b[\"at\"], b[\"rot\"], fp)\n"
             "                        for b, fp in zip(buildings, fp_list) if fp]\n"
             "            placed_n, need_north = _empties.infill(\n"
             "                _empty_rows, _ext, site_variation.stream(int(seed) ^ 0x2A11E5),\n"
             "                roads, spec[\"ground\"][\"size_x\"], _rects_n)\n"),
            ("        for p in placed_e:\n"
             "            aid = p[\"archetype\"]\n",
             "        for p in placed_e + placed_n:\n"
             "            aid = p[\"archetype\"]\n"),
            ("            half_y = need_half + _empties.CLEARANCE\n",
             "            half_y = max(need_half, need_north) + _empties.CLEARANCE\n"),
            ("            print(f\"[site] {len(blockers)} Empt{'y' if len(blockers) == 1 else 'ies'} \"\n"
             "                  f\"across the street{' (an urban wall)' if _urban else ''}, \"\n",
             "            _near_say = (f\"{len(placed_n)} on the near side between the mission's buildings, \"\n"
             "                         if _urban else \"\")\n"
             "            print(f\"[site] {len(placed_e)} Empt{'y' if len(placed_e) == 1 else 'ies'} \"\n"
             "                  f\"across the street{' (an urban wall)' if _urban else ''}, {_near_say}\"\n"),
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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.201.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.201.0: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.201.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.201.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, edits in _edits().items():
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
    print("Level Factory 0.200.0 -> 0.201.0")


if __name__ == "__main__":
    main()
