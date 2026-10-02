"""Zoo 1.45.0: screens that run -- shutters over the ATM's and the video poker's CRTs.

The walker, 2026-10-02, after walking cold run 9131: "there is a relatively
frozen/static feeling, where the lights in the atm, gambling machine, and
cash register are just fixed with nothing dynamic/alive about them", and of
four steps toward levels that feel alive, the first: "screens that run".

A SHUTTER is a black quad standing 3 mm proud of a lit screen, over ONE PART
of its picture, with a schedule: the fraction of a period in which it is
OPEN. Closed, it hides that part; open, it is not there. Everything a screen
does is already painted on it, and the shutters decide when each part shows:

  * the video poker DEALS: five shutters, one a card, opening one after
    another, holding the hand, and closing together for the next deal;
  * the ATM alternates its greeting and INSERT CARD.

WHAT ZOO SHIPS, and what it does not. The quads, in one more object a
machine (`<Name>_Shutter`), on one material named `M_Shutter_Screen`,
exported FULLY TRANSPARENT -- so a consumer that knows nothing about
shutters draws the screen exactly as it was. The schedule rides in the
quad's two UV sets: UV is (open from, open to), UV2 is (period in seconds,
phase in seconds). The clock is the consumer's: Level Factory's import
(0.127.0) swaps the material for a shader that reads them.

WHAT IT COSTS: one more draw a machine, transparent, over a few thousand
pixels. No script, no light, no texture.

    python patch_zoo_shutters.py            # the repo
    ZOO_ROOT=<copy> python patch_zoo_shutters.py   # a scratch copy

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import json
import os
import pathlib

ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or pathlib.Path(__file__).resolve().parents[1] / "zoo")


def _edit(rel, pairs):
    p = ZOO / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.replace(b"\r\n", b"\n").decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    b = s.encode("utf-8")
    p.write_bytes(b.replace(b"\n", b"\r\n") if crlf else b)
    print("patched", rel)


SHUTTERS = '''"""Shutters: the parts of a lit screen that come and go (1.45.0).

The walker, 2026-10-02: the lit screens are "just fixed with nothing
dynamic/alive about them". A screen's picture is one painted image and stays
one; a SHUTTER is a black quad a hair proud of it, over one part of the
picture, that is OPEN for a stated fraction of a stated period. Closed, the
part is hidden; open, the shutter is not drawn. A dealt card, a line that
flashes, a cursor: each is a part of the picture and a shutter over it.

Pure Python. A planner calls `over` and puts the prim in its list with the
rest; `recipes/_card_atlas.build_shutters` builds every prim carrying a
``shutter`` into one object.

