"""Lot 0.97.3: no spawn inside an Empty, and no enemy behind an Empty row's
front line.

MEASURED. Laser Tag refused four candidates in cold runs 9164 to 9186 on
UNREACHABLE_SPAWN: seed_9061 in 9170 and 9174, seed_9205 in 9179 and 9186.
- In each one, Enemy_5 stood inside an Empty: e15, then e9. As a control, the
  other 17 enemies of 9186's three candidates stand in the open.
- `place_enemies` had pushed it off the route, 24.0 m in 9186, which is the
  run's own LOT_ENEMY_SPAWN_PUSHED figure. `outdoors()` called the point open
  because `footprints()` reads `site_spec["buildings"]`, and an Empty is a
  blocker.
- Run on 9186's seed_9205 inputs with Lot's collision reading, 0.97.2
  reproduces all six shipped enemies, Enemy_5 at (-17.70, -35.46) inside e9.
  On the declared-footprint fallback it puts Enemy_4 inside e13 as well.

WHY THE BAND AS WELL. Measured with `docs/findings/enemy_inside_an_empty/
place_variants.py`, with the collision reading Lot passes. With it, 0.97.2
reproduces every shipped enemy exactly, on six candidates.
- On 9186's seed_9205, keeping the Empties out is enough. Enemy_5 goes to
  1.33 m clear of the row's front line, pushed 19.5 m, and nothing else
  moves.
- On 9174's seed_9061 it is not. Kept out of the Empties alone, Enemy_4 and
  Enemy_5 land behind the front line at (35.14, -43.77) and (34.13, -48.01).
  That is the ground the row's fences shut off out to the plate's edge.
- `plan_fences` already models that band ("NEVER ENCLOSE A MARKER"). It
  leaves a row open rather than strand a marker in it, but it skips a marker
  inside a house, which is how 9186's fence went up around an enemy already
  shut in.
- With the band kept out as well, 9174's two enemies stand in open ground on
  the far side of the route, pushed 50.0 and 45.0 m. Those are large moves,
  and `LOT_ENEMY_SPAWN_PUSHED` reports them.
- The declared-footprint fallback, taken when the collision reading is
  incomplete, shows the same on 9186: there the Empties alone push Enemy_4
  through its house into the strip behind the row.

REFUTED, KEPT. The first draft of this docstring quoted that fallback run
(Enemy_4 behind the row, "pushed 18.5 and 12.5 m") as if it were Lot's
placement. It was measured without the collision reading, and on that site
the collision reading moves only Enemy_5.

ON THE RUNS IN FLIGHT: under the collision reading, 0.97.3 moves no enemy on
any candidate of cold runs 9187 and 9178.

WHAT CHANGES:
- `site_extent.blocker_rect`: one reader for a blocker's plan rect, used by
  the ground (`content`), the fences and the spawns. Three copies of the
  rule existed.
- `site_fences.shut_band` / `shut_bands`: the band `plan_fences` computed
  inline, as a function both the fences and the enemies ask.
- `site_spawns.solid_rects`: building footprints and blockers. The crew's
  spawns and the enemies ask `outdoors()` of it. The enemies also keep out
  of `shut_band_rects`.
- Cover planning (`plan_cover`) and the pylons still read `footprints()`
  alone. Whether an Empty should count as a sightline occluder there is a
  different question, with a visible effect, and is left open.

    python patch_lot_spawns_keep_out.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOT = ROOT / "lot"

EXTENT_POINT = '''def _point(value):
    if not value:
        return None
    try:
        return float(value[0]), float(value[1])
    except (TypeError, ValueError, IndexError):
        return None


def content(site_spec):
'''
EXTENT_POINT_NEW = '''def _point(value):
    if not value:
        return None
    try:
        return float(value[0]), float(value[1])
    except (TypeError, ValueError, IndexError):
        return None


def blocker_rect(bk):
    """A blocker's plan rect, or None when it has no position.

    A blocker's ``size_x``/``size_y`` are WORLD extents, 12 m each when
    unsaid, so no rotation applies. The ground (`content`), the fences
    (`site_fences`) and the spawns (`site_spawns`) all ask here; each used to
    spell the rule out itself (0.97.3).
    """
    at = _point(bk.get("at"))
    if at is None:
        return None
    return rect_of(at[0], at[1], float(bk.get("size_x", 12.0) or 12.0),
                   float(bk.get("size_y", 12.0) or 12.0))


def content(site_spec):
'''

EXTENT_CONTENT = '''    for i, bk in enumerate(site_spec.get("blockers") or []):
        at = _point(bk.get("at"))
        if at is None:
            continue
        sx = float(bk.get("size_x", 12.0) or 12.0)
        sy = float(bk.get("size_y", 12.0) or 12.0)
        rects.append((str(bk.get("id", f"blocker_{i}")),
                      rect_of(at[0], at[1], sx, sy)))
'''
EXTENT_CONTENT_NEW = '''    for i, bk in enumerate(site_spec.get("blockers") or []):
        rect = blocker_rect(bk)
        if rect is None:
            continue
        rects.append((str(bk.get("id", f"blocker_{i}")), rect))
'''

FENCES_EMPTIES = '''        at = bk.get("at")
        if not at:
            continue
        rect = site_extent.rect_of(float(at[0]), float(at[1]),
                                   float(bk.get("size_x", 12.0) or 12.0),
                                   float(bk.get("size_y", 12.0) or 12.0))
        rot = '''
FENCES_EMPTIES_NEW = '''        rect = site_extent.blocker_rect(bk)
        if rect is None:
            continue
        rot = '''

FENCES_STRIP = '''def _strip(axis, s0, s1, front, sign):
'''
FENCES_STRIP_NEW = '''def shut_band(axis, front, sign, ground):
    """The plan rect a row's fences shut off from the street: from the plate's
    edge behind the row up to its front line, across the plate's whole width
    along the row.

    `plan_fences` leaves a row open rather than strand a mission marker in
    it, and `site_spawns.place_enemies` never places an enemy in it (0.97.3).
    Both ask this one function: an enemy pushed into the strip behind a row
    is a spawn nobody can reach, and the fence check only saw markers
    outside the houses.
    """
    lo_i = 1 if axis == 0 else 0
    band = list(ground)
    if sign > 0:
        band[lo_i + 2] = front           # from the plate's edge up to the front
    else:
        band[lo_i] = front
    return tuple(band)


def shut_bands(site_spec, roads_list, ground) -> list:
    """`shut_band` for every Empty row on the site; none without a plate."""
    if not ground:
        return []
    out = []
    for axis, members in rows(site_spec):
        front, sign = front_line(axis, members, roads_list, ground)
        out.append(shut_band(axis, front, sign, ground))
    return out


def _strip(axis, s0, s1, front, sign):
'''

FENCES_KEEP = '''    for bk in site_spec.get("blockers") or []:
        at = bk.get("at")
        if at:
            keep.append(site_extent.rect_of(float(at[0]), float(at[1]),
                                            float(bk.get("size_x", 12.0) or 12.0),
                                            float(bk.get("size_y", 12.0) or 12.0)))
'''
FENCES_KEEP_NEW = '''    for bk in site_spec.get("blockers") or []:
        rect = site_extent.blocker_rect(bk)
        if rect:
            keep.append(rect)
'''

FENCES_BAND = '''        if ground:
            lo_i = 1 if axis == 0 else 0
            band = list(ground)
            if sign > 0:
                band[lo_i + 2] = front           # from the plate's edge up to the front
            else:
                band[lo_i] = front
            houses = [r for _e, r in members]
'''
FENCES_BAND_NEW = '''        if ground:
            band = shut_band(axis, front, sign, ground)
            houses = [r for _e, r in members]
'''

SPAWNS_FOOTPRINTS = '''def footprints(site_spec, margin: float = WALL_MARGIN) -> list:
    rects = []
    for bdef in site_spec.get("buildings", []) or []:
        rect = footprint_rect(bdef, margin)
        if rect:
            rects.append(rect)
    return rects
'''
SPAWNS_FOOTPRINTS_NEW = SPAWNS_FOOTPRINTS + '''

def blocker_rects(site_spec, margin: float = WALL_MARGIN) -> list:
    """Every blocker's rect (`site_extent.blocker_rect`), grown by ``margin``
    as a building's footprint is.

    A blocker is solid filler, and an Empty is a house with its doors shut
    (Level Factory 0.143.0): nothing inside either is reachable. `footprints`
    reads `buildings` only, and that admitted an enemy into an Empty on all
    four candidates Laser Tag refused on UNREACHABLE_SPAWN in cold runs 9164
    to 9186 (0.97.3).
    """
    import site_extent
    rects = []
    for bk in site_spec.get("blockers") or []:
        rect = site_extent.blocker_rect(bk)
        if rect:
            rects.append(site_extent.grow(rect, margin) if margin else rect)
    return rects


def solid_rects(site_spec, margin: float = WALL_MARGIN) -> list:
    """What a spawn is kept out of: the buildings' footprints and the
    blockers. The crew's spawns and the enemies ask `outdoors()` of this."""
    return footprints(site_spec, margin) + blocker_rects(site_spec, margin)


