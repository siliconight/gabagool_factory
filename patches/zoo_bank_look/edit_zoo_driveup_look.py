"""Zoo 1.139.0, part two: the drive-up as the research drew it. Run in a Zoo clone's root, after
edit_zoo_bank_materials.py.

- The canopy's tube run ENCLOSED, a boxed chase under the deck: the remote-banking patents run the horizontal tube in
  an enclosure below the canopy (US 4,455,112), where 1.138.0 drew a bare pipe.
- DRIVE-UP lettered on the canopy's two ends, the faces a driver meets coming up the lane, on boards in the bank's
  colours (the teller line's nameboard painter).
- The station a VISUAL customer terminal: a teller's screen beside the grille (US 4,462,721, "visual customer
  terminal"), the cabinet taller to hold it.

Every anchor is asserted to occur exactly once; nothing is written on a miss.
"""
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


edit("zoo_keeper/recipes/drive_up_canopy.py", [
('''TUBE_R = 0.065
TUBE_DROP = 0.18         # the run's centre under the soffit''',
 '''TUBE_R = 0.065
TUBE_DROP = 0.18         # the run's centre under the soffit
#: THE CHASE (1.139.0): the run enclosed in a boxed housing, its section square about the run's centre -- the
#: remote-banking patents' "enclosed horizontal pneumatic tube portions ... below a canopy" (US 4,455,112), where
#: 1.138.0 drew a bare pipe. The station's tube rises 6 cm into it.
CHASE = 0.24
#: THE ENDS' BOARDS (1.139.0): DRIVE-UP on the two faces a driver meets coming up the lane, in the bank's colours.
#: The deck steps in by the board's thickness at each end and the board fills the step, so the envelope is the deck's
#: (the teller line's nameboard, 1.137.0). The words set on the nameboard painter at 0.17 m and up.
BOARD_T = 0.02
BOARD_INSET = 0.04
BOARD_TEXT = "DRIVE-UP"'''),
('''    # the deck: the fascia's colour all round, the module's width and depth; its -X face meets the building's wall
    bm = geometry.new_bm()
    box(bm, (-w / 2.0, -d / 2.0, soffit), (w / 2.0, d / 2.0, top))
    finish(bm, "DriveUpCanopy_Deck", fascia_rgb(variant))''',
 '''    # the deck: the fascia's colour all round, the module's width; its -X face meets the building's wall, and it
    # stands in by the boards' thickness at each end, where they fill the step
    bm = geometry.new_bm()
    box(bm, (-w / 2.0, -d / 2.0 + BOARD_T, soffit), (w / 2.0, d / 2.0 - BOARD_T, top))
    finish(bm, "DriveUpCanopy_Deck", fascia_rgb(variant))'''),
('''    # the tube's run under the soffit, from the island line to the wall
    bm = geometry.new_bm()
    rz = floor + run_z(h)
    geometry.add_cylinder(bm, ((cx - w / 2.0) / 2.0, 0.0, rz), TUBE_R, cx + w / 2.0, segments=SEG, axis="X")
    finish(bm, "DriveUpCanopy_Tube", TUBE_RGB)''',
 '''    # the tube's run under the soffit, from the island line to the wall, in its chase; the chase's top is buried in the
    # soffit, its island end runs past the column line by half its section
    bm = geometry.new_bm()
    rz = floor + run_z(h)
    box(bm, (-w / 2.0, -CHASE / 2.0, rz - CHASE / 2.0), (cx + CHASE / 2.0, CHASE / 2.0, soffit - SOFFIT_T + BURY))
    finish(bm, "DriveUpCanopy_Chase", TUBE_RGB)'''),
('''    body = materials.make_material(f"M_DriveUpCanopy_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, body)''',
 '''    body = materials.make_material(f"M_DriveUpCanopy_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, body)
    # the ends' boards: an art front and four edges a board, no back (it would lie in the deck's stepped face)
    from ..core import prims as P
    from ._card_atlas import build_art
    said = TF.bank_said(variant)
    quad_uv = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))]
    bx0, bx1 = -w / 2.0 + BOARD_INSET, w / 2.0 - BOARD_INSET
    bz0, bz1 = soffit + BOARD_INSET / 2.0, top - BOARD_INSET / 2.0
    prims = []
    for sgn in (-1.0, 1.0):
        yf = sgn * d / 2.0                  # the board's front
        yb = sgn * (d / 2.0 - BOARD_T)      # the deck's stepped face
        tag = "S" if sgn < 0 else "N"
        # the front, wound to face out (-Y at the -Y end, +Y at the +Y end), read left to right from outside
        xa, xb = (bx0, bx1) if sgn < 0 else (bx1, bx0)
        art = P.mesh(f"DriveUpCanopy_Board{tag}", "art", [(xa, yf, bz0), (xb, yf, bz0), (xb, yf, bz1), (xa, yf, bz1)],
                     [(0, 1, 2, 3)])
        art["tile"] = "board"
        art["uvs"] = list(quad_uv)
        rim = P.box(f"DriveUpCanopy_BoardRim{tag}", "art", (bx0, min(yf, yb), bz0), (bx1, max(yf, yb), bz1))
        rim["faces"] = [f for k, f in enumerate(rim["faces"]) if k in (0, 1, 3, 5)]
        rim["tile"] = "edge"
        rim["uvs"] = list(quad_uv) * len(rim["faces"])
        prims += [art, rim]
    tiles = {"board": {"kind": "teller_board", "w_m": bx1 - bx0, "h_m": bz1 - bz0, "text": BOARD_TEXT,
                       "colours": said["colours"], "voice": "shop", "numbers": []},
             "edge": {"kind": "storefront_sign", "w_m": 0.1, "h_m": 0.1, "edge": True, "text": "",
                      "colours": said["colours"]}}
    got, _atlas = build_art(prims, collection, dict(plan, _tiles=tiles), streams, "DriveUpCanopy_Board", smooth=True)
    objs += got'''),
])

