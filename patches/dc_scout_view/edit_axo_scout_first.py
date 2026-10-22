"""Prototype edit: axonometric.render_axonometric(..., scout=True) -- the scout view (roadmap 296, the walker's
"simple and not noisy ... carry all of the signals needed"). Anchored; refuses on a miss. Usage: scout_edit.py <repo>"""
import pathlib
import sys

p = pathlib.Path(sys.argv[1]) / "axonometric.py"
b = p.read_bytes()
crlf = b"\r\n" in b
t = b.decode("utf-8").replace("\r\n", "\n")

EDITS = [
    # the module's docstring: what the scout view is
    ("""Deterministic SVG strings: no Pillow, no Blender, no generative model.
""",
     """THE SCOUT VIEW (0.258.0, the factory's roadmap 296). The walker, of this drawing on two busy buildings: "we need
to find a way to be simple and not noisy visually", and what a player should see is "simpler but carry all of the
signals needed". `scout=True` draws the same storeys, cut and offset the same way, with only what a body finds its
way by: walls, doors and windows, stairs as their treads, ladders, and the holes in a floor. Furniture, room names
and role tints, markers, and the dashed lines that join the storeys are left out -- a flight's treads already rise
to the hole they reach, and a ladder keeps its one solid line.

Deterministic SVG strings: no Pillow, no Blender, no generative model.
"""),
    ("""          (FP.LADDER_COLOR, "ladder"), (FP.VOID_COLOR, "open to below"), ("#c3ccd6", "furniture"))
""",
     """          (FP.LADDER_COLOR, "ladder"), (FP.VOID_COLOR, "open to below"), ("#c3ccd6", "furniture"))
#: The scout view's legend: what it draws, and nothing it leaves out.
SCOUT_LEGEND = tuple(e for e in LEGEND if e[1] != "furniture")
"""),
    ("""def render_axonometric(spec, azimuth=AZIMUTH_DEG, elevation=ELEVATION_DEG, cut=PLAN_CUT_M, gap=None):
    \"\"\"One SVG string: every storey of ``spec``, exploded, cut and seen from the south-west.\"\"\"
""",
     """def render_axonometric(spec, azimuth=AZIMUTH_DEG, elevation=ELEVATION_DEG, cut=PLAN_CUT_M, gap=None, scout=False):
    \"\"\"One SVG string: every storey of ``spec``, exploded, cut and seen from the south-west. ``scout``: only what a
    body finds its way by (the module's docstring).\"\"\"
"""),
    ("""    for m in getattr(spec, "markers", []) or []:
        s = FP._marker_story(spec, m)
        if s in drawn:
            pts.append((getattr(m, "x", 0.0), getattr(m, "y", 0.0), drawn[s]))
""",
     """    for m in ([] if scout else getattr(spec, "markers", []) or []):
        s = FP._marker_story(spec, m)
        if s in drawn:
            pts.append((getattr(m, "x", 0.0), getattr(m, "y", 0.0), drawn[s]))
"""),
    ("""    title = "%s — exploded axonometric" % spec.name
    lines = ("each storey drawn %.1f m higher than the one below over its %.1f m floor to floor; the elevations are "
             "not moved" % (g, sh),
             "walls cut at %.1f m · seen from the south-west · deterministic render, no generative model" % cut)
""",
     """    title = "%s — %s" % (spec.name, "scout view" if scout else "exploded axonometric")
    lines = ("each storey drawn %.1f m higher than the one below over its %.1f m floor to floor; the elevations are "
             "not moved" % (g, sh),
             "walls cut at %.1f m · seen from the south-west · deterministic render, no generative model" % cut)
    if scout:
        lines = ("storeys lifted apart · walls cut at %.1f m · seen from the south-west" % cut,)
    legend = SCOUT_LEGEND if scout else LEGEND
"""),
    ("""            PADDING + sum(12 + len(t) * 6.0 + 14 for _c, t in LEGEND) - 14 + PADDING)
""",
     """            PADDING + sum(12 + len(t) * 6.0 + 14 for _c, t in legend) - 14 + PADDING)
"""),
    ("""           'font-family="Inter,Segoe UI,sans-serif" data-view="exploded-axonometric" data-azimuth="%g" '
           'data-elevation-angle="%.3f" data-cut="%g" data-gap="%.3f">' % (W, H, W, H, azimuth, elevation, cut, g),
""",
     """           'font-family="Inter,Segoe UI,sans-serif" data-view="%s" data-azimuth="%g" '
           'data-elevation-angle="%.3f" data-cut="%g" data-gap="%.3f">'
           % (W, H, W, H, "scout" if scout else "exploded-axonometric", azimuth, elevation, cut, g),
"""),
    ("""        for r in getattr(spec, "rooms", []) or []:
            if r.story != s:
                continue
""",
     """        for r in ([] if scout else getattr(spec, "rooms", []) or []):
            if r.story != s:
                continue
"""),
    ("""            grp.append(cv.poly(_rect_pts(r, z), "none", stroke=color, width=1.0,
                               extra=' stroke-dasharray="3 2" data-void="%s"' % FP._esc(kind)))
        # stairs and ladders, outlined on every storey they serve
        for i, st in enumerate(getattr(spec, "stairs", []) or []):
""",
     """            grp.append(cv.poly(_rect_pts(r, z), "none", stroke=color, width=1.0,
                               extra='%s data-void="%s"' % ("" if scout else ' stroke-dasharray="3 2"',
                                                             FP._esc(kind))))
        # stairs and ladders, outlined on every storey they serve
        for i, st in enumerate([] if scout else getattr(spec, "stairs", []) or []):
"""),
    ("""        for v in getattr(spec, "volumes", []) or []:
            if not getattr(v, "visual", True):
""",
     """        for v in ([] if scout else getattr(spec, "volumes", []) or []):
            if not getattr(v, "visual", True):
"""),
    ("""        for m in getattr(spec, "markers", []) or []:
            if FP._marker_story(spec, m) != s:
                continue
            color, glyph""",
     """        for m in ([] if scout else getattr(spec, "markers", []) or []):
            if FP._marker_story(spec, m) != s:
                continue
            color, glyph"""),
    ("""    for i, st in enumerate(getattr(spec, "stairs", []) or []):
        served = [s for s in _sw.floors_served(spec, st) if s in drawn]
""",
     """    for i, st in enumerate([] if scout else getattr(spec, "stairs", []) or []):
        served = [s for s in _sw.floors_served(spec, st) if s in drawn]
"""),
    ("""    for s, rects in sorted(holes.items()):
        if s not in drawn or (s - 1) not in drawn:
            continue
""",
     """    for s, rects in sorted(holes.items()):
        if scout or s not in drawn or (s - 1) not in drawn:
            continue
"""),
    ("""    for y, line in zip((38, 50), lines):""", """    for y, line in zip((38, 50), lines):"""),
    ("""    for color, txt in LEGEND:
        leg.append(""", """    for color, txt in legend:
        leg.append("""),
]
for o, n in EDITS:
    assert t.count(o) == 1, o[:70]
    t = t.replace(o, n)
p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
print("edited", p, "crlf" if crlf else "lf")
