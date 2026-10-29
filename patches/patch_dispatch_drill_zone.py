"""Dispatch 0.8.0: a zone may fire on entry and exit, and name what it acts on (the factory's roadmap 323).

The walker: "opening the safe should be a gameplay event where you have to stand in an area for a certain amount of
time close to the 'drill' and then the door opens". `fires` may list rules, normalised to the vocabulary's order (one
rule stays a string); `target` names the interactive the event acts on. The hold's length is the game's.

Proven: tests/test_events.py's new tests fail on 0.7.0 (fails_on_old.out.txt); the clone's 114 tests pass.
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'dispatch'
PINS = {'CHANGELOG.md': '631dd201dd5ec0df', 'VERSION': '967d9afb10134666', 'dispatch/__init__.py': '64395d83bef5a23b', 'dispatch/anchors.py': '91e33c5c42169bfa', 'tests/test_events.py': '000ea0de10d5eec9'}
EDITS = {'CHANGELOG.md': [('lines 1-2', '# Changelog\n\n', '# Changelog\n\n## v0.8.0 — 2026-10-28\n\n**A zone may fire on entry and exit, and name what it acts on.** The factory\'s walker: "opening the safe should be a\ngameplay event where you have to stand in an area for a certain amount of time close to the \'drill\' and then the\ndoor opens". A game times that hold itself, so it must hear both edges: `fires` may list several rules\n(`["on_enter", "on_exit"]`), normalised to the vocabulary\'s order; one rule stays a string, so every block written\nbefore reads exactly as it did. `target` names the interactive the event acts on -- a vault door\'s id, whose states\n(locked, unlocked, open, breached) the game already drives -- and is carried with the rest. How long a drill takes,\nwhether it pauses or jams, and what it sets off are the game\'s. `tests/test_events.py` (fails on 0.7.0).\n\n')], 'VERSION': [('lines 1-1', '0.7.0\n', '0.8.0\n')], 'dispatch/__init__.py': [('lines 14-14', '__version__ = "0.7.0"\n', '__version__ = "0.8.0"\n')], 'dispatch/anchors.py': [('lines 122-122', '    ``radius`` (metres in plan, positive): the extent a body enters."""\n', '    ``radius`` (metres in plan, positive): the extent a body enters.\n\n    0.8.0: ``fires`` may list several rules -- a drill zone is sent as a body enters AND as it leaves, so a game can\n    time the hold itself -- normalised to the vocabulary\'s order; one rule stays a string, so every block written\n    before is read exactly as it was. ``target`` names the interactive the event acts on (a vault door\'s id), passed\n    through; what acting means -- how long a drill takes, what opens -- is the game\'s."""\n'), ('lines 131-133', '    out = {"event": name, "fires": str(raw.get("fires", "on_touch")), "repeat": str(raw.get("repeat", "edge"))}\n    if out["fires"] not in EVENT_FIRES or out["repeat"] not in EVENT_REPEAT:\n        raise ValueError("anchor %s: event %r fires %r repeat %r" % (anchor.id, name, out["fires"], out["repeat"]))\n', '    fires = raw.get("fires", "on_touch")\n    rules = [fires] if isinstance(fires, str) else list(fires) if isinstance(fires, (list, tuple)) else [None]\n    out = {"event": name, "repeat": str(raw.get("repeat", "edge"))}\n    if (not rules or len(set(rules)) != len(rules) or any(r not in EVENT_FIRES for r in rules)\n            or out["repeat"] not in EVENT_REPEAT):\n        raise ValueError("anchor %s: event %r fires %r repeat %r" % (anchor.id, name, fires, out["repeat"]))\n    ordered = [r for r in EVENT_FIRES if r in rules]\n    out = {"event": name, "fires": ordered[0] if len(ordered) == 1 else ordered, "repeat": out["repeat"]}\n'), ('lines 136-136', '    for k in ("fixture", "room"):\n', '    for k in ("fixture", "room", "target"):\n')], 'tests/test_events.py': [('lines 76-76', '    assert EVENT_FIRES == ("on_touch", "on_enter", "on_exit") and EVENT_REPEAT == ("edge", "once")\n', '    assert EVENT_FIRES == ("on_touch", "on_enter", "on_exit") and EVENT_REPEAT == ("edge", "once")\n\n\ndef test_a_drill_zone_fires_on_entry_and_exit_and_names_its_door():\n    """0.8.0: a drill zone is sent as a body enters and as it leaves, so a game times the hold; it names the\n    interactive it acts on. FAILS ON 0.7.0, which takes one rule and drops the target."""\n    a, = _anchors({"id": "dc:drill", "type": "trigger", "pos": [0, 0, 0],\n                   "event": {"event": "zone.drill", "fires": ["on_exit", "on_enter"], "radius": 1.0,\n                             "target": "bank_branch_a02:if:5f1e", "fixture": "vault_door"}})\n    ev = event_block(a)\n    assert ev["fires"] == ["on_enter", "on_exit"] and ev["target"] == "bank_branch_a02:if:5f1e"\n    reg = {r["shell_id"].split("/")[-1]: r for r in build_anchor_registry(SPEC, [a])["anchors"]}\n    assert reg["dc:drill"]["event"]["fires"] == ["on_enter", "on_exit"]\n\n\n@pytest.mark.parametrize("fires", [[], ["on_enter", "on_enter"], ["on_enter", "while_inside"], 3])\ndef test_a_firing_list_a_consumer_could_not_read_is_refused(fires):\n    a, = _anchors({"id": "dc:bad", "type": "trigger", "pos": [0, 0, 0],\n                   "event": {"event": "zone.drill", "fires": fires, "radius": 1.0}})\n    with pytest.raises(ValueError):\n        event_block(a)\n\n\ndef test_one_rule_is_still_a_string():\n    a, = _anchors({"id": "lot:van", "type": "extraction", "pos": [0, 0, 0],\n                   "event": {"event": "zone.extraction", "fires": ["on_enter"], "radius": 1.75}})\n    assert event_block(a)["fires"] == "on_enter"\n')]}
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