THE CONTRACT WITH WHOEVER DRAWS IT (Level Factory's import, 0.127.0):

  * the material's name BEGINS `MATERIAL` and it is exported fully
    transparent, so a consumer that does nothing shows the screen as painted;
    its BASE COLOUR is the colour a closed shutter is -- the screen's own
    background, so a hidden card is empty screen and not a black hole (the
    first frames: black blocks on the poker's blue tube);
  * UV  = (open_from, open_to), fractions of the period, 0 <= from < to <= 1;
  * UV2 = (period_s, phase_s);
  * the shutter is OPEN while ``fract((t + phase_s) / period_s)`` is in
    ``[open_from, open_to)``, and the closed colour otherwise.

KNOWN: the closed colour is drawn unlit, so on a machine with its power cut
a closed shutter is still its dark background colour where the dead screen
round it is the room's light on its picture. Both are dark; they are not the
same dark.
"""
from __future__ import annotations

from . import prims as P

MATERIAL = "M_Shutter_Screen"
MAT = "shutter"


def material_name(rgb):
    """The shutter material for a screen whose background is ``rgb`` (0-255):
    `MATERIAL` and the colour, so two machines built in one session do not
    share one material and one colour."""
    return "%s_%02x%02x%02x" % ((MATERIAL,) + tuple(int(c) for c in rgb))
#: Proud of the screen: past `prims.coincident_pairs`' 2 mm, so the two are
#: not one plane, and little enough to stay inside the screen's recess.
PROUD = 0.003


def over(part, screen, rect, schedule):
    """A shutter over part of a screen.

    ``screen`` is the screen quad's corners -- bottom-left, bottom-right,
    top-right, top-left as the viewer sees it. ``rect`` is ``(u0, v0, u1,
    v1)``, fractions of the screen, v UP. ``schedule`` is ``(open_from,
    open_to, period_s, phase_s)``."""
    u0, v0, u1, v1 = rect
    a, b, period, phase = schedule
    if not (0.0 <= u0 < u1 <= 1.0 and 0.0 <= v0 < v1 <= 1.0):
        raise ValueError(f"shutter {part}: rect {rect!r} is not inside its screen")
    if not (0.0 <= a < b <= 1.0 and period > 0.0):
        raise ValueError(f"shutter {part}: schedule {schedule!r}")
    bl, br, _tr, tl = screen
    ex = [br[k] - bl[k] for k in range(3)]
    ey = [tl[k] - bl[k] for k in range(3)]
    n = (ex[1] * ey[2] - ex[2] * ey[1], ex[2] * ey[0] - ex[0] * ey[2], ex[0] * ey[1] - ex[1] * ey[0])
    size = sum(c * c for c in n) ** 0.5
    n = [c / size * PROUD for c in n]

    def at(u, v):
        return tuple(bl[k] + ex[k] * u + ey[k] * v + n[k] for k in range(3))
    p = P.mesh(part, MAT, [at(u0, v0), at(u1, v0), at(u1, v1), at(u0, v1)], [(0, 1, 2, 3)])
    p["shutter"] = (float(a), float(b), float(period), float(phase))
    return p


def is_open(schedule, t):
    """Is a shutter with ``schedule`` open at time ``t`` seconds?"""
    a, b, period, phase = schedule
    f = ((t + phase) / period) % 1.0
    return a <= f < b
'''

MATERIALS = [
    ('''def make_painted_material(name, image, roughness, tile=False):''', '''def make_shutter_material(name, rgb=(0, 0, 0)):
    """A shutter's material (1.45.0, `core/shutters.py`): black and FULLY
    TRANSPARENT. What draws a shutter is the consumer's shader, found by
    this name; a consumer without one draws nothing here, which is the
    screen as painted. (Alpha 0 on a blended material leaves the glTF
    exporter as alphaMode MASK: under the cutoff, so still nothing drawn.)"""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    # the closed colour, sRGB 0-255 to the linear the socket and glTF hold
    lin = [((c / 255.0) / 12.92 if c / 255.0 <= 0.04045 else ((c / 255.0 + 0.055) / 1.055) ** 2.4)
           for c in rgb]
    bsdf.inputs["Base Color"].default_value = (lin[0], lin[1], lin[2], 1.0)
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Alpha"].default_value = 0.0
    for _attr, _val in (("blend_method", "BLEND"),
                        ("surface_render_method", "BLENDED")):
        try:
            setattr(mat, _attr, _val)
        except Exception:
            pass
    return mat


def make_painted_material(name, image, roughness, tile=False):'''),
]

ATLAS = [
    ('''def build_art(prims, collection, plan, streams, name, roughness=None, lit=None):''',
     '''def build_shutters(prims, collection, streams, name, rgb=(0, 0, 0)):
    """Every prim carrying a ``shutter`` (`core/shutters.py`, 1.45.0) built
    into ONE object, ``<name>_Shutter``, on the shutter material. The
    schedule goes into two UV sets as glTF will read them: Blender's v is
    glTF's 1 - v, so each second component is written flipped and arrives
    as it was meant -- UV (open from, open to), UV2 (period, phase).
    ``rgb`` is the screen's background, the colour a closed shutter is."""
    from ..core import shutters as SH
    quads = [p for p in prims if p.get("shutter")]
    if not quads:
        return []
    bm = geometry.new_bm()
    uv = bm.loops.layers.uv.new("UVMap")
    uv2 = bm.loops.layers.uv.new("Schedule")
    for q in quads:
        a, b, period, phase = q["shutter"]
        vs = [bm.verts.new(v) for v in q["verts"]]
        for face in q["faces"]:
            f = bm.faces.new([vs[i] for i in face])
            for loop in f.loops:
                loop[uv].uv = (a, 1.0 - b)
                loop[uv2].uv = (period, 1.0 - phase)
    bm.normal_update()
    # every Zoo mesh carries `Wear` (the build's own check warns without it);
    # a shutter does not grime, so it is white
    geometry.wear_colors(bm, streams.stream("shutters"), 0.0)
    obj = geometry.bm_to_object(bm, f"{name}_Shutter", collection, finish=False)
    obj.data.materials.append(materials.make_shutter_material(SH.material_name(rgb), rgb))
    return [obj]


def build_art(prims, collection, plan, streams, name, roughness=None, lit=None):'''),
]

POKER = [
    ('''from . import prims as P
''', '''from . import prims as P
from . import shutters as SH
'''),
    ('''SCREEN_INSET = 0.015
TEXEL = 256
''', '''SCREEN_INSET = 0.015
TEXEL = 256
#: THE DEAL (1.45.0). The screen's five cards come up one after another,
#: the hand holds, and all five go for the next deal: a shutter a card,
#: open from `DEAL_FIRST + i * DEAL_STEP` to `DEAL_HOLD` of a period.
DEAL_PERIOD_S = 8.0
DEAL_FIRST = 0.08
DEAL_STEP = 0.05
DEAL_HOLD = 0.92
#: A closed shutter's colour: the tube's blue, between its two scanline rows.
SHUTTER_RGB = (7, 17, 80)
'''),
    ('''    prims += _box("VP_Marquee", "paint", "trim", (x0, yh, zh), (x1, y1, h), skip=("front", "bottom"))''',
     '''    # THE DEAL: a shutter over each card on the screen, a pixel wider all
    # round than the card it hides
    screen = [(sx0, yi, sz0), (sx1, yi, sz0), (sx1, yi, sz1), (sx0, yi, sz1)]
    wpx, hpx = _px(sw), _px(sh)
    for i, (bx0, by0, bx1, by1) in enumerate(card_boxes(wpx, hpx)):
        rect = (max(0.0, (bx0 - 1) / wpx), max(0.0, 1.0 - (by1 + 1) / hpx),
                min(1.0, (bx1 + 1) / wpx), min(1.0, 1.0 - (by0 - 1) / hpx))
        prims.append(SH.over("VP_ScreenShutter", screen, rect,
                             (DEAL_FIRST + i * DEAL_STEP, DEAL_HOLD, DEAL_PERIOD_S, 0.0)))
    prims += _box("VP_Marquee", "paint", "trim", (x0, yh, zh), (x1, y1, h), skip=("front", "bottom"))'''),
    ('''            "facts": {"brand": brand, "variant": v, "tris": P.tri_count(prims), "materials": 2}}''',
     '''            "facts": {"brand": brand, "variant": v, "tris": P.tri_count(prims), "materials": 3}}'''),
    ('''SUIT_RGB = {"S": (20, 20, 24), "C": (20, 20, 24), "H": (200, 20, 30), "D": (200, 20, 30)}
