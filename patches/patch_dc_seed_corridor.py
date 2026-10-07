"""Deli Counter 0.195.0: a seeded piece leaves a body's width on every side.

    python patch_dc_seed_corridor.py

Anchored on level_design.py as read 2026-10-06 (256,675 bytes, LF); every
anchor must match exactly once or nothing is written.

  * `_box_gap` and `_corridor_obstacles`, new, before `_seed_clear`.
  * `_seed_clear(..., corridor=False)`: when true, a piece standing on the
    floor keeps `agent_contract.min_corridor_width()` clear of every wall
    box, stair reserve and standing volume. Opt-in: furnish's seven callers
    are unchanged.
  * `seed_cover` passes it at both of its calls.
  * `reseat_piece(..., corridor=False)`: when true, a piece seed_cover placed
    moves when the corridor rule refuses where it stands, instead of when L23
    names it. Furniture is left to furnish.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LD = ROOT / "deli_counter" / "level_design.py"

EDITS = []

# 1. the helpers, and the signature
EDITS.append((
    '''def _seed_clear(spec, room, px, py, placed, half=0.0, above=None,
                below=None, over_openings=False):
''',
    '''def _box_gap(a, b):
    """Clear plan distance between two (x0, y0, x1, y1) boxes, 0 when they
    touch or overlap. Corner to corner it is the diagonal: a margin asked per
    axis is a box, not a radius, and over-reports at a corner."""
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dy = max(b[1] - a[3], a[1] - b[3], 0.0)
    return math.hypot(dx, dy)


def _corridor_obstacles(spec, story, floor, sh):
    """The plan boxes a seeded piece keeps a corridor from (`_seed_clear`'s
    `corridor`): the four exterior walls on the footprint's edge and this
    storey's partitions, each `wall_thick` thick and centred on its line as
    the builder stands them (both read `wall_thick`; LevelSpec's default is
    0.3); every stair reserve, all storeys, as the stair rule above reads
    them (`_stair_reserved_rects`); and every volume on this storey, less a
    hung collision-free one, which is over heads (`_HUNG_MIN`)."""
    hx = spec.get("footprint_x", 20) / 2.0
    hy = spec.get("footprint_y", 20) / 2.0
    t = float(spec.get("wall_thick", 0.3))
    out = [(-hx, hy - t / 2, hx, hy + t / 2), (-hx, -hy - t / 2, hx, -hy + t / 2),
           (hx - t / 2, -hy, hx + t / 2, hy), (-hx - t / 2, -hy, -hx + t / 2, hy)]
    for p in spec.get("partitions", []):
        if p.get("story", 0) != story:
            continue
        lo, hi = (-hy, hy) if p["axis"] == "Y" else (-hx, hx)
        s = lo if p.get("start") is None else p["start"]
        e = hi if p.get("end") is None else p["end"]
        s, e = min(s, e), max(s, e)
        if p["axis"] == "Y":
            out.append((p["pos"] - t / 2, s, p["pos"] + t / 2, e))
        else:
            out.append((s, p["pos"] - t / 2, e, p["pos"] + t / 2))
    out.extend(tuple(r) for r in _stair_reserved_rects(spec))
    for v in spec.get("volumes", []):
        vz, vh = float(v.get("z", 0.0)), float(v.get("size_z", 0.0))
        if not _on_storey(vz, vh, floor, sh):
            continue
        if v.get("collision") == "none" and vz - vh / 2.0 - floor >= _HUNG_MIN:
            continue
        ax = float(v.get("size_x", 1)) / 2.0
        ay = float(v.get("size_y", 1)) / 2.0
        out.append((v["x"] - ax, v["y"] - ay, v["x"] + ax, v["y"] + ay))
    return out


def _seed_clear(spec, room, px, py, placed, half=0.0, above=None,
                below=None, over_openings=False, corridor=False):
'''))

# 2. the docstring says what `corridor` is for
EDITS.append((
    '''    those two really do intersect."""
    story = room.get("story", 0)
