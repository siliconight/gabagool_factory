"""Deli Counter 0.166.0, follow-up to `patch_dc_inner_face.py`: decide the
room face where the slot's FINAL kind is known.

That patch stamped `material_in` when a slot was recorded, and the first
library build with it changed 4 slot manifests of the 15 it should have.
Two reasons, both the same shape -- the record step does not know the kind
the manifest will carry:

  * a slot's `material` at record time is the spec's palette id
    (`stone_ext`, `brick_ext`); `write_slot_manifest` maps it to its kind
    (`stone`, `brick`) when it writes the file. Only the four plain-`wood`
    buildings matched;
  * a back room's stretch of the shop front is recorded as storefront glass
    and becomes a solid wall in the building's default material in the
    WRITER (`back_room_wall`, 0.159.0): gas_station_a02's ext_0_E segments
    5-8, stone in the manifest, recorded as glass.

So the stamp moves into `write_slot_manifest`, after the kind and the glazing
are settled -- one rule, in the one place that knows -- and the record-time
stamps (the first patch's WALL_NEW / OPEN_NEW) come out. A first draft of this
follow-up mapped the id with `kind_for` at record time; it fixed the first
reason and missed the second, which the gas station's own manifest showed.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

P = pathlib.Path(__file__).resolve().parents[1] / "deli_counter" / "deli_counter.py"

PAIRS = [
    # the record-time stamp on a wall segment comes out
    ('''        scale = dims[:] if size_mod == "end" else [1.0, 1.0, 1.0]
        # THE ROOM FACE (0.166.0): a full segment of an exterior wall in an
        # outside-only finish names the building's interior finish too. Not
        # a remainder (`end`): that is a unit box scaled per slot, and its
        # few centimetres keep the wall's finish.
        inner = self._material_in(wall_name, mat) if size_mod != "end" else None
        self.slots.append({
            "slot_id": vname, "role": role, "size_mod": size_mod,
            "style": style, "material": mat,
            **({"material_in": inner} if inner else {}),''',
     '''        scale = dims[:] if size_mod == "end" else [1.0, 1.0, 1.0]
        self.slots.append({
            "slot_id": vname, "role": role, "size_mod": size_mod,
            "style": style, "material": mat,'''),
    # ...and on an opening
    ('''        # an opening in an exterior wall takes the wall's room face (0.166.0)
        inner = (self._material_in(vb.rsplit("_open", 1)[0], mat)
                 if role in ("doorway", "window", "breach") else None)
        slot = {
            "slot_id": vb, "role": role, "size_mod": "full",
            "style": style, "material": mat,
            **({"material_in": inner} if inner else {}),''',
     '''        slot = {
            "slot_id": vb, "role": role, "size_mod": "full",
            "style": style, "material": mat,'''),
    # `_material_in` reads a KIND now; its caller passes the final one
    ('''    def _material_in(self, wall_name, mat):
        """`material_in` for a slot on `wall_name`, or None: only an EXTERIOR
        wall (`ext_<story>_<N|E|S|W>`) in an outside-only finish has one."""
        parts = str(wall_name).split("_")
        if (len(parts) >= 3 and parts[0] == "ext" and parts[2] in ("N", "E", "S", "W")
                and mat in self.OUTSIDE_ONLY):
            return self._interior_finish()
        return None''',
     '''    def _material_in(self, slot):
        """`material_in` for a slot AS THE MANIFEST WILL WRITE IT (its final
        kind and glazing), or None: only a full wall segment or an opening in
        an EXTERIOR wall (`ext_<story>_<N|E|S|W>`) in an outside-only finish
        has one. Not a remainder (`end`, a unit box scaled per slot) and not
        a storefront (glass)."""
        parts = str(slot.get("wall") or "").split("_")
        if (len(parts) >= 3 and parts[0] == "ext" and parts[2] in ("N", "E", "S", "W")
                and slot.get("role") in ("wall", "window", "doorway", "breach")
                and slot.get("size_mod") != "end" and not slot.get("glazing")
                and slot.get("material") in self.OUTSIDE_ONLY):
            return self._interior_finish()
        return None'''),
    # the stamp, in the writer, after kind and glazing are settled
    ('''        if _s.get("role") in LIGHT_BUDGET_ROLES and _s.get("room") in _lit:
            _s = dict(_s, light_budget_tiles=True)
        _slots.append(_s)''',
     '''        if _s.get("role") in LIGHT_BUDGET_ROLES and _s.get("room") in _lit:
            _s = dict(_s, light_budget_tiles=True)
        # THE ROOM FACE (0.166.0), here and not where the slot was recorded:
        # only now is its kind final -- a palette id became `stone` above, a
        # back room's glass became the default wall
        _in = builder._material_in(_s)
        if _in:
            _s = dict(_s, material_in=_in)
        _slots.append(_s)'''),
]


def main():
    raw = P.read_bytes()
    assert b"\r\n" not in raw
    s = raw.decode("utf-8")
    for old, new in PAIRS:
        assert s.count(old) == 1, (s.count(old), old[:70])
        s = s.replace(old, new)
    P.write_bytes(s.encode("utf-8"))
    print("patched deli_counter.py")


if __name__ == "__main__":
    main()
