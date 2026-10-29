"""Deli Counter 0.291.0: where a crew stands to drill (the factory's roadmap 323).

Every vault door and deposit wall writes one `drill` marker: a zone in front of its face (half the slot's depth plus
the contract's body radius out; radius half the opening's width plus that radius), `zone.drill` on entry and exit,
naming the interactive it opens. No drill time: the walker's, "no drill time from the factory ... we just want the
seams/hooks in place".

Proven: tests/test_drill_zones.py fails on 0.290.0 (fails_on_old.out.txt); the clone built (build.py --all) and passed
check.py, the commit hook's gate.
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'deli_counter'
PINS = {'CHANGELOG.md': '043ac2a8472be9ea', 'VERSION': 'dee993f3c5012ec6', 'deli_counter.py': 'e7f9d848db26e33e', 'score_alarms.py': 'cf6021c51dc98841'}
EDITS = {'CHANGELOG.md': [('lines 1-1', "## [0.290.0] - a bank's vault gate is a vault door\n", '## [0.291.0] - where a crew stands to drill\n\nThe factory\'s roadmap 323; the walker: "opening the safe should be a gameplay event where you have to stand in an\narea for a certain amount of time close to the \'drill\' and then the door opens", then "no drill time from the factory\n... These will be networked events programmed somwhere else...we just want the seams/hooks in place on some level so\nwe can invoke them visually on peoples clients if needed later (muiltiplayer game)". Every vault door and deposit wall\n(`score_alarms.DRILL_FIXTURES`) writes one `drill` marker, `drill_<slot>`: a zone in front of its face\n(`score_alarms.drill_zone` -- its centre half the slot\'s depth plus the contract\'s body radius out along the slot\'s\nfacing, its radius half the opening\'s width plus that radius: 1.0 m at a vault door), its event `zone.drill` sent on\nentry and exit, `repeat: edge`, and its `target` the interactive it opens -- a vault door\'s (locked, unlocked, open,\nbreached), a deposit unit\'s (intact, drilled). A vault door\'s zone stands in the room it is entered from; a deposit\nwall\'s inside the vault, before the boxes. No drill time, timer or response: the game\'s. Level Factory 0.267.0 stages\nit for Dispatch 0.8.0 when a level\'s gameplay events are on. Tests: tests/test_drill_zones.py (fails on 0.290.0).\n\n## [0.290.0] - a bank\'s vault gate is a vault door\n')], 'VERSION': [('lines 1-1', 'Deli Counter 0.290.0', 'Deli Counter 0.291.0')], 'deli_counter.py': [('lines 3311-3314', '                "meta": {"event": row[2], "audible": row[3], "fixture": row[1]}})\n            n += 1\n        return n\n\n', '                "meta": {"event": row[2], "audible": row[3], "fixture": row[1]}})\n            n += 1\n        # ...and where a crew stands to drill a vault door or a deposit wall (0.291.0): one `drill` marker per slot a\n        # `DRILL_FIXTURES` row names, at `score_alarms.drill_zone`, naming the interactive it opens. No drill time.\n        import agent_contract\n        body = agent_contract.body_radius()\n        for s in self.slots:\n            if not any(s.get(k) == v for k, v in score_alarms.DRILL_FIXTURES):\n                continue\n            zone = score_alarms.drill_zone(s, body)\n            if zone is None:\n                continue\n            x, y, z, radius = zone\n            story = s.get("story")\n            story = int(story) if story is not None else int(math.floor((z + 1e-6) / H))\n            holding = [r for r in rooms if int(r.get("story", 0) or 0) == story\n                       and r["bounds"][0] <= x <= r["bounds"][2] and r["bounds"][1] <= y <= r["bounds"][3]]\n            room = min(holding, key=lambda r: (r["bounds"][2] - r["bounds"][0]) * (r["bounds"][3] - r["bounds"][1]),\n                       default=None)\n            name = "DRILL_%s" % s["slot_id"].upper()\n            self._empty(name, (x, y, z), self.MARKERS)\n            self.gameplay["markers"].append({\n                "name": name, "type": "drill", "id": "drill_" + s["slot_id"], "x": round(x, 4), "y": round(y, 4),\n                "z": z, "rot_z": 0.0, "room": room["id"] if room else None,\n                "meta": {"event": "zone.drill", "fires": ["on_enter", "on_exit"], "repeat": "edge",\n                         "radius": round(radius, 4), "target": s["interactive"]["id"], "fixture": s["role"]}})\n            n += 1\n        return n\n\n')], 'score_alarms.py': [('lines 22-22', ')\n', ')\n\n\n#: WHERE A DRILL STANDS (0.291.0, the factory\'s roadmap 323). The walker: "opening the safe should be a gameplay event\n#: where you have to stand in an area for a certain amount of time close to the \'drill\' and then the door opens". A\n#: drill zone is DATA like a hook: where the crew stands to drill, sent as a body enters it and as it leaves (Dispatch\n#: 0.8.0\'s two-rule `fires`), naming the interactive it opens (`target`). How long the drill takes, whether it pauses\n#: or jams, and what it sets off are the game\'s. (key, value) -- the slot\'s `role`: a vault door, whose interactive\n#: goes locked -> unlocked -> open, and a deposit unit, whose goes intact -> drilled.\nDRILL_FIXTURES = (\n    ("role", "vault_door"),\n    ("role", "safe_deposit_boxes"),\n)\n\n\ndef drill_zone(slot, body_radius):\n    """``(x, y, z, radius)`` of the drill zone in front of ``slot``, or None when it has no interactive to open.\n\n    A slot\'s `rot_y` is a compass bearing that turns its local +y onto world (sin t, cos t) (`vault_room`\'s WORLD), and\n    a vault door\'s +y looks out of the vault toward its approach (its `face`), as a deposit unit\'s looks out of its\n    wall. The zone stands there: its centre half the slot\'s depth plus a body\'s radius out from the face, its radius\n    half the opening\'s width plus a body\'s radius, so a body anywhere across the face is in it. Plan metres, the\n    builder\'s Z-up frame; ``z`` is the slot\'s, as an alarm\'s is."""\n    import math\n    iv = slot.get("interactive") or {}\n    if not iv.get("id"):\n        return None\n    x, y, z = (float(v) for v in slot["transform"]["translation"])\n    t = math.radians(float(slot["transform"].get("rot_y", 0.0) or 0.0))\n    fit = slot.get("fit") or {}\n    dims = fit.get("dims") or [0.0, 0.0, 0.0]\n    openings = fit.get("openings") or []\n    width = float(openings[0].get("width") or dims[0]) if openings else float(dims[0])\n    out = float(dims[1]) / 2.0 + float(body_radius)\n    return (x + math.sin(t) * out, y + math.cos(t) * out, z, width / 2.0 + float(body_radius))\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_drill_zones.py': '"""Where a crew stands to drill (0.291.0, the factory\'s roadmap 323).\n\nThe walker: "opening the safe should be a gameplay event where you have to stand in an area for a certain amount of\ntime close to the \'drill\' and then the door opens", then "no drill time from the factory ... These will be networked\nevents programmed somwhere else...we just want the seams/hooks in place". Every vault door and deposit wall writes one\n`drill` marker: a zone in front of it, sent on entry and exit, naming the interactive it opens. FAILS ON 0.290.0, which\nwrites none.\n"""\nimport json\nimport math\nimport os\n\nimport score_alarms\n\nHERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\nBUILD = os.path.join(HERE, "build")\nBANKS = ("bank_branch_a02", "bank_branch_a03", "bank_job", "bank_tower_a01", "bank_branch_a04", "credit_union_a03")\n\n\ndef _built(name):\n    slots = json.load(open(os.path.join(BUILD, name + ".slots.json"), encoding="utf-8"))["slots"]\n    gp = json.load(open(os.path.join(BUILD, name + ".gameplay.json"), encoding="utf-8"))\n    return slots, gp\n\n\ndef _room(rooms, x, y, story):\n    holding = [r for r in rooms if int(r.get("story", 0) or 0) == story\n               and r["bounds"][0] <= x <= r["bounds"][2] and r["bounds"][1] <= y <= r["bounds"][3]]\n    return min(holding, key=lambda r: (r["bounds"][2] - r["bounds"][0]) * (r["bounds"][3] - r["bounds"][1]),\n               default=None)\n\n\ndef test_every_vault_door_and_deposit_wall_has_one_drill_zone_naming_it():\n    for name in BANKS:\n        slots, gp = _built(name)\n        drills = {m["id"]: m for m in gp["markers"] if m["type"] == "drill"}\n        want = [s for s in slots if any(s.get(k) == v for k, v in score_alarms.DRILL_FIXTURES)]\n        assert want and len(drills) == len(want), (name, len(drills), len(want))\n        for s in want:\n            m = drills["drill_" + s["slot_id"]]\n            assert m["meta"]["target"] == s["interactive"]["id"] and m["meta"]["fixture"] == s["role"]\n            assert m["meta"]["event"] == "zone.drill" and m["meta"]["fires"] == ["on_enter", "on_exit"]\n            assert m["meta"]["repeat"] == "edge" and m["meta"]["radius"] > 0\n\n\ndef test_a_vault_doors_zone_stands_on_its_approach_and_reaches_across_its_face():\n    """The zone\'s centre is in the room the door is entered from, not the vault; a body at either jamb is in it."""\n    import agent_contract\n    body = agent_contract.body_radius()\n    for name in ("bank_branch_a02", "bank_job", "bank_tower_a01"):\n        slots, gp = _built(name)\n        rooms = gp["rooms"]\n        for s in [s for s in slots if s.get("role") == "vault_door"]:\n            m = next(m for m in gp["markers"] if m["id"] == "drill_" + s["slot_id"])\n            x, y, _z = s["transform"]["translation"]\n            story = s.get("story", 0)\n            vault = _room(rooms, *(score_alarms.drill_zone(dict(s, transform=dict(s["transform"],\n                          rot_y=s["transform"].get("rot_y", 0) + 180)), body)[:2]), story)\n            here = _room(rooms, m["x"], m["y"], story)\n            assert here is not None and vault is not None and here["id"] != vault["id"], (name, here, vault)\n            half = s["fit"]["openings"][0]["width"] / 2.0\n            assert math.isclose(m["meta"]["radius"], half + body, abs_tol=1e-3)\n\n\ndef test_no_drill_time_anywhere():\n    """The walker: "no drill time from the factory". A drill marker carries where, how big, which edges, what it\n    opens -- nothing about how long."""\n    _slots, gp = _built("bank_branch_a02")\n    for m in [m for m in gp["markers"] if m["type"] == "drill"]:\n        assert set(m["meta"]) == {"event", "fires", "repeat", "radius", "target", "fixture"}\n'}


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