''', '''SUIT_RGB = {"S": (20, 20, 24), "C": (20, 20, 24), "H": (200, 20, 30), "D": (200, 20, 30)}


def card_boxes(w, h):
    """The five cards' pixel boxes on a ``w`` x ``h`` screen, row 0 at the
    top: ONE derivation for the painter and for the shutters that hide them
    (1.45.0), so a shutter cannot drift off its card."""
    n = 5
    gap = max(2, w // 60)
    cw = (w - 8 - gap * (n - 1)) // n
    cy0, cy1 = int(h * 0.26), int(h * 0.74)
    return [(4 + i * (cw + gap), cy0, 4 + i * (cw + gap) + cw, cy1) for i in range(n)]
'''),
    ('''        n = 5
        gap = max(2, w // 60)
        cw = (w - 8 - gap * (n - 1)) // n
        cy0, cy1 = int(h * 0.26), int(h * 0.74)
        for i, (rank, suit) in enumerate(HANDS[v]):
            x = 4 + i * (cw + gap)
            c.rect(x, cy0, x + cw, cy1, (248, 248, 240))''',
     '''        for (x, cy0, x1, cy1), (rank, suit) in zip(card_boxes(w, h), HANDS[v]):
            cw = x1 - x
            c.rect(x, cy0, x + cw, cy1, (248, 248, 240))'''),
]

ATM = [
    ('''from . import prims as P
from .vending_forms import Canvas
''', '''from . import prims as P
from . import shutters as SH
from .vending_forms import Canvas
'''),
    ('''SCREEN_INSET = 0.012
TEXEL = 256
''', '''SCREEN_INSET = 0.012
TEXEL = 256
#: THE SCREEN CYCLES (1.45.0): its greeting and INSERT CARD take turns, half
#: of this period each.
CYCLE_PERIOD_S = 3.0
#: A closed shutter's colour: the tube's dark green, between its scanline rows.
SHUTTER_RGB = (4, 14, 6)
'''),
    ('''    if sign:
        # the topper: the head's footprint, its front lit, its other sides body''',
     '''    # THE CYCLE: the greeting and the line under it take turns. A tube too
    # small for two lines shows its one line and has no shutter.
    wpx, hpx = _px(sw), _px(sh)
    lines, band = crt_bands(hpx, greet)
    if len(lines) >= 2:
        screen = [(sx0, yi, sz0), (sx1, yi, sz0), (sx1, yi, sz1), (sx0, yi, sz1)]
        for i, (a, b) in enumerate(((0.0, 0.5), (0.5, 1.0))):
            top, foot = 4 + i * band - 1, 4 + (i + 1) * band - 1
            rect = (2.0 / wpx, max(0.0, 1.0 - foot / float(hpx)),
                    1.0 - 2.0 / wpx, min(1.0, 1.0 - top / float(hpx)))
            prims.append(SH.over("ATM_ScreenShutter", screen, rect, (a, b, CYCLE_PERIOD_S, 0.0)))
    if sign:
        # the topper: the head's footprint, its front lit, its other sides body'''),
    ('''def _px(m):
    return max(4, int(round(m * TEXEL)))


def paint(spec):''', '''def _px(m):
    return max(4, int(round(m * TEXEL)))


def crt_bands(h, greet):
    """``(lines, band)`` for a tube ``h`` px tall: as many lines as it holds
    at 9 px a line, the greeting first, and each line's band height. ONE
    derivation for the painter and for the shutters (1.45.0)."""
    lines = ((greet,) + SCREEN_LINES)[:max(1, (h - 8) // 9)]
    return lines, (h - 8) // len(lines)


def paint(spec):'''),
    ('''        lines = ((spec["greet"],) + SCREEN_LINES)[:max(1, (h - 8) // 9)]
        band = (h - 8) // len(lines)
''', '''        lines, band = crt_bands(h, spec["greet"])
'''),
]

