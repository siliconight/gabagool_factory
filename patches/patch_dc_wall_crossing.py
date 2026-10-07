"""Deli Counter 0.199.0: no piece passes through a wall.

    python patch_dc_wall_crossing.py

Three edits, each anchored and asserted once, nothing written on a miss:
  * `layout_lint.py` (61,059 bytes, LF, as read 2026-10-06): `built_walls`,
    `wall_crossings` and the L25 rule after L23, wired into `lint_spec`;
  * `presets.py` (222,398 bytes, LF): `make` trims the recipe's pieces
    through its own walls before any pass places round them;
  * `migrate_wall_crossing.py`, NEW: the trim, and the migration that brings
    the library to it.

MEASURED FIRST (the factory's docs/findings/pieces_through_walls/): 19 pieces
in 15 of 146 non-LF specs reach past both faces of a built wall -- 7 through
one (six deli cases, 0.825 m; warehouse's shelving run, 3.85 m) and 12 along
one -- and of the 23 recipes, `corner_deli` and `hospital` generate a piece
through a wall. Two instruments agree on the 19: one on the authored runs,
one on the walls the builder cuts (setbacks, stairwell splits, every
exterior side, turned pieces).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
LINT = DC / "layout_lint.py"
PRESETS = DC / "presets.py"
MIGRATION = DC / "migrate_wall_crossing.py"

LINT_ANCHOR = '''        out.append(f"L23 a piece over an opening or in a stair's walk: "
                   f"'{p['name']}' on storey {p['story']} has "
                   + " and ".join(where))
    return out


def ladder_findings(spec):
'''

LINT_NEW = '''        out.append(f"L23 a piece over an opening or in a stair's walk: "
                   f"'{p['name']}' on storey {p['story']} has "
                   + " and ".join(where))
    return out


#: Slack for float noise, not a tolerance on the finding (L25): a piece one
#: millimetre past a wall's far face is through it.
WALL_CROSS_EPS = 1e-6


def _spec_value(spec, key):
    """A spec's field, or `LevelSpec`'s default when the dict leaves it out:
    the builder reads the dataclass, so a missing key builds the default, not
    nothing (`migrate_window_sign._grid`'s rule, for any field)."""
    v = spec.get(key)
    if v is not None:
        return v
    import dataclasses
    import spec_types
    return next(f.default for f in dataclasses.fields(spec_types.LevelSpec)
                if f.name == key)


def built_walls(spec):
    """``[(label, story, n, plane, half, spans)]``: every wall the builder
    stands, in the spec's frame (metres, the footprint centred on 0). ``n``
    is the axis the wall's faces look along (0: a wall running along y),
    ``plane`` its centreline, ``half`` half its thickness and ``spans`` the
    stretches of its run that are built.

    AS `deli_counter.Builder` STANDS THEM, asked of the helpers it asks:
    - a partition is `partition_bounds.partition_spans` of its authored run,
      clamped to its storey's `setbacks.storey_extent` and split round
      `stairwell.wall_voids`, `min_span` the wall's thickness
      (`Builder._partitions`), and is named `int_<storey>_<index>` as it is;
    - an exterior wall runs its storey's extent edge on every storey from the
      basement to `n_stories`: all four sides under `auto_exterior`, else the
      sides `ext_walls` lists (`Builder._exterior`).

    OPENINGS ARE NOT CUT. A door's leaf, a breach panel, a rollgate and a
    pane each fill theirs, so a piece across one meets built geometry as it
    meets a wall. Measured first, no crossing in the library stands at an
    opening: 19 with the openings cut, the same 19 without."""
    import partition_bounds
    import setbacks
    fx, fy = spec.get("footprint_x"), spec.get("footprint_y")
    if not fx or not fy:
        return []
    fx, fy = float(fx), float(fy)
    half = float(_spec_value(spec, "wall_thick")) / 2.0
    view = _LintSpec(spec)
    voids = {}
    if spec.get("stairs") or spec.get("ramps") or spec.get("slab_holes"):
        import spec_loader
        import stairwell
        voids = stairwell.wall_voids(spec_loader.spec_from_dict(spec))
    out = []
    for i, p in enumerate(spec.get("partitions") or []):
        story = int(p.get("story", 0) or 0)
        ax = str(p.get("axis", "X")).upper()
        lo, hi = (-fx / 2.0, fx / 2.0) if ax == "X" else (-fy / 2.0, fy / 2.0)
        start = lo if p.get("start") is None else float(p["start"])
        end = hi if p.get("end") is None else float(p["end"])
        pos = float(p.get("pos", 0.0))
        spans = partition_bounds.partition_spans(
            start, end, ax, pos, fx, fy, voids.get(story, ()),
            min_span=2.0 * half, extent=setbacks.storey_extent(view, story))
        out.append((f"int_{story}_{i}", story, 0 if ax == "Y" else 1, pos,
                    half, list(spans)))
    explicit = {(str(w.get("wall")), int(w.get("story", 0) or 0))
                for w in spec.get("ext_walls") or []}
    auto = bool(_spec_value(spec, "auto_exterior"))
    base = -1 if _spec_value(spec, "has_basement") else 0
    for story in range(base, int(_spec_value(spec, "n_stories"))):
        x0, y0, x1, y1 = setbacks.storey_extent(view, story)
        for side in ("N", "S", "E", "W"):
            if (side, story) not in explicit and not auto:
                continue
            if side in ("N", "S"):
                out.append((f"ext_{story}_{side}", story, 1,
                            y1 if side == "N" else y0, half, [(x0, x1)]))
            else:
                out.append((f"ext_{story}_{side}", story, 0,
                            x1 if side == "E" else x0, half, [(y0, y1)]))
    return out


def _piece_footprints(v):
    """``[(kind, polygon)]``: the plan shapes a piece occupies. ``box`` is the
    authored box -- the greybox and its collider, drawn axis-aligned whatever
    `rot_z` says (`Builder._volumes`). ``art``, when `rot_z` turns the piece,
    is that box turned about its centre as the slot turns the module:
    counter-clockwise from above, Blender's z."""
    x, y = float(v.get("x", 0.0)), float(v.get("y", 0.0))
    hx = float(v.get("size_x", 0.0)) / 2.0
    hy = float(v.get("size_y", 0.0)) / 2.0
    box = [(x - hx, y - hy), (x + hx, y - hy), (x + hx, y + hy), (x - hx, y + hy)]
    out = [("box", box)]
    rz = float(v.get("rot_z", 0.0) or 0.0) % 360.0
    if min(rz, 360.0 - rz) > WALL_CROSS_EPS:
        c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz))
        out.append(("art", [(x + c * (px - x) - s * (py - y),
                             y + s * (px - x) + c * (py - y)) for px, py in box]))
    return out


