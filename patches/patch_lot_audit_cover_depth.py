"""Lot 0.98.2: the audit measures cover by its depth, not its height (roadmap
211), and 0.98.1's two overstatements corrected.

`site_audit._cover_rects` read `size[1]` -- the height -- as the plan depth
since v0.17.1. Census (`lot_audit_cover_depth/census_naked_anchor.py`): 115
site specs on disk, 18 `S_NAKED_ANCHOR` as shipped, 0 that the fix moves.

New file from `lot_audit_cover_depth/`: `tests/test_audit_cover_depth.py`.
Anchored edits (every anchor once; refuses on a miss): `site_audit.py`
(`_cover_rects` reads the third number), `site_spawns.py` (the one-leg spread
held "one at a time from one side" on two sites of three -- cold run 9199's
seed_9256). CHANGELOG and VERSION from `lot_audit_cover_depth/CHANGELOG_0.98.2.md`.

    python patch_lot_audit_cover_depth.py
    LOT_ROOT=<copy> python patch_lot_audit_cover_depth.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_audit_cover_depth"

EDITS = {
    "site_audit.py": [
        ('def _cover_rects(site):\n'
         '    out = []\n'
         '    for c in site.get("cover", []):\n'
         '        (x, y), s = c["at"][:2], c.get("size", [1, 1, 1])\n'
         '        out.append((x - s[0] / 2, y - s[1] / 2, x + s[0] / 2, y + s[1] / 2))\n'
         '    return out\n',
         'def _cover_rects(site):\n'
         '    """Every cover piece\'s plan rect. ``size`` is [plan x, height, plan\n'
         '    y], the frame `lot.py` stands each piece\'s box in: the MIDDLE number\n'
         '    is the height (0.98.2, roadmap 211). This read it as the depth from\n'
         '    v0.17.1 on, so every rect had its height for a depth -- 3.05 m for the\n'
         '    getaway van\'s 6.8 m, 6.0 m for a streetlight\'s 0.7 m. Audited both\n'
         '    ways over the 115 site specs on disk, it had moved no verdict."""\n'
         '    out = []\n'
         '    for c in site.get("cover", []):\n'
         '        (x, y), s = c["at"][:2], c.get("size", [1, 1, 1])\n'
         '        out.append((x - s[0] / 2, y - s[2] / 2, x + s[0] / 2, y + s[2] / 2))\n'
         '    return out\n'),
    ],
    "site_spawns.py": [
        ('    # design. Left as it is: enemy placement is provisional until a\n'
         '    # gameplay layer owns it, and what a there-and-back heist\'s fight\n'
         '    # should be is the walker\'s call (roadmap 206).\n',
         '    # design. Left as it is: enemy placement is provisional until a\n'
         '    # gameplay layer owns it, and what a there-and-back heist\'s fight\n'
         '    # should be is the walker\'s call (roadmap 206).\n'
         '    #\n'
         '    # "ONE AT A TIME FROM ONE SIDE" HELD ON TWO SITES OF THREE (0.98.2).\n'
         '    # Cold run 9199 played seed_9256 with the van for the first time: the\n'
         '    # line from its van to its vault runs through the spawn building, so\n'
         '    # the samples that fell in it were pushed out to either side -- two\n'
         '    # enemies 17.7 and 23.4 m from the crew, 94 degrees apart -- and the\n'
         '    # crew lost 41 in 25 runs (49 in 9197). What the crew\'s losses track\n'
         '    # is enemies arriving together from more than one direction, which\n'
         '    # the one-leg spread makes on some sites and not on others. The\n'
         '    # walker has since decided the walk back: responders arrive after\n'
         '    # the job, spawned by the gameplay layer (roadmap 212).\n'),
    ],
}

NEW = {
    pathlib.Path("tests") / "test_audit_cover_depth.py": "test_audit_cover_depth.py",
}


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.98.1", v.read_bytes()
    for rel in NEW:
        assert not (LOT / rel).exists(), ("already applied", rel)
    staged = {}
    for name, edits in EDITS.items():
        p = LOT / name
        d = p.read_bytes()
        crlf = b"\r\n" in d
        assert not (crlf and d.replace(b"\r\n", b"").count(b"\n")), (name, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            n = t.count(old)
            assert n == 1, (name, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    entry = (SRC / "CHANGELOG_0.98.2.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.98.1 - no crew member stands in the getaway van"), text[:60]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    for rel, src in NEW.items():
        (LOT / rel).write_bytes((SRC / src).read_bytes())
    cl.write_bytes((entry + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.98.2")
    print("Lot 0.98.1 -> 0.98.2")


if __name__ == "__main__":
    main()
