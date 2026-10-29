"""Level Factory 0.267.0: a drill zone names the door it opens (the factory's roadmap 323).

With gameplay events on, Deli Counter 0.291.0's `drill` markers are staged as trigger anchors carrying `zone.drill`,
both edges, the zone's radius and its target interactive (Dispatch 0.8.0). No drill time: the walker's, "no drill time
from the factory". Off, nothing changes.

Proven: tests/unit/test_gameplay_events.py's new test fails on 0.266.0 (fails_on_old.out.txt); the clone's full suite,
2790 tests, 0 failures, 0 errors, 20 skipped (junit).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'level_factory'
PINS = {'CHANGELOG.md': '9bfd619994963475', 'VERSION': 'e42fefdc9a49a1b6', 'packages/staging/dispatch_inputs.py': '6b04b340629b251a', 'tests/unit/test_gameplay_events.py': 'f64728b9aa22c240'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [0.266.0] - the getaway is an end zone a game may be sent\n', '## [0.267.0] - a drill zone names the door it opens\n\nThe factory\'s roadmap 323; the walker: "opening the safe should be a gameplay event where you have to stand in an area\nfor a certain amount of time close to the \'drill\' and then the door opens", then "no drill time from the factory ...\nThese will be networked events programmed somwhere else...we just want the seams/hooks in place". With a level\'s\ngameplay events on, Deli Counter 0.291.0\'s `drill` markers -- where a crew stands to drill a vault door or a deposit\nwall -- are staged as `trigger` anchors whose event carries `zone.drill`, both edges (`fires: ["on_enter",\n"on_exit"]`, Dispatch 0.8.0), the zone\'s `radius` and the `target` interactive it opens. `EVENT_MARKERS` gains\n`drill`; `EVENT_KEYS` names what a marker\'s meta may carry. No drill time, here or anywhere in the factory. Off,\nnothing changes. Tests: tests/unit/test_gameplay_events.py, a drill zone names the door it opens (fails on 0.266.0).\n\n## [0.266.0] - the getaway is an end zone a game may be sent\n')], 'VERSION': [('lines 1-1', '0.266.0', '0.267.0')], 'packages/staging/dispatch_inputs.py': [('lines 39-40', '    "alarm": "trigger",\n}\n', '    "alarm": "trigger",\n    # where a crew stands to drill a vault door or a deposit wall (Deli Counter 0.291.0): a zone naming its target\n    "drill": "trigger",\n}\n'), ('lines 42-42', 'EVENT_MARKERS = ("alarm",)\n', 'EVENT_MARKERS = ("alarm", "drill")\n#: What an event marker\'s `meta` may carry into its anchor\'s event (Dispatch 0.8.0\'s `event_block`): the event, its\n#: firing edges and repeat, a zone\'s `radius` and the interactive it acts on (`target`, 0.267.0), and plain facts.\nEVENT_KEYS = ("event", "audible", "fixture", "fires", "repeat", "radius", "target")\n'), ('lines 107-107', '            ev = {k: v for k, v in rec["meta"].items() if k in ("event", "audible", "fixture", "fires", "repeat")}\n', '            ev = {k: v for k, v in rec["meta"].items() if k in EVENT_KEYS}\n')], 'tests/unit/test_gameplay_events.py': [('lines 97-97', '    assert not any("event" in a for a in site_markers_to_anchors(bare, "lot", events=True))\n', '    assert not any("event" in a for a in site_markers_to_anchors(bare, "lot", events=True))\n\n\nDRILL = {"markers": [\n    {"name": "b0/DRILL_INT_-1_6_OPEN1", "type": "drill", "id": "int_-1_6_open1", "x": -4.0, "y": -2.5, "z": -1.95,\n     "room": "b0/vault_west", "building": "b0",\n     "meta": {"event": "zone.drill", "fires": ["on_enter", "on_exit"], "repeat": "edge", "radius": 1.0,\n              "target": "bank_branch_a02:if:00d81faa", "fixture": "vault_door"}},\n    {"name": "b0/OBJECTIVE_A", "type": "objective", "id": "A", "x": -8.0, "y": 5.0, "z": -3.3, "building": "b0"},\n]}\n\n\ndef test_on_a_drill_zone_is_a_trigger_naming_the_door_it_opens():\n    """0.267.0: Deli Counter 0.291.0\'s drill marker -- where a crew stands to drill, sent on entry and exit -- carries\n    its radius and its target interactive into the anchor\'s event. No drill time: the game\'s. FAILS ON 0.266.0, which\n    drops the marker and would drop the radius and target."""\n    on = markers_to_anchors(DRILL, "lot", events=True)\n    trig, = [a for a in on if a["type"] == "trigger"]\n    assert trig["event"] == {"event": "zone.drill", "fires": ["on_enter", "on_exit"], "repeat": "edge",\n                             "radius": 1.0, "target": "bank_branch_a02:if:00d81faa", "fixture": "vault_door",\n                             "room": "b0/vault_west"}\n    off = markers_to_anchors(DRILL, "lot")\n    assert [a["type"] for a in off] == ["objective"]\n    assert [a for a in on if a["type"] != "trigger"] == off\n')]}
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
