"""Edit a Deli Counter clone for 0.285.0: a bank's public room panelled below a chair rail, and its glass front a
storefront -- the walker's bank comps' wood and their tall window to the street, where the frames showed plaster from
floor to ceiling and the front as a wall of dark bars. Run from the clone's root. Asserts every anchor once; refuses on
a miss."""
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


edit("deli_counter.py", [
('''    BANK_INTERIOR = "plaster"

    def _is_bank(self):
''',
'''    BANK_INTERIOR = "plaster"

    #: A BANK'S PUBLIC WALLS ARE PANELLED BELOW A CHAIR RAIL (0.285.0, the
    #: factory's roadmap 321). The walker's bank comps: "dark wood veneer on
    #: the counter fronts and panelling (2, 4, 7), against white or beige
    #: walls" -- 0.282.0 gave a bank the plaster and not the wood, and its
    #: lobby read as one grey wall floor to ceiling (docs/findings/
    #: bank_interior/, frames 09-10). A wall slot is one material a face, so
    #: the panelling is geometry of its own on the room face of each wall and
    #: window slot along a bank's public room (`_dados`): a sheet from the
    #: wall's foot, `BANK_DADO_T` proud -- 1/4 in sheet panelling -- under a
    #: rail `BANK_RAIL_H` high and `BANK_RAIL_T` proud, its top `BANK_DADO_TOP`
    #: over the foot, about 36 in, or a window's sill where that is lower. Both
    #: stay inside `level_design._WALL_PIECE_AIR` (0.01 m), so a chair or an
    #: ATM against the wall still clears them, and both are four or more times
    #: `zfight_gate.TOL` off the face. Each is a `wallEnd` slot, the unit box
    #: Deli Counter scales, in `BANK_DADO`, named under its wall: no module is
    #: added to a kit, and the export's merge (Level Factory 0.223.0) folds the
    #: sheets and rails of a wall side into one mesh with one material. No
    #: collision. A door, a breach, the teller line and glass take none.
    BANK_DADO = "wood_panel"
    BANK_DADO_TOP = 0.9
    BANK_DADO_T = 0.006
    BANK_RAIL_H = 0.05
    BANK_RAIL_T = 0.009
    _DADO_ROLES = ("wall", "window")
    #: what stands on a room's edge, for the thickness its corners are cut to
    _EDGE_ROLES = ("wall", "window", "doorway", "breach", "teller_line", "vault_door",
                   "safe_deposit_boxes")

    def _is_bank(self):
'''),
('''    def _slot_orient(self, wall_name, axis):
''',
'''    def _dados(self):
        """A bank's public rooms' panelling and chair rail (`BANK_DADO`,
        0.285.0): on the room face of every wall and window slot on a public
        room's edge, over the stretch of the slot that edge covers, cut at the
        faces of the walls across the edge's ends. Where two walls meet, the one
        along X owns the corner: the one along Y stops at its rail's face, so
        no two pieces overlap. Returns the number of slots added."""
        if not self._is_bank():
            return 0
        import level_design
        import lights
        import material_kind
        business = level_design.club_building_id(self.s)
        rooms = [r for r in self.gameplay["rooms"] if lights.bank_public(r, business)]
        if not rooms:
            return 0

        def line(s):
            # (the axis it runs along, its centreline, its centre along that
            # axis, its length, its thickness, its translation)
            d = s["fit"]["dims"]
            at = s["transform"]["translation"]
            axis = 0 if s.get("facing") in ("N", "S", "X") else 1
            return axis, float(at[1 - axis]), float(at[axis]), float(d[0]), float(d[1]), at

        edge_slots = [s for s in self.slots if s.get("role") in self._EDGE_ROLES]
        rail = self.BANK_RAIL_T
        n = 0
        for r in rooms:
            x0, y0, x1, y1 = (float(v) for v in r["bounds"])
            story = int(r.get("story", 0) or 0)
            # an edge: (the axis its wall runs along, its line, +1 if the room
            # is on the line's + side)
            edges = {"S": (0, y0, 1), "N": (0, y1, -1), "W": (1, x0, 1), "E": (1, x1, -1)}
            span = {0: (x0, x1), 1: (y0, y1)}
            on = {k: [] for k in edges}
            for s in edge_slots:
                if int(s.get("story", 0) or 0) != story:
                    continue
                axis, c, u, length, thick, _at = line(s)
                for k, (ea, el, _side) in edges.items():
                    lo, hi = span[ea]
                    if (ea == axis and abs(c - el) <= thick / 2.0 + 0.01
                            and min(hi, u + length / 2.0) - max(lo, u - length / 2.0) > 0.05):
                        on[k].append(s)
            half = {k: max([line(s)[4] for s in v] or [0.0]) / 2.0 for k, v in on.items()}
            run = {0: (x0 + half["W"], x1 - half["E"]),
                   1: (y0 + half["S"] + rail, y1 - half["N"] - rail)}
            for k, (ea, _el, side) in edges.items():
                for s in on[k]:
                    if s.get("role") not in self._DADO_ROLES:
                        continue
                    if material_kind.kind_for(s.get("material")) in ("glass", "glass_facade"):
                        continue
                    _axis, c, u, length, thick, at = line(s)
                    lo, hi = run[ea]
                    a, b = max(lo, u - length / 2.0), min(hi, u + length / 2.0)
                    if b - a <= 0.05:
                        continue
                    foot = float(at[2]) - float(s["fit"]["dims"][2]) / 2.0
                    top = self.BANK_DADO_TOP
                    if s.get("role") == "window":
                        sill = ((s["fit"].get("openings") or [{}])[0]).get("sill")
                        top = min(top, float(sill or 0.0))
                    if top <= self.BANK_RAIL_H + 0.05:
                        continue
                    wall = s.get("wall")
                    mid = (a + b) / 2.0
                    for z0, z1, t in ((0.0, top - self.BANK_RAIL_H, self.BANK_DADO_T),
                                      (top - self.BANK_RAIL_H, top, self.BANK_RAIL_T)):
                        face = c + side * (thick / 2.0 + t / 2.0)
                        centre = (mid, face, 0.0) if ea == 0 else (face, mid, 0.0)
                        size = (b - a, t, z1 - z0) if ea == 0 else (t, b - a, z1 - z0)
                        self._seg_box(f"{wall}_seg_dado{n}", f"{wall}_dado{n}_col", centre,
                                      size, ea, 0.0, b - a, foot + (z0 + z1) / 2.0, z1 - z0,
                                      role="wall", collide=False, material=self.BANK_DADO,
                                      size_mod="end")
                        n += 1
        return n

    def _slot_orient(self, wall_name, axis):
'''),
('''        self._rooms()
        self._stair_semantics()
''',
'''        self._rooms()
        # after the rooms: a bank's panelling is laid along its public room's
        # edges (0.285.0)
        self._dados()
        self._stair_semantics()
'''),
('''def storefront_slot(slot, spec_material, builder):
    """Is this slot a storefront's full wall or door? Read against the SPEC's
    material id -- the manifest writes the skin kind, `glass_facade`, which
    every curtain wall shares -- on a building with an interior (a facade
    shell's glass stays opaque; there is nothing behind it), in front of a
    customer room (`SHOPFRONT_ROOMS`, 0.159.0)."""
    return (spec_material in STOREFRONT_MATERIALS
            and slot.get("role") in STOREFRONT_ROLES
            and slot.get("size_mod", "full") == "full"
            and not getattr(builder.s, "facade", False)
            and slot_room(slot, builder) in SHOPFRONT_ROOMS)
''',
'''#: A BANK'S GLASS FRONT IS A STOREFRONT (0.285.0, the factory's roadmap 321).
#: The library's banks name their front `glass`, which Zoo builds as a solid
#: slab in `glass_facade` (its `OPAQUE_FOR`: a wall with a solid collider
#: must not be seen through) -- so the comps' "tall window to the street"
#: stood in every bank as a wall of dark bars inside and a blank one outside
#: (docs/findings/bank_interior/, frames 09, 10 and 13). A shop front is the
#: one glazed wall the walker made see-through (2026-09-28: "make the
#: storefront see-through glass"), and a bank's public room is a customer
#: room by its role, `lights.bank_public`. Not the bank's other rooms: an
#: office behind a glass wall keeps it. The other 49 `glass` walls in the
#: library -- the pharmacies, supermarkets, pawn shops, clinics and offices
#: -- are not touched: the walker's call, asked in the factory's
#: docs/findings/bank_interior/.
BANK_FRONT_MATERIALS = ("glass",)


def bank_front(slot, spec_material, builder):
    """Is this slot a bank's glass wall or door in front of its public room
    (`BANK_FRONT_MATERIALS`, 0.285.0)?"""
    if spec_material not in BANK_FRONT_MATERIALS or not builder._is_bank():
        return False
    room = slot_room(slot, builder)
    return any(r.get("id") == room and r.get("role") == "public_entry"
               for r in builder.gameplay.get("rooms", []))


def storefront_slot(slot, spec_material, builder):
    """Is this slot a storefront's full wall or door? Read against the SPEC's
    material id -- the manifest writes the skin kind, `glass_facade`, which
    every curtain wall shares -- on a building with an interior (a facade
    shell's glass stays opaque; there is nothing behind it), in front of a
    customer room (`SHOPFRONT_ROOMS`, 0.159.0), or a bank's glass front
    (`bank_front`, 0.285.0)."""
    if not (slot.get("role") in STOREFRONT_ROLES
            and slot.get("size_mod", "full") == "full"
            and not getattr(builder.s, "facade", False)):
        return False
    if spec_material in STOREFRONT_MATERIALS:
        return slot_room(slot, builder) in SHOPFRONT_ROOMS
    return bank_front(slot, spec_material, builder)
'''),
('''        role = {"door": "doorway", "garage": "doorway", "window": "window",
                "breach": "breach", "vault": "vault_door",
                "teller": "teller_line", "safe_deposit": "safe_deposit_boxes"}.get(kind, "doorway")
        u, w, hh, sill = h["u"], h["w"], h["h"], h["sill"]
        if axis == 0:
            oc = (center[0] + u, center[1], center[2])
            wall_thick = size[1]''',
'''        role = {"door": "doorway", "garage": "doorway", "window": "window",
                "breach": "breach", "vault": "vault_door",
                "teller": "teller_line", "safe_deposit": "safe_deposit_boxes"}.get(kind, "doorway")
        if role in self.FIXTURE_OPENINGS:
            import prop_species
            mat = prop_species.material_for(role, h.get("material") or mat)
        u, w, hh, sill = h["u"], h["w"], h["h"], h["sill"]
        if axis == 0:
            oc = (center[0] + u, center[1], center[2])
            wall_thick = size[1]'''),
('''                    # and what an Empty's window shows where its preset says
                    # (0.218.0): a corner shop's front
                    pane=getattr(op, "pane", None))''',
'''                    # and what an Empty's window shows where its preset says
                    # (0.218.0): a corner shop's front
                    pane=getattr(op, "pane", None),
                    # and what a vault's fixture is made of (0.285.0,
                    # `FIXTURE_OPENINGS`)
                    material=getattr(op, "material", None))'''),
('''    def _record_opening_slot(self, vb, center, size, axis, h, ref=None,
                             material=None):''',
'''    #: A VAULT'S FIXTURES ASK FOR WHAT THEY ARE MADE OF (0.285.0, the
    #: factory's roadmap 321). An opening slot took its WALL's material, so the
    #: library's five deposit-box walls and three vault doors asked Zoo for
    #: `concrete` -- which Zoo builds, options or not, and which the vault
    #: door's genome even offers. The spec names their own (`metal`), and a
    #: fixture asks its species for it the way a placed piece does
    #: (`prop_species.material_for`, 0.284.0): the deposit boxes' bare steel
    #: (Zoo 1.140.0), the door's painted. A doorway, a window and a breach are
    #: the wall and keep it.
    FIXTURE_OPENINGS = ("vault_door", "safe_deposit_boxes")

    def _record_opening_slot(self, vb, center, size, axis, h, ref=None,
                             material=None):'''),
])


