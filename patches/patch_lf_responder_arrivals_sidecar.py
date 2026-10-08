"""Level Factory 0.157.0: the package says how responders arrive (roadmap 212,
item 204's second half for the arrivals).

Level Factory 0.156.0 put each responder stop in `gameplay_anchors.json`, an
`ai_spawn` tagged `responder`. A Dispatch anchor holds a position and tags;
the rest of an arrival -- the road end a vehicle appears at, the lane it
drives in by, the stop's room, which way it faces -- now ships beside it as
`responder_arrivals.json`, keyed by that anchor's id.

Anchored edits (every anchor once; refuses on a miss):
- `packages/staging/dispatch_inputs.py`: `site_marker_anchor_pairs`, one
  counting of the site-marker anchor ids for the staging and the export;
- `packages/exporting/export.py`: `write_responder_arrivals`, called before
  the glb scan, the closure verdict and the manifest walk; `export_mission
  (lot_gameplay=)`; a paragraph in HANDOFF.md;
- `packages/exporting/closure.py`: the file is metadata, not a resource;
- `apps/cli/commands/__init__.py`: `cmd_export` passes the selected Lot
  candidate's gameplay.
New file from `lf_responder_arrivals_sidecar/`:
`tests/unit/test_responder_arrivals_in_package.py`. CHANGELOG and VERSION
from `lf_responder_arrivals_sidecar/CHANGELOG_0.157.0.md`.

    python patch_lf_responder_arrivals_sidecar.py
    LF_ROOT=<copy> python patch_lf_responder_arrivals_sidecar.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_responder_arrivals_sidecar"
CHANGELOG_HEAD = "## [0.156.0] - The package starts and ends the mission at the getaway van\n"

OLD_SITE_MARKERS_FN = (
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
    '    return anchors\n')
NEW_SITE_MARKERS_FN = (
    'def site_marker_anchor_pairs(gameplay: dict, source: str) -> list:\n'
    '    """``(marker, anchor)`` for each of Lot\'s site-level markers that becomes a\n'
    '    Dispatch anchor (0.156.0, roadmap 204). One counting of the ids for every\n'
    '    reader of them: the staging, and the export\'s `responder_arrivals.json`,\n'
    '    which names each arrival by the anchor it is (0.157.0) -- two spellings\n'
    '    of one id would be two places for it to drift.\n'
    '\n'
    '    `_iter_records` reads `markers`, `objectives` and `loot`, and the site\'s\n'
    '    own markers live in `site_markers` -- so until 0.156.0 no site-level\n'
    '    marker reached Dispatch. The getaway van\'s crew spawn and extraction\n'
    '    never became the package\'s; `ensure_mission_anchors` synthesized a\n'
    '    `player_start` at the centroid of every Lot anchor and tagged every\n'
    '    building\'s extraction as the mission\'s (cold run 9198\'s package:\n'
    '    `lot:mission_start` at (-7.03, 0.68), 14 m from the van).\n'
    '\n'
    '    A site marker stands on the plate: `at` is a plan point, and its height\n'
    '    is the ground\'s, as `lot._walk_positions` reads it. No facing is\n'
    '    passed: a Lot slot yaw and a Dispatch `rot_y` have not been shown to\n'
    '    share a convention, and a yaw read in the wrong one is silently wrong."""\n'
    '    pairs: list = []\n'
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
    '        pairs.append((m, anchor))\n'
    '    return pairs\n'
    '\n'
    '\n'
    'def site_markers_to_anchors(gameplay: dict, source: str) -> list:\n'
    '    """Lot\'s site-level markers as Dispatch anchors: the anchors of\n'
    '    `site_marker_anchor_pairs`."""\n'
    '    return [anchor for _m, anchor in site_marker_anchor_pairs(gameplay, source)]\n')