def shut_band_rects(site_spec, margin: float = WALL_MARGIN) -> list:
    """The ground behind every Empty row's front line, grown by ``margin``:
    what the row's fences shut off from the street, by the function
    `plan_fences` asks (`site_fences.shut_bands`)."""
    import site_extent
    import site_fences
    import site_streets
    ground = site_extent.resolve(site_spec).rect
    return [site_extent.grow(b, margin) if margin else b
            for b in site_fences.shut_bands(site_spec, site_streets.roads(site_spec), ground)]
'''

SPAWNS_CREW = '''    ground = ground_rect(site_spec)
    rects = footprints(site_spec)
    z = base[2] if len(base) > 2 else GROUND_Z
'''
SPAWNS_CREW_NEW = '''    ground = ground_rect(site_spec)
    rects = solid_rects(site_spec)
    z = base[2] if len(base) > 2 else GROUND_Z
'''

SPAWNS_CLEAR = '''    rects = footprints(site_spec)
    ground = ground_rect(site_spec)
    if ground is None and not rects:
        # Nothing known to place against. `place_enemies` says the same of the
'''
SPAWNS_CLEAR_NEW = '''    rects = solid_rects(site_spec)
    ground = ground_rect(site_spec)
    if ground is None and not rects:
        # Nothing known to place against. `place_enemies` says the same of the
