"""Edit a Deli Counter clone for 0.278.0: a supermarket's gondolas are Zoo 1.133.0's grocery form, each the variant of
its line and turned so the faces either side of a lane sell what that lane's marker says. Run from the clone's root.
Asserts every anchor once; refuses on a miss."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


edit("level_design.py", [
('''def aisle_markers(spec, room):
    """``[(x, y, sx, sy), ...]``: where a supermarket's sales floor hangs its
    aisle markers, aisle 1 first (0.276.0). Read off the gondolas standing on
    the room's floor (`gondola_*`, authored or laid by its rows): grouped into
    LINES along the axis most of them are long in, each lane between two
    neighbouring lines takes one marker at its storefront end -- the end
    nearer the storey's glazed wall, else the low end. A board is
    `_MARKER_W` across the lane, or the lane's width less 10 cm."""
    x0, y0, x1, y1 = room["bounds"]
    sh = _story_height(spec)
    story = int(room.get("story", 0) or 0)
    floor = story * sh
    gon = [v for v in spec.get("volumes") or []
           if str(v.get("name", "")).startswith("gondola_")
           and x0 <= v.get("x", 1e9) <= x1 and y0 <= v.get("y", 1e9) <= y1
           and stands_on_storey(float(v.get("z", 0.0)), float(v.get("size_z", 0.0)), floor, sh)]
    if len(gon) < 2:
        return []
    along_y = sum(1 for v in gon if v["size_y"] >= v["size_x"]) * 2 >= len(gon)
    lines = []
    for v in sorted(gon, key=lambda v: v["x"] if along_y else v["y"]):
        c = v["x"] if along_y else v["y"]
        dep = v["size_x"] if along_y else v["size_y"]
        a = v["y"] if along_y else v["x"]
        ln = v["size_y"] if along_y else v["size_x"]
        if lines and abs(c - lines[-1]["c"]) <= _LINE_TOL:
            g = lines[-1]
            g["lo"], g["hi"] = min(g["lo"], a - ln / 2.0), max(g["hi"], a + ln / 2.0)
            g["half"] = max(g["half"], dep / 2.0)
        else:
            lines.append({"c": c, "half": dep / 2.0, "lo": a - ln / 2.0, "hi": a + ln / 2.0})
    # the storefront''',
'''def _gondola_lines(spec, room):
    """``(along_y, lines)``: the gondolas standing on ``room``'s floor
    (`gondola_*`, authored or laid by its rows), grouped into LINES along the
    axis most of them are long in, sorted from the low end of the cross axis
    -- each ``{"c", "half", "lo", "hi", "vols"}``. ``(None, [])`` under two
    gondolas. One grouping for the markers (0.276.0) and the stock they name
    (0.278.0), so the two cannot disagree about which line is which."""
    x0, y0, x1, y1 = room["bounds"]
    sh = _story_height(spec)
    story = int(room.get("story", 0) or 0)
    floor = story * sh
    gon = [v for v in spec.get("volumes") or []
           if str(v.get("name", "")).startswith("gondola_")
           and x0 <= v.get("x", 1e9) <= x1 and y0 <= v.get("y", 1e9) <= y1
           and stands_on_storey(float(v.get("z", 0.0)), float(v.get("size_z", 0.0)), floor, sh)]
    if len(gon) < 2:
        return None, []
    along_y = sum(1 for v in gon if v["size_y"] >= v["size_x"]) * 2 >= len(gon)
    lines = []
    for v in sorted(gon, key=lambda v: v["x"] if along_y else v["y"]):
        c = v["x"] if along_y else v["y"]
        dep = v["size_x"] if along_y else v["size_y"]
        a = v["y"] if along_y else v["x"]
        ln = v["size_y"] if along_y else v["size_x"]
        if lines and abs(c - lines[-1]["c"]) <= _LINE_TOL:
            g = lines[-1]
            g["lo"], g["hi"] = min(g["lo"], a - ln / 2.0), max(g["hi"], a + ln / 2.0)
            g["half"] = max(g["half"], dep / 2.0)
            g["vols"].append(v)
        else:
            lines.append({"c": c, "half": dep / 2.0, "lo": a - ln / 2.0, "hi": a + ln / 2.0,
                          "vols": [v]})
    return along_y, lines


def aisle_markers(spec, room):
    """``[(x, y, sx, sy), ...]``: where a supermarket's sales floor hangs its
    aisle markers, aisle 1 first (0.276.0). Read off the gondolas' LINES
    (`_gondola_lines`): each lane between two neighbouring lines takes one
    marker at its storefront end -- the end nearer the storey's glazed wall,
    else the low end. A board is `_MARKER_W` across the lane, or the lane's
    width less 10 cm."""
    along_y, lines = _gondola_lines(spec, room)
    if not lines:
        return []
    story = int(room.get("story", 0) or 0)
    # the storefront'''),