EDITS = {
    "packages/staging/dispatch_inputs.py": [
        (OLD_SITE_MARKERS_FN, NEW_SITE_MARKERS_FN),
    ],
    "packages/exporting/export.py": [
        ('    clutter_dir: Path | None = None,\n'
         ') -> ExportResult:\n',
         '    clutter_dir: Path | None = None,\n'
         '    #: Where responders arrive (0.157.0, roadmap 212): the selected Lot\n'
         '    #: candidate\'s `site.site.gameplay.json`, read for its\n'
         '    #: `responder_plan`. None for a caller with nothing to pass, and then\n'
         '    #: the package is exactly what it was.\n'
         '    lot_gameplay: Path | None = None,\n'
         ') -> ExportResult:\n'),
        ('def strip_dead_node_paths(export_dir: Path) -> dict:\n',
         '#: The package\'s account of how responders arrive (0.157.0, roadmap 212).\n'
         'RESPONDER_ARRIVALS_NAME = "responder_arrivals.json"\n'
         '\n'
         '\n'
         'def _package_xz(x, y) -> list:\n'
         '    """A site plan point in the package\'s frame: x, then z = -(site y).\n'
         '    `+ 0.0` so a point on the axis writes 0.0, not -0.0."""\n'
         '    return [x + 0.0, -y + 0.0]\n'
         '\n'
         '\n'
         'def write_responder_arrivals(export_dir: Path, lot_gameplay) -> dict | None:\n'
         '    """How each responder arrives, in the package\'s frame -- or None, and no\n'
         '    file, when Lot\'s gameplay carries no `responder_plan`.\n'
         '\n'
         '    The walker, 2026-10-08: "have responders show up after the job, on the\n'
         '    way back (and this would be on the gameplay layer, but we can make thee\n'
         '    assets and ensure there is clearance and routes for their arrival)".\n'
         '    Lot 0.99.0 plans each arrival and reserves its lane and its stop from\n'
         '    everything it stands in the street. 0.156.0 put each stop in\n'
         '    `gameplay_anchors.json` as an `ai_spawn` tagged `responder`. A Dispatch\n'
         '    anchor holds a position and tags, so the rest is here, keyed by that\n'
         '    anchor\'s id: the road end a vehicle appears at, the stop, which way it\n'
         '    faces arriving, the lane and stop boxes nothing else stands in, and the\n'
         '    point of the crew\'s way back the stop was chosen for.\n'
         '\n'
         '    Frame: Godot -- x, y up, z = -(site y) -- metres, the frame of every\n'
         '    position in `gameplay_anchors.json`; the ground at y 0. A box is the\n'
         '    x/z extent of a plan rect. Lot\'s output from before 0.99.0 carries no\n'
         '    `responder_plan`, and its package is exactly what it was."""\n'
         '    import math\n'
         '    if not lot_gameplay or not Path(lot_gameplay).is_file():\n'
         '        return None\n'
         '    gp = json.loads(Path(lot_gameplay).read_text(encoding="utf-8"))\n'
         '    if "responder_plan" not in gp:\n'
         '        return None\n'
         '    from packages.staging.dispatch_inputs import site_marker_anchor_pairs\n'
         '    arrivals = []\n'
         '    for marker, anchor in site_marker_anchor_pairs(gp, "lot"):\n'
         '        a = marker.get("arrival")\n'
         '        if marker.get("type") != "responder_spawn" or not isinstance(a, dict):\n'
         '            continue\n'
         '        (ex, ez), (sx, sz) = _package_xz(*a["entry"][:2]), _package_xz(*a["stop"][:2])\n'
         '        dx, dz = sx - ex, sz - ez\n'
         '        n = math.hypot(dx, dz) or 1.0\n'
         '        tx, tz = _package_xz(*a["toward"][:2])\n'
         '        boxes = {}\n'
         '        for key in ("stop_box", "lane_box"):\n'
         '            x0, y0, x1, y1 = a[key]\n'
         '            boxes[key] = {"min": _package_xz(x0, y1), "max": _package_xz(x1, y0)}\n'
         '        arrivals.append({\n'
         '            "anchor": anchor["id"],\n'
         '            "entry": [ex, 0.0, ez], "stop": [sx, 0.0, sz],\n'
         '            "forward": [dx / n, 0.0, dz / n],\n'
         '            "vehicle_m": list(a.get("vehicle") or []),\n'
         '            "stop_box": boxes["stop_box"], "lane_box": boxes["lane_box"],\n'
         '            "toward": [tx, 0.0, tz],\n'
         '            "to_way_back_m": a.get("to_way_back"), "run_m": a.get("run"),\n'
         '        })\n'
         '    doc = {"schema": "level_factory.responder_arrivals.v1",\n'
         '           "frame": "Godot: x, y up, z = -(site y); metres; the ground at y 0",\n'
         '           "what": ("Where responders can arrive. The factory reserves each "\n'
         '                    "lane and stop; spawning and timing responders is the "\n'
         '                    "runtime\'s. Each `anchor` is an `ai_spawn` tagged "\n'
         '                    "`responder` in gameplay_anchors.json."),\n'
         '           "arrivals": arrivals}\n'
         '    (export_dir / RESPONDER_ARRIVALS_NAME).write_text(pretty_dumps(doc), encoding="utf-8")\n'
         '    return doc\n'
         '\n'
         '\n'
         'def strip_dead_node_paths(export_dir: Path) -> dict:\n'),
        ('    bindings = strip_dead_node_paths(export_dir)\n'
         '    if bindings.get("moved_total"):\n'
         '        print("[export] %d handoff node path(s) named nothing in the package "\n'
         '              "and were moved to node_dispatch -- see handoff_bindings.json"\n'
         '              % bindings["moved_total"])\n',
         '    bindings = strip_dead_node_paths(export_dir)\n'
         '    if bindings.get("moved_total"):\n'
         '        print("[export] %d handoff node path(s) named nothing in the package "\n'
         '              "and were moved to node_dispatch -- see handoff_bindings.json"\n'
         '              % bindings["moved_total"])\n'
         '\n'
         '    # 4.81 HOW RESPONDERS ARRIVE (0.157.0, roadmap 212). Above the glb\n'
         '    # scan, the closure verdict and the manifest walk, so the file is inside\n'
         '    # the package each of them describes and the manifest lists it.\n'
         '    # `closure._METADATA_FILES` names it: its anchor ids are shaped like the\n'
         '    # NodePath strings the authoring-path test reads as paths, the reasoning\n'
         '    # that put `handoff_bindings.json` there.\n'
         '    arrivals_doc = write_responder_arrivals(export_dir, lot_gameplay)\n'
         '    if arrivals_doc is not None:\n'
         '        print("[export] responder arrivals: %d, in %s"\n'
         '              % (len(arrivals_doc["arrivals"]), RESPONDER_ARRIVALS_NAME))\n'),
        ('    "Level Factory and its authoring tools are not required to consume this package.\\n\\n"\n',
         '    "WHERE THE MISSION STARTS AND ENDS, AND WHERE RESPONDERS ARRIVE. "\n'
         '    "`gameplay_anchors.json` tags the mission\'s start `mission_start` and its exit "\n'
         '    "`extraction` -- on a heist, both at the crew\'s getaway van -- and tags each "\n'
         '    "place responders can arrive `responder`. `responder_arrivals.json`, when "\n'
         '    "present, says how each arrives: the road end a vehicle appears at, the lane it "\n'
         '    "drives in by and the stop it pulls up at, both kept clear by the factory, and "\n'
         '    "which way it faces. Spawning and timing responders is your runtime\'s.\\n\\n"\n'
         '    "Level Factory and its authoring tools are not required to consume this package.\\n\\n"\n'),
    ],
    "packages/exporting/closure.py": [
        ('_METADATA_FILES = {\n'
         '    "portable_resource_manifest.json", "LICENSES.json", "export_profile.json",\n',
         '_METADATA_FILES = {\n'
         '    # 0.157.0: how responders arrive. LF\'s own account, read by no Godot\n'
         '    # loader, whose anchor ids (`lot:responder_arrival_...`) are shaped like\n'
         '    # the NodePath strings the authoring-path test reads as paths.\n'
         '    "responder_arrivals.json",\n'
         '    "portable_resource_manifest.json", "LICENSES.json", "export_profile.json",\n'),
    ],
    "apps/cli/commands/__init__.py": [
        ('        clutter_dir=clutter_dir if clutter_dir.is_dir() else None,\n'
         '    )\n',
         '        clutter_dir=clutter_dir if clutter_dir.is_dir() else None,\n'
         '        # how responders arrive (0.157.0, roadmap 212): the selected\n'
         '        # candidate\'s Lot gameplay, read for its `responder_plan`\n'
         '        lot_gameplay=(lot_out / "site.site.gameplay.json"\n'
         '                      if lot_out is not None\n'
         '                      and (lot_out / "site.site.gameplay.json").is_file()\n'
         '                      else None),\n'
         '    )\n'),
    ],
}

NEW = {
    pathlib.Path("tests") / "unit" / "test_responder_arrivals_in_package.py":
        "test_responder_arrivals_in_package.py",
}


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.156.0", repr(v)
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
    entry = (SRC / "CHANGELOG_0.157.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
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
    (LF / "VERSION").write_bytes(b"0.157.0")
    print("Level Factory 0.156.0 -> 0.157.0")


if __name__ == "__main__":
    main()
