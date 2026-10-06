"""Lot 0.97.1: a fence does not grow the plate it marks the edge of.

Cold run 9183, measured on its own scenes:
- The greybox `site.tscn` (lot_assemble, seed_9181) and the themed one both
  stand `perim_S` at 254 m.
- 9182, the same candidate without fences, stands it at 246 m.

THE MECHANISM (`site_extent.required_rect`). The ground carries the union of
everything on the site grown by `CLEARANCE` (4 m), and every cover piece is
in that union.
- `site_fences` runs a row's end fences OUT TO the plate's edge by design.
- So when the scene writer re-resolved the ground with the fences standing,
  it grew the plate 4 m past each end run.
- Each end fence then stopped 4 m short of the perimeter wall: a walk-around
  at both ends of the row, which is what the end runs exist to close.

The same growth widened the ground boxes, which is where 22 of the run's +32
mesh instances came from. The 9183 notes put them down to tiling first; that
account was wrong, and the notes keep the retraction.

A fence marks the playable edge; it is not content the ground has to carry
clearance around. `content` leaves out cover that `site_fences` placed.

    python patch_lot_fence_plate.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOT = ROOT / "lot"

EDITS = {
    LOT / "site_extent.py": [
        ('''    for i, cv in enumerate(site_spec.get("cover") or []):
        at = _point(cv.get("at"))
        if at is None:
            continue
        sz = cv.get("size") or (1.0, 1.0, 1.0)
''',
         '''    for i, cv in enumerate(site_spec.get("cover") or []):
        at = _point(cv.get("at"))
        if at is None:
            continue
        # A FENCE IS THE EDGE, NOT CONTENT (0.97.1). `site_fences` runs a
        # row's end fences out to the plate's edge by design; counted here,
        # they grew the plate by CLEARANCE past themselves and each stopped
        # 4 m short of the new perimeter (cold run 9183: 246 -> 254 m).
        if cv.get("source") == "site_fences":
            continue
        sz = cv.get("size") or (1.0, 1.0, 1.0)
'''),
    ],
    LOT / "tests/test_site_fences.py": [
        ('''def test_a_row_facing_x_runs_along_y():
''',
         '''def test_the_fence_does_not_grow_the_plate_it_marks():
    """0.97.1. Cold run 9183's plate went 246 -> 254 m: the end runs reach
    the plate's edge, and counted as content they asked for CLEARANCE past
    themselves, so each ended 4 m short of the moved perimeter."""
    import site_extent
    site = {"name": "t", "buildings": [], "roads": [_EW_ROAD],
            "blockers": [_empty("e0", -10, -4), _empty("e1", -1, 5)],
            "ground": {"size_x": 60, "size_y": 100}}
    before = site_extent.resolve(site).rect
    fences = SF.plan_fences(site, site_streets.roads(site), before, BODY)
    assert any("end" in f["breaks"] for f in fences)
    site["cover"] = fences
    assert site_extent.resolve(site).rect == before
    # and the end runs still reach it, within the centimetre a run's length
    # is quantised to
    xs = [f["at"][0] + s * f["dims"][0] / 2 for f in fences for s in (-1, 1)]
    assert abs(min(xs) - before[0]) < SF.QUANTUM and abs(max(xs) - before[2]) < SF.QUANTUM


def test_a_row_facing_x_runs_along_y():
'''),
    ],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
