"""Lot 0.96.0: a standing piece keeps dressing out of its own footprint, not
a 3 m circle.

`site_surfaces.exclusions` has given every cover piece a `cover_edge`
exclusion of `site_cover.MARKER_CLEARANCE` (3 m) from its centre, "a cover
piece whose base is buried in scatter stops reading as cover". The rule
never ran in the pipeline: the surfaces job read the authored spec, which
carries no cover. Lot 0.95.0 made it read the site as drawn, and on cold run
9143 the rule met 164 pieces -- lamps, trees, benches, hydrants, bins, the
kerb lane's cars and the fields' -- and exclusion refusals went from 493 to
2,061: every kerb line a 3 m clear ring, the sidewalk under each lamp bare
in the frames where 9141's had litter.

The premise does not hold for dressing: a dressing piece is at most the
`low` band (0.30 m, `BANDS`) and the shortest cover piece is
`site_cover.MIN_COVER_HEIGHT` (1.3 m), so scatter cannot bury cover. What a
standing piece does need is no dressing INSIDE it. So a cover piece's
exclusion is now its own footprint (`size` in plan, as `assemble` stands
it; `lot.COVER` when it carries none), with no radius; the markers keep
`MARKER_CLEARANCE`.

Anchored edits (every anchor once; refuses on a miss): `site_surfaces.py`,
`tests/test_site_surfaces.py`. CHANGELOG and VERSION from
`lot_cover_footprint/CHANGELOG_0.96.0.md`.

    python patch_lot_cover_footprint.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_cover_footprint"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LOT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lot 0.95.0", v
    _edit(LOT / "site_surfaces.py", [
        ('    for i, c in enumerate(site_spec.get("cover", []) or []):\n'
         '        at = c.get("at")\n'
         '        if not at:\n'
         '            continue\n'
         '        out.append({\n'
         '            "tag": "cover_edge",\n'
         '            "declared_by": "lot",\n'
         '            "pos": [float(at[0]), float(at[1]), 0.0],\n'
         '            # site_cover\'s own clearance for a placed marker. A cover piece\n'
         '            # whose base is buried in scatter stops reading as cover, and\n'
         '            # cover that does not read is the same as cover that is not there.\n'
         '            "radius_m": site_cover.MARKER_CLEARANCE,\n'
         '        })\n',
         '    # A STANDING PIECE KEEPS DRESSING OUT OF ITSELF (0.96.0), its own\n'
         '    # footprint as `assemble` stands it, no radius. Until 0.95.0 this was\n'
         '    # a `MARKER_CLEARANCE` (3 m) circle from the centre, "a cover piece\n'
         '    # whose base is buried in scatter stops reading as cover" -- never live,\n'
         '    # because the surfaces job read the authored spec, which carries no\n'
         '    # cover. Live on cold run 9143 it met 164 lamps, trees, benches and\n'
         '    # parked cars and cleared every kerb line in a 3 m ring (exclusion\n'
         '    # refusals 493 -> 2,061). Scatter is at most the `low` band (0.30 m)\n'
         '    # and cover at least `site_cover.MIN_COVER_HEIGHT` (1.3 m), so it\n'
         '    # cannot bury one; what it must not do is stand inside one.\n'
         '    import lot as _lot\n'
         '    for i, c in enumerate(site_spec.get("cover", []) or []):\n'
         '        at = c.get("at")\n'
         '        if not at:\n'
         '            continue\n'
         '        sx, _sy, sz = c.get("size") or _lot.COVER\n'
         '        x, y = float(at[0]), float(at[1])\n'
         '        out.append({\n'
         '            "tag": "cover_edge",\n'
         '            "declared_by": "lot",\n'
         '            "aabb": _aabb((x - sx / 2.0, y - sz / 2.0, x + sx / 2.0, y + sz / 2.0),\n'
         '                          0.0, cap["unassisted_step_max_m"]),\n'
         '        })\n'),
    ])
    _edit(LOT / "tests" / "test_site_surfaces.py", [
        ('def test_exclusion_radius_is_site_covers_number():\n'
         '    xs, _ = SS.exclusions(spec())\n'
         '    assert {e["radius_m"] for e in xs} == {site_cover.MARKER_CLEARANCE}\n',
         'def test_exclusion_radius_is_site_covers_number():\n'
         '    """The markers\' circles; a cover piece is its footprint (0.96.0)."""\n'
         '    xs, _ = SS.exclusions(spec())\n'
         '    assert {e["radius_m"] for e in xs if "radius_m" in e} == {site_cover.MARKER_CLEARANCE}\n'
         '    assert all("aabb" in e and "radius_m" not in e for e in xs if e["tag"] == "cover_edge")\n'
         '\n'
         '\n'
         'def test_a_standing_piece_excludes_its_footprint_and_not_a_ring():\n'
         '    """A 4.3 x 1.75 m parked car at (10, 0): a point on its roof is\n'
         '    excluded, a point 0.5 m off its side is not -- the 3 m circle this\n'
         '    replaced reached 3.0 m from the centre, 2.1 m past the side. The\n'
         '    literals are the geometry."""\n'
         '    s = spec()\n'
         '    s["cover"] = [{"at": [10, 0], "size": [4.3, 1.45, 1.75]}]\n'
         '    xs, _ = SS.exclusions(s)\n'
         '    assert SS.excluded((10.0, 0.5), xs) == ["cover_edge"]\n'
         '    assert SS.excluded((10.0, 0.875 + 0.5), xs) == []\n'
         '    assert SS.excluded((12.0, 0.0), xs) == ["cover_edge"]\n'
         '    assert SS.excluded((12.15 + 0.1, 0.0), xs) == []\n'),
    ])
    ch = LOT / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    anchor = "## 0.95.0 - "
    assert s.count(anchor) == 1, "changelog anchor"
    ch.write_text(s.replace(anchor, (SRC / "CHANGELOG_0.96.0.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + anchor), encoding="utf-8", newline="\n")
    (LOT / "VERSION").write_text("Lot 0.96.0", encoding="utf-8", newline="\n")
    print("Lot 0.96.0 applied")


if __name__ == "__main__":
    main()
