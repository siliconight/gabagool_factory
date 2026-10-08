"""Level Factory 0.156.0: Lot's site-level markers reach Dispatch (roadmap 204).

`packages/staging/dispatch_inputs.py` turned Lot's gameplay `markers`,
`objectives` and `loot` into Dispatch anchors and never read `site_markers`,
so the getaway van's crew spawn and extraction, and Lot 0.99.0's responder
arrivals, never reached the package -- and `ensure_mission_anchors`
synthesized the mission's start at the centroid of every Lot anchor.

Anchored edits (every anchor once; refuses on a miss): `dispatch_inputs.py`
(`site_markers_to_anchors`, staged ahead of the buildings' markers). New
file from `lf_site_markers/`: `tests/unit/test_dispatch_site_markers.py`.
CHANGELOG and VERSION from `lf_site_markers/CHANGELOG_0.156.0.md`.

    python patch_lf_site_markers.py
    LF_ROOT=<copy> python patch_lf_site_markers.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_site_markers"
CHANGELOG_HEAD = "## [0.155.0] - The crew leaves from where it came: the extraction is the spawn building\n"

EDITS = {
    "packages/staging/dispatch_inputs.py": [
        ('        anchors.append(anchor)\n'
         '    return anchors\n',
         '        anchors.append(anchor)\n'
         '    return anchors\n'
         '\n'
         '\n'
         '#: Lot\'s SITE-LEVEL markers (its gameplay file\'s `site_markers`) -> the\n'
         '#: Dispatch anchor type each becomes and the mission-flow tag it carries.\n'
         '#: A site-level `crew_spawn` and `extraction` are the mission\'s own: Lot\'s\n'
         '#: `_walk_positions` takes them over any building\'s, which is how the\n'
         '#: getaway van (Lot 0.98.0) puts the crew\'s start and exit at its door. A\n'
         '#: `responder_spawn` is where responders arrive (Lot 0.99.0, roadmap 212).\n'
         '_SITE_MARKERS = {\n'
         '    "crew_spawn": ("player_start", "mission_start"),\n'
         '    "extraction": ("extraction", "extraction"),\n'
         '    "responder_spawn": ("ai_spawn", "responder"),\n'
         '}\n'
         '\n'
         '\n'
         'def site_markers_to_anchors(gameplay: dict, source: str) -> list:\n'
         '    """Lot\'s site-level markers as Dispatch anchors (0.156.0, roadmap 204).\n'
         '\n'
         '    `_iter_records` reads `markers`, `objectives` and `loot`, and the site\'s\n'
         '    own markers live in `site_markers` -- so until this no site-level marker\n'
         '    reached Dispatch. The getaway van\'s crew spawn and extraction never\n'
         '    became the package\'s; `ensure_mission_anchors` synthesized a\n'
         '    `player_start` at the centroid of every Lot anchor and tagged every\n'
         '    building\'s extraction as the mission\'s (cold run 9198\'s package:\n'
         '    `lot:mission_start` at (-7.03, 0.68), 14 m from the van).\n'
         '\n'
         '    A site marker stands on the plate: `at` is a plan point, and its height\n'
         '    is the ground\'s, as `lot._walk_positions` reads it. No facing is\n'
         '    passed: a Lot slot yaw and a Dispatch `rot_y` have not been shown to\n'
         '    share a convention, and a yaw read in the wrong one is silently wrong."""\n'
         '    anchors: list = []\n'
         '    counts: dict = {}\n'
         '    for m in gameplay.get("site_markers", []) or []:\n'
         '        if not isinstance(m, dict):\n'
         '            continue\n'
         '        at = m.get("at")\n'
         '        if not isinstance(at, (list, tuple)) or len(at) < 2:\n'
         '            continue\n'
         '        raw = str(m.get("type") or "interaction")\n'
         '        atype, tag = _SITE_MARKERS.get(raw, (_TYPE_MAP.get(raw, raw), None))\n'
         '        origin = str(m.get("source") or "site")\n'
         '        n = counts.get((origin, raw), 0)\n'
         '        counts[(origin, raw)] = n + 1\n'
         '        anchor = {"id": f"{source}:{origin}_{raw}_{n}", "type": atype,\n'
         '                  "pos": [_num(at[0]), _num(at[1]), 0.0]}\n'
         '        if tag:\n'
         '            anchor["tags"] = [tag]\n'
         '        anchors.append(anchor)\n'
         '    return anchors\n'),
        ('    lot_anchors = ensure_mission_anchors(\n'
         '        markers_to_anchors(lot_gp, "lot", lot_up), "lot", lot_up)\n',
         '    # THE SITE\'S OWN MARKERS FIRST (0.156.0, roadmap 204): the getaway van\'s\n'
         '    # start and exit carry the mission\'s tags, so `ensure_mission_anchors`\n'
         '    # finds them tagged -- it neither synthesizes a start at the centroid\n'
         '    # nor tags every building\'s extraction as the mission\'s.\n'
         '    lot_anchors = ensure_mission_anchors(\n'
         '        site_markers_to_anchors(lot_gp, "lot") + markers_to_anchors(lot_gp, "lot", lot_up),\n'
         '        "lot", lot_up)\n'),
    ],
}

NEW = {
    pathlib.Path("tests") / "unit" / "test_dispatch_site_markers.py": "test_dispatch_site_markers.py",
}


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.155.0", repr(v)
    for rel in NEW:
        assert not (LF / rel).exists(), ("already applied", rel)
    staged = {}
    for name, edits in EDITS.items():
        p = LF / name
        d = p.read_bytes()
        crlf = b"\r\n" in d
        assert not (crlf and d.replace(b"\r\n", b"").count(b"\n")), (name, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            n = t.count(old)
            assert n == 1, (name, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    entry = (SRC / "CHANGELOG_0.156.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    c = (LF / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:80]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    for rel, src in NEW.items():
        (LF / rel).write_bytes((SRC / src).read_bytes())
    (LF / "CHANGELOG.md").write_bytes((entry + text).encode("utf-8"))
    (LF / "VERSION").write_bytes(b"0.156.0")
    print("Level Factory 0.155.0 -> 0.156.0")


if __name__ == "__main__":
    main()
