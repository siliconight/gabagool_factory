"""Deli Counter 0.222.0: the delis' basement divider runs wall to wall (the walker's walk of cold runs 9305-9307,
finding 5: the factory's `docs/findings/walk_2026-10-14/`; the walker's call, 2026-10-14, "close the basement").

Anchored edits, each asserted exactly once and each file's sha16 pinned, nothing written until all matched:
  presets.py                 `corner_deli`'s basement divider runs -half_x..half_x, its door and breach kept at
                             -8.5 and 7.0
  migrate_basement_wall.py   NEW (`dc_basement_wall/migrate_basement_wall.py.txt`); run once here, and it must
                             migrate exactly the six delis
  presets.py (again)         the cold-room wall gains the utility room's door, midway between its breach
                             and the divider (the walker's call, 2026-10-14, by L24's rule of 2026-10-06)
  test_walk_reach.py         `test_deli_a01s_utility_room_is_open_floor` is `..._is_walked_into`: the
                             gap that made it open floor is closed, and its door is asserted
  test_basement_wall.py      NEW (`dc_basement_wall/test_basement_wall.py.txt`)
CHANGELOG and VERSION from `dc_basement_wall/CHANGELOG_0.222.0.md`; `--results-pending` leaves RESULT_ keys to
`--fill`. The six shells are built after (`build.py --all`, since `presets.py` moves).

Read before it was written, in this session: `presets.corner_deli`'s head (535-560: fx 38, fy 28, half_x, half_y)
and its partitions (610-640: every other partition -19..19, the basement's -12..12); `deli_counter.py`'s
`snap`, `_opening_to_hole` and the partition pass (1704-1790: a span clamped to the extent keeps each opening's
ABSOLUTE position, `remap_opening`); `migrate_wall_crossing.py` (the migration pattern, `json.dumps(d,
indent=1) + "\\n"`); the six delis' basements (partitions, stairs, volumes on storey -1: nothing stands on the
divider's new line), their openings' tags, and that each round-trips through `json.dumps(indent=1)` byte for byte;
`BREACHPANEL` (a breach builds as a solid panel with a collider). Every file LF.

    python patches/patch_dc_basement_wall.py --results-pending
    (python -m pytest -q in deli_counter; then python build.py --all --blender C:/blender/blender.exe)
    python patches/patch_dc_basement_wall.py --fill
"""
import hashlib
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_basement_wall"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_FAILING": "result_failing.txt", "RESULT_SUITE": "result_suite.txt",
           "RESULT_BUILD": "result_build.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.221.0", b"Deli Counter 0.222.0"
CHANGELOG_HEAD = "## [0.221.0] - a switchback's second flight stands on the floor under it\n"
SHA = {"presets.py": "f16c636746625742", "test_walk_reach.py": "8c76c6f933197fb1"}
NEW = {"migrate_basement_wall.py": "migrate_basement_wall.py.txt",
       "test_basement_wall.py": "test_basement_wall.py.txt"}
DELIS = ["corner_deli_heist_01.json", "cr_deli.json", "deli_a01.json", "deli_a02.json", "deli_a03.json",
         "night_deli.json"]

PRESET_OLD = '''    if basement:
        parts += [
            {"story": -1, "axis": "X", "pos": 1.0, "start": -12.0, "end": 12.0, "material": "brick_ext", "openings": [
                {"kind": "door", "pos": -0.35, "width": DOOR_W, "tag": "basement_corridor"},
                {"kind": "breach", "pos": 0.3, "width": 1.4, "breach_class": "reinforceable", "material": "brick_ext", "reinforceable": True, "tag": "vault_side_breach"}]},
'''
PRESET_NEW = '''    if basement:
        parts += [
            # WALL TO WALL (0.222.0). This divider stood x -12..12 under rooms
            # that meet across the whole basement: 7 m open at each end, the
            # vault open to the utility room beside the breach that was its way
            # in (the walker, cold run 9305: "this wall supposed to stop here and
            # have this big opening?"; asked, "close the basement"). The door and
            # the breach stay where 0.221.0 built them, snap(-0.35 * 24) = -8.5
            # and snap(0.3 * 24) = 7.0 (`migrate_basement_wall.py`).
            {"story": -1, "axis": "X", "pos": 1.0, "start": -half_x, "end": half_x, "material": "brick_ext", "openings": [
                {"kind": "door", "pos": -8.5 / fx, "width": DOOR_W, "tag": "basement_corridor"},
                {"kind": "breach", "pos": 7.0 / fx, "width": 1.4, "breach_class": "reinforceable", "material": "brick_ext", "reinforceable": True, "tag": "vault_side_breach"}]},
'''