edit("tests/test_storefront_glazing.py", [
('''def test_a_curtain_wall_and_a_facade_shell_are_not_storefronts():
    """`glass` is every bank's and tower's opaque curtain wall."""
    import glob
    for p in sorted(glob.glob(os.path.join(HERE, "build", "*.slots.json"))):
        b = os.path.basename(p)[: -len(".slots.json")]
        # 0.171.0: and the video store, a glass shopfront on a sales floor
        if b in STORES or b in ("card_shop_a01", "video_store_a01"):
            continue''',
'''def test_a_curtain_wall_and_a_facade_shell_are_not_storefronts():
    """`glass` is every tower's opaque curtain wall, and every other building's -- except a bank's front before its
    public room, a storefront since 0.285.0 (`deli_counter.bank_front`): the three whose front is `glass`."""
    import glob
    for p in sorted(glob.glob(os.path.join(HERE, "build", "*.slots.json"))):
        b = os.path.basename(p)[: -len(".slots.json")]
        # 0.171.0: and the video store, a glass shopfront on a sales floor
        if b in STORES or b in ("card_shop_a01", "video_store_a01"):
            continue
        if b in ("bank_branch_a02", "bank_branch_a03", "bank_job"):
            continue'''),
])


edit("prop_species.py", [
("""    'roller_grill': ('metal_bare', ('metal_bare', 'glass')),
""", """    'roller_grill': ('metal_bare', ('metal_bare', 'glass')),
    # a vault's fixtures, which `deli_counter`'s `FIXTURE_OPENINGS` asks by (0.285.0)
    'safe_deposit_boxes': ('metal_bare', ('metal_bare', 'laminate')),
"""),
("""    'teller_line': ('metal', ('metal', 'laminate', 'concrete', 'wood')),
""", """    'teller_line': ('metal', ('metal', 'laminate', 'concrete', 'wood')),
    'vault_door': ('metal_painted', ('metal_painted', 'concrete')),
"""),
])
