"""Patina 0.25.0: gutters at the eave, and downspouts to the ground.

The walker, 2026-10-04: "also we need rain gutters". Two things, measured on
cold run 9151's own orders:
  * since Deli Counter 0.177.0 made parapets into wall slots, the "top storey"
    `roofline_slots` picks is the parapet: `gs_empty_rowhome_f`'s gutters went
    from z 8.92 under the roof (9148) to 9.92 on `parapet_*` slots, the top of
    the parapet, and the freight terminal's to its parapet top at 6.92;
  * nothing draws a downspout, the pipe that makes a gutter read from the
    street.
See `patina_downspouts/CHANGELOG_0.25.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  patina/framing.py   `roofline_slots` skips parapets; `downspout_orders`
  patina/openings.py  a downspout's cross-axis, and its vertical run
  patina/cli.py       `--gutters` brings the downspouts
  patina/version.py   0.25.0
Copies the test; CHANGELOG and VERSION.

    python patch_patina_downspouts.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PA = HERE.parent / "patina"
SRC = HERE / "patina_downspouts"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


ROOF_OLD = '''    Slots with no ``story`` fall back to every wall slot -- an older manifest
    should keep its old output rather than silently lose its gutters.
    """
    walls = wall_slots(manifest)
'''
ROOF_NEW = '''    Slots with no ``story`` fall back to every wall slot -- an older manifest
    should keep its old output rather than silently lose its gutters.

    A PARAPET IS NOT A ROOFLINE (0.25.0). Deli Counter 0.177.0 made each
    parapet tile a wall slot on the storey above the top floor, so "the top
    storey" became the parapet and the gutters went up onto it: cold run 9151
    put `gs_empty_rowhome_f`'s at z 9.92 on `parapet_*` slots, the top of the
    parapet, where 9148 had them at 8.92 under the roof. A gutter hangs at
    the eave, which is the top of the highest STOREY wall, so parapets are
    left out before the top storey is found.
    """
    walls = [s for s in wall_slots(manifest) if not _is_parapet(s)]
'''

DOWN_ANCHOR = '''def pilaster_orders(manifest: SlotManifest, regions: list, *, seed: int,
'''
DOWN_NEW = '''def _is_parapet(slot) -> bool:
    """A parapet tile's slot (Deli Counter >= 0.177.0): `parapet_<side>...`."""
    return str(slot.slot_id).startswith("parapet_")


#: A DOWNSPOUT A FACE, AND ONE MORE FOR EVERY TWELVE METRES OF GUTTER
#: (0.25.0). The rule of thumb is one downspout per 30 to 40 feet of gutter --
#: 9 to 12 m -- and twelve is its long end. Chosen from that, not derived: no
#: roof area and no rainfall are modelled.
DOWNSPOUT_EVERY = 12.0
#: The pipe's centre, in from the end of its face, metres -- at the corner or
#: the party line, where the walker's South Philly row has it.
DOWNSPOUT_INSET = 0.15
#: The gutter's height on the wall, mirrored from Zoo's
#: `zoo_keeper/core/dressing.py` `_COVER["gutter_run"]["cross"]`, which
#: `openings._ZOO_CROSS` mirrors too: the pipe tops out at the gutter's
#: underside.
GUTTER_CROSS = 0.14
#: Opening slots: a face carrying one of these is a face somebody looks at.
_FACE_ROLES = ("window", "doorway", "breach")


def _side(frame) -> tuple:
    """A face's key: its outward normal, rounded to whole units -- exact for
    the axis-aligned shells Deli Counter emits. `facing` is not used: it
    points into the room a wall bounds (see `test_framing`)."""
    out = frame[3]
    return (round(out[0]), round(out[1]))


