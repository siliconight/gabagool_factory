"""Level Factory 0.206.1: a spent bag is not a closed run -- `_cornered`'s fill deals afresh before it gives up
(factory roadmap 241, the corner shop).

Cold run 9295's seed_9003 closed its urban wall 12.70 m short of the run's end, where 9294's stopped 3.70 m short,
so its closing corner did not stand at the corner. Traced (`lf_corner_fill/replay_9003.py`, its replay standing the
run's wall block for block): the fill stopped at x 55.50 with 18.70 m to fill before the closing corner's room and
one block left on the bag, `gs_midrise_f` at 19.8 m. 0.206.0's `_cornered` stopped when nothing LEFT ON THE BAG
fit -- the condition `infill` met on the near side and answered in 0.203.0 with a fresh deal behind the remainder.
Measured before this was written (`lf_corner_fill/measure_remainder.py`, 600 walls at the factory's thirteen built
widths): 0.206.0 stopped a median 4.70 m short, 90th percentile 12.70, worst 14.20, and more than the narrowest
design's 6.6 m on 171; the fresh deal a median 0.60 m, 90th 2.60, worst 4.10, and on none.

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  packages/pipeline/empties.py            `_cornered`'s fill: where nothing on the bag fits before the closing
                                          corner's room and some design does, a fresh deal behind the remainder;
                                          without heights, the next dealt that fits, as `infill` takes it
  tests/unit/test_urban_corner_shops.py   one check over the 600 walls, at the built widths; the neighbours'
                                          rule corrected to `_by_height`'s (alike only where no other fits)
CHANGELOG and VERSION from `lf_corner_fill/CHANGELOG_0.206.1.md`; `--results-pending` leaves RESULT_ keys to
`--fill`.

Read before it was written, in this session: `_cornered` as 0.206.0 committed it (e8bd89b), its fill loop and
docstring; `infill`'s fresh deal (`_fitting`, `_deal(...) + bag`); `_by_height`'s fit test; the test file as
0.206.0 installed it. Every file LF.

    python patches/patch_lf_corner_fill.py --results-pending
    (python -m pytest -q in level_factory)
    python patches/patch_lf_corner_fill.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_corner_fill"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_FAILING": "result_failing.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.206.0", b"0.206.1"
CHANGELOG_HEAD = "## [0.206.0] - Corner shops: an urban wall's runs open and close on a corner block\n"
SHA = {"packages/pipeline/empties.py": "94f80f97ec71befa", "tests/unit/test_urban_corner_shops.py": "2a0524046de3f323"}

EMPTIES = [
    ("    Between them the wall is dealt as `terrace` deals it, heights by cause where given, and keeps clear before\n"
     "    the run's end the narrowest closing block's width, so the run can close. The wall's remainder stays where\n"
     "    it always stood, at the run's end. A run no corner block fits is dealt plainly.\"\"\"\n",
     "    Between them the wall is dealt as `terrace` deals it, heights by cause where given, and keeps clear before\n"
     "    the run's end the narrowest closing block's width, so the run can close. Where nothing left on the bag fits\n"
     "    before that room and some design does, a fresh deal goes behind what is left (0.206.1), as `infill`'s\n"
     "    does. The wall's remainder stays where it always stood, at the run's end, less than the narrowest design.\n"
     "    A run no corner block fits is dealt plainly.\"\"\"\n"),
    ("    out, need, prev, bag, cbag = [], 0.0, None, [], []\n"
     "\n"
     "    def place(pick, x):\n",
     "    out, need, prev, bag, cbag = [], 0.0, None, [], []\n"
     "\n"
     "    def fit(bag, x, end):\n"
     "        \"\"\"The index on ``bag`` of the next block to stand at ``x`` before ``end``, or None.\"\"\"\n"
     "        if by_cause:\n"
     "            return _by_height(bag, extents, heights, x, end, float(action), reach, lo, hi, prev)\n"
     "        return next((i for i in range(len(bag) - 1, -1, -1) if x + _width(extents, bag[i][\"id\"]) <= end), None)\n"
     "\n"
     "    def place(pick, x):\n"),
    ("        while True:\n"
     "            if not bag:\n"
     "                bag = _deal(usable, stream, prev)\n"
     "            if by_cause:\n"
     "                i = _by_height(bag, extents, heights, x, end, float(action), reach, lo, hi, prev)\n"
     "            else:\n"
     "                i = len(bag) - 1 if x + _width(extents, bag[-1][\"id\"]) <= end else None\n"
     "            if i is None:\n"
     "                break                                  # nothing on the bag fits before the closing corner\n",
     "        while True:\n"
     "            if not bag:\n"
     "                bag = _deal(usable, stream, prev)\n"
     "            i = fit(bag, x, end)\n"
     "            if i is None and any(x + _width(extents, r[\"id\"]) <= end for r in usable):\n"
     "                # A SPENT BAG IS NOT A CLOSED RUN (0.206.1): nothing left on the bag fits\n"
     "                # and some design does, so a fresh deal goes behind what is left, as\n"
     "                # `infill`'s (0.203.0). Cold run 9295's seed_9003 stopped with 18.70 m\n"
     "                # to fill, one 19.8 m block on the bag, and closed 12.70 m short.\n"
     "                bag = _deal(usable, stream, prev) + bag\n"
     "                i = fit(bag, x, end)\n"
     "            if i is None:\n"
     "                break                                  # no design fits before the closing corner\n"),
]

TEST_TAIL = '''

#: The factory's thirteen designs at their built widths and heights (storeys x 3.1 m plus the parapet, as
#: `street_line.shell_top` reads them), as cold run 9295 stood them: nine mid-rises, the narrowest 6.6 m, and the
#: four corner blocks.
BUILT = {"gs_midrise_a": (15.3, 16.5), "gs_midrise_b": (18.3, 19.8), "gs_midrise_c": (21.3, 22.7),
         "gs_midrise_d": (16.8, 26.2), "gs_midrise_e": (24.3, 32.5), "gs_midrise_f": (19.8, 38.7),
         "gs_midrise_g": (12.3, 19.6), "gs_midrise_h": (10.3, 16.5), "gs_midrise_i": (6.6, 13.2),
         "gs_cornershop_a": (15.3, 19.6), "gs_cornershop_b": (18.3, 26.0), "gs_cornershop_c": (12.3, 16.5),
         "gs_cornershop_d": (16.8, 23.1)}


def test_a_run_closes_within_the_narrowest_design_of_its_end():
    """FAILS ON 0.206.0: its fill stopped when nothing LEFT ON THE BAG fit before the closing corner's room, and
    cold run 9295's seed_9003 closed its wall 12.70 m short of the run's end, one 19.8 m block left on the bag with
    18.70 m to fill (the factory root's `patches/lf_corner_fill/replay_9003.py`). Over these 600 walls -- the three
    candidates' plates, no action and four, seeds 1-40 -- 0.206.0 stopped more than the narrowest design short on
    171; with a fresh deal behind the remainder, as `infill`'s, on none, the worst 4.10 m."""
    ext = {k: (-w / 2.0, w / 2.0, -7.65, 7.65) for k, (w, _t) in BUILT.items()}
    tops = {k: t for k, (_w, t) in BUILT.items()}
    rows = [{"id": k, "family": "corner" if k.startswith("gs_cornershop_") else "empty"} for k in BUILT]
    narrowest = min(w for k, (w, _t) in BUILT.items() if not k.startswith("gs_cornershop_"))
    for span in (171, 173, 181):
        through = {"a": [-span / 2.0, -21.665], "b": [span / 2.0, -21.665], "width": 10.0, "sidewalk": 3.0}
        for action in (None, -2.5, -28.5, -27.0, 30.0):
            for seed in range(1, 41):
                placed, _ = empties.terrace(rows, ext, site_variation.stream(seed), [through], float(span),
                                            continuous=True, action=action,
                                            heights=tops if action is not None else None)
                short = span / 2.0 - empties.CLEARANCE - (placed[-1]["at"][0] + placed[-1]["size_x"] / 2.0)
                assert placed[0]["archetype"].startswith("gs_cornershop_"), (span, action, seed)
                assert placed[-1]["archetype"].startswith("gs_cornershop_"), (span, action, seed)
                assert short < narrowest, (span, action, seed, round(short, 2))
'''

RULE = [
    ("def test_the_wall_s_own_rule_still_holds_between_the_corners():\n"
     "    \"\"\"Every mid-rise design stands, and no two neighbours are alike, as 0.204.0's wall.\"\"\"\n"
     "    for seed, action in WALLS:\n"
     "        placed = _wall(seed, action)\n"
     "        assert {p[\"archetype\"] for p in placed[1:-1]} == set(EXT), (seed, action)\n"
     "        for a, b in zip(placed, placed[1:]):\n"
     "            assert a[\"archetype\"] != b[\"archetype\"], (seed, action, a, b)\n",
     "def test_the_wall_s_own_rule_still_holds_between_the_corners():\n"
     "    \"\"\"Every mid-rise design stands, and no two neighbours are alike while another design fits: `_by_height`'s\n"
     "    rule, and `infill`'s. CORRECTED (0.206.1): this asserted no two neighbours alike at all, which 0.206.0 met by\n"
     "    stopping short of its corner instead. With the fresh deal a room only the block just placed fits takes it\n"
     "    again (on these walls, seed 2 with the action at x 55 stands `a` at x 47.5 and 62.5); on the factory's\n"
     "    thirteen built widths, 20 of 600 walls stand a narrow block beside itself, every one where no other design\n"
     "    fits (the factory root's\n"
     "    `patches/lf_corner_fill/measure_remainder.py`).\"\"\"\n"
     "    x1 = 180.0 / 2.0 - empties.CLEARANCE\n"
     "    width = {k: v[1] - v[0] for k, v in ALL_EXT.items()}\n"
     "    for seed, action in WALLS:\n"
     "        placed = _wall(seed, action)\n"
     "        assert {p[\"archetype\"] for p in placed[1:-1]} == set(EXT), (seed, action)\n"
     "        end = x1 - min(w for k, w in width.items() if k in CORNER_EXT and k != placed[0][\"archetype\"])\n"
     "        for a, b in zip(placed, placed[1:]):\n"
     "            if a[\"archetype\"] == b[\"archetype\"]:\n"
     "                x = b[\"at\"][0] - b[\"size_x\"] / 2.0\n"
     "                others = [k for k in EXT if k != a[\"archetype\"] and x + width[k] <= end + 1e-9]\n"
     "                assert not others, (seed, action, a, b, others)\n"),
]

EDITS = {"packages/pipeline/empties.py": EMPTIES, "tests/unit/test_urban_corner_shops.py": RULE}
APPEND = {"tests/unit/test_urban_corner_shops.py": TEST_TAIL}


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
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.206.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.206.1: results filled")


def main():
    if FILL:
        return fill()
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.206.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.206.1] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel in dict.fromkeys(list(EDITS) + list(APPEND)):
        raw = (LF / rel).read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in EDITS.get(rel, ()):
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:60])
            text = text.replace(old, new)
        if rel in APPEND:
            assert "test_a_run_closes_within_the_narrowest_design_of_its_end" not in text, ("already applied", rel)
            text = text.rstrip("\n") + "\n" + APPEND[rel]
        compile(text, rel, "exec")
        writes[rel] = (text, eol)
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for rel, (text, eol) in writes.items():
        (LF / rel).write_bytes(text.encode("utf-8").replace(b"\n", eol))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.206.0 -> 0.206.1")


if __name__ == "__main__":
    main()
