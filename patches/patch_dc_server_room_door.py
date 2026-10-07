"""Deli Counter 0.194.0: deli_a01's server room gets a door.

    python patch_dc_server_room_door.py

The walker's call, 2026-10-06, on `docs/findings/deli_a01_upper_storey_9188/`
at the factory root: the 186 m2 server room on story 1 had two soft-wall
breaches and no door, and 9188's site bake made it its own navmesh island.

THE DOOR. Story 1's partition along x = -2 (y -14..14) holds the door between
the manager office and the apartment at pos 0.0 (y 0) and the hall-to-server
breach at pos 0.36 (y 10.08). The new door is between them at pos 0.25:
y = 0 + 0.25 * 28 = 7.0 (layout_lint._opening_xy's formula), 1.25 m wide like
the storey's other door, tagged `hall_to_server_room`. It joins the upper
hall, where the up-stair arrives, to the server room. Clearances: 4.2 m from
the partition along y = 2 and 1.75 m from the breach, which stays: it is a
way in for whoever breaches, and the door is the way in for everyone else.

REFURNISHED, because a door changes what `furnish` lays out beside it: the
spec must stay a fixed point of furnish (test_club_fixtures).
`migrate_furnish_recipes.migrate` strips what furnish wrote and runs it
again; authored and seeded pieces are untouched.

Anchored on the partition as read 2026-10-06; refuses on any difference, and
refuses unless the file round-trips through `json.dumps(indent=1)`, the form
every spec migration writes, so the diff is the door and the furniture only.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
sys.path.insert(0, str(DC))
SPEC = DC / "specs" / "deli_a01.json"

OLD_OPENINGS = [
    {"kind": "door", "pos": 0.0, "width": 1.25, "tag": "hall_to_manager_office"},
    {"kind": "breach", "pos": 0.36, "width": 1.4, "breach_class": "soft_wall", "material": "drywall"},
]
DOOR = {"kind": "door", "pos": 0.25, "width": 1.25, "tag": "hall_to_server_room"}


def main():
    raw = SPEC.read_bytes()
    assert b"\r\n" not in raw, "deli_a01.json has CRLF; refusing"
    text = raw.decode("utf-8")
    d = json.loads(text)
    assert json.dumps(d, indent=1) + "\n" == text, "deli_a01.json does not round-trip; refusing"
    parts = [p for p in d["partitions"]
             if p.get("story") == 1 and p.get("axis") == "Y" and p.get("pos") == -2.0]
    assert len(parts) == 1, parts
    p = parts[0]
    assert (p.get("start"), p.get("end")) == (-14.0, 14.0), p
    assert p["openings"] == OLD_OPENINGS, p["openings"]
    p["openings"] = [OLD_OPENINGS[0], DOOR, OLD_OPENINGS[1]]
    import migrate_furnish_recipes
    vols_before = {v.get("name") for v in d.get("volumes") or []}
    removed, added = migrate_furnish_recipes.migrate(d)
    vols_after = {v.get("name") for v in d.get("volumes") or []}
    again = json.loads(json.dumps(d))
    migrate_furnish_recipes.migrate(again)
    assert json.dumps(again, sort_keys=True) == json.dumps(d, sort_keys=True), \
        "a second refurnish moved something: not a fixed point; refusing to write"
    SPEC.write_bytes((json.dumps(d, indent=1) + "\n").encode("utf-8"))
    print("deli_a01: door 'hall_to_server_room' at pos 0.25 (x -2, y 7.0); "
          "refurnished: %d removed, %d added" % (removed, added))
    print("  volumes gone: %s" % sorted(n for n in vols_before - vols_after if n))
    print("  volumes new:  %s" % sorted(n for n in vols_after - vols_before if n))


if __name__ == "__main__":
    main()