edit("zoo_keeper/recipes/drive_up_tube.py", [
('''CAB_TOP = 1.55           # the cabinet's top over the ground: a sedan's roof''',
 '''CAB_TOP = 1.80           # the cabinet's top over the ground: room over the receptacle for the teller's screen (1.139.0)'''),
('''GRILLE = (0.18, 0.12)
GRILLE_Z = 1.42''',
 '''GRILLE = (0.12, 0.14)
GRILLE_Z = 1.55
#: THE TELLER'S SCREEN (1.139.0): a visual customer terminal (US 4,462,721) -- the teller's face on a small screen
#: over the receptacle, at a seated driver's eye, the grille and the call button beside it
SCREEN = (0.24, 0.19)
SCREEN_RGB = (0.05, 0.08, 0.10)'''),
('''    # the speaker grille and the call button on the face above it, standing a few mm proud
    gw, gh = GRILLE
    gz = floor + GRILLE_Z
    # buried twice as deep as the hood: at one depth the census read their backs on one plane inside the cabinet
    box("DriveUp_Grille", (-gw / 2.0, cy0 - 0.006, gz - gh / 2.0), (gw / 2.0, cy0 + 2.0 * BURY, gz + gh / 2.0),
        GRILLE_RGB)
    bx = gw / 2.0 + 0.06''',
 '''    # the teller's screen, the speaker grille beside it and the call button beyond, a few mm proud; each buried to
    # its own depth, so no two backs share a plane inside the cabinet
    gw, gh = GRILLE
    gz = floor + GRILLE_Z
    sw, sh = SCREEN
    sx0 = -cw / 2.0 + 0.05
    box("DriveUp_Screen", (sx0, cy0 - 0.008, gz - sh / 2.0), (sx0 + sw, cy0 + 3.0 * BURY, gz + sh / 2.0), SCREEN_RGB)
    gx0 = sx0 + sw + 0.04
    # the grille buried twice as deep as the hood: at one depth the census read their backs on one plane
    box("DriveUp_Grille", (gx0, cy0 - 0.006, gz - gh / 2.0), (gx0 + gw, cy0 + 2.0 * BURY, gz + gh / 2.0),
        GRILLE_RGB)
    bx = gx0 + gw + 0.05'''),
])
