"""Zoo 1.38.0: a wall module with a room face.

Cold run 9120's FLAPPHAS walk, finding 3: stone inside the gas station. A
wall module wore its slot's one material on both faces, deliberately -- the
relief is carved on both faces so the module "needs no idea which face is the
street" (`arch.relief_parts`). Deli Counter 0.166.0 now says which: an
exterior wall in an outside-only finish carries `material_in`, and the room
face is local -Y, measured through Deli Counter's own placement basis on all
four facings (`patch_dc_inner_face.py`).

  * `kit.plan_kit`: a wall-family slot's `material_in` (a known kind) is in
    the module key and the stem, `_i<kind>` after `_m<kind>` -- the one-
    material and two-material modules of one wall are two builds;
  * `dna.resolve_module_plan`: carries it onto the plan;
  * `_arch.build_slab`: every structure face pointing -Y on the -Y half of
    the module takes `material_in` -- the room face, and the room faces of
    the relief's recessed fields with it. The jambs, sill and head of an
    opening keep the wall's own finish. One more material on the module:
    one more draw where it applies, which is what the measurement prices.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

ZOO = pathlib.Path(__file__).resolve().parents[1] / "zoo"


def _edit(rel, pairs):
    p = ZOO / rel
    raw = p.read_bytes()
    assert b"\r\n" not in raw, f"{rel}: CRLF in an LF file"
    s = raw.decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    p.write_bytes(s.encode("utf-8"))
    print("patched", rel)


KIT = [
    ('''LIGHT_BUDGET_ROLES = ("floor", "ceiling")''',
     '''LIGHT_BUDGET_ROLES = ("floor", "ceiling")
#: The roles whose module can carry a ROOM FACE (1.38.0): a full wall segment
#: and the openings in one. Deli Counter's `themed_tscn.INNER_FACE_ROLES` is
#: the mirror.
INNER_FACE_ROLES = ("wall", "window", "doorway", "breach")'''),
    ('''                variant: int = None, material: str = None,
                glazing: str = None, budget_tiles: bool = False) -> str:
    """The exact filename stem Deli Counter's resolver looks for:
    ``<type>[_<species>]_<theme>_<style:02d>[_w<cm>][_d<cm>][_h<cm>][_f<form>][_s<stock>][_n<variant>][_m<material>][_v<hash>][_o<hash>][_<state>]``.''',
     '''                variant: int = None, material: str = None,
                glazing: str = None, budget_tiles: bool = False,
                material_in: str = None) -> str:
    """The exact filename stem Deli Counter's resolver looks for:
    ``<type>[_<species>]_<theme>_<style:02d>[_w<cm>][_d<cm>][_h<cm>][_f<form>][_s<stock>][_n<variant>][_m<material>][_i<material_in>][_v<hash>][_o<hash>][_<state>]``.

    ``material_in`` (1.38.0) is a wall's ROOM-FACE kind: an exterior wall in
    an outside-only finish is built with its room face in the building's
    interior finish, and that is another build of the same wall.'''),
    ('''    if material:
        base += f"_m{material}"
    # THE STOREFRONT IN THE NAME (1.18.0)''',
     '''    if material:
        base += f"_m{material}"
    if material_in:
        base += f"_i{material_in}"
    # THE STOREFRONT IN THE NAME (1.18.0)'''),
    ('''        storefront = s.get("glazing") if s.get("glazing") in STEM_GLAZINGS else None
        budget = bool(s.get("light_budget_tiles")) and typ in LIGHT_BUDGET_ROLES
''',
     '''        storefront = s.get("glazing") if s.get("glazing") in STEM_GLAZINGS else None
        budget = bool(s.get("light_budget_tiles")) and typ in LIGHT_BUDGET_ROLES
        # THE ROOM FACE (1.38.0): a known kind on a wall-family slot, else none
        inner = (str(s["material_in"]) if typ in INNER_FACE_ROLES and s.get("material_in")
                 in skins.KNOWN_KINDS else None)
'''),
    ('''                               material=mtag, glazing=storefront,
                               budget_tiles=budget, **dress)''',
     '''                               material=mtag, glazing=storefront,
                               budget_tiles=budget, material_in=inner, **dress)'''),
    ('''                   _opening_key(fit.get("openings")), budget)''',
     '''                   _opening_key(fit.get("openings")), budget, inner)'''),
    ('''                    "light_budget_tiles": budget,
                    "count": 0,''',
     '''                    "light_budget_tiles": budget,
                    "material_in": inner,
                    "count": 0,'''),
]

DNA = [
    ('''    if module.get("light_budget_tiles"):
        plan["light_budget_tiles"] = True
''',
     '''    if module.get("light_budget_tiles"):
        plan["light_budget_tiles"] = True
    # A wall's ROOM FACE (1.38.0): the kind its -Y face is built in
    if module.get("material_in"):
        plan["material_in"] = str(module["material_in"])
'''),
]

ARCH = [
    ('''    structure = materials.make_material(
        f"M_{root}_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, structure)
''',
     '''    structure = materials.make_material(
        f"M_{root}_{plan['material']}", plan["color"], plan["material"])
    materials.assign(objs, structure)
    # THE ROOM FACE (1.38.0). Deli Counter places a wall module with its
    # local +Y outdoors on every facing (measured through its placement
    # basis), so the ROOM is at -Y: every structure face pointing -Y on the
    # -Y half -- the wall's inner face and its recessed fields' -- takes the
    # interior finish. Jambs, sill and head keep the wall's own: they face
    # across the opening, not into the room. Before the storefront panes and
    # the window glass below, which are not structure.
    inner = plan.get("material_in")
    if inner and species in ("wall", "window", "doorway", "breach") and not plan.get("storefront"):
        room = materials.make_material(f"M_{root}_{inner}", INNER_COLOR, inner)
        done = set()
        for o in objs:
            if id(o.data) in done:        # a mesh shared by two parts takes it once
                continue
            done.add(id(o.data))
            o.data.materials.append(room)
            for poly in o.data.polygons:
                if poly.normal.y < -0.9 and poly.center.y < 0.0:
                    poly.material_index = len(o.data.materials) - 1
'''),
    ('''def build_slab(plan, streams, collection, species):''',
     '''#: The flat colour a room face falls back to with no skin library: a warm
#: off-white wall, the drywall a 1990s store is painted.
INNER_COLOR = (0.82, 0.80, 0.74)


def build_slab(plan, streams, collection, species):'''),
]


def main():
    _edit("zoo_keeper/core/kit.py", KIT)
    _edit("zoo_keeper/core/dna.py", DNA)
    _edit("zoo_keeper/recipes/_arch.py", ARCH)


if __name__ == "__main__":
    main()
