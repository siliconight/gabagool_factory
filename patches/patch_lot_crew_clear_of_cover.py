"""Lot 0.98.1: no crew member stands in the getaway van (roadmap 206).

Cold run 9198, bank_block_001 seed_9256: `crew_spawns` put LT_PlayerSpawn_1
at (20.812, -1.8), inside the step_van's slot, and Laser Tag refused the map
with SPAWN_IN_COLLISION before a single run. The crew's other members were
tested against the buildings and the blockers only.

New files from `lot_crew_clear_of_cover/`: `tests/test_crew_keeps_out_of_the_van.py`
and its fixture, `tests/fixtures/bank_block_001_seed_9256.site.json` (that
candidate's `site.site.drawn.json`, byte for byte). Anchored edits to
`site_spawns.py` (every anchor once; refuses on a miss): `cover_rects`, asked
by `crew_spawns` beside `solid_rects`; the docstring that says what a member
is kept out of; and the one-leg enemy spread's comment, whose "going in and
coming out" 9198 measured wrong -- the behaviour is kept. CHANGELOG and
VERSION from `lot_crew_clear_of_cover/CHANGELOG_0.98.1.md`.

    python patch_lot_crew_clear_of_cover.py
    LOT_ROOT=<copy> python patch_lot_crew_clear_of_cover.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_crew_clear_of_cover"

EDITS = {
    "site_spawns.py": [
        ('def solid_rects(site_spec, margin: float = WALL_MARGIN) -> list:\n'
         '    """What a spawn is kept out of: the buildings\' footprints and the\n'
         '    blockers. The crew\'s spawns and the enemies ask `outdoors()` of this."""\n'
         '    return footprints(site_spec, margin) + blocker_rects(site_spec, margin)\n',
         'def solid_rects(site_spec, margin: float = WALL_MARGIN) -> list:\n'
         '    """What a spawn is kept out of: the buildings\' footprints and the\n'
         '    blockers. The crew\'s spawns and the enemies ask `outdoors()` of this."""\n'
         '    return footprints(site_spec, margin) + blocker_rects(site_spec, margin)\n'
         '\n'
         '\n'
         'def cover_rects(site_spec, margin: float = WALL_MARGIN) -> list:\n'
         '    """Every cover piece\'s plan rect, grown by ``margin``: the getaway van,\n'
         '    the parked cars, the kerb-line furniture, the pieces `site_cover`\n'
         '    stands on the routes.\n'
         '\n'
         '    ``size`` is [plan x, height, plan y] -- the Godot frame `lot.py`\n'
         '    stands each piece\'s box in, at half the MIDDLE number -- so the\n'
         '    middle number is the height and the third is the depth. A piece\n'
         '    with no ``size`` is `lot.COVER`\'s metre cube.\n'
         '\n'
         '    The crew\'s spawns ask this beside `solid_rects` (0.98.1).\n'
         '    `place_enemies` does not: it runs before most of the cover exists --\n'
         '    `assemble` plans the furniture, the parked cars, the fences and\n'
         '    `site_cover`\'s pieces after it -- so there it would see the van and\n'
         '    little else."""\n'
         '    rects = []\n'
         '    for cv in site_spec.get("cover") or []:\n'
         '        at = cv.get("at") if isinstance(cv, dict) else None\n'
         '        if not at or len(at) < 2:\n'
         '            continue\n'
         '        sx, _h, sy = tuple(cv.get("size") or (1.0, 1.0, 1.0))[:3]\n'
         '        rects.append((at[0] - sx / 2.0 - margin, at[1] - sy / 2.0 - margin,\n'
         '                      at[0] + sx / 2.0 + margin, at[1] + sy / 2.0 + margin))\n'
         '    return rects\n'),
        ('    walks, and each has to be `outdoors()` of every building and ``spacing``\n'
         '    clear of every crew position already placed. Nearest-first for the reason\n',
         '    walks, and each has to be `outdoors()` of every building, blocker and\n'
         '    piece of cover (`cover_rects`, 0.98.1) and ``spacing`` clear of every\n'
         '    crew position already placed. Nearest-first for the reason\n'),
        ('    ground = ground_rect(site_spec)\n'
         '    rects = solid_rects(site_spec)\n'
         '    z = base[2] if len(base) > 2 else GROUND_Z\n',
         '    ground = ground_rect(site_spec)\n'
         '    # NOT IN THE VAN, NOR IN ANY OTHER COVER (0.98.1). This asked only\n'
         '    # `solid_rects`, the buildings and the blockers, and no cover had\n'
         '    # stood near a spawn until 0.98.0 parked the getaway van at one.\n'
         '    # Cold run 9198, bank_block_001 seed_9256: the rings start along +X,\n'
         '    # the van\'s slot stood 1.25 m off the spawn on that side, and\n'
         '    # LT_PlayerSpawn_1 went to (20.812, -1.8), inside it -- Laser Tag\n'
         '    # refused the map with SPAWN_IN_COLLISION and played no run of it.\n'
         '    # The margin is `WALL_MARGIN`, for the reason a wall gets it: the\n'
         '    # bake erodes the navmesh round every solid, and a body inside that\n'
         '    # band has nothing to path from.\n'
         '    rects = solid_rects(site_spec) + cover_rects(site_spec)\n'
         '    z = base[2] if len(base) > 2 else GROUND_Z\n'),
        ('    # the spawn it ends at. The enemies spread along the one leg; the crew\n'
         '    # passes them going in and coming out.\n',
         '    # the spawn it ends at. The enemies spread along the one leg; the crew\n'
         '    # passes them going in and coming out.\n'
         '    #\n'
         '    # "GOING IN AND COMING OUT" WAS WRONG (cold run 9198; kept, 0.98.1).\n'
         '    # `LT_EnemyBrain` walks every enemy that cannot see the crew toward it\n'
         '    # from the first frame, so a spread along the route is a set of\n'
         '    # arrival bearings and times, not a sequence: on seed_9054 and\n'
         '    # seed_9155, in 9197 and 9198 alike, every enemy\'s median time of\n'
         '    # death was 3.5 to 10.7 s, whichever leg it stood on. Strung along one\n'
         '    # leg, six arrive one at a time from one side, and the crew\'s losses\n'
         '    # over 25 runs fell from 48 to 1 (seed_9054) and from 19 to 0\n'
         '    # (seed_9155, which Laser Tag called a trivial encounter). 9197\'s\n'
         '    # two-leg routes, ending at another building, had put two enemies\n'
         '    # behind the crew (seed_9054) and two pairs at one distance each\n'
         '    # (seed_9155) -- by where that building happened to stand, not by\n'
         '    # design. Left as it is: enemy placement is provisional until a\n'
         '    # gameplay layer owns it, and what a there-and-back heist\'s fight\n'
         '    # should be is the walker\'s call (roadmap 206).\n'),
    ],
}

NEW = {
    pathlib.Path("tests") / "test_crew_keeps_out_of_the_van.py": "test_crew_keeps_out_of_the_van.py",
    pathlib.Path("tests") / "fixtures" / "bank_block_001_seed_9256.site.json":
        "bank_block_001_seed_9256.site.json",
}


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.98.0", v.read_bytes()
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
    entry = (SRC / "CHANGELOG_0.98.1.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.98.0 - the getaway van at the spawn"), text[:60]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    for rel, src in NEW.items():
        (LOT / rel).parent.mkdir(parents=True, exist_ok=True)
        (LOT / rel).write_bytes((SRC / src).read_bytes())
    cl.write_bytes((entry + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.98.1")
    print("Lot 0.98.0 -> 0.98.1")


if __name__ == "__main__":
    main()