R_ATM = [
    ('''    from ._card_atlas import build_art
    objs = []''', '''    from ._card_atlas import build_art, build_shutters
    objs = []'''),
    ('''    f = got["facts"]
    print(f"[atm] {w:.2f} x {d:.2f} x {h:.2f} network={f['network']} sign={f['sign']} "
          f"{f['tris']} tris, 2 materials")''', '''    # the screen's shutters (1.45.0): one more object, drawn by the consumer
    objs += build_shutters(got["prims"], collection, streams, "ATM", AF.SHUTTER_RGB)
    f = got["facts"]
    print(f"[atm] {w:.2f} x {d:.2f} x {h:.2f} network={f['network']} sign={f['sign']} "
          f"{f['tris']} tris, 3 materials")'''),
]

R_POKER = [
    ('''    from ._card_atlas import build_art
    objs = []''', '''    from ._card_atlas import build_art, build_shutters
    objs = []'''),
    ('''    f = got["facts"]
    print(f"[video_poker] {w:.2f} x {d:.2f} x {h:.2f} brand={f['brand']} {f['tris']} tris, 2 materials")''',
     '''    # the deal's shutters (1.45.0): one more object, drawn by the consumer
    objs += build_shutters(got["prims"], collection, streams, "VideoPoker", VF.SHUTTER_RGB)
    f = got["facts"]
    print(f"[video_poker] {w:.2f} x {d:.2f} x {h:.2f} brand={f['brand']} {f['tris']} tris, 3 materials")'''),
]

T_POKER = [
    ('''    assert g["parts"] == ["VideoPoker_Art", "VideoPokerGlow_Art"] and g["module_variants"] == 4''',
     '''    assert g["parts"] == ["VideoPoker_Art", "VideoPokerGlow_Art", "VideoPoker_Shutter"]
    assert g["module_variants"] == 4'''),
    ('''    g = F.plan(0.65, 0.65, 1.75, 1)
    assert {p["mat"] for p in g["prims"]} == {"paint", "glow"}''',
     '''    g = F.plan(0.65, 0.65, 1.75, 1)
    # 1.45.0: and the deal's shutters, which are neither atlas
    assert {p["mat"] for p in g["prims"]} == {"paint", "glow", "shutter"}'''),
    ('''    assert len(objs) == 2
''', '''    assert len(objs) == 3                # 1.45.0: paint, glow, and the screen's shutters
    assert sum(o.name.endswith("_Shutter") for o in objs) == 1
'''),
    ('''    assert len(mats) == 2
''', '''    assert len(mats) == 3
    shut = [m for m in mats if m["name"].startswith("M_Shutter_Screen")]
    # alpha 0 leaves Blender's exporter as MASK (measured: BLEND was asked
    # for), which is what is wanted anyway -- under the cutoff, nothing drawn
    assert len(shut) == 1 and shut[0].get("alphaMode") == "MASK"
    assert shut[0]["pbrMetallicRoughness"]["baseColorFactor"][3] == 0.0
'''),
]

