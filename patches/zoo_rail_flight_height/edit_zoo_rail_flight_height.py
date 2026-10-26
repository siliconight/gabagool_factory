"""Zoo 1.129.0 on a CLONE (<repo>): `stoop_railing`'s flight form reaches a storey -- the raking rail along a
switchback's upper flight (the walker's walk of cold run 9386, finding 6). Anchored; refuses on a miss.

    python edit_zoo_rail_flight_height.py <repo>
"""
import json
import pathlib
import sys

R = pathlib.Path(sys.argv[1])
gp = R / "zoo_keeper" / "genome" / "species" / "stoop_railing.json"
raw = gp.read_bytes()
crlf = b"\r\n" in raw
t = raw.decode("utf-8").replace("\r\n", "\n")
g = json.loads(t)
assert g["dimensions"]["height"] == {"min": 0.85, "max": 1.6, "default": 0.9144}, g["dimensions"]["height"]
old = '''    "height": {
      "min": 0.85,
      "max": 1.6,'''
new = '''    "height": {
      "min": 0.85,
      "max": 6.0,'''
assert t.count(old) == 1
t = t.replace(old, new)
note_old = g["license"]["notes"]
NOTE = (" A STOREY'S FLIGHT (1.129.0): Deli Counter >= 0.269.0 stands this species' flight form along a switchback's upper"
        " flight, its box the flight's rise plus `RAIL_H` -- a 3.6 m storey asks 4.51 m -- so the height reaches 6.0 m"
        " (a 5.0 m storey and its rail). Planning reads no limit from the genome, so no railing built before moves.")
assert t.count(json.dumps(note_old)[1:-1]) == 1
t = t.replace(json.dumps(note_old)[1:-1], json.dumps(note_old + NOTE)[1:-1])
g2 = json.loads(t)
assert g2["dimensions"]["height"]["max"] == 6.0 and g2["license"]["notes"].endswith("no railing built before moves.")
gp.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))

TEST = '''"""A storey's flight (1.129.0): `stoop_railing`'s flight form, as tall as a storey's rise and its rail, plans as the
species. For a switchback's upper flight (the walker's walk of cold run 9386, finding 6). FAILS ON 1.128.0."""
from zoo_keeper.core import kit


def test_a_storeys_flight_rail_plans_as_the_species():
    slot = {"slot_id": "stair_rake_0", "role": "prop", "size_mod": "full", "style": 1, "material": "metal_painted",
            "species": "stoop_railing", "form": "flight",
            "fit": {"dims": [5.2339, 0.05, 3.6 + 0.9144], "pivot": "center", "collision": "none"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    assert plan["modules"][0]["species"] == "stoop_railing", plan.get("species_fallbacks")
    assert not plan.get("species_fallbacks"), plan["species_fallbacks"]
'''
(R / "tests" / "test_rail_flight_height.py").write_text(TEST, encoding="utf-8", newline="\n")
print("stoop_railing height to 6.0 m; tests/test_rail_flight_height.py")
