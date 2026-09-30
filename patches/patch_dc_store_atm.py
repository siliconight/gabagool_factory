"""Deli Counter 0.164.0: the store ATM fixture (atm_store), one per building.

Anchored: every anchor must match exactly once or nothing is written.
"""
import pathlib
import sys

P = pathlib.Path(__file__).resolve().parent.parent / "deli_counter" / "level_design.py"
EDITS = [('           reserved_by=None, off_glass=False, backed_by=None,\n           ceiling=None, under_hung=False, twin=False, wall_band=False,\n           rooms=None, distinct=False):\n    return {"name": name, "sizes": tuple(sizes), "where": where,\n            "front": front, "stock": stock, "variants": variants,\n', '           reserved_by=None, off_glass=False, backed_by=None,\n           ceiling=None, under_hung=False, twin=False, wall_band=False,\n           rooms=None, distinct=False, solo=False):\n    return {"name": name, "sizes": tuple(sizes), "where": where,\n            "front": front, "stock": stock, "variants": variants,\n'), ('            "wall_band": wall_band,\n            "rooms": frozenset(rooms) if rooms else None,\n            "distinct": distinct}\n\n\n', '            "wall_band": wall_band,\n            "rooms": frozenset(rooms) if rooms else None,\n            "distinct": distinct, "solo": solo}\n\n\n'), ('           front=True, most=3, variants=True),\n    _piece("atm", ((0.6, 0.55, 1.45),), "wall", front=True, most=1),\n    _piece("payphone", ((0.75, 0.5, 2.3),), "wall", front=True, most=1),\n    _piece("chair_waiting", ((2.4, 0.6, 0.9), (1.8, 0.6, 0.9),\n', '           front=True, most=3, variants=True),\n    _piece("atm", ((0.6, 0.55, 1.45),), "wall", front=True, most=1),\n    # THE STORE\'S ATM (0.164.0). The walker, 2026-09-29: "Convenient stores\n    # should also have ATMs". Zoo 1.35.0 drew a 1990s freestanding surcharge\n    # unit, four invented networks by variant. A FIXTURE, so a selling floor\n    # does not draw for it; one a room, gated to rooms that sell as the sale\n    # posters are; placed before them, so no poster hangs over it. Four\n    # variants, keyed by the volume\'s name (past four `_make_volume` keys a\n    # variant on the building). Standing, with collision: a body walks into\n    # an ATM.\n    # SOLO: one in the BUILDING, not one a room -- a deli\'s customer floor and\n    # its market aisles are two selling rooms and one store, and with the\n    # per-room cap alone six delis carried two ATMs each (measured, 37 in 31\n    # specs, before this).\n    _piece("atm_store", ((0.6, 0.55, 1.45),), "wall", front=True, most=1, variants=4,\n           rooms=("sales", "retail", "shop", "customer", "market", "showroom", "stall"),\n           solo=True),\n    _piece("payphone", ((0.75, 0.5, 2.3),), "wall", front=True, most=1),\n    _piece("chair_waiting", ((2.4, 0.6, 0.9), (1.8, 0.6, 0.9),\n'), ('                   "floor": (),\n                   "clusters": ((("cartons",), 2, 3), (("litter_bin",), 1, 1)),\n                   "fixtures": ("poster_wall_store",)},\n    "garage": {"anchors": ("workbench",),\n               "wall": ("shelf_run", "cabinet_tool"),\n', '                   "floor": (),\n                   "clusters": ((("cartons",), 2, 3), (("litter_bin",), 1, 1)),\n                   "fixtures": ("atm_store", "poster_wall_store")},\n    "garage": {"anchors": ("workbench",),\n               "wall": ("shelf_run", "cabinet_tool"),\n'), ('            only = _PIECES[key]["rooms"]\n            if only and not tokens & only:\n                continue\n            for k in range(fixture_limit(key, area)):\n', '            only = _PIECES[key]["rooms"]\n            if only and not tokens & only:\n                continue\n            if _PIECES[key]["solo"] and any(\n                    str(v.get("name", "")).startswith(key + "_") for v in spec.get("volumes") or []):\n                continue\n            for k in range(fixture_limit(key, area)):\n')]


def main():
    s = P.read_bytes().decode("utf-8")
    for a, b in EDITS:
        if s.count(a) != 1:
            sys.exit("REFUSED: anchor x%d: %r" % (s.count(a), a[:80]))
        s = s.replace(a, b, 1)
    P.write_bytes(s.encode("utf-8"))
    print("patched level_design.py")


if __name__ == "__main__":
    main()