T_ATM = [
    ('''    assert g["parts"] == ["ATM_Art", "ATMGlow_Art"] and g["module_variants"] == 4''',
     '''    assert g["parts"] == ["ATM_Art", "ATMGlow_Art", "ATM_Shutter"] and g["module_variants"] == 4'''),
    ('''    g = A.plan(0.6, 0.55, 1.45, 1)
    assert {p["mat"] for p in g["prims"]} == {"paint", "glow"}''',
     '''    g = A.plan(0.6, 0.55, 1.45, 1)
    # 1.45.0: and the screen's shutters, which are neither atlas
    assert {p["mat"] for p in g["prims"]} == {"paint", "glow", "shutter"}'''),
    ('''    assert len(objs) == 2
''', '''    assert len(objs) == 3                # 1.45.0: paint, glow, and the screen's shutters
    assert sum(o.name.endswith("_Shutter") for o in objs) == 1
'''),
    ('''    assert len(mats) == 2
''', '''    assert len(mats) == 3
    shut = [m for m in mats if m["name"].startswith("M_Shutter_Screen")]
    # alpha 0 leaves Blender's exporter as MASK (measured: BLEND was asked
    # for), which is what is wanted anyway -- under the cutoff, nothing drawn
    assert len(shut) == 1 and shut[0].get("alphaMode") == "MASK"
    assert shut[0]["pbrMetallicRoughness"]["baseColorFactor"][3] == 0.0
'''),
]

