"""Lot 0.99.0: where responders arrive, and the room they need to (roadmap
212, phase 1). The walker, 2026-10-08: "have responders show up after the
job, on the way back (and this would be on the gameplay layer, but we can
make thee assets and ensure there is clearance and routes for their
arrival)".

New files from `lot_responder_arrivals/`: `site_responders.py` (an arrival
per open road end: the entry, the inbound lane, a stop a cruiser fits with
its doors open, the way back it serves) and `tests/test_site_responders.py`.
Anchored edits (every anchor once; refuses on a miss):
- `site_streets.py`: `end_lies_on`, the one test whether a road's end lies
  on another road, read by `_ends_on`, `_slab` and the arrivals;
- `site_cover.py`: `plan_cover(keep_out=)`, rects no piece may stand in that
  occlude nothing;
- `lot.py`: `assemble` plans the arrivals after the enemies and before
  anything is parked or stood in the street, reserves their lanes and stops
  from the parking and the cover, writes each as a `responder_spawn` site
  marker, and reads the reservation back after every planner.
CHANGELOG and VERSION from `lot_responder_arrivals/CHANGELOG_0.99.0.md`.

    python patch_lot_responder_arrivals.py
    LOT_ROOT=<copy> python patch_lot_responder_arrivals.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_responder_arrivals"

EDITS = {
    "site_streets.py": [
        ('def _ends_on(road, other) -> bool:\n'
         '    """An end of ``road`` lies on ``other``\'s centre line, within a metre\n'
         '    across and within its extent: ``road`` is a leg that ENDS at ``other``."""\n'
         '    for end in (road.a, road.b):\n'
         '        dx, dy = end[0] - other.a[0], end[1] - other.a[1]\n'
         '        across = dx * other.perp[0] + dy * other.perp[1]\n'
         '        along = dx * other.along[0] + dy * other.along[1]\n'
         '        if abs(across) <= 1.0 and -1.0 <= along <= other.length + 1.0:\n'
         '            return True\n'
         '    return False\n',
         'def end_lies_on(end, other) -> bool:\n'
         '    """``end``, a plan point, lies on ``other``\'s centre line: within a metre\n'
         '    across and within its extent. One test for every reader (0.99.0) -- a\n'
         '    road that ENDS on another (`_ends_on`), a slab trimmed at a mouth\n'
         '    (`_slab`), and an end a vehicle can arrive by (`site_responders`):\n'
         '    three spellings of one test are three places for it to drift."""\n'
         '    dx, dy = end[0] - other.a[0], end[1] - other.a[1]\n'
         '    across = dx * other.perp[0] + dy * other.perp[1]\n'
         '    along = dx * other.along[0] + dy * other.along[1]\n'
         '    return abs(across) <= 1.0 and -1.0 <= along <= other.length + 1.0\n'
         '\n'
         '\n'
         'def _ends_on(road, other) -> bool:\n'
         '    """An end of ``road`` lies on ``other``\'s centre line, within a metre\n'
         '    across and within its extent: ``road`` is a leg that ENDS at ``other``."""\n'
         '    return any(end_lies_on(end, other) for end in (road.a, road.b))\n'),
        ('        for end, which in ((road.a, 0), (road.b, 1)):\n'
         '            dx, dy = end[0] - other.a[0], end[1] - other.a[1]\n'
         '            along = dx * other.along[0] + dy * other.along[1]\n'
         '            across = dx * other.perp[0] + dy * other.perp[1]\n'
         '            if abs(across) > 1.0 or along < -1.0 or along > other.length + 1.0:\n'
         '                continue\n',
         '        for end, which in ((road.a, 0), (road.b, 1)):\n'
         '            if not end_lies_on(end, other):\n'
         '                continue\n'),
    ],
    "site_cover.py": [
        ('               species=None, standing=None) -> CoverPlan:\n',
         '               species=None, standing=None, keep_out=None) -> CoverPlan:\n'),
        ('    for rect in standing or ():\n'
         '        measured.append(tuple(rect))\n'
         '        placeable.append(_grow(tuple(rect), COVER_EDGE_GAP))\n',
         '    for rect in standing or ():\n'
         '        measured.append(tuple(rect))\n'
         '        placeable.append(_grow(tuple(rect), COVER_EDGE_GAP))\n'
         '    # THE RESPONDERS\' LANES AND STOPS (0.99.0, roadmap 212): no piece\n'
         '    # stands in them, and they hide nobody -- an empty lane is not an\n'
         '    # occluder -- so they join where a piece may not stand and stay out\n'
         '    # of what is measured.\n'
         '    for rect in keep_out or ():\n'
         '        placeable.append(tuple(rect))\n'),
    ],
    "lot.py": [
        ('    # The collision reading read four lines up. It was already going to\n'
         '    # `seat_destinations`; the enemies are placed against sightlines and had\n'
         '    # been getting declared footprints instead.\n'
         '    spawn_plan = site_spawns.place_enemies(site_spec, walk_pos, solids=solids)\n',
         '    # The collision reading read four lines up. It was already going to\n'
         '    # `seat_destinations`; the enemies are placed against sightlines and had\n'
         '    # been getting declared footprints instead.\n'
         '    spawn_plan = site_spawns.place_enemies(site_spec, walk_pos, solids=solids)\n'
         '\n'
         '    # WHERE RESPONDERS ARRIVE (0.99.0, roadmap 212), before anything is\n'
         '    # parked or stood in the street, so every later planner keeps out of\n'
         '    # the lanes and the stops. The walker: "have responders show up after\n'
         '    # the job, on the way back (and this would be on the gameplay layer,\n'
         '    # but we can make thee assets and ensure there is clearance and routes\n'
         '    # for their arrival)". Spawning them is the gameplay layer\'s. Each\n'
         '    # arrival is written as a `responder_spawn` site marker, which the\n'
         '    # audit judges and the nav QA spawns a bot at and walks to the crew.\n'
         '    import site_responders\n'
         '    responder_findings = []\n'
         '    arrivals = site_responders.plan(site_spec, walk_pos, findings=responder_findings)\n'
         '    responder_keep_out = site_responders.keep_out(arrivals)\n'
         '    if arrivals:\n'
         '        _arrival_markers = [site_responders.marker(a) for a in arrivals]\n'
         '        _declared = site_spec.setdefault("site_markers", [])\n'
         '        _declared.extend(_arrival_markers)\n'
         '        if merged.get("site_markers") is not _declared:\n'
         '            merged.setdefault("site_markers", []).extend(_arrival_markers)\n'
         '        print(f"[lot] LOT_RESPONDERS_PLACED: {len(arrivals)} arrival(s), "\n'
         '              + "; ".join(f"road {a[\'road\']} from ({a[\'entry\'][0]:.1f}, "\n'
         '                          f"{a[\'entry\'][1]:.1f}) to a stop at ({a[\'stop\'][0]:.1f}, "\n'
         '                          f"{a[\'stop\'][1]:.1f}), {a[\'to_way_back\']:.1f} m off the way back"\n'
         '                          for a in arrivals))\n'),
        ('    parked = site_parking.plan_parking(site_streets.roads(site_spec), standing,\n'
         '                                       list(cover_points.values()))\n',
         '    # the responders\' stops and lanes are not standing, so they reach the\n'
         '    # parking alone: a bay beside a stop holds no car to block a door\n'
         '    parked = site_parking.plan_parking(site_streets.roads(site_spec),\n'
         '                                       standing + list(responder_keep_out),\n'
         '                                       list(cover_points.values()))\n'),
        ('        species=site_cover.COVER_SPECIES,\n'
         '        # the kerb line and the parked cars, already standing\n'
         '        standing=standing)\n'
         '    site_spec["cover"].extend(c.as_site_cover() for c in cover_plan.cover)\n',
         '        species=site_cover.COVER_SPECIES,\n'
         '        # the kerb line and the parked cars, already standing\n'
         '        standing=standing,\n'
         '        # the responders\' lanes and stops (0.99.0): nothing stands in them,\n'
         '        # and they hide nobody\n'
         '        keep_out=responder_keep_out)\n'
         '    site_spec["cover"].extend(c.as_site_cover() for c in cover_plan.cover)\n'
         '    # THE RESERVATION, READ BACK (0.99.0): every piece every planner stood,\n'
         '    # against every arrival\'s stop and lane. Empty when it held.\n'
         '    responder_findings += site_responders.blocked(arrivals, site_spec["cover"])\n'
         '    merged["responder_plan"] = {"arrivals": arrivals, "findings": responder_findings}\n'),
        ('    for f_ in (seat_findings + clear_findings + spawn_plan.findings\n'
         '               + cover_findings):\n',
         '    for f_ in (seat_findings + clear_findings + spawn_plan.findings\n'
         '               + cover_findings + responder_findings):\n'),
    ],
}

NEW = {
    pathlib.Path("site_responders.py"): "site_responders.py",
    pathlib.Path("tests") / "test_site_responders.py": "test_site_responders.py",
}


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.98.2", v.read_bytes()
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
    entry = (SRC / "CHANGELOG_0.99.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.98.2 - the audit measures cover by its depth"), text[:60]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    for rel, src in NEW.items():
        (LOT / rel).write_bytes((SRC / src).read_bytes())
    cl.write_bytes((entry + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.99.0")
    print("Lot 0.98.2 -> 0.99.0")


if __name__ == "__main__":
    main()