''',
    '''    those two really do intersect.

    `corridor` (0.195.0; the seeder's own calls) asks one thing more of a
    piece standing on the floor: that its square leave `min_corridor_width`
    (agent_contract, 1.1 m: 2 x the bake radius + 0.3) clear of every wall's
    box, every stair reserve and every standing volume
    (`_corridor_obstacles`). The margins above are each a fraction of a body
    -- 0.3 m off a stair's reserve, 0.9 m off a volume, 1.0 m from a
    partition's LINE to the piece's centre, nothing off an exterior wall --
    so a crate could stand where it left a slot no body fits through.
    deli_a01's stairwell held two that between them cut its up-stair off from
    the stairwell's only door, and its whole upper storey with it (cold runs
    9187 and 9188; `docs/findings/deli_a01_upper_storey_9188/` at the
    factory root); across the library 40 of 69 seeded pieces stood within a
    body of something. With it, every passage round a seeded piece is a body
    wide or there is none, so a seeded piece cannot cut a floor in two.
    Opt-in, because furnish's callers stand furniture against walls on
    purpose and answer to their own rules."""
    story = room.get("story", 0)
'''))

# 3. the rule itself, before the spread rule
EDITS.append((
    '''    for (qx, qy) in placed:
        if math.hypot(qx - px, qy - py) < 2.2:
            return False
    return True
''',
    '''    # A BODY PASSES EVERY SIDE OF A SEEDED PIECE (`corridor`, 0.195.0; see
    # the docstring). The box is the piece's worst-case square, as above.
    if corridor and above is None:
        import agent_contract
        cw = agent_contract.min_corridor_width()
        box = (px - half, py - half, px + half, py + half)
        if any(_box_gap(box, r) < cw
               for r in _corridor_obstacles(spec, story, floor, sh)):
            return False
    for (qx, qy) in placed:
        if math.hypot(qx - px, qy - py) < 2.2:
            return False
    return True
'''))

# 4. the seeder asks it
EDITS.append((
    "                if not _seed_clear(spec, room, px, py, placed, half=s_half):\n",
    "                if not _seed_clear(spec, room, px, py, placed, half=s_half,\n"
    "                                   corridor=True):\n"))
EDITS.append((
    "            if not _seed_clear(spec, room, px, py, placed, half=arch_half):\n",
    "            if not _seed_clear(spec, room, px, py, placed, half=arch_half,\n"
    "                               corridor=True):\n"))

# 5. reseat_piece can move a seeded piece by the corridor rule
EDITS.append((
    "def reseat_piece(spec, name, reach=12.0, step=0.1, margin=0.15):\n",
    "def reseat_piece(spec, name, reach=12.0, step=0.1, margin=0.15, corridor=False):\n"))
EDITS.append((
    '''    Candidates are a `step` m grid, nearest first, ties broken by position,
    so a re-run makes the same move."""
''',
    '''    Candidates are a `step` m grid, nearest first, ties broken by position,
    so a re-run makes the same move.

    `corridor` (0.195.0) asks the seeder's corridor rule instead of L23: a
    piece `seed_cover` placed moves when `_seed_clear(..., corridor=True)`
    refuses where it stands, to the nearest place that rule allows, and
    `(0.0, 0.0)` comes back for a piece that passes or is not the seeder's --
    furniture is furnish's. `migrate_seed_corridor.py` drives it."""
'''))
EDITS.append((
    '''    if not any(p["name"] == name for p in layout_lint.stale_pieces(spec)):
        return (0.0, 0.0)
    story = layout_lint.piece_story(spec, v)
    if story is None:
        return None
    room = _room_for_point(spec, float(v["x"]), float(v["y"]), story)
    if room is None:
        return None
''',
    '''    if not corridor and not any(p["name"] == name for p in layout_lint.stale_pieces(spec)):
        return (0.0, 0.0)
    story = layout_lint.piece_story(spec, v)
    if story is None:
        return (0.0, 0.0) if corridor else None
    room = _room_for_point(spec, float(v["x"]), float(v["y"]), story)
    if room is None:
        return (0.0, 0.0) if corridor else None
'''))
EDITS.append((
    '''    half = max(sx, sy) / 2.0
    door_ok_before = _seed_clear_doors(spec, room, float(v["x"]), float(v["y"]), half)
''',
    '''    half = max(sx, sy) / 2.0
    door_ok_before = _seed_clear_doors(spec, room, float(v["x"]), float(v["y"]), half)
    if corridor and (not seeded or _seed_clear(without, room, float(v["x"]), float(v["y"]),
                                               placed, half=half, corridor=True)):
        return (0.0, 0.0)
'''))
EDITS.append((
    "        if seeded and not _seed_clear(without, room, px, py, placed, half=half):\n",
    "        if seeded and not _seed_clear(without, room, px, py, placed, half=half,\n"
    "                                      corridor=corridor):\n"))


def main():
    data = LD.read_bytes()
    assert len(data) == 256675, "level_design.py is %d bytes, not the 256,675 read; refusing" % len(data)
    assert b"\r\n" not in data, "CRLF in level_design.py; refusing"
    text = data.decode("utf-8")
    for old, _new in EDITS:
        n = text.count(old)
        assert n == 1, "anchor found %d times, not once: %r" % (n, old[:80])
    for old, new in EDITS:
        text = text.replace(old, new)
    LD.write_bytes(text.encode("utf-8"))
    print("level_design.py: %d edits; %d -> %d bytes" % (len(EDITS), len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
