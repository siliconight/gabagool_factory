"""Deli Counter 0.192.0, the code: layout_lint L23 asks every piece of the
spec as it stands, and level_design.reseat_piece moves one out of a stair's
way by its own placement rule.

MEASURED (`docs/findings/presentation_gates/stale_pieces.py` at the factory
root): 64 pieces in 18 of 146 shells stand over a slab opening or in a
stair's walk on their own storey. Every placement pass (presets,
`seed_cover`, `furnish`) checks the stairs when it places a piece and is
idempotent by name, so a piece placed before a stair changed is never asked
again. 0.190.0 widened twin_a01's flights and left two wardrobes over the
new hole; its swept gate passed, because walking is unaffected.

    python patch_dc_stale_pieces.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
LINT = DC / "layout_lint.py"
DESIGN = DC / "level_design.py"

LINT_ANCHOR = '''def ladder_findings(spec):
'''
LINT_NEW = '''#: A piece this far into a hole or a stair's walk on BOTH axes is in it; less
#: is a touch at an edge, where a guard stands (metres).
STALE_TOL_M = 0.02
#: A base this close to a floor line stands on that floor: a slab's thickness.
STAND_TOL_M = 0.25


def _plan_overlap(a, b):
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    return ox * oy if ox > STALE_TOL_M and oy > STALE_TOL_M else 0.0


def stair_space(spec):
    """``(holes, walks)`` for a dict spec, each ``{storey: [rect]}``.

    HOLES are what the builder cuts (`stairwell.slab_openings`, filed under
    the slab's storey). WALKS are a flight's rectangle on the storey it climbs
    from (`flight_rect(st, s)` on storey s) and its landing rects
    (`stairwell.stair_endpoints`: "lower" on the stair's lowest storey,
    "upper" on its highest -- the endpoint carries no storey of its own).
    A spiral reserves no walk."""
    import types
    import stairwell
    stairs = [st for st in (_stair_obj(r) for r in spec.get("stairs", []) or [])
              if st is not None]
    holes = stairwell.slab_openings(types.SimpleNamespace(
        slab_holes=[types.SimpleNamespace(**h) for h in spec.get("slab_holes", []) or []],
        stairs=stairs))
    walks = {}
    for st in stairs:
        if getattr(st, "style", None) == "spiral":
            continue
        lo, hi = min(st.from_story, st.to_story), max(st.from_story, st.to_story)
        for k in range(lo, hi):
            walks.setdefault(k, []).append(stairwell.flight_rect(st, k))
        for e in stairwell.stair_endpoints(st):
            walks.setdefault(lo if e["end"] == "lower" else hi, []).append(e["rect"])
    return holes, walks


def piece_story(spec, v):
    """The storey a volume stands on, or None for one HUNG (collision-free
    and `level_design._HUNG_MIN` or more above its floor).

    A base within `STAND_TOL_M` of a floor stands on it -- final_stand's
    `boss_desk` stands 5 cm below storey 2's floor line. Any other base is
    floored, not rounded: `level_design._volume_story`'s round puts a sign
    hung 2.2 m up a 3.3 m storey on the storey above."""
    import level_design
    sh = level_design._story_height(spec)
    base = float(v.get("z", 0.0)) - float(v.get("size_z", 0.0)) / 2.0
    near = round(base / sh)
    story = near if abs(base - near * sh) <= STAND_TOL_M else math.floor(base / sh)
    if v.get("collision") == "none" and base - story * sh >= level_design._HUNG_MIN:
        return None
    return story


def stale_pieces(spec):
    """``[{name, story, hole, walk}]``: every volume standing over a slab
    opening or in a stair's walk on its own storey, ``hole`` and ``walk`` in
    m2 of its plan.

    A stair's own guards (`circulation.GUARD_PREFIX`) stand at its hole's
    edge by design and are not pieces; a hung piece is over the furniture,
    not among it."""
    import circulation
    if not spec.get("stairs") and not spec.get("slab_holes"):
        return []
    holes, walks = stair_space(spec)
    out = []
    for v in spec.get("volumes", []) or []:
        name = str(v.get("name", ""))
        if name.startswith(circulation.GUARD_PREFIX):
            continue
        story = piece_story(spec, v)
        if story is None:
            continue
        sx, sy = float(v.get("size_x", 0.0)), float(v.get("size_y", 0.0))
        x, y = float(v.get("x", 0.0)), float(v.get("y", 0.0))
        r = (x - sx / 2.0, y - sy / 2.0, x + sx / 2.0, y + sy / 2.0)
        hole = sum(_plan_overlap(r, h) for h in holes.get(story, []))
        walk = sum(_plan_overlap(r, w) for w in walks.get(story, []))
        if hole or walk:
            out.append({"name": name, "story": story,
                        "hole": round(hole, 3), "walk": round(walk, 3)})
    return out


def stale_piece_findings(spec):
    """L23 (WARN, 0.192.0): a piece over a slab opening or in a stair's walk
    on its own storey. 64 pieces in 18 of 146 shells (measured 2026-10-06),
    for two causes the census cannot tell apart:
    - STALE. Every placement pass -- the presets, `seed_cover`, `furnish` --
      clears a piece of the stairs when it PLACES it, and each is idempotent
      by name, so a piece placed before a stair lengthened or widened is
      never asked again. 0.190.0 widened twin_a01's flights and left two
      wardrobes over the new hole; its swept gate passed, because walking is
      unaffected.
    - UNSEEN. `furnish` and `seed_cover` clear the STAIRS
      (`_stair_reserved_rects`), not an authored `slab_holes` opening, so
      today's furnish still stands apartment_walkup_a01's dining set over one.
    This asks the spec as it stands, and says what it measured, not why.

    Born WARN: 44 pieces in 7 shells stand frozen in
    `stale_pieces_baseline.json` until each is looked at, and
    `test_stale_pieces.py` fails a new one. Move the piece
    (`level_design.reseat_piece`), not the stair."""
    out = []
    for p in stale_pieces(spec):
        where = []
        if p["hole"]:
            where.append(f"{p['hole']:.2f} m2 over a slab opening")
        if p["walk"]:
            where.append(f"{p['walk']:.2f} m2 in a stair's walk")
        out.append(f"L23 a piece over an opening or in a stair's walk: "
                   f"'{p['name']}' on storey {p['story']} has "
                   + " and ".join(where))
    return out


def ladder_findings(spec):
'''

LINT_WIRE_OLD = '''    fails += stair_wall_findings(spec, warns)  # L21 stair hole cuts a wall / door
'''
LINT_WIRE_NEW = '''    fails += stair_wall_findings(spec, warns)  # L21 stair hole cuts a wall / door
    warns += stale_piece_findings(spec)     # L23 a piece where a stair now is
'''

DESIGN_ANCHOR = '''def seed_cover(spec):
'''
DESIGN_NEW = '''def _seeded_cover(v, room):
    """Was `v` placed by `seed_cover` in `room`? Its names are
    ``{piece}_{room}_{k}`` and ``{shelter}_{room}_shelter``."""
    if not room:
        return False
    name, rid = str(v.get("name", "")), str(room.get("id", ""))
    pieces = {p[0] for _w, arch in _SEED_ARCHETYPES for p in arch}
    pieces |= {p[0] for p in _SEED_DEFAULT}
    shelters = {p[0] for _w, p in _SEED_SHELTER} | {_SEED_SHELTER_DEFAULT[0]}
    if name in {f"{s}_{rid}_shelter" for s in shelters}:
        return True
    head, _sep, k = name.rpartition("_")
    return k.isdigit() and any(head == f"{p}_{rid}" for p in pieces)


def reseat_piece(spec, name, reach=12.0, step=0.1, margin=0.15):
    """Move ONE volume to the nearest place clear of every stair (layout_lint
    L23), and return the move ``(dx, dy)``: ``(0.0, 0.0)`` when it already
    stood clear, ``None`` when nothing within `reach` m answers.

    WHY (0.192.0). Every placement pass clears a piece of the stairs when it
    places it and is idempotent by name, so a piece placed before a stair
    changed is never asked again: deli_a01-a03's counter islands stood 41%
    and 54% over the up-stair's hole, and 0.190.0's wider flights put
    twin_a01's wardrobes over theirs.

    The new place keeps the piece IN ITS ROOM and off every other piece on
    its storey; stays `margin` m clear of the stair's holes and walks (a
    guard's thickness and a hand); and is never in a door's approach the old
    place was not in. A piece `seed_cover` placed (`_seeded_cover`) goes only
    where the seeder itself would put it: `_seed_clear`, the same rule.
    Candidates are a `step` m grid, nearest first, ties broken by position,
    so a re-run makes the same move."""
    import layout_lint
    vols = spec.get("volumes") or []
    v = next((x for x in vols if x.get("name") == name), None)
    if v is None:
        return None
    if not any(p["name"] == name for p in layout_lint.stale_pieces(spec)):
        return (0.0, 0.0)
    story = layout_lint.piece_story(spec, v)
    if story is None:
        return None
    room = _room_for_point(spec, float(v["x"]), float(v["y"]), story)
    if room is None:
        return None
    holes, walks = layout_lint.stair_space(spec)
    keep = [(r[0] - margin, r[1] - margin, r[2] + margin, r[3] + margin)
            for r in holes.get(story, []) + walks.get(story, [])]
    sx, sy = float(v.get("size_x", 0.0)), float(v.get("size_y", 0.0))
    others = []
    for o in vols:
        if o is v or layout_lint.piece_story(spec, o) != story:
            continue
        hx, hy = float(o.get("size_x", 0.0)) / 2.0, float(o.get("size_y", 0.0)) / 2.0
        others.append((o["x"] - hx, o["y"] - hy, o["x"] + hx, o["y"] + hy))
    rb = room["bounds"]
    rx0, rx1 = sorted((rb[0], rb[2]))
    ry0, ry1 = sorted((rb[1], rb[3]))
    without = dict(spec)
    without["volumes"] = [o for o in vols if o is not v]
    seeded = _seeded_cover(v, room)
    placed = [(float(o["x"]), float(o["y"])) for o in vols
              if o is not v and _seeded_cover(o, room)]
    half = max(sx, sy) / 2.0
    door_ok_before = _seed_clear_doors(spec, room, float(v["x"]), float(v["y"]), half)
    n = int(round(reach / step))
    cands = sorted(((i * step, j * step) for i in range(-n, n + 1)
                    for j in range(-n, n + 1)
                    if (i * step) ** 2 + (j * step) ** 2 <= reach ** 2 + 1e-9),
                   key=lambda d: (round(d[0] ** 2 + d[1] ** 2, 6), d))
    for dx, dy in cands:
        px, py = float(v["x"]) + dx, float(v["y"]) + dy
        r = (px - sx / 2.0, py - sy / 2.0, px + sx / 2.0, py + sy / 2.0)
        if r[0] < rx0 or r[2] > rx1 or r[1] < ry0 or r[3] > ry1:
            continue
        if any(min(r[2], k[2]) > max(r[0], k[0]) and min(r[3], k[3]) > max(r[1], k[1])
               for k in keep):
            continue
        if any(min(r[2], o[2]) - max(r[0], o[0]) > -0.05
               and min(r[3], o[3]) - max(r[1], o[1]) > -0.05 for o in others):
            continue
        if door_ok_before and not _seed_clear_doors(spec, room, px, py, half):
            continue
        if seeded and not _seed_clear(without, room, px, py, placed, half=half):
            continue
        v["x"], v["y"] = round(px, 2), round(py, 2)
        return (round(dx, 2), round(dy, 2))
    return None


def _seed_clear_doors(spec, room, px, py, half):
    """`_seed_clear`'s door-approach rule, on its own so `reseat_piece` asks
    the same one: no piece within 1.5 m of an exterior or partition opening
    on its storey, measured FROM THE EDGE, like every other check there -- a
    flat 1.5 m from the CENTRE let a 1.6 m desk stand 0.2 m off a door jamb."""
    story = room.get("story", 0)
    hx = spec.get("footprint_x", 20) / 2
    hy = spec.get("footprint_y", 20) / 2
    for w in spec.get("ext_walls", []):
        if w.get("story", 0) != story:
            continue
        run = spec.get("footprint_x", 20) if w["wall"] in ("N", "S") else spec.get("footprint_y", 20)
        for op in w.get("openings", []):
            u = op.get("pos", 0.0) * run
            ox, oy = {"N": (u, hy), "S": (u, -hy), "E": (hx, u), "W": (-hx, u)}[w["wall"]]
            if math.hypot(ox - px, oy - py) < 1.5 + half:
                return False
    for p in spec.get("partitions", []):
        if p.get("story", 0) != story:
            continue
        run = abs(p["end"] - p["start"])
        for op in p.get("openings", []):
            u = p["start"] + (op.get("pos", 0.0) + 0.5) * run
            ox, oy = (p["pos"], u) if p["axis"] == "Y" else (u, p["pos"])
            if math.hypot(ox - px, oy - py) < 1.5 + half:
                return False
    return True


def seed_cover(spec):
'''


SEED_DOORS_OLD = '''    # exterior + partition opening approach clearance
    hx = spec.get("footprint_x", 20) / 2
    hy = spec.get("footprint_y", 20) / 2
    for w in spec.get("ext_walls", []):
        if over_openings:
            break
        if w.get("story", 0) != story:
            continue
        run = spec.get("footprint_x", 20) if w["wall"] in ("N", "S") else spec.get("footprint_y", 20)
        for op in w.get("openings", []):
            u = op.get("pos", 0.0) * run
            ox, oy = {"N": (u, hy), "S": (u, -hy), "E": (hx, u), "W": (-hx, u)}[w["wall"]]
            # FROM THE EDGE, like every other check here: a flat 1.5 m from
            # the CENTRE let a 1.6 m desk stand 0.2 m off a door jamb.
            if math.hypot(ox - px, oy - py) < 1.5 + half:
                return False
    for p in spec.get("partitions", []):
        if over_openings:
            break
        if p.get("story", 0) != story:
            continue
        run = abs(p["end"] - p["start"])
        for op in p.get("openings", []):
            u = p["start"] + (op.get("pos", 0.0) + 0.5) * run
            ox, oy = (p["pos"], u) if p["axis"] == "Y" else (u, p["pos"])
            if math.hypot(ox - px, oy - py) < 1.5 + half:
                return False
'''
SEED_DOORS_NEW = '''    # exterior + partition opening approach clearance (`_seed_clear_doors`,
    # which `reseat_piece` asks too: one spelling of the rule, 0.192.0)
    if not over_openings and not _seed_clear_doors(spec, room, px, py, half):
        return False
'''


def _patch(path, edits):
    data = path.read_bytes()
    assert b"\r\n" not in data, f"{path.name} is LF"
    text = data.decode("utf-8")
    for old, new in edits:
        n = text.count(old)
        assert n == 1, (path.name, "anchor matched %d times" % n, old[:70])
        text = text.replace(old, new)
    return text


def main():
    lint = _patch(LINT, [(LINT_ANCHOR, LINT_NEW), (LINT_WIRE_OLD, LINT_WIRE_NEW)])
    design = _patch(DESIGN, [(SEED_DOORS_OLD, SEED_DOORS_NEW), (DESIGN_ANCHOR, DESIGN_NEW)])
    LINT.write_bytes(lint.encode("utf-8"))
    DESIGN.write_bytes(design.encode("utf-8"))
    print("layout_lint.py: L23 stale_pieces; level_design.py: reseat_piece")


if __name__ == "__main__":
    main()
