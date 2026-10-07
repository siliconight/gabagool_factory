"""Deli Counter 0.201.0: a deli hangs its beer sign in its front window and
tapes its sale posters under it.

    python patch_dc_deli_window.py

Four files, every anchor asserted once, nothing written on a miss (as read
2026-10-06, all LF):
  * `migrate_window_sign.py` (10,152 bytes): `is_deli`, `front_window`,
    `plan_window`; `migrate` plans a store's sign beside its door and a
    deli's in its window;
  * `migrate_window_poster.py` (9,079 bytes): `plan_window`, and the same
    dispatch;
  * `level_design.py` (261,319 bytes): `_room_volume_count` counts a sign
    hung in a window as standing on no floor;
  * `presets.py` (222,917 bytes): `corner_deli` dresses its window by the two
    rules, as `gas_station` dresses its glass.

MEASURED FIRST: not one of the six library delis carries a window sign or a
window poster. The store rules qualify `migrate_slush_machine.is_store`
(a `sales_floor` and snack gondolas) and a storey-0 `storefront_glass`
wall; a deli's street face is brick with one punched window, 2.0 m wide,
sill 0.85, head 2.25 (`Opening.resolved`'s 1.4 m height), its customers'
door 10.5 m along the wall.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

SIGN_PLAN_END = '''        return None, "no room beside an entrance on the %s storefront" % wall["wall"]
    return None, "no storefront on the sales floor"


#: The sign's material, as the 166 specs that define it do. A store's own
'''
SIGN_PLAN_END_NEW = '''        return None, "no room beside an entrance on the %s storefront" % wall["wall"]
    return None, "no storefront on the sales floor"


# --------------------------------------------------------------------------
# THE DELI'S WINDOW (0.201.0). A corner deli has no shop front of glass: its
# street face is brick, with the customers' door and one punched window
# (`presets.corner_deli`'s S wall: the door at pos -0.28, a 2.0 m window at
# pos 0.0, sill 0.85). Its beer sign hangs IN that window -- centred on it,
# its top the window's head, `WINDOW_INSET` inside the wall's inner face,
# against the pane as a deli's neon hangs -- not beside a door in a wall of
# glass. Not one of the six library delis had a sign before this.
DELI_CASE = "deli_case"
DOOR_TAG = "front_customer_entry"
WINDOW_INSET = 0.04              # inside the wall's inner face: on the pane
WINDOW_MARGIN = 0.10             # the sign's ends inside the window's jambs


def is_deli(d):
    """A corner deli: a building with a deli case (`presets.corner_deli`'s
    `deli_case_cover`, Zoo's `deli_case`)."""
    return any(str(v.get("name", "")).startswith(DELI_CASE) for v in d.get("volumes") or [])


def front_window(d):
    """The storey-0 window on the wall that carries the customers' door
    (`DOOR_TAG`), nearest that door, in the spec's frame: ``{wall, axis,
    line, inward, u, width, sill, head, door_u}`` -- ``u`` and ``door_u``
    along the wall from its centre, snapped as the builder cuts them; ``sill``
    and ``head`` over the storey's floor, `Opening.resolved`'s defaults where
    the spec gives none. None when no such window stands."""
    import spec_types
    grid = _grid(d)
    best = None
    for wall in d.get("ext_walls") or []:
        if int(wall.get("story", 0) or 0) != 0:
            continue
        ops = wall.get("openings") or []
        door = next((o for o in ops if o.get("kind") == "door" and o.get("tag") == DOOR_TAG), None)
        if door is None:
            continue
        axis, line, run, inward = _wall_geometry(d, wall["wall"])
        du = _snap(float(door.get("pos", 0.0)) * run, grid)
        for o in ops:
            if o.get("kind") != "window":
                continue
            r = spec_types.Opening(kind="window", width=o.get("width"), height=o.get("height"),
                                   sill=o.get("sill")).resolved()
            u = _snap(float(o.get("pos", 0.0)) * run, grid)
            got = {"wall": wall["wall"], "axis": axis, "line": line, "inward": inward, "u": u,
                   "width": float(r["width"]), "sill": float(r["sill"]),
                   "head": float(r["sill"]) + float(r["height"]), "door_u": du}
            if best is None or abs(u - du) < abs(best["u"] - du):
                best = got
    return best


def plan_window(d):
    """``(volume, why)``: the sign a deli hangs in its front window, or None
    and the reason it cannot."""
    fw = front_window(d)
    if fw is None:
        return None, "no window on the wall of the customers' door"
    w, dp, h = SIZE
    if fw["width"] < w + 2.0 * WINDOW_MARGIN:
        return None, "the front window is %.2f m wide, and the sign needs %.2f" % (
            fw["width"], w + 2.0 * WINDOW_MARGIN)
    if fw["head"] - fw["sill"] < h:
        return None, "the front window is %.2f m tall, and the sign is %.2f" % (
            fw["head"] - fw["sill"], h)
    wt = float(d.get("wall_thick") or 0.3)
    inset = wt / 2.0 + WINDOW_INSET + dp / 2.0
    ix, iy = fw["inward"]
    x, y = ((fw["u"], fw["line"] + iy * inset) if fw["axis"] == 0
            else (fw["line"] + ix * inset, fw["u"]))
    vol = {"name": NAME, "x": round(x, 3), "y": round(y, 3), "z": round(fw["head"] - h / 2.0, 3),
           "size_x": w if fw["axis"] == 0 else dp, "size_y": dp if fw["axis"] == 0 else w,
           "size_z": h, "collision": "none", "material": MATERIAL["id"],
           "form": "window",
           "variant": zlib.crc32(str(d.get("name", "")).encode()) % NAMES}
    # out of the building: S and W already face out (-y, -x)
    if fw["wall"] in ("N", "E"):
        vol["rot_z"] = 180.0
    return vol, None


#: The sign's material, as the 166 specs that define it do. A store's own
'''

SIGN_MIGRATE = '''def migrate(d):
    """``(changed, why)`` for one spec dict, in place."""
    if not migrate_slush_machine.is_store(d):
        return False, None
    vols = d.get("volumes") or []
    have = [i for i, v in enumerate(vols) if v.get("name") == NAME]
    if have:
        # RE-PLACED where the rule has moved (0.160.0's sign-box clearance),
        # in its own slot in the list, so nothing around it moves
        changed = _define_material(d)
        want, _why = plan(d)
'''
SIGN_MIGRATE_NEW = '''def migrate(d):
    """``(changed, why)`` for one spec dict, in place: a store's sign beside
    its door (`plan`), a deli's in its front window (`plan_window`, 0.201.0)."""
    if migrate_slush_machine.is_store(d):
        planner = plan
    elif is_deli(d):
        planner = plan_window
    else:
        return False, None
    vols = d.get("volumes") or []
    have = [i for i, v in enumerate(vols) if v.get("name") == NAME]
    if have:
        # RE-PLACED where the rule has moved (0.160.0's sign-box clearance),
        # in its own slot in the list, so nothing around it moves
        changed = _define_material(d)
        want, _why = planner(d)
'''
SIGN_PLAN_CALL = '''    _define_material(d)
    vol, why = plan(d)
'''
SIGN_PLAN_CALL_NEW = '''    _define_material(d)
    vol, why = planner(d)
'''

POST_PLAN_END = '''        return None, "no clear glass beside an entrance on the %s storefront" % wall["wall"]
    return None, "no storefront on the sales floor"


def migrate(d):
    """``(changed, why)`` for one spec dict, in place."""
    if not migrate_slush_machine.is_store(d):
        return False, None
    vols = d.get("volumes") or []
    have = [i for i, v in enumerate(vols) if v.get("name") == NAME]
    if have:
        changed = _define_material(d)
        bare = dict(d, volumes=[v for v in vols if v.get("name") != NAME])
        want, _why = plan(bare)
        if want is not None and vols[have[0]] != want:
            vols[have[0]] = want
            changed = True
        return changed, None
    vol, why = plan(d)
'''
POST_PLAN_END_NEW = '''        return None, "no clear glass beside an entrance on the %s storefront" % wall["wall"]
    return None, "no storefront on the sales floor"


# --------------------------------------------------------------------------
# THE DELI'S WINDOW (0.201.0, the sign's own reason: `migrate_window_sign`).
# The pair is taped LOW on the deli's front window, under where its beer sign
# hangs -- `WINDOW_FOOT` over the sill, `WINDOW_GAP` under the sign's foot --
# and shifted `WINDOW_SHIFT` toward the customers' door, where they pass:
# taped by somebody, not centred by a rule.
WINDOW_FOOT = 0.10
WINDOW_GAP = 0.05
WINDOW_SHIFT = 0.25


def plan_window(d):
    """``(volume, why)``: the pair a deli tapes in its front window, or None
    and the reason it cannot."""
    fw = SIGN.front_window(d)
    if fw is None:
        return None, "no window on the wall of the customers' door"
    w, dp, h = SIZE
    sign = next((v for v in d.get("volumes") or [] if v.get("name") == SIGN.NAME), None)
    sign_foot = (float(sign["z"]) - float(sign["size_z"]) / 2.0 if sign is not None
                 else fw["head"] - SIGN.SIZE[2])
    foot, top = fw["sill"] + WINDOW_FOOT, sign_foot - WINDOW_GAP
    if top - foot < h:
        return None, "the front window has %.2f m under the sign, and the pair is %.2f" % (
            max(0.0, top - foot), h)
    lo = fw["u"] - fw["width"] / 2.0 + SIGN.WINDOW_MARGIN + w / 2.0
    hi = fw["u"] + fw["width"] / 2.0 - SIGN.WINDOW_MARGIN - w / 2.0
    if hi < lo:
        return None, "the front window is %.2f m wide, and the pair is %.2f" % (fw["width"], w)
    toward = -1.0 if fw["door_u"] < fw["u"] else 1.0
    c = min(hi, max(lo, fw["u"] + toward * WINDOW_SHIFT))
    wt = float(d.get("wall_thick") or 0.3)
    inset = wt / 2.0 + INSET + dp / 2.0
    ix, iy = fw["inward"]
    x, y = ((c, fw["line"] + iy * inset) if fw["axis"] == 0
            else (fw["line"] + ix * inset, c))
    vol = {"name": NAME, "x": round(x, 3), "y": round(y, 3), "z": round(foot + h / 2.0, 3),
           "size_x": w if fw["axis"] == 0 else dp, "size_y": dp if fw["axis"] == 0 else w,
           "size_z": h, "collision": "none", "material": MATERIAL["id"],
           "form": FAMILY,
           "variant": zlib.crc32((str(d.get("name", "")) + "|window_poster").encode()) % VARIANTS}
    if fw["wall"] in ("N", "E"):
        vol["rot_z"] = 180.0
    return vol, None


def migrate(d):
    """``(changed, why)`` for one spec dict, in place: a store's pair beside
    its door (`plan`), a deli's under its window sign (`plan_window`, 0.201.0)."""
    if migrate_slush_machine.is_store(d):
        planner = plan
    elif SIGN.is_deli(d):
        planner = plan_window
    else:
        return False, None
    vols = d.get("volumes") or []
    have = [i for i, v in enumerate(vols) if v.get("name") == NAME]
    if have:
        changed = _define_material(d)
        bare = dict(d, volumes=[v for v in vols if v.get("name") != NAME])
        want, _why = planner(bare)
        if want is not None and vols[have[0]] != want:
            vols[have[0]] = want
            changed = True
        return changed, None
    vol, why = planner(d)
'''

LD_COUNT = '''        if v.get("collision") == "none" and v.get("material") == "paper":
            continue
'''
LD_COUNT_NEW = '''        if v.get("collision") == "none" and v.get("material") == "paper":
            continue
        # A SIGN HUNG IN A WINDOW stands on no floor either (0.201.0): a
        # deli's punched window puts its beer sign's foot at 1.65 m, under
        # the headroom line, and counted it would cost the market aisles a
        # piece -- the store's window sign's defect again, a storey lower
        if v.get("collision") == "none" and v.get("form") == "window":
            continue
'''

PRESET_END = '''    spec.setdefault("ladders", []).append(
        {"x": -7.0, "y": -13.0, "from_story": -1, "to_story": 0,
         "facing": "N", "cut_slabs": True})
    return spec


# ---------------------------------------------------------------------------
# COMPOUND  --  multi-story assault compound with a central atrium + boss room
'''
PRESET_END_NEW = '''    spec.setdefault("ladders", []).append(
        {"x": -7.0, "y": -13.0, "from_story": -1, "to_story": 0,
         "facing": "N", "cut_slabs": True})
    # THE WINDOW (0.201.0): the beer sign in the deli's front window and the
    # pair of sale posters under it, by the rules the library's delis were
    # given them with (`migrate_window_sign`, `migrate_window_poster`), as
    # `gas_station` dresses its glass (0.188.0). A refusal leaves the spec
    # without one; `test_deli_window` holds that this recipe is not refused.
    migrate_window_sign.migrate(spec)
    migrate_window_poster.migrate(spec)
    return spec


# ---------------------------------------------------------------------------
# COMPOUND  --  multi-story assault compound with a central atrium + boss room
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
    plans = [
        (DC / "migrate_window_sign.py", 10152,
         [(SIGN_PLAN_END, SIGN_PLAN_END_NEW), (SIGN_MIGRATE, SIGN_MIGRATE_NEW),
          (SIGN_PLAN_CALL, SIGN_PLAN_CALL_NEW)]),
        (DC / "migrate_window_poster.py", 9079, [(POST_PLAN_END, POST_PLAN_END_NEW)]),
        (DC / "level_design.py", 261319, [(LD_COUNT, LD_COUNT_NEW)]),
        (DC / "presets.py", 222917, [(PRESET_END, PRESET_END_NEW)]),
    ]
    out = [(p, _apply(p, n, e)) for p, n, e in plans]
    for p, text in out:
        p.write_bytes(text.encode("utf-8"))
        b = p.read_bytes()
        assert b"\r\n" not in b, p.name
        print("%s: %d bytes" % (p.name, len(b)))


if __name__ == "__main__":
    main()
