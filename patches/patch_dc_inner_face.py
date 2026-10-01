"""Deli Counter 0.166.0: an outside-only wall finish stops at the wall.

Cold run 9120's FLAPPHAS walk, finding 3: the interior faces of the gas
station's exterior walls wear the exterior stone -- behind the register, in
the stockroom and the office. Every exterior wall slot names ONE material and
Zoo's module wears it on both faces, so wherever the outside is a finish that
belongs outside (brick, stone, wood boards, siding), the inside is too: 2,000
modules in 15 buildings of the library. Concrete, painted block and metal
read the same both sides and are left alone.

This side: an exterior wall's slot -- a full segment, a window, a door, a
breach -- whose material is in `OUTSIDE_ONLY` carries `material_in`, the
building's interior finish (`_interior_finish`: the commonest kind among its
partitions that is not itself outside-only, else drywall). Zoo 1.38.0 builds
the module's ROOM face in it. Which face that is was MEASURED, not reasoned:
pushed through `tscn_export.godot_basis` for N/E/S/W at 0/90/180/270, a
module's local +Y lands outdoors on all four, so the room side is local -Y;
and `themed_tscn._fit_rotation` tries the slot's own rotation first and keeps
it on a tie, so a south wall stays at 180 and is not turned inside out.

`themed_tscn.module_stem` mirrors Zoo's `_i<kind>`, and `resolve_slot_choice`
asks for it first and the plain name second, so a library built before it
still resolves.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

DC = pathlib.Path(__file__).resolve().parents[1] / "deli_counter"


def _edit(rel, pairs):
    p = DC / rel
    raw = p.read_bytes()
    assert b"\r\n" not in raw, f"{rel}: CRLF in an LF file"
    s = raw.decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    p.write_bytes(s.encode("utf-8"))
    print("patched", rel)


# --- deli_counter.py ------------------------------------------------------------

ORIENT_OLD = '''    def _slot_orient(self, wall_name, axis):'''
ORIENT_NEW = '''    #: Wall finishes that belong OUTSIDE (0.166.0). An exterior wall in one of
    #: these carries `material_in`, its building's interior finish, which Zoo
    #: builds on the module's room face; concrete, painted block and metal
    #: read the same both sides and stay one material.
    OUTSIDE_ONLY = frozenset({"brick", "stone", "wood", "siding"})

    def _interior_finish(self):
        """The building's interior wall finish: the commonest skin kind among
        its partitions that is not itself outside-only, else drywall. A card
        shop panelled in wood gets wood panel; a deli whose partitions are
        mostly drywall with a brick feature wall gets drywall."""
        cached = getattr(self, "_inner_finish", None)
        if cached:
            return cached
        import collections
        import material_kind
        seen = collections.Counter()
        for p in self.s.partitions:
            m = p.material or self.s.default_material
            k = material_kind.kind_for(m, m if m in material_kind.SKIN_KINDS else None)
            if k and k in material_kind.SKIN_KINDS and k not in self.OUTSIDE_ONLY:
                seen[k] += 1
        self._inner_finish = (sorted(seen.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
                              if seen else "drywall")
        return self._inner_finish

    def _material_in(self, wall_name, mat):
        """`material_in` for a slot on `wall_name`, or None: only an EXTERIOR
        wall (`ext_<story>_<N|E|S|W>`) in an outside-only finish has one."""
        parts = str(wall_name).split("_")
        if (len(parts) >= 3 and parts[0] == "ext" and parts[2] in ("N", "E", "S", "W")
                and mat in self.OUTSIDE_ONLY):
            return self._interior_finish()
        return None

    def _slot_orient(self, wall_name, axis):'''

WALL_OLD = '''        scale = dims[:] if size_mod == "end" else [1.0, 1.0, 1.0]
        self.slots.append({
            "slot_id": vname, "role": role, "size_mod": size_mod,
            "style": style, "material": mat,'''
WALL_NEW = '''        scale = dims[:] if size_mod == "end" else [1.0, 1.0, 1.0]
        # THE ROOM FACE (0.166.0): a full segment of an exterior wall in an
        # outside-only finish names the building's interior finish too. Not
        # a remainder (`end`): that is a unit box scaled per slot, and its
        # few centimetres keep the wall's finish.
        inner = self._material_in(wall_name, mat) if size_mod != "end" else None
        self.slots.append({
            "slot_id": vname, "role": role, "size_mod": size_mod,
            "style": style, "material": mat,
            **({"material_in": inner} if inner else {}),'''

OPEN_OLD = '''        slot = {
            "slot_id": vb, "role": role, "size_mod": "full",
            "style": style, "material": mat,
            "current_ref": ref or f"{role}_greybox_01", "kit_axis": "theme",
            "wall": vb.rsplit("_open", 1)[0], "story": story, "facing": facing,'''
OPEN_NEW = '''        # an opening in an exterior wall takes the wall's room face (0.166.0)
        inner = (self._material_in(vb.rsplit("_open", 1)[0], mat)
                 if role in ("doorway", "window", "breach") else None)
        slot = {
            "slot_id": vb, "role": role, "size_mod": "full",
            "style": style, "material": mat,
            **({"material_in": inner} if inner else {}),
            "current_ref": ref or f"{role}_greybox_01", "kit_axis": "theme",
            "wall": vb.rsplit("_open", 1)[0], "story": story, "facing": facing,'''

# --- themed_tscn.py ---------------------------------------------------------------

STEM_SIG_OLD = '''                variant: int = None, material: str = None,
                glazing: str = None, budget_tiles: bool = False) -> str:
    """``<type>[_<species>]_<theme>_<style:02d>[_w<cm>][_d<cm>][_h<cm>][_f<form>][_s<stock>][_n<variant>][_m<material>][_v<hash>][_o<hash>][_<state>]``.'''
STEM_SIG_NEW = '''                variant: int = None, material: str = None,
                glazing: str = None, budget_tiles: bool = False,
                material_in: str = None) -> str:
    """``<type>[_<species>]_<theme>_<style:02d>[_w<cm>][_d<cm>][_h<cm>][_f<form>][_s<stock>][_n<variant>][_m<material>][_i<material_in>][_v<hash>][_o<hash>][_<state>]``.'''

STEM_M_OLD = '''    if material:
        base += f"_m{material}"
    if glazing in STEM_GLAZINGS:'''
STEM_M_NEW = '''    if material:
        base += f"_m{material}"
    # THE ROOM FACE (Zoo 1.38.0, `kit.module_stem`): an exterior wall whose
    # inside is another finish is another build, after the material
    if material_in:
        base += f"_i{material_in}"
    if glazing in STEM_GLAZINGS:'''

RESOLVE_OLD = '''    stem = module_stem(typ, theme, eff_style, width_cm,
                       state if state else _default_stem_state(slot),
                       depth_cm, vtag, otag, height_cm, species=species,
                       material=material, glazing=glazing, budget_tiles=budget,
                       **dress)
    return stem, (not exact)'''
RESOLVE_NEW = '''    inner = slot.get("material_in") if typ in INNER_FACE_ROLES else None
    stem = module_stem(typ, theme, eff_style, width_cm,
                       state if state else _default_stem_state(slot),
                       depth_cm, vtag, otag, height_cm, species=species,
                       material=material, glazing=glazing, budget_tiles=budget,
                       material_in=inner, **dress)
    return stem, (not exact)


#: The roles whose module can have a room face (Zoo 1.38.0,
#: `kit.INNER_FACE_ROLES`): full exterior wall segments and their openings.
INNER_FACE_ROLES = ("wall", "window", "doorway", "breach")'''

CAND_OLD = '''    if slot.get("light_budget_tiles"):
        candidates = candidates + [dict(c, light_budget_tiles=None) for c in candidates]
    mat = stem_material(slot)'''
CAND_NEW = '''    if slot.get("light_budget_tiles"):
        candidates = candidates + [dict(c, light_budget_tiles=None) for c in candidates]
    # ...and a wall with a room face to the plain one (Zoo 1.38.0): a library
    # built before it has the one-material module and no `_i<kind>`.
    if slot.get("material_in"):
        candidates = candidates + [dict(c, material_in=None) for c in candidates]
    mat = stem_material(slot)'''

TEST = '''"""An outside-only wall finish stops at the wall (0.166.0).

