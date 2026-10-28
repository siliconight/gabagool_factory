"""Zoo 1.138.0, part one: `price_pylon` form `bank` -- a bank's time-and-temperature sign. Run in a Zoo clone's root.

Every anchor is asserted to occur exactly once; nothing is written on a miss.
"""
import json
import pathlib

R = pathlib.Path.cwd()


def edit(rel, pairs):
    p = R / rel
    t = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n")
    for a, b in pairs:
        assert t.count(a) == 1, (rel, t.count(a), a[:80])
        t = t.replace(a, b)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print(p, "edited")


edit("zoo_keeper/core/price_pylon_forms.py", [
('''def art(w, h, variant=0):
    """ONE image: the brand face (`brand`), the price face (`price`), the
    strip (`strip`), and an `edge` block. ``{canvas, size, rects, name,
    said}``; rects are pixel boxes, row 0 at the top."""
    field, rule, ink = COLOURWAYS[variant % len(COLOURWAYS)]''',
 '''def art(w, h, variant=0, form="auto"):
    """ONE image: the brand face (`brand`), the price face (`price`), the
    strip (`strip`), and an `edge` block. ``{canvas, size, rects, name,
    said}``; rects are pixel boxes, row 0 at the top. ``form`` "bank" is
    `bank_art`'s: the same three faces saying a bank's name, the time and
    the temperature."""
    if form == "bank":
        return bank_art(w, h, variant)
    field, rule, ink = COLOURWAYS[variant % len(COLOURWAYS)]'''),
])