PRESET_DOOR_OLD = '''                {"kind": "door", "pos": 0.1, "width": DOOR_W, "tag": "cold_room_door"},
                {"kind": "breach", "pos": -0.32, "width": 1.4, "breach_class": "reinforceable", "material": "brick_ext", "reinforceable": True}]},
        ]
    spec["partitions"] = parts
'''
PRESET_DOOR_NEW = '''                {"kind": "door", "pos": 0.1, "width": DOOR_W, "tag": "cold_room_door"},
                {"kind": "breach", "pos": -0.32, "width": 1.4, "breach_class": "reinforceable", "material": "brick_ext", "reinforceable": True},
                # A WALK-IN WAY TO THE UTILITY ROOM (0.222.0). Wall to wall, the
                # divider above leaves its two breaches the only ways in, and a room
                # a body reaches only by breaching gets a door unless it is the
                # objective (the walker, 2026-10-06; layout_lint L24). Asked, the
                # walker chose the door, from the corridor (2026-10-14): midway
                # between this wall's breach at y -9.0 and the divider at y 1.0.
                {"kind": "door", "pos": -4.0 / fy, "width": DOOR_W, "tag": "corridor_to_utility"}]},
        ]
    spec["partitions"] = parts
'''

WALK_OLD = '''def test_deli_a01s_utility_room_is_open_floor():
    spec = json.load(open(os.path.join(HERE, "specs", "deli_a01.json"), encoding="utf-8"))
    assert "utility_room" not in _walk(spec)
'''
WALK_NEW = '''def test_deli_a01s_utility_room_is_walked_into():
    """0.197.0 found it open floor: the basement divider stopped at x 12. Since
    0.222.0 the divider runs wall to wall and the room has its own door from
    the corridor -- the walker's call of 2026-10-14, by the rule of 2026-10-06
    this file was written for."""
    spec = json.load(open(os.path.join(HERE, "specs", "deli_a01.json"), encoding="utf-8"))
    assert "utility_room" not in _walk(spec)
    doors = [o for p in spec["partitions"] if p.get("story") == -1
             for o in p.get("openings", []) if o.get("tag") == "corridor_to_utility"]
    assert len(doors) == 1 and doors[0]["kind"] == "door", doors
'''

EDITS = {"presets.py": [(PRESET_OLD, PRESET_NEW), (PRESET_DOOR_OLD, PRESET_DOOR_NEW)],
         "test_walk_reach.py": [(WALK_OLD, WALK_NEW)]}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.222.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.222.0: results filled")


def main():
    if FILL:
        return fill()
    vraw = (DC / "VERSION").read_bytes()
    assert vraw.strip() == VERSION_WAS, vraw
    entry = (SRC / "CHANGELOG_0.222.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.222.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel in SHA:
        p = DC / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in EDITS[rel]:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    for rel, name in NEW.items():
        p = DC / rel
        assert not p.exists(), (rel, "already exists")
        writes[p] = (SRC / name).read_bytes().replace(b"\r\n", b"\n")
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(vraw.replace(VERSION_WAS, VERSION))
    print("Deli Counter 0.221.0 -> 0.222.0")
    # the one-shot migration, run once: it must touch exactly the six delis
    r = subprocess.run([sys.executable, "migrate_basement_wall.py"], cwd=str(DC), capture_output=True, text=True)
    print(r.stdout.rstrip())
    got = sorted(line.split(":")[0] for line in r.stdout.splitlines() if line.endswith(".json") is False
                 and line.split(":")[0].endswith(".json"))
    assert r.returncode == 0 and got == DELIS, ("the migration touched", got, r.stderr[-400:])
    # THE REFURNISH THE MOVED WALL ASKS FOR (0.214.0's pattern): the library is held to be a fixed point of
    # `level_design.furnish` (`test_deli_window`, `test_club_fixtures`), and a wall where there was none moves what
    # furnish stands beside it. Measured on a copy before this was written (the factory's
    # `docs/findings/door_widths/refurnish_delta.py`): it moves deli_a03 alone, one chair set lost at the vault's
    # count table, which stands 0.15 m from the new wall.
    specs = DC / "specs"
    before = {p.name: p.read_bytes() for p in specs.glob("*.json") if not p.name.startswith("lf_")}
    r = subprocess.run([sys.executable, "migrate_furnish_recipes.py"], cwd=str(DC), capture_output=True, text=True)
    print(r.stdout.rstrip())
    moved = sorted(n for n, b in before.items() if (specs / n).read_bytes() != b)
    assert r.returncode == 0 and moved == ["deli_a03.json"], ("the refurnish moved", moved, r.stderr[-400:])


if __name__ == "__main__":
    main()