Cold run 9120, finding 3: the gas station's exterior stone on the inside of
its exterior walls. Held here: every exterior wall slot in brick, stone, wood
or siding names its building's interior finish as `material_in`, no other
slot does, a remainder never does; the finish is never itself outside-only;
the stem mirror writes `_i<kind>` and resolves the plain name when the tagged
one is not built; and the room face is local -Y on all four facings,
measured through `tscn_export.godot_basis`, the transform every package is
placed with.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import themed_tscn  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUTSIDE_ONLY = {"brick", "stone", "wood", "siding"}


def _manifests():
    for p in sorted(glob.glob(os.path.join(HERE, "build", "*.slots.json"))):
        with open(p, encoding="utf-8") as f:
            yield json.load(f)


def test_every_outside_only_exterior_wall_names_its_room_face_and_nothing_else_does():
    tagged = 0
    for d in _manifests():
        for s in d["slots"]:
            parts = str(s.get("wall") or "").split("_")
            ext = len(parts) >= 3 and parts[0] == "ext" and parts[2] in ("N", "E", "S", "W")
            want = (ext and s.get("material") in OUTSIDE_ONLY and s.get("size_mod") != "end"
                    and s.get("role") in ("wall", "window", "doorway", "breach"))
            if want:
                tagged += 1
                assert s.get("material_in"), (d["building_id"], s["slot_id"])
                assert s["material_in"] not in OUTSIDE_ONLY, (d["building_id"], s["slot_id"])
            else:
                assert "material_in" not in s, (d["building_id"], s["slot_id"])
    assert tagged >= 1500, tagged


