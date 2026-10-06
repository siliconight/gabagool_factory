"""Lot 0.79.0 tests -- every exterior light stands on a pole.

Anchored patch. Replaces the test that asserted the path rows and the
perimeter ring, because that behaviour is the defect being removed, and adds
the one the walk-copy probe would have caught: the coincidence check itself,
run on a planned kerb line rather than on a hand-written spec.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
T = ROOT / "lot" / "tests" / "test_lot.py"


def _apply(path, pairs):
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit(f"REFUSED: {path} has mixed line endings "
                         f"({crlf} CRLF of {lf} LF)")
    eol = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    if eol == "\r\n":
        text = text.replace("\r\n", "\n")
    for i, (old, new) in enumerate(pairs):
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"REFUSED: anchor {i} matches {n} times, not 1")
        text = text.replace(old, new, 1)
    out = text.replace("\n", eol) if eol == "\r\n" else text
    path.write_bytes(out.encode("utf-8"))
    print(f"[patch] {path.name}: {len(pairs)} block(s), "
          f"{len(raw)} -> {len(out.encode('utf-8'))} bytes, eol={eol!r}")


OLD = '''def test_lights_streetlights_paths_and_perimeter():
    """Lot derives exterior streetlights along paths and the ground perimeter."""
    spec = json.load(open(os.path.join(SPECS, "example_compound.json")))
    m = lot.merge_lights(spec, SPECS)
    ids = [a["id"] for a in m["anchors"] if a["type"] == "streetlight"]
    assert "site/path_0_lights" in ids                 # a row down the road
    assert {"site/perimeter_s_lights", "site/perimeter_n_lights",
            "site/perimeter_w_lights", "site/perimeter_e_lights"} <= set(ids)
    # streetlights are exterior: not alarm-reactive, mounted high
    sl = next(a for a in m["anchors"] if a["id"] == "site/path_0_lights")
    assert sl["reacts_to_alarm"] is False and sl["pos"][2] == lot.STREETLIGHT_H
'''

NEW = '''def test_lights_stand_on_the_poles_the_site_stands():
    """EVERY STREETLIGHT IS ON A LAMP, measured the way the walk copy measured
    it and found it was not.

    Until 0.79.0 Lot derived exterior light ROWS from the path graph and from
    a ring 2 m inside the ground rect, while `site_furniture` stood the poles
    along the kerb bands. `pole_vs_light.gd` on cold run 9087\'s walk copy: 54
    lights, 48 poles, nearest pole to a light min 3.50 m, median 24.93 m, max
    93.68 m -- 0 of 54 within a metre. This is that probe as a unit test, run
    on a planned kerb line rather than a hand-written spec, so the thing under
    test is the agreement between the two planners and not a fixture.
    """
    import math
    import site_furniture
    import site_streets
    spec = json.load(open(os.path.join(SPECS, "coldrun_kerb_probe.json")))
    poles = [p for p in site_furniture.plan_furniture(site_streets.roads(spec))
             if p["species"] == "streetlight"]
    assert poles, "the probe spec stands no lamps, so this proves nothing"
    spec.setdefault("cover", []).extend(poles)
    m = lot.merge_lights(spec, SPECS)
    lights = [a for a in m["anchors"] if a["type"] == "streetlight"]

    # one light per pole, no more and no fewer
    assert len(lights) == len(poles)
    for a in lights:
        best = min(math.hypot(a["pos"][0] - p["at"][0], a["pos"][1] - p["at"][1])
                   for p in poles)
        assert best <= 0.001, (a["id"], best)     # coincident, not merely near
        # the lamp point is under the lens, which is 0.175 below the module\'s
        # top -- a light at the top would be inside the shoebox head
        assert abs(a["pos"][2] - (lot.SIDEWALK_H + 6.0 - lot.STREETLIGHT_LENS_DROP)) < 1e-6
        assert a["row"] == {"count": 1, "spacing": 0.0}
        assert a["reacts_to_alarm"] is False
        # the pole is already built by the site kit; Zoo\'s fixture pass reads
        # this and skips the anchor instead of standing a second one inside it
        assert a["hardware"].startswith("slot:cover_")

    # and each id names a slot that exists in the manifest Lot writes beside it
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "s.slots.json")
        lot.write_site_slots(spec, out)
        slot_ids = {s["slot_id"] for s in json.load(open(out))["slots"]}
    assert {a["hardware"].split(":", 1)[1] for a in lights} <= slot_ids


def test_lights_no_pole_means_no_exterior_light_rather_than_a_row():
    """The removed behaviour, asserted gone.

    A site with paths and a ground rect but no streetlight pole used to get a
    row of lights down every path and a ring round the boundary -- light from
    nowhere, which is the frame the walker was standing in when they asked
    where it came from. It now gets none, and `write_site` prints
    LOT_NO_EXTERIOR_LIGHTS rather than filling the gap in.
    """
    spec = json.load(open(os.path.join(SPECS, "example_compound.json")))
    assert spec.get("paths"), "this spec is meant to have paths to derive from"
    m = lot.merge_lights(spec, SPECS)
    assert [a for a in m["anchors"] if a["type"] == "streetlight"] == []
'''


def main():
    if not T.exists():
        raise SystemExit(f"REFUSED: {T} not found")
    _apply(T, [(OLD, NEW)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
