"""Edit a Deli Counter clone for 0.276.0: a supermarket hangs a numbered grocery marker over each aisle (Zoo 1.131.0's
`aisle_sign` form `grocery`). Run from the clone's root. Asserts every anchor once; refuses on a miss."""
from pathlib import Path

p = Path("level_design.py")
t = p.read_bytes().decode("utf-8")
assert "\r\n" not in t


def sub(old, new):
    global t
    assert t.count(old) == 1, (old[:70], t.count(old))
    t = t.replace(old, new)


sub('''def authored_aisles(spec, room):''', '''#: THE SUPERMARKET'S AISLE MARKERS (0.276.0). The walker's grocery comps,
#: 2026-10-26 (the factory's docs/reference/GROCERY_STORE_COMPS.md): a printed
#: sign over the head of every aisle, its number large and what is down it
#: beside it. One hangs over each LANE between two lines of a supermarket's
#: gondolas -- its own aisles or the rows furnish laid -- at the lane's end
#: nearer the storefront, where a shopper walking in reads it, its board
#: across the lane. Lanes are numbered from the low end of the cross axis,
#: aisle 1 first; Zoo's `aisle_sign` form `grocery` prints the number the
#: variant gives (aisle n is variant n - 1) and twelve aisles' worth of lines.
_MARKER_W = 1.4
_MARKER_D = 0.06
_MARKER_H = 0.5
#: How far in from a lane's end the marker hangs: over the lane, clear of the
#: gondolas' end caps.
_MARKER_IN = 0.6
#: Two gondolas stand in one LINE when their centres across it are this close.
_LINE_TOL = 0.3
#: Zoo's `aisle_sign` builds 0.5 to 1.8 m wide; a lane narrower than this
#: takes no marker.
_MARKER_MIN_W = 0.5
_MARKERS_MAX = 12


def aisle_markers(spec, room):
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
    # the storefront: a glazed exterior wall on this storey, on the lanes' ends
    glass = {w.get("wall") for w in spec.get("ext_walls") or []
             if "glass" in str(w.get("material") or "") and int(w.get("story", 0) or 0) == story}
    low_end = ("S" in glass) if along_y else ("W" in glass)
    high_end = ("N" in glass) if along_y else ("E" in glass)
    out = []
    for g0, g1 in zip(lines, lines[1:]):
        a, b = g0["c"] + g0["half"], g1["c"] - g1["half"]
        width = min(_MARKER_W, (b - a) - 0.1)
        if width < _MARKER_MIN_W:
            continue
        lo, hi = max(g0["lo"], g1["lo"]), min(g0["hi"], g1["hi"])
        if hi - lo < 2.0 * _MARKER_IN:
            continue
        at = hi - _MARKER_IN if (high_end and not low_end) else lo + _MARKER_IN
        mid = (a + b) / 2.0
        if along_y:
            out.append((mid, at, width, _MARKER_D))
        else:
            out.append((at, mid, _MARKER_D, width))
    return out[:_MARKERS_MAX]


def authored_aisles(spec, room):''')

sub('''            got = _move(vol, (hx, hy), how, hseq, key, size)
            added += got if got else -1
    # THE BACK BARS BEFORE THE FIXTURES''', '''            got = _move(vol, (hx, hy), how, hseq, key, size)
            added += got if got else -1
        # A SUPERMARKET'S AISLE MARKERS (0.276.0, `aisle_markers`), hung last,
        # over the lanes its gondolas now leave, numbered from aisle 1; a room
        # whose storey cannot give a body its headroom under one hangs none
        if kind == "supermarket" and hung_headroom_ok(spec, _PIECES["aisle_sign"], _MARKER_H):
            for n, (mx, my, sx, sy) in enumerate(aisle_markers(spec, room)):
                vol = _volume("aisle_sign", mx, my, sx, sy, _MARKER_H, 0.0)
                vol["form"] = "grocery"
                vol.pop("variant", None)
                if n:
                    vol["variant"] = n
                spec["volumes"].append(vol)
                added += 1
    # THE BACK BARS BEFORE THE FIXTURES''')

p.write_bytes(t.encode("utf-8"))
print("level_design.py edited")