def test_the_gas_station_s_stone_walls_are_drywall_inside():
    d = json.load(open(os.path.join(HERE, "build", "gas_station_a02.slots.json"), encoding="utf-8"))
    stone = [s for s in d["slots"] if s.get("material") == "stone" and s.get("material_in")]
    assert stone and {s["material_in"] for s in stone} == {"drywall"}


def test_the_stem_mirror_writes_the_room_face_and_falls_back(tmp_path):
    slot = {"slot_id": "ext_0_N_seg0", "role": "wall", "size_mod": "full", "style": 1,
            "material": "stone", "material_in": "drywall",
            "fit": {"dims": [2.0, 0.3, 3.9], "pivot": "center"}}
    tagged, _ = themed_tscn.resolve_themed_stem(slot, "delco_1997", 1, material="stone")
    plain, _ = themed_tscn.resolve_themed_stem(dict(slot, material_in=None), "delco_1997", 1,
                                               material="stone")
    assert tagged == plain.replace("_mstone", "_mstone_idrywall") and "_idrywall" in tagged
    # only the plain module built: the resolver lands on it
    (tmp_path / (plain + ".glb")).write_bytes(b"")
    got = themed_tscn.resolve_slot_ref(slot, "delco_1997", 1, str(tmp_path))[0]
    assert got == plain
    (tmp_path / (tagged + ".glb")).write_bytes(b"")
    assert themed_tscn.resolve_slot_ref(slot, "delco_1997", 1, str(tmp_path))[0] == tagged


def test_the_room_face_is_local_minus_y_on_every_facing():
    from tscn_export import godot_basis
    for facing, rot, out in (("N", 0, (0, 1)), ("E", 90, (1, 0)), ("S", 180, (0, -1)),
                             ("W", 270, (-1, 0))):
        b = godot_basis(rot, [1.0, 1.0, 1.0])
        rows = [b[0:3], b[3:6], b[6:9]]
        v = (0.0, 0.0, 1.0)              # local -Y in Blender is +Z in the module's Godot frame
        w = [sum(rows[i][k] * v[k] for k in range(3)) for i in range(3)]
        assert (round(w[0], 6), round(-w[2], 6)) == (-out[0], -out[1]), facing
'''


def main():
    t = DC / "test_inner_face.py"
    assert not t.exists(), "already applied"
    _edit("deli_counter.py", [(ORIENT_OLD, ORIENT_NEW), (WALL_OLD, WALL_NEW), (OPEN_OLD, OPEN_NEW)])
    _edit("themed_tscn.py", [(STEM_SIG_OLD, STEM_SIG_NEW), (STEM_M_OLD, STEM_M_NEW),
                             (RESOLVE_OLD, RESOLVE_NEW), (CAND_OLD, CAND_NEW)])
    t.write_bytes(TEST.encode("utf-8"))
    print("wrote test_inner_face.py")


if __name__ == "__main__":
    main()
