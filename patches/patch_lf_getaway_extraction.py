"""Level Factory 0.155.0: the extraction is the spawn building (roadmap 206).
The walker, 2026-10-07: "location of the getaway vehicle should be the same as
the missions spawn point. you spawn, do the job, then return to the car" --
Lot 0.98.0 parks the van at the spawn building's kerb; this makes the
building the mission's extraction, with the draw that chose another one still
made so no later number a seed gives moves.

Anchored edits (every anchor once; refuses on a miss):
`packages/pipeline/site_variation.py`, `tests/unit/test_score_building.py`,
`tests/unit/test_candidate_distinctness.py`. CHANGELOG and VERSION from
`lf_getaway_extraction/CHANGELOG_0.155.0.md`.

    python patch_lf_getaway_extraction.py
    LF_ROOT=<copy> python patch_lf_getaway_extraction.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_getaway_extraction"
CHANGELOG_HEAD = "## [0.154.0] - The contract's step-up reaches Laser Tag's crew\n"

EDITS = {
    "packages/pipeline/site_variation.py": [
        ("    # Prefer an extraction that is not the spawn, so the route crosses the site.\n"
         "    others = [b for b in ids if b != spawn] or ids\n"
         "    extraction = others[next(rng) % len(others)]\n",
         "    # THE CREW LEAVES FROM WHERE IT CAME (0.155.0, roadmap 206). The walker,\n"
         "    # 2026-10-07: \"location of the getaway vehicle should be the same as the\n"
         "    # missions spawn point. you spawn, do the job, then return to the car\" --\n"
         "    # so the extraction is the spawn building, and Lot (0.98.0) parks the\n"
         "    # getaway van at its kerb and puts the crew's start and exit at the van's\n"
         "    # door. The draw that chose another building is still made, so no number\n"
         "    # a seed gives after it moves. *As first written:* \"Prefer an extraction\n"
         "    # that is not the spawn, so the route crosses the site.\" -- which on 43\n"
         "    # of 136 specs crossed it into the score building itself.\n"
         "    next(rng)\n"
         "    extraction = spawn\n"),
    ],
    "tests/unit/test_score_building.py": [
        ("        assert p[\"extraction\"] != p[\"spawn\"], (\"the route should cross the site\", s, p)\n",
         "        # the crew leaves from where it came: the getaway van (0.155.0)\n"
         "        assert p[\"extraction\"] == p[\"spawn\"], (\"the van is at the spawn\", s, p)\n"),
        ("    \"\"\"Pinned on 0.151.0's own output, so a site with no anchored score -- and\n"
         "    every candidate already graded -- keeps its roles.\"\"\"\n"
         "    expect = {9000: (\"b0\", \"b0\", \"b1\"), 9001: (\"b2\", \"b1\", \"b0\"),\n"
         "              9002: (\"b2\", \"b2\", \"b0\"), 9003: (\"b1\", \"b0\", \"b0\")}\n",
         "    \"\"\"Pinned on 0.151.0's own output, so a site with no anchored score -- and\n"
         "    every candidate already graded -- keeps its spawn and its objective. The\n"
         "    extraction is the spawn since 0.155.0 (the getaway van); 0.151.0 drew\n"
         "    b1, b0, b0, b0 for these four, and that draw is still made.\"\"\"\n"
         "    expect = {9000: (\"b0\", \"b0\", \"b0\"), 9001: (\"b2\", \"b1\", \"b2\"),\n"
         "              9002: (\"b2\", \"b2\", \"b2\"), 9003: (\"b1\", \"b0\", \"b1\")}\n"),
    ],
    "tests/unit/test_candidate_distinctness.py": [
        ("        assert p[\"extraction\"] != p[\"spawn\"], \"the route should cross the site\"\n",
         "        # the crew leaves from where it came: the getaway van (0.155.0)\n"
         "        assert p[\"extraction\"] == p[\"spawn\"], \"the van is at the spawn\"\n"),
    ],
}


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.154.0", repr(v)
    for name, edits in EDITS.items():
        p = LF / name
        d = p.read_bytes()
        crlf = b"\r\n" in d
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            n = t.count(old)
            assert n == 1, (name, n, old[:70])
            t = t.replace(old, new)
        p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    c = (LF / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1
    entry = (SRC / "CHANGELOG_0.155.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    (LF / "CHANGELOG.md").write_bytes((entry + text).encode("utf-8"))
    (LF / "VERSION").write_bytes(b"0.155.0")
    print("Level Factory 0.154.0 -> 0.155.0")


if __name__ == "__main__":
    main()