TEST = '''"""Screens that run (1.45.0): shutters over the ATM's and the video poker's CRTs.

The walker, 2026-10-02: the lit screens are "just fixed with nothing
dynamic/alive about them". Held: a shutter stands proud of its screen, inside
it, facing the viewer; its schedule is a real one; the poker's five are over
its five cards and DEAL -- one after another, a held hand, then none; the
ATM's two are over its first two lines and take turns, never both, never
neither; a tube too small for two lines has none; and a built machine
carries the schedule in the two UV sets a consumer reads.
"""
from __future__ import annotations

import json
import os
import struct

import pytest

from zoo_keeper.core import atm_forms as A
from zoo_keeper.core import kit
from zoo_keeper.core import prims as P
from zoo_keeper.core import shutters as SH
from zoo_keeper.core import video_poker_forms as F


def _normal(p):
    a, b, c = (p["verts"][i] for i in p["faces"][0][:3])
    u = [b[k] - a[k] for k in range(3)]
    v = [c[k] - a[k] for k in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    size = sum(x * x for x in n) ** 0.5
    return tuple(x / size for x in n)


def _screen(prims, part):
    (s,) = [p for p in prims if p["part"] == part]
    return s


def _shutters(prims):
    return [p for p in prims if p.get("shutter")]


@pytest.mark.parametrize("plan,part", [(F.plan(0.65, 0.65, 1.75, 0), "VP_Screen"),
                                       (A.plan(0.6, 0.55, 1.45, 0), "ATM_Screen")])
def test_a_shutter_stands_proud_of_its_screen_inside_it_facing_out(plan, part):
    screen = _screen(plan["prims"], part)
    lo, hi = P.bounds([screen])
    shut = _shutters(plan["prims"])
    assert shut
    for p in shut:
        assert p["mat"] == SH.MAT and "tile" not in p
        assert all(abs(a - b) < 1e-9 for a, b in zip(_normal(p), _normal(screen)))
        slo, shi = P.bounds([p])
        assert abs((lo[1] - slo[1]) - SH.PROUD) < 1e-9 and abs(slo[1] - shi[1]) < 1e-12   # toward -Y
        assert lo[0] - 1e-9 <= slo[0] < shi[0] <= hi[0] + 1e-9
        assert lo[2] - 1e-9 <= slo[2] < shi[2] <= hi[2] + 1e-9
        a, b, period, _phase = p["shutter"]
        assert 0.0 <= a < b <= 1.0 and period > 0.0
    assert P.coincident_pairs(plan["prims"]) == []


def test_the_poker_deals_one_card_after_another_holds_and_clears():
    g = F.plan(0.65, 0.65, 1.75, 2)
    shut = sorted(_shutters(g["prims"]), key=lambda p: min(v[0] for v in p["verts"]))
    assert len(shut) == 5
    # left to right, each opens later than the one before and all close together
    opens = [p["shutter"][0] for p in shut]
    assert opens == sorted(opens) and len(set(opens)) == 5
    assert {p["shutter"][1] for p in shut} == {F.DEAL_HOLD}
    period = F.DEAL_PERIOD_S

    def showing(t):
        return [SH.is_open(p["shutter"], t) for p in shut]
    assert showing(0.0) == [False] * 5                          # a new deal: no cards
    assert showing(period * (F.DEAL_FIRST + 0.5 * F.DEAL_STEP)) == [True] + [False] * 4
    assert showing(period * 0.5) == [True] * 5                  # the hand, held
    assert showing(period * 0.96) == [False] * 5                # cleared
    assert showing(period * 1.5) == [True] * 5                  # and round again
    # each is over its card, a pixel wider all round
    screen = _screen(g["prims"], "VP_Screen")
    lo, hi = P.bounds([screen])
    tile = g["tiles"]["screen"][1]
    wpx, hpx = F._px(tile["w_m"]), F._px(tile["h_m"])
    for p, (bx0, by0, bx1, by1) in zip(shut, F.card_boxes(wpx, hpx)):
        slo, shi = P.bounds([p])
        u0 = (slo[0] - lo[0]) / (hi[0] - lo[0])
        u1 = (shi[0] - lo[0]) / (hi[0] - lo[0])
        v_top = 1.0 - (shi[2] - lo[2]) / (hi[2] - lo[2])
        v_foot = 1.0 - (slo[2] - lo[2]) / (hi[2] - lo[2])
        assert u0 * wpx <= bx0 and bx1 <= u1 * wpx and u1 * wpx - bx1 <= 1.0 + 1e-6
        assert v_top * hpx <= by0 and by1 <= v_foot * hpx


def test_the_atm_takes_turns_between_its_greeting_and_insert_card():
    g = A.plan(0.6, 0.55, 1.45, 1)
    shut = sorted(_shutters(g["prims"]), key=lambda p: -max(v[2] for v in p["verts"]))
    assert len(shut) == 2                                        # top line first
    assert [p["shutter"][:2] for p in shut] == [(0.0, 0.5), (0.5, 1.0)]
    for t in (0.0, 0.7, 1.4, 1.6, 2.9, 3.1, 100.3):
        both = [SH.is_open(p["shutter"], t) for p in shut]
        assert sum(both) == 1, (t, both)                         # never both, never neither
    # the two do not overlap and the first is above the second
    (alo, ahi), (blo, bhi) = P.bounds([shut[0]]), P.bounds([shut[1]])
    assert alo[2] >= bhi[2] - 1e-9


def test_a_tube_too_small_for_two_lines_has_no_shutter():
    seen = set()
    for w, d, h in ((0.5, 0.4, 1.2), (0.6, 0.55, 1.45), (0.75, 0.7, 1.65)):
        g = A.plan(w, d, h, 0)
        tile = g["tiles"]["screen"][1]
        lines, _band = A.crt_bands(A._px(tile["h_m"]), tile["greet"])
        n = len(_shutters(g["prims"]))
        assert n == (2 if len(lines) >= 2 else 0), (w, d, h, len(lines), n)
        seen.add(n)
    assert 2 in seen


def test_a_schedule_outside_its_period_or_its_screen_is_refused():
    screen = [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]
    SH.over("x", screen, (0.1, 0.1, 0.9, 0.9), (0.0, 0.5, 2.0, 0.0))
    for rect, sched in (((0.5, 0.1, 0.4, 0.9), (0.0, 0.5, 2.0, 0.0)),
                        ((0.1, 0.1, 1.2, 0.9), (0.0, 0.5, 2.0, 0.0)),
                        ((0.1, 0.1, 0.9, 0.9), (0.6, 0.5, 2.0, 0.0)),
                        ((0.1, 0.1, 0.9, 0.9), (0.0, 0.5, 0.0, 0.0))):
        with pytest.raises(ValueError):
            SH.over("x", screen, rect, sched)


# --------------------------------------------------------------------------- #
# The built half
# --------------------------------------------------------------------------- #

def _accessor(doc, raw, idx):
    acc = doc["accessors"][idx]
    view = doc["bufferViews"][acc["bufferView"]]
    ln = struct.unpack_from("<I", raw, 12)[0]
    start = 20 + ln + 8 + view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    n = {"VEC2": 2, "VEC3": 3}[acc["type"]]
    stride = view.get("byteStride") or 4 * n
    return [struct.unpack_from("<%df" % n, raw, start + i * stride) for i in range(acc["count"])]


@pytest.mark.parametrize("species,dims", [("video_poker", (0.65, 0.65, 1.75)), ("atm", (0.6, 0.55, 1.45))])
def test_bpy_the_schedule_arrives_in_two_uv_sets(tmp_path, species, dims):
    pytest.importorskip("bpy")
    from zoo_keeper.bpylayer import build
    slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": species,
            "variant": 1, "material": "metal_painted", "fit": {"dims": list(dims), "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "t", "slots": [slot]}, theme="delco_1997", style=1)
    res = build.build_module(plan["modules"][0], str(tmp_path), theme="delco_1997", style=1,
                             options={"save_blend": False})
    assert res["report"]["status"] == "pass", res["report"]["checks"]
    raw = open(os.path.join(str(tmp_path), res["files"]["glb"]), "rb").read()
    ln = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20:20 + ln])
    module = A if species == "atm" else F
    mat = next(i for i, m in enumerate(doc["materials"])
               if m["name"] == SH.material_name(module.SHUTTER_RGB))
    # its base colour is the tube's background (linear), its alpha nothing
    factor = doc["materials"][mat]["pbrMetallicRoughness"]["baseColorFactor"]
    assert factor[3] == 0.0
    srgb = [round(255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055)) for c in factor[:3]]
    assert all(abs(a - b) <= 1 for a, b in zip(srgb, module.SHUTTER_RGB)), (srgb, module.SHUTTER_RGB)
    prims = [p for m in doc["meshes"] for p in m["primitives"] if p.get("material") == mat]
    assert len(prims) == 1
    attrs = prims[0]["attributes"]
    assert "TEXCOORD_0" in attrs and "TEXCOORD_1" in attrs
    uv = set(_accessor(doc, raw, attrs["TEXCOORD_0"]))
    uv2 = set(_accessor(doc, raw, attrs["TEXCOORD_1"]))
    want = {p["shutter"] for p in module.plan(*dims, 1)["prims"] if p.get("shutter")}
    assert {(round(a, 4), round(b, 4)) for a, b in uv} == {(round(a, 4), round(b, 4)) for a, b, _p, _q in want}
    assert {(round(a, 4), round(b, 4)) for a, b in uv2} == {(round(p, 4), round(q, 4)) for _a, _b, p, q in want}
'''