# appended: the bank's faces
p = R / "zoo_keeper/core/price_pylon_forms.py"
t = p.read_bytes().decode("utf-8")
assert "def bank_art(" not in t
t = t.rstrip("\n") + '''


# --- a bank's time and temperature (1.138.0) ---------------------------------------------

#: THE BANK FORM. The walker's bank list, outside: a bank's street sign that
#: flashed the time and the temperature, from 1951 on (Watchfire's history; the
#: factory's docs/reference/BANK_INTERIOR_COMPS.md) -- a gas pylon's frame, its
#: brand cabinet the bank's name, its price cabinet the time over the
#: temperature in amber lamps on black, its strip the deposit insurance line.
#: The name and its colours are the teller line's (`teller_line_forms.bank_said`):
#: the sixteen variants are four names in four colourways, and
#: `teller_line_forms.variant_for` is the one over the bank's door.
BANK_STRIP = "MEMBER FDIC"
LAMP = (255, 168, 40)
LAMP_OFF = (52, 34, 12)
#: what a sign reads, a reading a variant: the hour and the temperature it was
#: shot at (a still sign; the walker's "levels feel static" asks it to tick)
READINGS = (("7:42", 54), ("11:05", 38), ("2:17", 71), ("9:58", 86))


def _lamps(c, text, x0, y0, x1, y1, face):
    """``text`` in lamp dots inside the box, centred: unlit bulbs over every
    dot of the box first, as a lamp matrix reads by day. Returns the width
    and scale it set at, or (0, 0) when it did not set."""
    k = _scale(text, x1 - x0 - 4, y1 - y0 - 4, face, 6)
    if not k:
        return 0, 0
    m = pt.trim(pt.render(text, k, face))
    x = x0 + (x1 - x0 - len(m[0])) // 2
    y = y0 + (y1 - y0 - len(m)) // 2
    for yy in range(y0 + 2, y1 - 2, max(2, k)):
        for xx in range(x0 + 2, x1 - 2, max(2, k)):
            c.px(xx, yy, LAMP_OFF)
    c.mask(m, x, y, LAMP)
    return len(m[0]), k


def _degrees(c, deg, x0, y0, x1, y1):
    """``deg`` degrees Fahrenheit in lamps, set tight as a sign sets it: the
    figures, a ring at their cap line, the F. The pixel faces have no degree
    sign (a ° renders as their "?"), so the ring is drawn: a square of lamps
    a third of the cap. Returns the scale, 0 when it did not set."""
    face = "m5x7"
    for k in range(6, 0, -1):
        fig = pt.trim(pt.render(deg, k, face))
        eff = pt.trim(pt.render("F", k, face))
        ring = max(3, len(fig) // 3)
        gap = max(1, k)
        wide = len(fig[0]) + gap + ring + gap + len(eff[0])
        if wide <= x1 - x0 - 4 and len(fig) <= y1 - y0 - 4:
            break
    else:
        return 0
    for yy in range(y0 + 2, y1 - 2, max(2, k)):
        for xx in range(x0 + 2, x1 - 2, max(2, k)):
            c.px(xx, yy, LAMP_OFF)
    x = x0 + (x1 - x0 - wide) // 2
    y = y0 + (y1 - y0 - len(fig)) // 2
    c.mask(fig, x, y, LAMP)
    rx = x + len(fig[0]) + gap
    th = max(1, k // 2 + 1)
    c.rect(rx, y, rx + ring, y + th, LAMP)
    c.rect(rx, y + ring - th, rx + ring, y + ring, LAMP)
    c.rect(rx, y, rx + th, y + ring, LAMP)
    c.rect(rx + ring - th, y, rx + ring, y + ring, LAMP)
    c.mask(eff, rx + ring + gap, y, LAMP)
    return k


def bank_art(w, h, variant=0):
    """`art`'s three faces for a bank: its name on its colours, the time
    over the temperature in lamps, and MEMBER FDIC. ``said`` names every
    word, ``unset`` any that did not set."""
    from . import teller_line_forms as TF
    said_bank = TF.bank_said(variant)
    field, rule, ink = (tuple(x) for x in said_bank["colours"])
    name = said_bank["text"]
    B = bands(h)
    FW = int(round((w - 2 * FACE_IN) * TEXEL))
    SW = int(round((w * 0.86 - 2 * FACE_IN) * TEXEL))
    BH = int(round((B["brand"][1] - B["brand"][0] - 2 * FACE_IN) * TEXEL))
    PH = int(round((B["price"][1] - B["price"][0] - 2 * FACE_IN) * TEXEL))
    SH = int(round((B["strip"][1] - B["strip"][0] - 2 * FACE_IN) * TEXEL))
    W, H = FW, BH + PH + SH + 10
    c = Canvas(W, H, INK)
    rects, said, unset = {}, [], []
    # the name: the brand cabinet on the bank's field, two lines when it sets bigger so
    c.rect(0, 0, FW, BH, field)
    c.rect(2, 2, FW - 2, 4, rule)
    c.rect(2, BH - 4, FW - 2, BH - 2, rule)
    words = name.split()
    half = max(1, len(words) // 2)
    lines = [name] if len(words) < 2 else [" ".join(words[:half]), " ".join(words[half:])]
    one = _scale(name, FW - 12, BH - 16, HEAD_FACE, 6)
    two = min(_scale(ln, FW - 12, (BH - 16) // 2 - 2, HEAD_FACE, 6) for ln in lines)
    use, k = ([name], one) if one >= two else (lines, two)
    if not k:
        unset.append(name)
    else:
        rows = [pt.trim(pt.render(ln, k, HEAD_FACE)) for ln in use]
        tall = sum(len(m) for m in rows) + 4 * (len(rows) - 1)
        y = (BH - tall) // 2
        for m in rows:
            c.mask(m, (FW - len(m[0])) // 2, y, rule, grow=1)
            c.mask(m, (FW - len(m[0])) // 2, y, ink)
            y += len(m) + 4
    said.append(name)
    rects["brand"] = (0, 0, FW, BH)
    # the lamps: the time over the temperature, a dark row between
    y0 = BH + 2
    c.rect(0, y0, FW, y0 + PH, INK)
    clock, temp = READINGS[variant % len(READINGS)]
    mid = y0 + PH // 2
    tw, tk = _lamps(c, clock, 0, y0, FW, mid - 1, "m5x7")
    deg = str(temp)
    dk = _degrees(c, deg, 0, mid + 1, FW, y0 + PH)
    for text, ok in ((clock, tk), (deg + "F", dk)):
        said.append(text)
        if not ok:
            unset.append(text)
    rects["price"] = (0, y0, FW, y0 + PH)
    # the strip
    y1 = y0 + PH + 2
    c.rect(0, y1, SW, y1 + SH, rule)
    ss = _scale(BANK_STRIP, SW - 8, SH - 4, "m5x7", 3)
    if ss:
        m = pt.trim(pt.render(BANK_STRIP, ss, "m5x7"))
        c.mask(m, (SW - len(m[0])) // 2, y1 + (SH - len(m)) // 2, field)
    else:
        unset.append(BANK_STRIP)
    said.append(BANK_STRIP)
    rects["strip"] = (0, y1, SW, y1 + SH)
    y2 = y1 + SH + 2
    rects["edge"] = (0, y2, 4, y2 + 4)
    c.rect(*rects["edge"], INK)
    digest = zlib.crc32(bytes(c.buf)) & 0xFFFFFFFF
    return {"canvas": c, "size": (W, H), "rects": rects, "said": said, "unset": unset,
            "name": f"pylon_bank_v{variant % 16}_{W}x{H}_{digest:08x}"}
'''
p.write_bytes(t.encode("utf-8"))
print(p, "appended")

edit("zoo_keeper/recipes/price_pylon.py", [
('''    A = PP.art(w, h, variant)''',
 '''    # a bank's time-and-temperature sign (1.138.0): the same frame, its own faces
    form = str((plan.get("params") or {}).get("form") or "auto")
    A = PP.art(w, h, variant, form)'''),
])

g = R / "zoo_keeper/genome/species/price_pylon.json"
raw = g.read_bytes()
crlf = b"\r\n" in raw
d = json.loads(raw)
assert (json.dumps(d, indent=1) + "\n").encode() == raw.replace(b"\r\n", b"\n") or \
       (json.dumps(d, indent=2) + "\n").encode() == raw.replace(b"\r\n", b"\n"), "the genome does not round-trip"
indent = 1 if (json.dumps(d, indent=1) + "\n").encode() == raw.replace(b"\r\n", b"\n") else 2
assert d["params"]["form"] == ["auto"] and d["module_variants"] == 4
d["params"]["form"] = ["auto", "bank"]
d["module_variants"] = 16
d["keywords"] = list(d.get("keywords") or []) + ["time and temperature sign", "bank sign"]
out = (json.dumps(d, indent=indent) + "\n").replace("\n", "\r\n" if crlf else "\n")
g.write_bytes(out.encode("utf-8"))
print(g, "edited")
