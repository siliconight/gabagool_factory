"""Lot 0.98.0: the getaway van at the spawn (roadmap 206, phase 2). The walker,
2026-10-07: "location of the getaway vehicle should be the same as the
missions spawn point. you spawn, do the job, then return to the car";
2026-10-08: "go ahead, place it at the spawn".

New files from `lot_getaway/`: `site_getaway.py` (where the van parks and
where the crew stands), `tests/test_site_getaway.py`. Anchored edits (every
anchor once; refuses on a miss): `lot.py` (the van planned before the walk
positions; `COVER_MATERIALS["step_van"]`), `site_spawns.py` (the enemies along
one leg of a there-and-back route), `site_audit.py` (`S_GETAWAY_AT_SPAWN` for
the van, two anchors at one point judged once). CHANGELOG and VERSION from
`lot_getaway/CHANGELOG_0.98.0.md`.

    python patch_lot_getaway.py
    LOT_ROOT=<copy> python patch_lot_getaway.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_getaway"

EDITS = {
    "lot.py": [
        ("    import site_spawns\n"
         "    raw_pos = _walk_positions(site_spec, merged)\n"
         "    walk_pos, seat_findings = site_spawns.seat_destinations(\n",
         "    # THE GETAWAY VAN (0.98.0, roadmap 206), before anything reads where\n"
         "    # the crew stands: its door's spawn is the site's `crew_spawn` and its\n"
         "    # `extraction`, both site-level, so `_walk_positions` takes them over\n"
         "    # the buildings' own, and the van joins the cover every later planner\n"
         "    # stands round -- the parked cars, the furniture, the fences, the\n"
         "    # cover. The walker: \"you spawn, do the job, then return to the car\".\n"
         "    import site_getaway\n"
         "    getaway_findings = []\n"
         "    getaway = site_getaway.plan(site_spec, merged, getaway_findings)\n"
         "    if getaway is not None:\n"
         "        site_spec.setdefault(\"cover\", []).append(getaway[\"van\"])\n"
         "        declared = site_spec.setdefault(\"site_markers\", [])\n"
         "        declared.extend(getaway[\"markers\"])\n"
         "        if merged.get(\"site_markers\") is not declared:\n"
         "            merged.setdefault(\"site_markers\", []).extend(getaway[\"markers\"])\n"
         "        print(f\"[lot] LOT_GETAWAY_PLACED: the {getaway['van']['species']} at \"\n"
         "              f\"{tuple(getaway['van']['at'])} ({getaway['van']['breaks']}), the crew's \"\n"
         "              f\"spawn and extraction at {tuple(getaway['markers'][0]['at'])}, \"\n"
         "              f\"{getaway['reach']:.1f} m from the spawn building's door\")\n"
         "    for f_ in getaway_findings:\n"
         "        print(f\"[lot] {f_}\")\n"
         "    merged[\"getaway_plan\"] = {\"placed\": getaway, \"findings\": getaway_findings}\n"
         "\n"
         "    import site_spawns\n"
         "    raw_pos = _walk_positions(site_spec, merged)\n"
         "    walk_pos, seat_findings = site_spawns.seat_destinations(\n"),
        ("COVER_MATERIALS = {\"box_truck\": \"metal_painted\", \"cargo_container\": \"metal_painted\",\n",
         "COVER_MATERIALS = {\"box_truck\": \"metal_painted\", \"cargo_container\": \"metal_painted\",\n"
         "                   # the crew's getaway van is flat black paint gone chalky,\n"
         "                   # Zoo's one option for it (0.98.0)\n"
         "                   \"step_van\": \"paint_matte\",\n"),
    ],
    "site_spawns.py": [
        ("    route = [tuple(positions[k][:2])\n"
         "             for k in (\"spawn\", \"objective\", \"extraction\")]\n"
         "    lengths = [max(1e-6, math.dist(a, b)) for a, b in zip(route, route[1:])]\n",
         "    route = [tuple(positions[k][:2])\n"
         "             for k in (\"spawn\", \"objective\", \"extraction\")]\n"
         "    # A THERE-AND-BACK ROUTE IS ONE LEG WALKED TWICE (0.98.0, roadmap 206).\n"
         "    # With the getaway van the extraction is the crew's spawn, and the\n"
         "    # return leg is the outbound one backwards: samples spread over both\n"
         "    # put half the enemies on ground the outbound half already holds,\n"
         "    # and every one near the end of the return inside the standoff from\n"
         "    # the spawn it ends at. The enemies spread along the one leg; the crew\n"
         "    # passes them going in and coming out.\n"
         "    if math.dist(route[0], route[2]) < THERE_AND_BACK:\n"
         "        route = route[:2]\n"
         "    lengths = [max(1e-6, math.dist(a, b)) for a, b in zip(route, route[1:])]\n"),
        ("#: Enemies closer together than this are one encounter wearing six hats.\n"
         "MIN_SEPARATION = 4.0\n",
         "#: Enemies closer together than this are one encounter wearing six hats.\n"
         "MIN_SEPARATION = 4.0\n"
         "\n"
         "#: A route whose extraction stands this close to its spawn goes there and\n"
         "#: back (the getaway van, 0.98.0): the enemies spread along its one leg.\n"
         "THERE_AND_BACK = 3.0\n"),
    ],
    "site_audit.py": [
        ("    # --- exfil shape (PayDay): the escape must not rewind the entry\n"
         "    if spawn and obj and extr and mode == \"heist\":\n",
         "    # --- exfil shape (PayDay): the escape must not rewind the entry --\n"
         "    # unless the exit IS the way in by design: the crew's getaway van,\n"
         "    # parked at their spawn (0.98.0, roadmap 206; the walker, 2026-10-07:\n"
         "    # \"you spawn, do the job, then return to the car\"). Said, as INFO,\n"
         "    # rather than graded MED on every level built that way.\n"
         "    getaway = _getaway(site)\n"
         "    if spawn and obj and extr and mode == \"heist\" and getaway:\n"
         "        F((\"INFO\", \"S_GETAWAY_AT_SPAWN\",\n"
         "           f\"the extraction is the crew's {getaway} at its spawn: the second \"\n"
         "           f\"half of the heist is the walk back to the van, by design\"))\n"
         "    elif spawn and obj and extr and mode == \"heist\":\n"),
        ("        for kind, pt in ((\"crew spawn\", spawn), (\"extraction\", extr)):\n"
         "            if not pt:\n"
         "                continue\n"
         "            for r in resp:\n",
         "        for kind, pt in _anchors(spawn, extr):\n"
         "            for r in resp:\n"),
        ("    for kind, pt in ((\"crew spawn\", spawn), (\"extraction\", extr)):\n"
         "        if not pt:\n"
         "            continue\n"
         "        d = min((_dist_pt_rect(pt[0], pt[1], r) for r in backstops),\n",
         "    for kind, pt in _anchors(spawn, extr):\n"
         "        d = min((_dist_pt_rect(pt[0], pt[1], r) for r in backstops),\n"),
        ("def _cover_rects(site):\n",
         "def _getaway(site):\n"
         "    \"\"\"The species of the getaway van the site's extraction marker names,\n"
         "    or None (0.98.0).\"\"\"\n"
         "    for m in site.get(\"site_markers\", []):\n"
         "        if m.get(\"type\") == \"extraction\" and m.get(\"getaway\"):\n"
         "            return m[\"getaway\"]\n"
         "    return None\n"
         "\n"
         "\n"
         "def _anchors(spawn, extr):\n"
         "    \"\"\"The crew's two anchors, labelled, absent ones dropped -- and one\n"
         "    point when they are one, so a finding about it is said once, not twice\n"
         "    (0.98.0: the getaway van puts both at its door).\"\"\"\n"
         "    if spawn and extr and math.hypot(spawn[0] - extr[0], spawn[1] - extr[1]) < 0.5:\n"
         "        return [(\"crew spawn and extraction\", spawn)]\n"
         "    return [(k, p) for k, p in ((\"crew spawn\", spawn), (\"extraction\", extr)) if p]\n"
         "\n"
         "\n"
         "def _cover_rects(site):\n"),
    ],
}


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.97.4", v.read_bytes()
    assert not (LOT / "site_getaway.py").exists(), "already applied"
    for name, edits in EDITS.items():
        p = LOT / name
        d = p.read_bytes()
        crlf = b"\r\n" in d
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            n = t.count(old)
            assert n == 1, (name, n, old[:70])
            t = t.replace(old, new)
        p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    (LOT / "site_getaway.py").write_bytes((SRC / "site_getaway.py").read_bytes())
    (LOT / "tests" / "test_site_getaway.py").write_bytes((SRC / "test_site_getaway.py").read_bytes())
    entry = (SRC / "CHANGELOG_0.98.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.97.4 - the root test moves under tests/"), text[:60]
    cl.write_bytes((entry + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.98.0")
    print("Lot 0.97.4 -> 0.98.0")


if __name__ == "__main__":
    main()