def _clip_to_run(poly, a, lo, hi):
    """A convex polygon cut to ``lo <= coordinate a <= hi``."""
    def keep(pts, inside, edge):
        out = []
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            if inside(p):
                out.append(p)
            if inside(p) != inside(q):
                t = (edge - p[a]) / (q[a] - p[a])
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        return out
    pts = keep(poly, lambda p: p[a] >= lo, lo)
    return keep(pts, lambda p: p[a] <= hi, hi) if pts else []


def wall_crossings(spec):
    """``[{index, name, wall, story, shape, past, footprint, axis, faces}]``:
    every piece whose plan reaches past BOTH faces of a built wall
    (`built_walls`) on a storey its height reaches -- matter on both sides.

    ``shape`` is ``through`` when the piece's centre stands off the wall, so
    its far end comes out of the wall's other face, and ``along`` when its
    centre is inside the wall's band, so the wall runs inside it. ``past`` is
    the shorter of its two overhangs beyond the wall's faces, in metres: for
    a piece through a wall, how far it comes out on the far side. ``axis``
    (``x`` or ``y``) is the one the wall's faces look along and ``faces``
    their two positions on it. A piece is reported once a wall: by its box
    when the box crosses, by its turned art when only the art does.

    A piece that ends inside a band, or meets a face, is not through it."""
    sh = float(_spec_value(spec, "story_height"))
    walls = built_walls(spec)
    eps = WALL_CROSS_EPS
    out = []
    for i, v in enumerate(spec.get("volumes") or []):
        z = float(v.get("z", 0.0))
        hz = float(v.get("size_z", 0.0)) / 2.0
        shapes = _piece_footprints(v)
        for label, story, n, plane, half, spans in walls:
            if z + hz <= story * sh + eps or z - hz >= (story + 1) * sh - eps:
                continue
            f0, f1 = plane - half, plane + half
            a = 1 - n
            for kind, poly in shapes:
                lo = hi = None
                for s0, s1 in spans:
                    pts = _clip_to_run(poly, a, s0, s1)
                    if len(pts) < 3:
                        continue
                    plo, phi = min(p[n] for p in pts), max(p[n] for p in pts)
                    if plo < f0 - eps and phi > f1 + eps:
                        lo = plo if lo is None else min(lo, plo)
                        hi = phi if hi is None else max(hi, phi)
                if lo is None:
                    continue
                c = sum(p[n] for p in poly) / len(poly)
                out.append({"index": i, "name": v.get("name"), "wall": label,
                            "story": story,
                            "shape": ("along" if f0 - eps <= c <= f1 + eps
                                      else "through"),
                            "past": round(min(hi - f1, f0 - lo), 6),
                            "footprint": kind, "axis": "xy"[n],
                            "faces": (f0, f1)})
                break
    return out


