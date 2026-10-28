"""Edit a Deli Counter clone for 0.282.0: a bank's concrete exterior walls are plastered on their room face above grade
-- the walker's bank comps' painted walls, where every frame showed raw concrete. Run from the clone's root. Asserts
every anchor once; refuses on a miss."""
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
('''    def _material_in(self, slot):
        """`material_in` for a slot AS THE MANIFEST WILL WRITE IT (its final
        kind and glazing), or None: only a wall segment -- a remainder too
        since 0.166.1 -- or an opening in an EXTERIOR wall
        (`ext_<story>_<N|E|S|W>`) in an outside-only finish has one. Not a
        storefront (glass)."""
        parts = str(slot.get("wall") or "").split("_")
        if (len(parts) >= 3 and parts[0] == "ext" and parts[2] in ("N", "E", "S", "W")
                and slot.get("role") in ("wall", "window", "doorway", "breach")
                and not slot.get("glazing")
                and slot.get("material") in self.OUTSIDE_ONLY):
            return self._interior_finish()
        return None''',
'''    #: A BANK'S WALLS ARE FINISHED INSIDE (0.282.0, the factory's roadmap 321).
    #: The walker's bank comps (docs/reference/BANK_INTERIOR_COMPS.md) paint
    #: every public room's walls -- white or beige plaster, wood below -- and
    #: concrete reads "the same both sides" above, so a bank built of it showed
    #: raw concrete in its lobby and offices (docs/findings/bank_interior/,
    #: frames 01-06). A bank's concrete exterior walls above grade take this on
    #: their room face; below grade, the money rooms, they stay concrete, the
    #: comps' "hard rooms".
    BANK_INTERIOR = "plaster"

    def _is_bank(self):
        cached = getattr(self, "_bank", None)
        if cached is None:
            import level_design
            import lights
            cached = self._bank = lights.is_bank(level_design.club_building_id(self.s))
        return cached

    def _material_in(self, slot):
        """`material_in` for a slot AS THE MANIFEST WILL WRITE IT (its final
        kind and glazing), or None: only a wall segment -- a remainder too
        since 0.166.1 -- or an opening in an EXTERIOR wall
        (`ext_<story>_<N|E|S|W>`) in an outside-only finish has one, or
        (0.282.0) a bank's concrete one above grade, `BANK_INTERIOR`. Not a
        storefront (glass)."""
        parts = str(slot.get("wall") or "").split("_")
        if not (len(parts) >= 3 and parts[0] == "ext" and parts[2] in ("N", "E", "S", "W")
                and slot.get("role") in ("wall", "window", "doorway", "breach")
                and not slot.get("glazing")):
            return None
        if slot.get("material") in self.OUTSIDE_ONLY:
            return self._interior_finish()
        story = int(parts[1]) if parts[1].lstrip("-").isdigit() else 0
        if slot.get("material") == "concrete" and story >= 0 and self._is_bank():
            return self.BANK_INTERIOR
        return None'''),
])

edit("tests/test_inner_face.py", [
('''import themed_tscn  # noqa: E402
''',
'''import lights  # noqa: E402
import themed_tscn  # noqa: E402
'''),
('''            want = (ext and s.get("material") in OUTSIDE_ONLY and not s.get("glazing")
                    and s.get("role") in ("wall", "window", "doorway", "breach"))''',
'''            opening = not s.get("glazing") and s.get("role") in ("wall", "window", "doorway", "breach")
            want = ext and s.get("material") in OUTSIDE_ONLY and opening
            # 0.282.0: a bank's concrete above grade is plastered inside
            bank = (ext and opening and s.get("material") == "concrete" and int(parts[1]) >= 0
                    and lights.is_bank(d["building_id"]))
            if bank:
                assert s.get("material_in") == "plaster", (d["building_id"], s["slot_id"])
                continue'''),
])
