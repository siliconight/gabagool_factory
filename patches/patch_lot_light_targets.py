"""Lot 0.99.1: a stage light's aim moves with its club (roadmap 207).

`merge_lights` carried a light anchor's `pos` into site space and copied
`target` -- the stage light's aim -- verbatim, so a club off the site's origin
aimed its stages 73-74 m away and Lux refused both (`LUX_CLUB_REFUSED`, cold
runs 9060, 9167, 9197).

Anchored edits (every anchor once; refuses on a miss): `lot.py` --
`_LIGHT_POINTS` and `_LIGHT_NOT_POINTS`, `_refuse_unknown_light_points`, and
`merge_lights` placing every listed point. New files from
`lot_light_targets/`: `tests/test_light_targets.py` and its fixture,
`tests/fixtures/strip_club_a01.lights.json` (Deli Counter's build, verbatim).
CHANGELOG and VERSION from `lot_light_targets/CHANGELOG_0.99.1.md`.

    python patch_lot_light_targets.py
    LOT_ROOT=<copy> python patch_lot_light_targets.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_light_targets"

EDITS = {
    "lot.py": [
        ('def merge_lights(site_spec, base_dir):\n',
         '#: Every POINT a light anchor carries, each moved into site space with its\n'
         '#: building (0.99.1, roadmap 207). `target` is the stage light\'s aim, Deli\n'
         '#: Counter\'s club rig. Copied verbatim it stayed in the building\'s frame,\n'
         '#: so a club standing off the site\'s origin aimed its two stages 73-74 m\n'
         '#: away, past the 12 m Lux clamps a stage light\'s range to, and Lux refused\n'
         '#: both (`LUX_CLUB_REFUSED`: cold runs 9060, 9167, 9197). Listed rather\n'
         '#: than discovered, as `_LADDER_POINTS_3` is.\n'
         '_LIGHT_POINTS = ("pos", "target")\n'
         '#: Numeric triples a light anchor carries that are NOT points: `size` is an\n'
         '#: extent in the light\'s own frame, which Lux turns with `rot_y`; a colour\n'
         '#: is never a point, whatever its shape.\n'
         '_LIGHT_NOT_POINTS = ("size", "color")\n'
         '\n'
         '\n'
         'def _refuse_unknown_light_points(anchor, bid, ref):\n'
         '    """Refuse a light anchor carrying a numeric triple this module has not\n'
         '    classed as a point or a non-point: a field added upstream must not ride\n'
         '    into site space in the building\'s frame unnoticed -- the rule\n'
         '    `_ladder_to_site` keeps, and the defect `target` was (0.99.1)."""\n'
         '    for k, v in anchor.items():\n'
         '        if k in _LIGHT_POINTS or k in _LIGHT_NOT_POINTS:\n'
         '            continue\n'
         '        if (isinstance(v, (list, tuple)) and len(v) == 3\n'
         '                and all(isinstance(c, (int, float)) and not isinstance(c, bool)\n'
         '                        for c in v)):\n'
         '            raise ValueError(\n'
         '                f"{ref}: light anchor {anchor.get(\'id\', \'?\')!r} of {bid} carries a "\n'
         '                f"numeric triple {k!r} that merge_lights has not classed as a point "\n'
         '                f"(_LIGHT_POINTS, placed) or not (_LIGHT_NOT_POINTS, kept); refusing "\n'
         '                f"rather than shipping it in the building\'s frame")\n'
         '\n'
         '\n'
         'def merge_lights(site_spec, base_dir):\n'),
        ('            wa["building"] = bid\n'
         '            x, y, z = a.get("pos", [0.0, 0.0, 0.0])\n'
         '            wx, wy, wz = _place_point(x, y, z, placement)\n'
         '            wa["pos"] = [round(wx, 4), round(wy, 4), round(wz, 4)]\n',
         '            wa["building"] = bid\n'
         '            # EVERY POINT, NOT ONLY `pos` (0.99.1, roadmap 207): a stage\n'
         '            # light\'s `target` rode in the copy in the building\'s frame.\n'
         '            _refuse_unknown_light_points(a, bid, ref)\n'
         '            for key in _LIGHT_POINTS:\n'
         '                if key != "pos" and key not in a:\n'
         '                    continue\n'
         '                x, y, z = a.get(key, [0.0, 0.0, 0.0])\n'
         '                wx, wy, wz = _place_point(x, y, z, placement)\n'
         '                wa[key] = [round(wx, 4), round(wy, 4), round(wz, 4)]\n'),
    ],
}

NEW = {
    pathlib.Path("tests") / "test_light_targets.py": "test_light_targets.py",
    pathlib.Path("tests") / "fixtures" / "strip_club_a01.lights.json": "strip_club_a01.lights.json",
}


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.99.0", v.read_bytes()
    for rel in NEW:
        assert not (LOT / rel).exists(), ("already applied", rel)
    staged = {}
    for name, edits in EDITS.items():
        p = LOT / name
        d = p.read_bytes()
        crlf = b"\r\n" in d
        assert not (crlf and d.replace(b"\r\n", b"").count(b"\n")), (name, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            n = t.count(old)
            assert n == 1, (name, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    entry = (SRC / "CHANGELOG_0.99.1.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.99.0 - where responders arrive"), text[:60]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    for rel, src in NEW.items():
        (LOT / rel).parent.mkdir(parents=True, exist_ok=True)
        (LOT / rel).write_bytes((SRC / src).read_bytes())
    cl.write_bytes((entry + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.99.1")
    print("Lot 0.99.0 -> 0.99.1")


if __name__ == "__main__":
    main()