('''def authored_aisles(spec, room):''',
'''#: THE STOCK THE MARKERS NAME (0.278.0). Zoo 1.133.0's `snack_gondola` form
#: `grocery` sells, on each face, one of the 24 categories the markers print,
#: two a lane: its VARIANT is the gondola's line, face -Y the second category
#: of the lane before and face +Y the first of the lane after. Twelve lines
#: sell all 24; a thirteenth starts round again.
_GROCERY_LINES = 12


def _plus_y_plan(v):
    """Where a gondola volume's module +Y points in plan, in degrees from
    plan +Y clockwise (0 +Y, 90 +X, 180 -Y, 270 -X): the slot's turn --
    `prop_species.long_axis_first`'s, plus the volume's own `rot_z` -- takes
    the module's +X to plan +X at 0, -Y at 90, -X at 180, +Y at 270 (the
    composer's measured convention, `deli_counter.py`'s stoop rails), so its
    +Y to plan +Y, +X, -Y, -X."""
    import prop_species
    _dims, turn = prop_species.long_axis_first(
        (v["size_x"], v["size_y"], v.get("size_z", 0.0)), "snack_gondola")
    return round((turn + float(v.get("rot_z", 0.0) or 0.0)) % 360.0, 4)


def stock_supermarket_gondolas(spec, room):
    """Make each of a supermarket's gondolas sell what the markers either
    side of it say (0.278.0): form `grocery`, the variant its line's
    (`_gondola_lines`, low end of the cross axis first), turned half round
    when its module's +Y points to the lower lane -- a gondola is an island,
    shopped both sides, so the turn moves nothing it collides with. Returns
    how many volumes changed; a second call changes none."""
    along_y, lines = _gondola_lines(spec, room)
    want_deg = 90.0 if along_y else 0.0
    changed = 0
    for n, line in enumerate(lines):
        for v in line["vols"]:
            before = (v.get("form"), v.get("variant"), v.get("rot_z"))
            v["form"] = "grocery"
            k = n % _GROCERY_LINES
            if k:
                v["variant"] = k
            else:
                v.pop("variant", None)
            if abs(_plus_y_plan(v) - want_deg) > 1e-6:
                rz = round((float(v.get("rot_z", 0.0) or 0.0) + 180.0) % 360.0, 4)
                if rz:
                    v["rot_z"] = rz
                else:
                    v.pop("rot_z", None)
            assert abs(_plus_y_plan(v) - want_deg) <= 1e-6, (v.get("name"), _plus_y_plan(v))
            if (v.get("form"), v.get("variant"), v.get("rot_z")) != before:
                changed += 1
    return changed


def authored_aisles(spec, room):'''),
('''                spec["volumes"].append(vol)
                added += 1
    # THE BACK BARS BEFORE THE FIXTURES,''',
'''                spec["volumes"].append(vol)
                added += 1
        # ...AND THE SHELVES UNDER THEM SELL WHAT THEY SAY (0.278.0,
        # `stock_supermarket_gondolas`): every line of gondolas, authored or
        # laid, the grocery form of its line
        if kind == "supermarket":
            stock_supermarket_gondolas(spec, room)
    # THE BACK BARS BEFORE THE FIXTURES,'''),
])