def wall_crossing_findings(spec):
    """L25 (WARN, 0.199.0): a piece passes through a wall.

    MEASURED 2026-10-06 across the 146 non-LF specs: 19 pieces in 15 shells.
    - THROUGH, 7: every deli's case came 0.825 m out of its partition into
      the market aisles, because `presets.corner_deli` authored it 7.0 m long
      from x -14.0 with that partition at x -8.0 (cold run 9189's composed
      deli_a01 builds it so: the case at x -14.0..-7.0, `int_0_0_seg6` at
      x -8.0 across it); `warehouse`'s 16 m shelving run, 3.85 m.
    - ALONG, 12: racks, forklift bays, vomitory covers, a rollgate, a vault
      door and four columns, each centred on a wall's line.
    No gate saw any of them: every rule asked of a piece where it stands,
    and none whether a wall stands in it.

    Born WARN. A recipe's piece through its own wall is trimmed where it is
    generated (`presets.make`, `migrate_wall_crossing.trim`), and the library
    was brought to the rule; the twelve ALONG a wall stand frozen in
    `wall_crossing_baseline.json` until each is looked at, and
    `test_wall_crossing.py` fails a new one. This says what it measured, not
    why."""
    out = []
    for r in wall_crossings(spec):
        art = " (its art, turned)" if r["footprint"] == "art" else ""
        if r["shape"] == "through":
            out.append(f"L25 a piece through a wall: '{r['name']}' comes "
                       f"{r['past']:.2f} m out of the far side of {r['wall']} "
                       f"on storey {r['story']}{art}")
        else:
            out.append(f"L25 a piece through a wall: {r['wall']} runs along "
                       f"inside '{r['name']}' on storey {r['story']}, "
                       f"{r['past']:.2f} m of it out each side{art}")
    return out


def ladder_findings(spec):
'''

WIRE_ANCHOR = '''    warns += stale_piece_findings(spec)     # L23 a piece where a stair now is
    lf22, lw22 = __import__("vault_room").findings(spec)
'''
WIRE_NEW = '''    warns += stale_piece_findings(spec)     # L23 a piece where a stair now is
    warns += wall_crossing_findings(spec)   # L25 a piece through a wall
    lf22, lw22 = __import__("vault_room").findings(spec)
'''

IMPORT_ANCHOR = '''import migrate_slush_machine
import migrate_window_poster
'''
IMPORT_NEW = '''import migrate_slush_machine
import migrate_wall_crossing
import migrate_window_poster
'''

MAKE_ANCHOR = '''    spec = REGISTRY[preset](**kwargs)
    if seed is not None:
        spec["seed"] = int(seed)
'''
MAKE_NEW = '''    spec = REGISTRY[preset](**kwargs)
    # NO PIECE THROUGH A WALL (0.199.0): a piece a recipe authors through one
    # of its own walls is trimmed back to the side it stands on --
    # `corner_deli`'s case came 0.825 m out into the market aisles and the
    # hospital's waiting seats 0.35 m into the next room. Here, before every
    # pass below, so the cover `enrich` seeds is placed round the piece that
    # is built. A piece ALONG a wall is reported (layout_lint L25), not moved.
    migrate_wall_crossing.trim(spec)
    if seed is not None:
        spec["seed"] = int(seed)