def main():
    core = ZOO / "zoo_keeper" / "core" / "shutters.py"
    assert not core.exists(), "already applied"
    core.write_bytes(SHUTTERS.encode("utf-8"))
    print("wrote core/shutters.py")
    _edit("zoo_keeper/bpylayer/materials.py", MATERIALS)
    _edit("zoo_keeper/recipes/_card_atlas.py", ATLAS)
    _edit("zoo_keeper/core/video_poker_forms.py", POKER)
    _edit("zoo_keeper/core/atm_forms.py", ATM)
    _edit("zoo_keeper/recipes/atm.py", R_ATM)
    _edit("zoo_keeper/recipes/video_poker.py", R_POKER)
    _edit("tests/test_video_poker.py", T_POKER)
    _edit("tests/test_atm.py", T_ATM)
    for species, part in (("atm", "ATM_Shutter"), ("video_poker", "VideoPoker_Shutter")):
        p = ZOO / "zoo_keeper" / "genome" / "species" / f"{species}.json"
        raw = p.read_bytes()
        crlf = b"\r\n" in raw
        g = json.loads(raw.decode("utf-8"))
        assert part not in g["parts"]
        g["parts"].append(part)
        out = (json.dumps(g, indent=2) + "\n").encode("utf-8")
        p.write_bytes(out.replace(b"\n", b"\r\n") if crlf else out)
        print("genome", species, g["parts"])
    (ZOO / "tests" / "test_shutters.py").write_bytes(TEST.encode("utf-8"))
    print("wrote tests/test_shutters.py")


if __name__ == "__main__":
    main()
