"""Level Factory 0.158.0: the package marks the score, names each anchor's
building, and carries no anchor from a building that is not there (roadmap
204's remaining half).

Anchored edits (every anchor once; refuses on a miss):
- `packages/staging/dispatch_inputs.py`:
  - `markers_to_anchors` passes a marker's `building` through, which Dispatch
    writes as `source_building`;
  - `stage_dispatch_inputs(lot_site=)` stages the generated Deli Counter
    shell's anchors only when Lot's site gameplay carries no markers, and
    tags the site's objective building's objective anchors `score`;
  - `mission_flow`, read off the staged Lot anchors.
- `apps/cli/commands/__init__.py`: `_write_dispatch_spec` passes the Lot
  job's drawn site spec and writes `mission_flow(stage_dir)`.
New file from `lf_package_score/`: `tests/unit/test_dispatch_score_and_buildings.py`.
CHANGELOG and VERSION from `lf_package_score/CHANGELOG_0.158.0.md`.

    python patch_lf_package_score.py
    LF_ROOT=<copy> python patch_lf_package_score.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_package_score"
CHANGELOG_HEAD = "## [0.157.0] - The package says how responders arrive\n"

EDITS = {
    "packages/staging/dispatch_inputs.py": [
        ('        if rec.get("objective"):\n'
         '            anchor["objective"] = str(rec["objective"])\n'
         '        if "rot_y" in rec or "rot" in rec:\n'
         '            anchor["rot_y"] = _num(rec.get("rot_y", rec.get("rot")))\n'
         '        anchors.append(anchor)\n',
         '        if rec.get("objective"):\n'
         '            anchor["objective"] = str(rec["objective"])\n'
         '        if "rot_y" in rec or "rot" in rec:\n'
         '            anchor["rot_y"] = _num(rec.get("rot_y", rec.get("rot")))\n'
         '        # THE BUILDING IT BELONGS TO (0.158.0, roadmap 204). Lot\n'
         '        # namespaces each marker by its building, and Dispatch writes an\n'
         '        # anchor\'s `building` as its `source_building` -- which was "" on\n'
         '        # every anchor of every package, because this never passed it.\n'
         '        if rec.get("building"):\n'
         '            anchor["building"] = str(rec["building"])\n'
         '        anchors.append(anchor)\n'),
        ('def stage_dispatch_inputs(dest_dir: Path, *, deli_gameplay: Path, shell_glb: Path,\n'
         '                          lot_gameplay: Path, mission_id: str,\n'
         '                          theme: str = "", up: str = "z") -> dict:\n'
         '    """Write Dispatch-shaped deli_counter/ and lot/ input trees under dest_dir.\n'
         '    Returns {"deli_counter": <manifest path>, "lot": <manifest path>}."""\n',
         'def stage_dispatch_inputs(dest_dir: Path, *, deli_gameplay: Path, shell_glb: Path,\n'
         '                          lot_gameplay: Path, mission_id: str,\n'
         '                          theme: str = "", up: str = "z",\n'
         '                          lot_site: Path | None = None) -> dict:\n'
         '    """Write Dispatch-shaped deli_counter/ and lot/ input trees under dest_dir.\n'
         '    Returns {"deli_counter": <manifest path>, "lot": <manifest path>}.\n'
         '\n'
         '    ``lot_site`` is the Lot job\'s drawn site spec (`site.site.drawn.json`),\n'
         '    read for which building is the score (0.158.0); without it nothing is\n'
         '    tagged `score`, and `mission_flow` writes the two beats it always did."""\n'),
        ('    # ---- deli_counter (collision shell) ----\n'
         '    dc_gp = _read_json(deli_gameplay)\n',
         '    # ---- deli_counter (collision shell) ----\n'
         '    # THE SITE CARRIES ITS BUILDINGS (0.158.0, roadmap 204). Lot\'s gameplay\n'
         '    # holds every placed building\'s markers in site space -- the\n'
         '    # generated shell\'s among them, when the lot places it. Staged beside\n'
         '    # them, the shell\'s own were wrong either way:\n'
         '    #   * on a library lot the shell is never placed, so they were the\n'
         '    #     anchors of a building that is not in the level, listed first\n'
         '    #     (cold run 9194: its vault objective among them);\n'
         '    #   * on deli_001 (cold run 9191), where it is placed, as b0 at (6, 0),\n'
         '    #     all 85 duplicated Lot\'s b0 anchors by name, in the shell\'s own\n'
         '    #     frame, 6 m off.\n'
         '    # So the shell side is staged only when the site has no markers to\n'
         '    # stand in for it. Its glb still passes through: it is the resolver\'s\n'
         '    # file check, not an anchor.\n'
         '    site_has_markers = bool(_read_json(Path(lot_gameplay)).get("markers"))\n'
         '    dc_gp = {} if site_has_markers else _read_json(deli_gameplay)\n'),
        ('    lot_anchors = ensure_mission_anchors(\n'
         '        site_markers_to_anchors(lot_gp, "lot") + markers_to_anchors(lot_gp, "lot", lot_up),\n'
         '        "lot", lot_up)\n',
         '    lot_anchors = ensure_mission_anchors(\n'
         '        site_markers_to_anchors(lot_gp, "lot") + markers_to_anchors(lot_gp, "lot", lot_up),\n'
         '        "lot", lot_up)\n'
         '    # THE SCORE (0.158.0, roadmap 204): the objective anchors of the site\'s\n'
         '    # objective building, tagged so the mission flow can bind a beat to\n'
         '    # them. Every anchor carried `"objective": ""`, so a package could not\n'
         '    # say which of its objectives was the job.\n'
         '    score = str(_read_json(Path(lot_site)).get("objective") or "") if lot_site else ""\n'
         '    if score:\n'
         '        for a in lot_anchors:\n'
         '            if a.get("type") == "objective" and a.get("building") == score:\n'
         '                a["tags"] = list(a.get("tags") or ()) + [SCORE_TAG]\n'),
        ('    return {"deli_counter": str(deli_dir / "shell.gameplay.json"),\n'
         '            "lot": str(lot_dir / "lot.layout.json")}\n',
         '    return {"deli_counter": str(deli_dir / "shell.gameplay.json"),\n'
         '            "lot": str(lot_dir / "lot.layout.json")}\n'
         '\n'
         '\n'
         '#: The tag the score\'s objective anchors carry, and the beat that binds them.\n'
         'SCORE_TAG = "score"\n'
         '\n'
         '\n'
         'def mission_flow(dest_dir: Path) -> list:\n'
         '    """The minimal flow for the staged inputs under ``dest_dir``: spawn, the\n'
         '    score when the staging tagged one, extract (0.158.0).\n'
         '\n'
         '    Still minimal and non-binding -- the gameplay team authors the real\n'
         '    objectives -- but a heist has three beats, and the package said two.\n'
         '    The score beat is written only when some anchor carries the tag:\n'
         '    Dispatch refuses a mission whose beat binds to no anchor ("BLOCKER\n'
         '    [assembly] Proposed beat \'extract\' binds to no anchor"), which is why\n'
         '    `ensure_mission_anchors` exists."""\n'
         '    staged = _read_json(Path(dest_dir) / "lot" / "lot.gameplay.json")\n'
         '    flow = [{"step": "spawn", "location_tag": "mission_start"}]\n'
         '    if any(SCORE_TAG in (a.get("tags") or ()) for a in staged.get("anchors", []) or []):\n'
         '        flow.append({"step": "score", "objective": SCORE_TAG})\n'
         '    flow.append({"step": "extract", "location_tag": "extraction"})\n'
         '    return flow\n'),
    ],
    "apps/cli/commands/__init__.py": [
        ('    from packages.staging.dispatch_inputs import stage_dispatch_inputs\n'
         '\n'
         '    stage_dir = ws.internal_dir / "temp" / model.mission_id / "dispatch_inputs"\n',
         '    from packages.staging.dispatch_inputs import mission_flow, stage_dispatch_inputs\n'
         '\n'
         '    stage_dir = ws.internal_dir / "temp" / model.mission_id / "dispatch_inputs"\n'),
        ('        lot_gameplay=_latest_output(lot_out, "site.site.gameplay.json"),\n'
         '        mission_id=model.mission_id,\n'
         '        theme=model.theme or "",\n'
         '    )\n',
         '        lot_gameplay=_latest_output(lot_out, "site.site.gameplay.json"),\n'
         '        mission_id=model.mission_id,\n'
         '        theme=model.theme or "",\n'
         '        # which building is the score (0.158.0): the spec as Lot drew it\n'
         '        lot_site=_latest_output(lot_out, "site.site.drawn.json"),\n'
         '    )\n'),
        ('        "mission_flow": [\n'
         '            {"step": "spawn", "location_tag": "mission_start"},\n'
         '            {"step": "extract", "location_tag": "extraction"},\n'
         '        ],\n',
         '        # spawn, the score when the staging tagged one, extract (0.158.0)\n'
         '        "mission_flow": mission_flow(stage_dir),\n'),
    ],
}

NEW = {
    pathlib.Path("tests") / "unit" / "test_dispatch_score_and_buildings.py":
        "test_dispatch_score_and_buildings.py",
}


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.157.0", repr(v)
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
    entry = (SRC / "CHANGELOG_0.158.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
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
    (LF / "VERSION").write_bytes(b"0.158.0")
    print("Level Factory 0.157.0 -> 0.158.0")


if __name__ == "__main__":
    main()