'''

MIGRATION_SRC = '''#!/usr/bin/env python3
"""
migrate_wall_crossing.py  --  a piece through a wall is trimmed back to its side
================================================================================
Deli Counter 0.199.0: the rule `presets.make` runs on every recipe, and the
one-shot, idempotent migration over specs/*.json that brings the library to
it.

MEASURED FIRST (the factory's docs/findings/pieces_through_walls/; layout_lint
L25 asks the same question): 19 pieces in 15 of the 146 non-LF specs reach
past both faces of a wall the builder stands. Seven pass THROUGH one: each of
the six delis' case, authored by `presets.corner_deli` 7.0 m long from x -14.0
with its own partition at x -8.0, so 0.825 m of it stood out in the market
aisles (cold run 9189's composed deli_a01 builds it so: the case at
x -14.0..-7.0, partition `int_0_0_seg6` at x -8.0 across it); and
`warehouse`'s 16 m shelving run, 3.85 m into the room past x 8.0. Of the 23
recipes, `corner_deli` and `hospital` generate one: the case, and the waiting
seats 0.35 m into the next room.

THE RULE, in the spec's frame (metres, the footprint centred on 0): a piece
THROUGH a wall (`layout_lint.wall_crossings`, shape ``through``) keeps the end
on the side its centre stands, and its far end comes back to that side's face
of the wall less `level_design._WALL_PIECE_AIR`, the air a wall-slotted piece
keeps to its wall. Only that one axis moves: the piece keeps its height, its
depth and its near end. REFUSED and reported, never forced:
  * a piece ALONG a wall, centred on its line: which side is it on?
  * a turned piece (`rot_z` not a half turn): its art is not its box;
  * a cut that would leave less than `KEEP_MIN` of the piece: a different
    piece, which its author should name;
  * a cut from under a marker, an objective or a loot point: what stands
    there would stand on nothing.

    python migrate_wall_crossing.py            # write specs/
    python migrate_wall_crossing.py --check    # report only; exit 1 if any
    python migrate_wall_crossing.py --dir D    # another spec directory
"""
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import layout_lint  # noqa: E402
import level_design  # noqa: E402

#: The least share of a piece a cut may leave. A centre off the wall loses
#: under half plus the air, so this bites only where the centre hugs a face.
KEEP_MIN = 0.5
#: Cuts one spec may take before it stands clear: one per piece and wall.
ROUNDS = 64


