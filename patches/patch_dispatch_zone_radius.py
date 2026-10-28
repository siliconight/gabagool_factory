"""Dispatch 0.7.0: a zone has an extent (the factory's roadmap 323).

The walker, of the trigger zones a player stands in: "we don't do that, we just have the event that we send (without
spamming/rate limiting)". 0.6.0 let an event say `fires: on_enter` and gave it nothing to be entered, so a game
reading `zone.extraction` would have had to invent the size of the getaway's end zone. `anchors.event_block` now
carries `radius` -- metres in plan around the anchor's position -- and requires it, positive and finite, on every
`zone.*` event. A point event (`alarm.*`, `score.*`) needs none.

Proven: tests/test_events.py's new cases fail on 0.6.0 (fails_on_old.out.txt) and the clone's 108 tests pass.
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'dispatch'
PINS = {'CHANGELOG.md': 'a4fc33350466935e', 'VERSION': '97a5d6e540a6120d', 'dispatch/__init__.py': '95c693f823bcf2d6', 'dispatch/anchors.py': '01ac41286aea1183', 'tests/test_events.py': '7bcc0e43b4d8028a'}
EDITS = {'CHANGELOG.md': [('lines 1-2', '# Changelog\n\n', "# Changelog\n\n## v0.7.0 — 2026-10-28\n\n**A zone has an extent.** 0.6.0 let an event say `fires: on_enter` and gave it nothing to be entered: a game reading\n`zone.extraction` would have had to invent the size of the getaway's end zone. `anchors.event_block` now carries\n`radius` -- metres in plan around the anchor's position -- and REQUIRES it, positive and finite, on every `zone.*`\nevent; a point event (`alarm.*`, `score.*`) needs none and may carry one. The registry and the node metadata carry it\nwith the rest of the block. Still data: how long a crew must stand in it, and what that ends, are the game's.\n`tests/test_events.py`: a zone without a real extent is refused (fails on 0.6.0).\n\n")], 'VERSION': [('lines 1-1', '0.6.0\n', '0.7.0\n')], 'dispatch/__init__.py': [('lines 14-14', '__version__ = "0.6.0"\n', '__version__ = "0.7.0"\n')], 'dispatch/anchors.py': [('lines 121-121', '    raises ValueError: a consumer could not read it the way it was meant."""\n', '    raises ValueError: a consumer could not read it the way it was meant. A `zone.*` event carries its\n    ``radius`` (metres in plan, positive): the extent a body enters."""\n'), ('lines 137-138', '            out[k] = str(raw[k])\n    return out\n', '            out[k] = str(raw[k])\n    # A zone is a place a body enters, so it has an extent: `radius`, metres in plan around the anchor\'s position\n    # (0.7.0). Without one `on_enter` has nothing to be entered, and a consumer would have to invent a size.\n    if "radius" in raw or name.startswith("zone."):\n        try:\n            r = float(raw.get("radius"))\n        except (TypeError, ValueError):\n            r = float("nan")\n        if not (r > 0.0 and r < float("inf")):\n            raise ValueError("anchor %s: event %r needs a positive radius in metres, got %r"\n                             % (anchor.id, name, raw.get("radius")))\n        out["radius"] = r\n    return out\n')], 'tests/test_events.py': [('lines 30-30', '                   "event": {"event": "zone.extraction", "fires": "on_enter", "repeat": "edge"}})\n', '                   "event": {"event": "zone.extraction", "fires": "on_enter", "repeat": "edge", "radius": 1.75}})\n'), ('lines 32-33', '    assert ev["fires"] == "on_enter" and ev["repeat"] == "edge" and "audible" not in ev\n\n', '    assert ev["fires"] == "on_enter" and ev["repeat"] == "edge" and "audible" not in ev\n    assert ev["radius"] == 1.75\n\n\n@pytest.mark.parametrize("radius", [None, 0, -1.0, "wide", float("nan"), float("inf")])\ndef test_a_zone_without_a_real_extent_is_refused(radius):\n    """0.7.0: on_enter needs something to be entered. FAILS ON 0.6.0, which takes a zone with no size."""\n    ev = {"event": "zone.extraction", "fires": "on_enter"}\n    if radius is not None:\n        ev["radius"] = radius\n    a, = _anchors({"id": "lot:van", "type": "trigger", "pos": [0, 0, 0], "event": ev})\n    with pytest.raises(ValueError):\n        event_block(a)\n\n\ndef test_a_point_event_needs_no_radius_and_the_registry_carries_a_zones():\n    point, zone = _anchors(\n        {"id": "dc:atm", "type": "trigger", "pos": [0, 0, 0], "event": {"event": "alarm.atm_tampered"}},\n        {"id": "lot:van", "type": "extraction", "pos": [5, 0, 0],\n         "event": {"event": "zone.extraction", "fires": "on_enter", "radius": 1.75}})\n    assert "radius" not in event_block(point)\n    reg = {r["shell_id"].split("/")[-1]: r for r in build_anchor_registry(SPEC, [point, zone])["anchors"]}\n    assert reg["lot:van"]["event"]["radius"] == 1.75\n\n'), ('lines 45-45', '                                   {"event": "zone.x", "repeat": "always"}])\n', '                                   {"event": "zone.x", "repeat": "always", "radius": 2.0}])\n')]}
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