'''

SPAWNS_ENEMIES = '''    rects = footprints(site_spec)
    ground = ground_rect(site_spec)
    spawn = route[0]
'''
SPAWNS_ENEMIES_NEW = '''    # NOT INSIDE AN EMPTY, NOT BEHIND ITS ROW (0.97.3). Every candidate Laser
    # Tag refused on UNREACHABLE_SPAWN in cold runs 9164 to 9186 -- four --
    # was an enemy pushed off the route into an Empty, which `footprints`
    # cannot see: 9186's seed_9205 Enemy_5, 24.0 m into e9. Keeping the
    # Empties out alone put 9174's seed_9061 Enemy_4 and Enemy_5 behind the
    # row's front line, on ground the row's fences shut off, so the band the
    # fences are planned against is kept out too.
    rects = solid_rects(site_spec) + shut_band_rects(site_spec)
    ground = ground_rect(site_spec)
    spawn = route[0]
'''

EDITS = {
    "site_extent.py": [(EXTENT_POINT, EXTENT_POINT_NEW), (EXTENT_CONTENT, EXTENT_CONTENT_NEW)],
    "site_fences.py": [(FENCES_EMPTIES, FENCES_EMPTIES_NEW), (FENCES_STRIP, FENCES_STRIP_NEW),
                       (FENCES_KEEP, FENCES_KEEP_NEW), (FENCES_BAND, FENCES_BAND_NEW)],
    "site_spawns.py": [(SPAWNS_FOOTPRINTS, SPAWNS_FOOTPRINTS_NEW), (SPAWNS_CREW, SPAWNS_CREW_NEW),
                       (SPAWNS_CLEAR, SPAWNS_CLEAR_NEW), (SPAWNS_ENEMIES, SPAWNS_ENEMIES_NEW)],
}


def main():
    staged = {}
    for name, edits in EDITS.items():
        data = (LOT / name).read_bytes()
        assert b"\r\n" not in data, name + " is LF; CRLF means it changed under us"
        text = data.decode("utf-8")
        for old, new in edits:
            n = text.count(old)
            assert n == 1, (name, "anchor matched %d times" % n, old[:70])
            text = text.replace(old, new)
        staged[name] = text
    for name, text in staged.items():
        (LOT / name).write_bytes(text.encode("utf-8"))
        print("patched", name)


if __name__ == "__main__":
    main()