def _on_the_cut(spec, v, axis, lo, hi):
    """Ids of the markers, objectives and loot standing on the part a cut
    takes away: in plan inside it, and on the piece's storey."""
    other = "y" if axis == "x" else "x"
    c, half = float(v[other]), float(v["size_" + other]) / 2.0
    sh = float(layout_lint._spec_value(spec, "story_height"))
    story = layout_lint.piece_story(spec, v)
    if story is None:
        story = int((float(v.get("z", 0.0)) - float(v.get("size_z", 0.0)) / 2.0) // sh)
    out = []
    for kind in ("markers", "objectives", "loot"):
        for m in spec.get(kind) or []:
            if not (lo <= float(m.get(axis, 0.0)) <= hi
                    and c - half <= float(m.get(other, 0.0)) <= c + half):
                continue
            if story * sh - 0.25 <= float(m.get("z", 0.0)) < (story + 1) * sh:
                out.append(str(m.get("id") or m.get("type") or kind))
    return out


def _why_not(spec, v, row):
    """``(why, cut)``: the reason a crossing is not trimmed, or None and the
    piece's new ``(lo, hi)`` on the wall's axis."""
    a = row["axis"]
    f0, f1 = row["faces"]
    if row["shape"] == "along":
        return ("it stands along %s, centred on its line: which side is it "
                "on?" % row["wall"]), None
    rz = float(v.get("rot_z", 0.0) or 0.0) % 180.0
    if min(rz, 180.0 - rz) > 1e-6:
        return ("it is turned %g degrees: its art is not its box"
                % float(v.get("rot_z"))), None
    c, length = float(v[a]), float(v["size_" + a])
    lo, hi = c - length / 2.0, c + length / 2.0
    air = level_design._WALL_PIECE_AIR
    if c < f0:
        new, taken = (lo, f0 - air), (f0 - air, hi)
    else:
        new, taken = (f1 + air, hi), (lo, f1 + air)
    if new[1] - new[0] < KEEP_MIN * length:
        return ("the cut would leave %.2f of its %.2f m, less than half of it"
                % (new[1] - new[0], length)), None
    under = _on_the_cut(spec, v, a, *taken)
    if under:
        return ("the cut would take the ground from under %s"
                % ", ".join(under)), None
    return None, new


def trim(spec):
    """``(trimmed, refused)`` for one spec dict, in place. ``trimmed`` holds a
    record a cut, ``{name, wall, axis, from, to}`` (the piece's ends on that
    axis before and after); ``refused`` holds ``(name, wall, why)``."""
    trimmed, refused, skip = [], [], set()
    for _ in range(ROUNDS):
        row = next((r for r in layout_lint.wall_crossings(spec)
                    if (r["index"], r["wall"]) not in skip), None)
        if row is None:
            break
        v = spec["volumes"][row["index"]]
        why, new = _why_not(spec, v, row)
        if why:
            refused.append((row["name"], row["wall"], why))
            skip.add((row["index"], row["wall"]))
            continue
        a = row["axis"]
        c, length = float(v[a]), float(v["size_" + a])
        v[a] = round((new[0] + new[1]) / 2.0, 4)
        v["size_" + a] = round(new[1] - new[0], 4)
        trimmed.append({"name": row["name"], "wall": row["wall"], "axis": a,
                        "from": [round(c - length / 2.0, 4), round(c + length / 2.0, 4)],
                        "to": [round(new[0], 4), round(new[1], 4)]})
    return trimmed, refused


def migrate(d):
    """``(changed, why)`` for one spec dict, in place."""
    trimmed, refused = trim(d)
    why = "; ".join("'%s' at %s: %s" % r for r in refused) or None
    return bool(trimmed), why


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    check = "--check" in argv
    root = os.path.join(HERE, "specs")
    if "--dir" in argv:
        root = argv[argv.index("--dir") + 1]
    n = 0
    for p in sorted(glob.glob(os.path.join(root, "*.json"))):
        if os.path.basename(p).startswith("lf_"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except ValueError:
            continue
        trimmed, refused = trim(d)
        for name, wall, why in refused:
            print(f"[wall_crossing] {os.path.basename(p)}: '{name}' at {wall} "
                  f"REFUSED -- {why}")
        if not trimmed:
            continue
        n += 1
        for t in trimmed:
            print(f"[wall_crossing] {os.path.basename(p)}: '{t['name']}' through "
                  f"{t['wall']}: {t['axis']} {t['from'][0]}..{t['from'][1]} -> "
                  f"{t['to'][0]}..{t['to'][1]}")
        if not check:
            io.open(p, "w", encoding="utf-8", newline="\\n").write(json.dumps(d, indent=1) + "\\n")
    print(f"[wall_crossing] {n} spec(s) {'need' if check else 'given'} a piece trimmed off a wall")
    return 1 if check and n else 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _apply(path, size, edits):
    data = path.read_bytes()
    assert len(data) == size, "%s is %d bytes, not the %d read; refusing" % (path.name, len(data), size)
    assert b"\r\n" not in data, "CRLF in %s; refusing" % path.name
    text = data.decode("utf-8")
    for old, _new in edits:
        n = text.count(old)
        assert n == 1, "%s: anchor found %d times, not once: %r" % (path.name, n, old[:60])
    for old, new in edits:
        text = text.replace(old, new)
    return text


def main():
    assert not MIGRATION.exists(), "migrate_wall_crossing.py already exists; refusing"
    lint = _apply(LINT, 61059, [(LINT_ANCHOR, LINT_NEW), (WIRE_ANCHOR, WIRE_NEW)])
    pre = _apply(PRESETS, 222398, [(IMPORT_ANCHOR, IMPORT_NEW), (MAKE_ANCHOR, MAKE_NEW)])
    LINT.write_bytes(lint.encode("utf-8"))
    PRESETS.write_bytes(pre.encode("utf-8"))
    MIGRATION.write_bytes(MIGRATION_SRC.encode("utf-8"))
    for p in (LINT, PRESETS, MIGRATION):
        b = p.read_bytes()
        assert b"\r\n" not in b, p.name
        print("%s: %d bytes" % (p.name, len(b)))


if __name__ == "__main__":
    main()
