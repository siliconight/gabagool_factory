"""Deli Counter 0.267.0 on a CLONE (<repo>): the loading dock's pile is pallet stacks, and a safe is painted steel
(the walker's walk of cold run 9386, findings 9 and 3). Anchored; refuses on a miss.

    python edit_dc_pallets_safes.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("presets.py", [
    ('''        {"name": "loading_pallet_stack", "x": 12.0, "y": 10.0, "z": 0.75, "size_x": 4.5, "size_y": 2.5, "size_z": 1.5, "collision": "convex", "material": "wood"},
''',
     '''        # the loading dock's pile, as pallet stacks (0.267.0, `pallet_pile`)
        *pallet_pile(12.0, 10.0, 0.0),
'''),
    ('''def video_store(''',
     '''#: A LOADING DOCK'S PILE IS PALLET STACKS (0.267.0). The walker, walking cold
#: run 9386, of deli_a03's stockroom: "not sure what this large boring wood
#: block is". It was one 4.5 x 2.5 x 1.5 m volume, and Zoo's `pallet_stack`
#: fits 0.84-1.80 x 0.70-1.50 x 0.665-1.425 m, so the kit refused the species
#: and built a plain box. The same footprint as a grid of stacks that each fit:
#: as many along each side as keep a stack inside `PALLET_MAX`, `PALLET_GAP`
#: apart -- too narrow for a body, so the pile is still one obstacle and the
#: cover it was -- at the heights a dock's stacks stand at (`PALLET_HEIGHTS`, in
#: turn), none over the genome's. A 4.5 x 2.5 pile is three by two of 1.4 x 1.15.
PALLET_MAX = (1.8, 1.5)
PALLET_GAP = (0.15, 0.2)
PALLET_HEIGHTS = (1.3, 1.1, 1.4, 1.2, 1.4, 1.0)


def pallet_pile(cx, cy, floor_z, size_x=4.5, size_y=2.5, material="wood"):
    """The pallet-stack volumes of a dock pile ``size_x`` by ``size_y`` centred
    on (cx, cy), standing on ``floor_z``: ``loading_pallet_stack_1`` .. ``_n``,
    row by row. One rule for the preset and for the stored specs
    (`migrations/migrate_pallet_pile.py`)."""
    import math
    (mx, my), (gx, gy) = PALLET_MAX, PALLET_GAP
    nx = max(1, int(math.ceil((size_x + gx) / (mx + gx) - 1e-9)))
    ny = max(1, int(math.ceil((size_y + gy) / (my + gy) - 1e-9)))
    uw = round((size_x - (nx - 1) * gx) / nx, 3)
    ud = round((size_y - (ny - 1) * gy) / ny, 3)
    # furnish counts a room's stacks as ONE piece of what it holds, as the one block they replace was
    # (`level_design._room_volume_count`, by their name)
    out = []
    k = 0
    for j in range(ny):
        for i in range(nx):
            h = PALLET_HEIGHTS[k % len(PALLET_HEIGHTS)]
            k += 1
            out.append({"name": "loading_pallet_stack_%d" % k,
                        "x": round(cx + (i - (nx - 1) / 2.0) * (uw + gx), 3),
                        "y": round(cy + (j - (ny - 1) / 2.0) * (ud + gy), 3),
                        "z": round(floor_z + h / 2.0, 3), "size_x": uw, "size_y": ud, "size_z": h,
                        "collision": "convex", "material": material})
    return out


def video_store('''),
])
edit("level_design.py", [
    ('''def _room_volume_count(spec, room):
''', '''#: the stacks of a loading dock's pile, `presets.pallet_pile`'s names (0.267.0)
PALLET_STACK_PREFIX = "loading_pallet_stack_"


def _room_volume_count(spec, room):
'''),
    ('''    headroom = agent_contract.min_headroom()
    n = 0
''', '''    headroom = agent_contract.min_headroom()
    n = 0
    pile_counted = False
'''),
    ('''                            story * sh, sh):
            n += 1
    return n
''', '''                            story * sh, sh):
            # A PILE IS ONE PIECE (0.267.0). A loading dock's pile was one
            # block and counted one; as `presets.pallet_pile` stands it, six
            # stacks -- and counted six, a deli's stockroom went without its
            # supply cabinet, file cabinet, shelf run, cartons and pallets,
            # five pieces in each of six delis, when the stored specs were
            # refurnished. A room's stacks count once, by their name: a volume
            # takes no key the spec loader does not know (`spec_loader.Volume`
            # refused a `pile` id), and no room holds two piles.
            if str(v.get("name", "")).startswith(PALLET_STACK_PREFIX):
                if pile_counted:
                    continue
                pile_counted = True
            n += 1
    return n
'''),
    ('''    (("stanchion_run",), "metal_painted"),
    (("safe", "tank",''',
     '''    (("stanchion_run",), "metal_painted"),
    # A SAFE IS PAINTED STEEL (0.267.0). The walker, walking cold run 9386, of
    # pharmacy_a01's drop safe: "looks like a brown box". `metal` is the
    # theme's street metal -- delco_1997's `metal_rusted_street`, averaging
    # (115, 80, 53) against its wood's (86, 60, 41) -- and `drop_safe` is the one
    # species in this row whose genome takes `metal`, so every safe in the
    # library wore street rust; the rest fall back to their own painted kind.
    # Above the row below, whose `safe` it is.
    (("safe",), "metal_painted"),
    (("safe", "tank",'''),
])

MIG = '''#!/usr/bin/env python3
"""
migrate_pallet_pile.py  --  a stored loading dock's pile becomes pallet stacks (0.267.0)
====================================================================================
One-shot, idempotent migration over specs/*.json, lf_ specs excepted. Each volume named exactly
`loading_pallet_stack` -- the 4.5 x 2.5 x 1.5 m block the corner deli preset authored, which Zoo's `pallet_stack`
cannot fit and built as a plain box -- is replaced, in its place in the list, by `presets.pallet_pile` at its centre
and on its floor (its z less half its height), over the block's own footprint, and the spec is refurnished
(`migrate_furnish_recipes.migrate`): the library is a fixed point of furnish. A spec already carrying
`loading_pallet_stack_1` is not touched.

    python migrations/migrate_pallet_pile.py            # write specs/
    python migrations/migrate_pallet_pile.py --check    # report only
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import migrate_furnish_recipes  # noqa: E402
import presets  # noqa: E402


def main():
    check = "--check" in sys.argv
    done = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "specs", "*.json"))):
        if os.path.basename(p).startswith("lf_"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(d, dict):
            continue
        vols = d.get("volumes") or []
        if any(v.get("name") == "loading_pallet_stack_1" for v in vols):
            continue
        out, changed = [], False
        for v in vols:
            if v.get("name") != "loading_pallet_stack":
                out.append(v)
                continue
            floor_z = float(v["z"]) - float(v["size_z"]) / 2.0
            out.extend(presets.pallet_pile(float(v["x"]), float(v["y"]), floor_z, float(v["size_x"]),
                                           float(v["size_y"]), v.get("material", "wood")))
            changed = True
        if changed:
            done += 1
            if not check:
                d["volumes"] = out
                # the room is refurnished around the stacks: the library is a fixed point of furnish, and a pile
                # in six pieces with gaps is new input to it (`migrate_cooler_wall`'s reason)
                migrate_furnish_recipes.migrate(d)
                io.open(p, "w", encoding="utf-8", newline="\\n").write(json.dumps(d, indent=1) + "\\n")
    print("[pallet_pile] %d spec(s) given pallet stacks%s" % (done, " -- check only, nothing written" if check else ""))


if __name__ == "__main__":
    main()
'''
(R / "migrations" / "migrate_pallet_pile.py").write_text(MIG, encoding="utf-8", newline="\n")

SAFE = '''#!/usr/bin/env python3
"""
migrate_safe_paint.py  --  a stored safe is painted steel (0.267.0)
==================================================================
One-shot, idempotent migration over specs/*.json, lf_ specs excepted. Every volume whose material `_prop_material`
now names from its name differs from the one stored only by `metal` -> `metal_painted` -- the safes, the one row this
release moved -- is repainted, and the spec's palette declares `metal_painted` the way `_prop_material` does. No other
volume is touched.

    python migrations/migrate_safe_paint.py            # write specs/
    python migrations/migrate_safe_paint.py --check    # report only
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import level_design  # noqa: E402


def main():
    check = "--check" in sys.argv
    specs = vols = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "specs", "*.json"))):
        if os.path.basename(p).startswith("lf_"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(d, dict):
            continue
        n = 0
        for v in d.get("volumes") or []:
            if v.get("material") != "metal":
                continue
            if level_design._prop_material(dict(d), str(v.get("name", ""))) != "metal_painted":
                continue
            if "safe" not in str(v.get("name", "")).lower():
                continue
            v["material"] = "metal_painted"
            n += 1
        if n:
            level_design._declare_material(d, "metal_painted", level_design._PROP_ACOUSTIC["metal_painted"])
            specs += 1
            vols += n
            if not check:
                io.open(p, "w", encoding="utf-8", newline="\\n").write(json.dumps(d, indent=1) + "\\n")
    print("[safe_paint] %d spec(s), %d safe(s) painted%s" % (specs, vols, " -- check only, nothing written" if check else ""))


if __name__ == "__main__":
    main()
'''
(R / "migrations" / "migrate_safe_paint.py").write_text(SAFE, encoding="utf-8", newline="\n")

TEST = '''"""The loading dock's pile is pallet stacks, and a safe is painted steel (0.267.0). The walker, walking cold run
9386: of deli_a03's stockroom, "not sure what this large boring wood block is" (finding 9), and of pharmacy_a01's drop
safe, "looks like a brown box" (finding 3)."""
import glob
import json
import os

import level_design
import presets

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: Zoo's `pallet_stack` genome, 1.122.0: what a stack may measure and still build as one (width, depth, height)
PALLET_FITS = ((0.84, 1.8), (0.7, 1.5), (0.665, 1.425))


def _fits(v):
    dims = (float(v["size_x"]), float(v["size_y"]), float(v["size_z"]))
    return all(lo - 1e-9 <= x <= hi + 1e-9 for x, (lo, hi) in zip(dims, PALLET_FITS))


import pytest


@pytest.mark.parametrize("sx,sy,n", [(4.5, 2.5, 6), (4.0, 3.0, 6)])
def test_the_pile_is_stacks_that_each_fit_and_no_body_passes_between(sx, sy, n):
    pile = presets.pallet_pile(12.0, 10.0, 0.0, sx, sy)
    assert len(pile) == n and all(_fits(v) for v in pile), [(v["size_x"], v["size_y"], v["size_z"]) for v in pile]
    uw, ud = pile[0]["size_x"], pile[0]["size_y"]
    xs = sorted({v["x"] for v in pile}); ys = sorted({v["y"] for v in pile})
    assert min(b - a for a, b in zip(xs, xs[1:])) - uw < 0.35   # a body is 0.7 m across
    assert min(b - a for a, b in zip(ys, ys[1:])) - ud < 0.35
    x0 = min(v["x"] - v["size_x"] / 2 for v in pile); x1 = max(v["x"] + v["size_x"] / 2 for v in pile)
    y0 = min(v["y"] - v["size_y"] / 2 for v in pile); y1 = max(v["y"] + v["size_y"] / 2 for v in pile)
    assert abs(x1 - x0 - sx) < 0.01 and abs(y1 - y0 - sy) < 0.01


def test_no_library_spec_keeps_the_one_block():
    """FAILS ON 0.266.0: eight library specs carry one block (six at 4.5 x 2.5, two at 4.0 x 3.0)."""
    held = []
    for p in sorted(glob.glob(os.path.join(HERE, "specs", "*.json"))):
        if os.path.basename(p).startswith("lf_"):
            continue
        d = json.load(open(p, encoding="utf-8"))
        if not isinstance(d, dict):
            continue
        held += [os.path.basename(p) for v in d.get("volumes") or [] if v.get("name") == "loading_pallet_stack"]
    assert not held, held


def test_a_pile_counts_as_one_piece_of_what_its_room_holds():
    """FAILS ON 0.266.0 (no pile there). Counted as six, a deli's stockroom went without five pieces of its
    furniture when the library was refurnished around the stacks."""
    d = json.load(open(os.path.join(HERE, "specs", "deli_a01.json"), encoding="utf-8"))
    stacks = [v for v in d["volumes"] if str(v.get("name", "")).startswith("loading_pallet_stack_")]
    assert len(stacks) == 6, [v["name"] for v in stacks]
    s = stacks[0]
    room = [r for r in d["rooms"] if r["bounds"][0] <= s["x"] <= r["bounds"][2] and r["bounds"][1] <= s["y"] <= r["bounds"][3]
            and r.get("story", 0) == 0][0]
    with_pile = level_design._room_volume_count(d, room)
    d["volumes"] = [v for v in d["volumes"] if v not in stacks]
    assert with_pile == level_design._room_volume_count(d, room) + 1


def test_a_safe_is_painted_steel():
    """FAILS ON 0.266.0: `safe` fell to the `metal` row, the theme's street rust."""
    for name in ("safe_floor", "count_safe", "office_safe", "exec_safe"):
        assert level_design._prop_material({}, name) == "metal_painted", name
    assert level_design._prop_material({}, "tank_0") == "metal"


def test_no_stored_safe_wears_street_metal():
    """FAILS ON 0.266.0: the library's stored safes say `metal`."""
    rust = []
    for p in sorted(glob.glob(os.path.join(HERE, "specs", "*.json"))):
        if os.path.basename(p).startswith("lf_"):
            continue
        d = json.load(open(p, encoding="utf-8"))
        if not isinstance(d, dict):
            continue
        rust += [(os.path.basename(p), v["name"]) for v in d.get("volumes") or []
                 if "safe" in str(v.get("name", "")).lower() and v.get("material") == "metal"]
    assert not rust, (len(rust), rust[:5])
'''
(R / "tests" / "test_pallets_safes.py").write_text(TEST, encoding="utf-8", newline="\n")
print("presets.pallet_pile, safe -> metal_painted, migrations/migrate_pallet_pile.py, tests/test_pallets_safes.py")
