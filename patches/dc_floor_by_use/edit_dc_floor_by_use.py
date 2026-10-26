"""Deli Counter 0.271.0 on a clone: a selling floor is tile and a working floor is concrete, whatever role routes it
to carpet (the factory's docs/findings/walk_2026-10-26_panel/, L4). Anchored; refuses on a miss.

    python edit_dc_floor_by_use.py <clone>

Copies tests/test_floor_by_use.py from `src/`; `floors._material` asks the room's own words before handing a floor
the role map's carpet.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("tests/test_floor_by_use.py",):
    assert not (C / rel).exists(), rel
    shutil.copyfile(HERE / "src" / rel, C / rel)
    print("wrote", rel)


def edit(rel, edits):
    p = C / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:80])
        t = t.replace(old, new)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("edited", rel, len(edits))


edit("floors.py", [
    ('''def _material(room, surface, mapping, default):
    """A room's own per-surface material wins (``floor_material`` /
    ``ceiling_material``); then its ``material`` for both; then the role
    map; then the spec default."""
    own = (getattr(room, "%s_material" % surface, None)
           or getattr(room, "material", None))
    if own:
        return own
    return mapping.get(getattr(room, "role", None), default)
''', '''#: A FLOOR BY ITS USE, WHERE THE ROLE WOULD CARPET IT (0.271.0). The walker,
#: 2026-10-26, in seed 9205's supermarket: "far too dark in teh super market".
#: Measured on its walk (the factory's docs/findings/walk_2026-10-26_panel/,
#: L4): the sales floor read luma p50 3 at Blue Hour against the back stock's
#: 77 next door; under an inspection light it is a dark maroon CARPET between
#: brown blocks; doubling the room fill raised both rooms alike and texels x2
#: changed nothing -- the room was lit like its neighbour and dark by what it
#: was made of. `public_entry` maps to carpet, which is right for a lobby, a
#: banking hall or a parlour and wrong for a shop: 33 `sales_floor`s, 21 delis'
#: `customer_floor`s and `stockroom_loading`s, pawn and pharmacy floors, market
#: stalls -- and a garage deck, a service bay, a loading dock, a train shed --
#: were all carpeted by their role. A 1990s store floor is vinyl tile and a
#: working floor is a slab. So where the role map would hand a floor CARPET,
#: the room's own id is asked first: a word that sells takes `tile`, a word
#: that works takes `concrete`. A room's own floor material still wins, the
#: ceiling is not touched, and the floor and ceiling stay different surfaces
#: (`tile` under `ceiling_tile`, `concrete` under it), as `test_floors` holds.
#: `main_floor` is a warehouse's and a club's both, so it is not here: what it
#: is needs the building, not the room.
_SELLING_FLOOR_WORDS = ("sales", "retail", "shop", "store", "market", "stall", "customer", "aisle")
_WORKING_FLOOR_WORDS = ("stock", "loading", "dock", "bay", "deck", "shed", "lanes", "works", "pour", "garage")


def floor_by_use(room_id):
    """``"tile"`` for a room whose id says it sells, ``"concrete"`` for one that says it works, else None. Whole
    words of the id (`room_id` split on ``_``): `stockroom_loading` works, `lobby` neither."""
    words = set(str(room_id or "").lower().replace("-", "_").split("_"))
    if any(w.startswith(k) for w in words for k in _WORKING_FLOOR_WORDS):
        return "concrete"
    if any(w.startswith(k) for w in words for k in _SELLING_FLOOR_WORDS):
        return "tile"
    return None


def _material(room, surface, mapping, default):
    """A room's own per-surface material wins (``floor_material`` /
    ``ceiling_material``); then its ``material`` for both; then the role
    map -- except that a floor the map would carpet is asked its use first
    (`floor_by_use`, 0.271.0); then the spec default."""
    own = (getattr(room, "%s_material" % surface, None)
           or getattr(room, "material", None))
    if own:
        return own
    got = mapping.get(getattr(room, "role", None), default)
    if surface == "floor" and got == "carpet":
        return floor_by_use(getattr(room, "id", None)) or got
    return got
'''),
])
