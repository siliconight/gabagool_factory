"""Lot 0.136.0: the getaway's end zone has an extent (the factory's roadmap 323).

The getaway van's extraction marker carries `zone_radius`: the crew's spawn point to the van body's kerb side
(`site_getaway.ZONE_TO_BODY`, 1.2 + 0.20) plus the agent contract's player radius (0.35), 1.75 m. Level Factory stages
it as `zone.extraction` (Dispatch 0.7.0) when a level's gameplay events are on. Lot only states it.

Proven: tests/test_site_getaway.py's two new tests fail on 0.135.0 (fails_on_old.out.txt); the clone's full suite,
878 passed, 17 skipped, with Deli Counter's build reachable beside it.
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'lot'
PINS = {'CHANGELOG.md': 'fd5939b0f6524374', 'VERSION': 'ac22979ec94f7cc5', 'lot.py': '37db66c068204444', 'site_getaway.py': '3bfccdb397b4d65a', 'tests/test_site_getaway.py': '78db3c86a7cedce9'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## 0.135.0 - the drive-up lane as the research drew it\n', '## 0.136.0 - the getaway\'s end zone has an extent\n\nThe factory\'s roadmap 323; the walker, of the zones a crew stands in at the end of a job: "we just have the event that\nwe send (without spamming/rate limiting)". The getaway van\'s extraction marker now carries `zone_radius`: the crew\'s\nspawn point to the van body\'s kerb side (`site_getaway.ZONE_TO_BODY`, `SPAWN_OFF_KERB` 1.2 + `KERB_GAP` 0.20) plus the\nagent contract\'s player radius (0.35) -- 1.75 m, so a crew member with a hand on the van is inside it. Level Factory\nstages it as the extraction\'s `zone.extraction` event (Dispatch 0.7.0) when a level\'s gameplay events are on. Lot only\nstates it: how long a crew stands in it, and what that ends, are the game\'s. Nothing else moves; a site with no van has\nno zone. Tests: tests/test_site_getaway.py, the extraction states its end zone, from the contract (fails on 0.135.0).\n\n## 0.135.0 - the drive-up lane as the research drew it\n')], 'VERSION': [('lines 1-1', 'Lot 0.135.0', 'Lot 0.136.0')], 'lot.py': [('lines 3749-3749', '    getaway = site_getaway.plan(site_spec, merged, getaway_findings)\n', '    getaway = site_getaway.plan(site_spec, merged, getaway_findings,\n                                body_radius=_agent()["characters"]["player"]["radius_m"])\n')], 'site_getaway.py': [('lines 65-66', 'FACING_DOT = 0.5\n\n', "FACING_DOT = 0.5\n#: The crew's spawn to the van body's kerb side, in plan: in from the kerb\n#: line, then the body's gap off it. The extraction's zone reaches this far\n#: plus a body's radius, so a crew member with a hand on the van is in it.\nZONE_TO_BODY = SPAWN_OFF_KERB + KERB_GAP\n\n"), ('lines 117-117', 'def plan(site_spec, merged=None, findings=None):\n', 'def plan(site_spec, merged=None, findings=None, body_radius=None):\n'), ('lines 124-124', '    ``findings`` (a list of strings) hears why there is no van."""\n', '    ``findings`` (a list of strings) hears why there is no van.\n\n    With ``body_radius`` (the contract\'s player radius, metres) the\n    extraction marker carries ``zone_radius``: the extent of the end zone a\n    game may send `zone.extraction` from (0.136.0, the factory\'s roadmap\n    323), `ZONE_TO_BODY` plus that radius. Lot only states it; whether a\n    game uses it, and for how long a crew must stand in it, are the game\'s."""\n'), ('lines 172-173', '                        {"type": "extraction", "at": list(at), "source": "getaway_van",\n                         "getaway": VAN[0]}],\n', '                        dict({"type": "extraction", "at": list(at), "source": "getaway_van",\n                              "getaway": VAN[0]},\n                             **({"zone_radius": round(ZONE_TO_BODY + float(body_radius), 3)}\n                                if body_radius is not None else {}))],\n')], 'tests/test_site_getaway.py': [('lines 182-182', '        assert abs(ey) <= 10.0, ("shoved off the route", ex, ey)\n', '        assert abs(ey) <= 10.0, ("shoved off the route", ex, ey)\n\n\ndef test_the_extraction_states_its_end_zone():\n    """0.136.0 (the factory\'s roadmap 323): the getaway\'s extraction carries\n    `zone_radius`, the spawn point to the van body\'s kerb side plus the\n    contract\'s player radius -- 1.40 + 0.35 -- so the zone reaches the van.\n    FAILS ON 0.135.0, whose extraction has no extent."""\n    spec = _probe()\n    g = site_getaway.plan(spec, lot.merge_gameplay(spec, SPECS), [], body_radius=0.35)\n    spawn, extr = g["markers"]\n    assert extr["zone_radius"] == 1.75 and "zone_radius" not in spawn\n    van = _rect(g["van"])\n    x, y = extr["at"]\n    gap = math.hypot(max(van[0] - x, 0.0, x - van[2]), max(van[1] - y, 0.0, y - van[3]))\n    assert gap < extr["zone_radius"], (gap, extr["zone_radius"])\n    assert "zone_radius" not in _plan()["markers"][1]\n\n\ndef test_an_assembled_site_writes_the_zone_from_the_contract(tmp_path):\n    lot.assemble(PROBE, str(tmp_path))\n    g = json.loads((tmp_path / "coldrun_kerb_probe.site.gameplay.json").read_text(encoding="utf-8"))\n    extr = [m for m in g["site_markers"] if m.get("source") == "getaway_van" and m["type"] == "extraction"]\n    want = round(site_getaway.ZONE_TO_BODY + lot._agent()["characters"]["player"]["radius_m"], 3)\n    assert len(extr) == 1 and extr[0]["zone_radius"] == want\n')]}
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
