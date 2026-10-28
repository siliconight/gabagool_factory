"""Level Factory 0.266.0: the getaway is an end zone a game may be sent (the factory's roadmap 323).

With a level's gameplay events on, the getaway's extraction anchor carries `zone.extraction` (on_enter, edge) with
the radius Lot 0.136.0 states, for Dispatch 0.7.0. An extraction with no stated extent gets no zone. Off, nothing
changes; on, no id moves.

Proven: tests/unit/test_gameplay_events.py's two new tests fail on 0.265.1 (fails_on_old.out.txt); the clone's full
suite, 2789 tests, 0 failures, 0 errors, 20 skipped (junit).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'level_factory'
PINS = {'CHANGELOG.md': '5002232c22cd7870', 'VERSION': '352df9a2ae83b66f', 'packages/staging/dispatch_inputs.py': '72f37d13a808e019', 'tests/unit/test_gameplay_events.py': '2b68e408c7480765'}
EDITS = {'CHANGELOG.md': [('lines 1-1', "## [0.265.1] - an event never moves another anchor's id\n", '## [0.266.0] - the getaway is an end zone a game may be sent\n\nThe factory\'s roadmap 323; the walker, of the zones a crew stands in after a score: "we don\'t do that, we just have\nthe event that we send (without spamming/rate limiting)". With a level\'s gameplay events on, the getaway\'s extraction\nanchor carries `zone.extraction`: sent once as a body enters it (`fires: on_enter`, `repeat: edge`), its `radius` the\nextent Lot 0.136.0 states (`zone_radius`, 1.75 m: the crew\'s spawn to the van body plus a body). Dispatch 0.7.0\nrequires that radius on every zone. An extraction with no stated extent -- a designer\'s own, or a site with no van --\ngets no zone: a size invented here would be a claim about geometry staging never saw. Off, nothing changes; on, no id\nmoves (the event rides an anchor that already existed, still tagged the mission\'s extraction).\n`dispatch_inputs.ZONE_EVENTS`, `site_markers_to_anchors(events=)`. Tests: tests/unit/test_gameplay_events.py, the\ngetaway is an end zone a body enters (fails on 0.265.1).\n\n## [0.265.1] - an event never moves another anchor\'s id\n')], 'VERSION': [('lines 1-1', '0.265.1', '0.266.0')], 'packages/staging/dispatch_inputs.py': [('lines 168-168', 'def site_markers_to_anchors(gameplay: dict, source: str) -> list:\n', '#: Lot\'s site-level markers that state a zone a crew enters -> the event a\n#: game may be sent when one does (0.266.0, the factory\'s roadmap 323).\nZONE_EVENTS = {"extraction": "zone.extraction"}\n\n\ndef site_markers_to_anchors(gameplay: dict, source: str, events: bool = False) -> list:\n'), ('lines 170-171', '    `site_marker_anchor_pairs`."""\n    return [anchor for _m, anchor in site_marker_anchor_pairs(gameplay, source)]\n', '    `site_marker_anchor_pairs`.\n\n    With ``events`` on, a marker in `ZONE_EVENTS` that states its extent\n    (Lot 0.136.0\'s ``zone_radius``, metres) carries its zone event: sent once\n    as a body enters it (`on_enter`, `edge`), Dispatch 0.7.0\'s ``radius``\n    the extent. A marker with no stated extent gets none: a size invented here\n    would be a claim about geometry this file never saw. The ids are\n    `site_marker_anchor_pairs`\' either way -- an event never moves one."""\n    out = []\n    for m, anchor in site_marker_anchor_pairs(gameplay, source):\n        name = ZONE_EVENTS.get(str(m.get("type") or ""))\n        radius = _num(m.get("zone_radius")) if events and name else 0.0\n        if 0.0 < radius < float("inf"):\n            anchor["event"] = {"event": name, "fires": "on_enter", "repeat": "edge", "radius": radius}\n        out.append(anchor)\n    return out\n'), ('lines 328-328', '        site_markers_to_anchors(lot_gp, "lot") + markers_to_anchors(lot_gp, "lot", lot_up, events=events),\n', '        site_markers_to_anchors(lot_gp, "lot", events=events)\n        + markers_to_anchors(lot_gp, "lot", lot_up, events=events),\n')], 'tests/unit/test_gameplay_events.py': [('lines 15-15', 'from packages.staging.dispatch_inputs import markers_to_anchors  # noqa: E402\n', 'from packages.staging.dispatch_inputs import (ensure_mission_anchors, markers_to_anchors,  # noqa: E402\n                                              site_markers_to_anchors)\n'), ('lines 67-67', '    assert before == off == on, (before, off, on)\n', '    assert before == off == on, (before, off, on)\n\n\nSITE = {"site_markers": [\n    {"type": "crew_spawn", "at": [10.0, -4.0], "source": "getaway_van"},\n    {"type": "extraction", "at": [10.0, -4.0], "source": "getaway_van", "getaway": "step_van", "zone_radius": 1.75},\n    {"type": "responder_spawn", "at": [40.0, -4.0]},\n]}\n\n\ndef test_on_the_getaway_is_an_end_zone_a_body_enters():\n    """0.266.0: Lot 0.136.0\'s extraction states its extent, and with the switch on the extraction anchor carries\n    `zone.extraction`, sent once as a body enters it, with Dispatch 0.7.0\'s radius. FAILS ON 0.265.1, which sends no\n    zone."""\n    on = site_markers_to_anchors(SITE, "lot", events=True)\n    zone, = [a for a in on if "event" in a]\n    assert zone["type"] == "extraction" and zone["pos"] == [10.0, -4.0, 0.0]\n    assert zone["event"] == {"event": "zone.extraction", "fires": "on_enter", "repeat": "edge", "radius": 1.75}\n    # the mission still binds to it: the end zone IS the mission\'s extraction\n    assert "extraction" in ensure_mission_anchors(on, "lot")[1]["tags"]\n\n\ndef test_off_or_without_a_stated_extent_there_is_no_zone_and_no_id_moves():\n    off = site_markers_to_anchors(SITE, "lot")\n    on = site_markers_to_anchors(SITE, "lot", events=True)\n    assert not any("event" in a for a in off)\n    assert [a["id"] for a in off] == [a["id"] for a in on]\n    assert [{k: v for k, v in a.items() if k != "event"} for a in on] == off\n    bare = {"site_markers": [dict(SITE["site_markers"][1], zone_radius=None)]}\n    assert not any("event" in a for a in site_markers_to_anchors(bare, "lot", events=True))\n')]}
WHOLE = {}
NEW_FILES = {}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s/%s has mixed line endings; nothing written" % (REPO.name, name))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %s/%s is %s, not the %s this patch was written against; nothing written"
                         % (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %s/%s: the anchor at %s is there %d times; nothing written"
                                 % (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
