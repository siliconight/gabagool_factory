"""Lot 0.87.0: an alley's poster runs are not all pasted at one height.

The poster pass the walker queued 2026-09-30, Lot's part. Every wall run was
pasted with its centre on the camera's eye, 1.6 m, on every wall of every
site -- the placement guide's "identical spacing, height, rotation, or
mounting pattern on every wall". The poles already start their tiers at
different heights (`test_no_shared_centreline_and_within_reach`); the walls
did not.

`site_posters.wall_height(name)`: the eye plus one of `WALL_STEPS`, by the
run's own name (building, side, ordinal -- stable, a run is never retried
under another). The steps are -0.30 / -0.15 / 0 / +0.09: the highest puts
the band's top at 2.097 m, under `REACH` 2.1, the guide's "posters placed
far above reach need a reason".

Deli Counter 0.170.0 is the indoor half; Zoo 1.41.0 the paper.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

LOT = pathlib.Path(__file__).resolve().parents[1] / "lot"


def _edit(rel, pairs):
    p = LOT / rel
    raw = p.read_bytes()
    assert b"\r\n" not in raw, f"{rel}: CRLF in an LF file"
    s = raw.decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    p.write_bytes(s.encode("utf-8"))
    print("patched", rel)


SRC = [
    ('''REACH = 2.1
''', '''REACH = 2.1
#: NOT EVERY WALL RUN AT ONE HEIGHT (0.87.0): a run's centre is the eye plus
#: one of these, by its own name (`wall_height`). The highest puts the band's
#: top at EYE + 0.09 + BAND_WALL / 2 = 2.097, under `REACH`.
WALL_STEPS = (-0.30, -0.15, 0.0, 0.09)
'''),
    ('''def _nearest(roads, px, py):''', '''def wall_height(name):
    """The height of a wall run's centre: the eye plus the step its name
    takes. The name is the building, the side and the run's ordinal on it,
    so the height is the same on every plan of the same site."""
    k = (zlib.crc32(str(name).encode("utf-8")) & 0xFFFFFFFF) % len(WALL_STEPS)
    return round(EYE + WALL_STEPS[k], 3)


def _nearest(roads, px, py):'''),
    ('''                    out.append(_record(name, (x, y), facing_yaw(nx, ny),
                                       (w, DEPTH, BAND_WALL), EYE,
''', '''                    out.append(_record(name, (x, y), facing_yaw(nx, ny),
                                       (w, DEPTH, BAND_WALL), wall_height(name),
'''),
]

TESTS = [
    ('''        assert r["z"] == P.EYE and r["form"] == "alley" and r["species"] == "poster_wall"
''', '''        # 0.87.0: at the eye plus the run's own step
        assert r["z"] == P.wall_height(r["name"]) and r["z"] - P.EYE in [pytest.approx(s) for s in P.WALL_STEPS]
        assert r["form"] == "alley" and r["species"] == "poster_wall"
'''),
    ('''def test_a_true_alley_is_papered_on_the_stretch_the_neighbour_faces_clear_of_its_door():''',
     '''def test_wall_runs_are_not_all_at_one_height_and_none_is_out_of_reach():
    """0.87.0, the placement guide: "identical ... height ... on every wall"
    is the tell, and "posters placed far above reach need a reason"."""
    assert 0.0 in P.WALL_STEPS
    for s in P.WALL_STEPS:
        assert P.EYE + s + P.BAND_WALL / 2 <= P.REACH + 1e-9, s
        assert P.EYE + s - P.BAND_WALL / 2 >= 0.8, s           # not on the ground
    names = [f"alley_poster_b{b}_{side}_{k}" for b in range(12) for side in "NESW" for k in range(2)]
    heights = {P.wall_height(n) for n in names}
    assert heights == {round(P.EYE + s, 3) for s in P.WALL_STEPS}, heights
    assert P.wall_height(names[0]) == P.wall_height(names[0])


def test_a_true_alley_is_papered_on_the_stretch_the_neighbour_faces_clear_of_its_door():'''),
]


def main():
    s = (LOT / "site_posters.py").read_text(encoding="utf-8")
    assert "WALL_STEPS" not in s, "already applied"
    _edit("site_posters.py", SRC)
    _edit("tests/test_site_posters.py", TESTS)


if __name__ == "__main__":
    main()