def downspout_orders(manifest: SlotManifest, regions: list, *, seed: int,
                     keep_out: list | None = None, drop: float = 0.08) -> list[dict]:
    """Downspouts from the gutter to the ground (0.25.0).

    The walker, 2026-10-04: "also we need rain gutters". A gutter reads from
    the street by the pipe that carries its water down; nothing drew one.

    * ON THE FACES SOMEBODY SEES: every roofline face with a window, door or
      breach on any storey. A blank side wall -- an Empty's party wall -- gets
      none.
    * ONE A FACE, ONE MORE PER `DOWNSPOUT_EVERY` OF GUTTER: a short face takes
      a seeded end; a longer one both ends, and the rest spread between them.
    * CLEAR OF THE OPENINGS by the keep-out Patina already enforces
      (`openings.keep_out_boxes`): a blocked end gives way to the other, an
      interior pipe slides to the nearest clear module seam, and a pipe with
      nowhere clear is left out. The placement and the filter are one test.
    * FROM THE GUTTER'S UNDERSIDE TO THE GROUND: the top storey's roofline
      less `drop` and half `GUTTER_CROSS`, down to the floor of the face's
      storey 0. ``size`` is the length and ``pos`` its middle, as a conduit's.
    """
    from . import openings as _openings
    uv = _uv(regions, "flashing")
    center = footprint_center(manifest)
    thick_m = modal_thickness(manifest)
    top = roofline_slots(manifest)
    if not top:
        return []
    faced = set()
    for s in manifest.slots:
        if s.role in _FACE_ROLES and str(s.slot_id).startswith("ext_"):
            faced.add(_side(wall_frame(s, center, thick_m)))
    ground = {}
    for s in wall_slots(manifest):
        if _is_parapet(s):
            continue
        key = _side(wall_frame(s, center, thick_m))
        z = _base_z(s)
        if s.story is not None and int(s.story) == 0:
            ground[key] = min(ground.get(key, z), z)
    runs = {}
    for s in top:
        frame = wall_frame(s, center, thick_m)
        runs.setdefault(_side(frame), []).append((s, frame))
    orders = []
    for key in sorted(runs):
        if key not in faced:
            continue
        items = runs[key]

        def span(item):
            s, (run, _t, along, _o) = item
            a = float(s.translation[0]) * along[0] + float(s.translation[1]) * along[1]
            return a - run / 2.0, a + run / 2.0, a

        lo, hi = min(span(it)[0] for it in items), max(span(it)[1] for it in items)
        s0, _f0 = items[0]
        top_z = _base_z(s0) + s0.size()[2] - drop - GUTTER_CROSS / 2.0
        base = ground.get(key, min(_base_z(s) for s, _f in items))
        if top_z - base <= 0.5:
            continue
        mid_z = (top_z + base) / 2.0
        rng = rng_for(seed, "downspout", f"{key[0]}_{key[1]}")

        def order_at(a):
            """The order whose pipe stands at along-coordinate ``a``."""
            for it in items:
                a0, a1, ac = span(it)
                if a0 - 1e-6 <= a <= a1 + 1e-6:
                    s, frame = it
                    pos, n = _face(s, a - ac, mid_z, frame)
                    return {"anchor_kind": "downspout", "cover": "downspout",
                            "collision": "none", "trim_piece": "flashing",
                            "uv_region": uv, "slot_id": s.slot_id,
                            "pos": pos, "normal": n,
                            "size": round(top_z - base, 3),
                            "seed_offset": int(rng.integers(0, 1_000_000))}
            return None

        def clear(o):
            return o is not None and (not keep_out or not _openings.hits(o, keep_out))

        ends = [lo + DOWNSPOUT_INSET, hi - DOWNSPOUT_INSET]
        if int(rng.integers(0, 2)):
            ends.reverse()
        n = max(1, math.ceil((hi - lo) / DOWNSPOUT_EVERY - 1e-9))
        picked, taken = [], []
        if n == 1:
            for a in ends:
                o = order_at(a)
                if clear(o):
                    picked.append(o)
                    break
        else:
            for a in sorted(ends):
                o = order_at(a)
                if clear(o):
                    picked.append(o)
                    taken.append(a)
            # the rest stand at module seams -- where gutter sections join --
            # nearest an even spacing, each sliding to the next seam out when
            # an opening is in its way
            seams = sorted({round(e, 6) for it in items for e in span(it)[:2]
                            if lo + 1e-6 < e < hi - 1e-6})
            for k in range(1, n - 1):
                target = lo + (hi - lo) * k / (n - 1)
                for a in sorted(seams, key=lambda e: abs(e - target)):
                    o = order_at(a)
                    if clear(o) and all(abs(a - t) > 1e-6 for t in taken):
                        picked.append(o)
                        taken.append(a)
                        break
        orders += picked
    return orders


def pilaster_orders(manifest: SlotManifest, regions: list, *, seed: int,
'''

CROSS_OLD = '''    "pilaster": 0.12, "frame": 0.12,
}
'''
CROSS_NEW = '''    "pilaster": 0.12, "frame": 0.12,
    # 0.25.0: a downspout is a 3-inch pipe, and runs up the wall like a conduit
    "downspout": 0.076,
}
'''

AXIS_OLD = '''    if order.get("cover") == "conduit_run":
        return (0.0, 0.0, 1.0)
'''
AXIS_NEW = '''    if order.get("cover") in ("conduit_run", "downspout"):
        return (0.0, 0.0, 1.0)
'''

CLI_OLD = '''                if args.gutters:
                    panels += framing.gutter_orders(slot_manifest, regions,
                                                    seed=args.seed)
'''
CLI_NEW = '''                if args.gutters:
                    panels += framing.gutter_orders(slot_manifest, regions,
                                                    seed=args.seed)
                    # 0.25.0: a gutter brings its downspouts, placed clear of
                    # the openings by the same keep-out the filter enforces
                    panels += framing.downspout_orders(
                        slot_manifest, regions, seed=args.seed,
                        keep_out=openings.keep_out_boxes(slot_manifest))
'''

HELP_OLD = '''                   help="with --dressing + slots.json: a gutter_run per "
                        "exterior wall slot, just under the roofline")
'''
HELP_NEW = '''                   help="with --dressing + slots.json: a gutter_run per "
                        "top-storey exterior wall slot, just under the "
                        "roofline, and downspouts down every face with an "
                        "opening (0.25.0)")
'''

VER_OLD = '__version__ = "0.24.0"\n'
VER_NEW = '__version__ = "0.25.0"\n'


def main():
    assert (PA / "VERSION").read_text(encoding="utf-8").strip() == "Patina 0.24.0"
    _edit(PA / "patina" / "framing.py", [(ROOF_OLD, ROOF_NEW), (DOWN_ANCHOR, DOWN_NEW)])
    _edit(PA / "patina" / "openings.py", [(CROSS_OLD, CROSS_NEW), (AXIS_OLD, AXIS_NEW)])
    _edit(PA / "patina" / "cli.py", [(CLI_OLD, CLI_NEW), (HELP_OLD, HELP_NEW)])
    _edit(PA / "patina" / "version.py", [(VER_OLD, VER_NEW)])
    shutil.copyfile(SRC / "test_downspouts.py", PA / "tests" / "test_downspouts.py")
    ch = PA / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    head = "## [0.24.0]"
    assert s.count(head) == 1
    ch.write_text(s.replace(head, (SRC / "CHANGELOG_0.25.0.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + head), encoding="utf-8", newline="\n")
    (PA / "VERSION").write_text("Patina 0.25.0", encoding="utf-8", newline="\n")
    print("applied Patina 0.25.0")


if __name__ == "__main__":
    main()
