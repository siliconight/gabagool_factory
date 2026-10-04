"""Level Factory 0.135.0: one building line a street.

Step 3 of `docs/proposals/LAND_USE_DESIGN.md`. `packages/pipeline/
street_line.py` and `tests/unit/test_street_line.py` copied from
`lf_street_line/`. Anchored edits (every anchor once; refuses on a miss):
`site_variation.py` (`site_placements` takes `extents` and stands a row's
street edges on one line; `ground_size` takes the placed `ys`),
`road_grammar.py` (`_south_face` reads a building's `street_reach`),
`apps/cli/commands/__init__.py` (both placement paths measure the extents,
carry `street_reach` onto the spec, size the plate from the placed row).
CHANGELOG and VERSION from `lf_street_line/CHANGELOG_0.135.0.md`.

    python patch_lf_street_line.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LF = HERE.parent / "level_factory"
SRC = HERE / "lf_street_line"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.134.0", v
    assert not (LF / "packages" / "pipeline" / "street_line.py").exists(), "already applied"
    sv = LF / "packages" / "pipeline" / "site_variation.py"
    _edit(sv, [
        ('def site_placements(seed: int, count: int, *, spacing: int = 45,\n'
         '                    footprints=None, shape=None, fronts=None) -> dict:\n',
         'def site_placements(seed: int, count: int, *, spacing: int = 45,\n'
         '                    footprints=None, shape=None, fronts=None,\n'
         '                    extents=None) -> dict:\n'),
        ('    # Roles: which building you start at, which one holds the objective, which\n',
         '    # ONE BUILDING LINE A STREET (0.135.0): on a row, every building\'s\n'
         '    # street edge -- the furthest its solids reach toward the through\n'
         '    # road once turned (`street_line.south_reach`) -- stands on one line,\n'
         '    # in place of the across draw above, which is still made so no other\n'
         '    # number a seed gives moves. A shape that turns keeps its stagger: its\n'
         '    # arms front different streets, and one line is not one street there.\n'
         '    if extents is not None and shape_of(shape) == "row":\n'
         '        from . import street_line\n'
         '        reaches = [street_line.south_reach(extents[i] if i < len(extents) else None, b["rot"])\n'
         '                   for i, b in enumerate(buildings)]\n'
         '        for b, y, r in zip(buildings, street_line.line_ys(reaches), reaches):\n'
         '            if y is not None:\n'
         '                b["at"][1] = y\n'
         '                b["street_reach"] = r\n'
         '\n'
         '    # Roles: which building you start at, which one holds the objective, which\n'),
        ('def ground_size(count: int, *, spacing: int = 45,\n'
         '                footprint: tuple[float, float] | None = None,\n'
         '                footprints=None, shape=None) -> tuple[int, int]:\n',
         'def ground_size(count: int, *, spacing: int = 45,\n'
         '                footprint: tuple[float, float] | None = None,\n'
         '                footprints=None, shape=None, ys=None) -> tuple[int, int]:\n'),
        ('        half_y = max(abs(o[1]) + _slack(1) + r for o, r in zip(offs, reaches))\n'
         '    else:\n'
         '        reach = _reach(footprint)\n'
         '        half_x = (count - 1) * spacing / 2.0 + slack + reach\n'
         '        half_y = max(abs(v) for v in _ACROSS) + reach\n',
         '        half_y = max(abs(o[1]) + _slack(1) + r for o, r in zip(offs, reaches))\n'
         '        if ys is not None:\n'
         '            # a row stood on one street line (0.135.0): its origins are\n'
         '            # where they are, not anywhere the stagger could have put them\n'
         '            half_y = max(abs(float(y)) + r for y, r in zip(ys, reaches))\n'
         '    else:\n'
         '        reach = _reach(footprint)\n'
         '        half_x = (count - 1) * spacing / 2.0 + slack + reach\n'
         '        half_y = max(abs(v) for v in _ACROSS) + reach\n'
         '        if ys is not None:\n'
         '            half_y = max(abs(float(y)) for y in ys) + reach\n'),
    ])
    _edit(LF / "packages" / "pipeline" / "road_grammar.py", [
        ('        x = float(b["at"][0])\n'
         '        face = float(b["at"][1]) - float(ext_y) / 2.0\n',
         '        x = float(b["at"][0])\n'
         '        face = float(b["at"][1]) - float(ext_y) / 2.0\n'
         '        # its real street edge when it was stood on the line (0.135.0):\n'
         '        # a canopy reaches further than half a symmetric footprint says,\n'
         '        # and an off-centre shell less\n'
         '        if b.get("street_reach") is not None:\n'
         '            face = float(b["at"][1]) - float(b["street_reach"])\n'),
    ])
    cmds = LF / "apps" / "cli" / "commands" / "__init__.py"
    _edit(cmds, [
        ('        placed = site_placements(seed, len(lot), footprints=footprints,\n'
         '                                 shape=model.site_shape,\n'
         '                                 fronts=[_fd.facing_yaw(w) for w, _r in front_of])\n',
         '        # each building\'s street edge, per side (0.135.0)\n'
         '        from packages.pipeline import street_line as _sl\n'
         '        placed = site_placements(seed, len(lot), footprints=footprints,\n'
         '                                 shape=model.site_shape,\n'
         '                                 fronts=[_fd.facing_yaw(w) for w, _r in front_of],\n'
         '                                 extents=[_sl.shell_extents(e["glb"]) for e in lot])\n'),
        ('             "front": {"wall": fw[0], "reason": fw[1]}}\n'
         '            for i, (e, p, fw) in enumerate(zip(lot, placed["buildings"], front_of))\n'
         '        ]\n'
         '        span_x, span_y = ground_size(len(lot), footprints=footprints,\n'
         '                                     shape=model.site_shape)\n',
         '             "front": {"wall": fw[0], "reason": fw[1]},\n'
         '             **({"street_reach": p["street_reach"]} if "street_reach" in p else {})}\n'
         '            for i, (e, p, fw) in enumerate(zip(lot, placed["buildings"], front_of))\n'
         '        ]\n'
         '        span_x, span_y = ground_size(\n'
         '            len(lot), footprints=footprints, shape=model.site_shape,\n'
         '            ys=([p["at"][1] for p in placed["buildings"]]\n'
         '                if any("street_reach" in p for p in placed["buildings"]) else None))\n'),
        ('        placed = site_placements(seed, count, spacing=spacing,\n'
         '                                 fronts=[_fd.facing_yaw(shell_front[0])] * count)\n',
         '        from packages.pipeline import street_line as _sl\n'
         '        placed = site_placements(seed, count, spacing=spacing,\n'
         '                                 fronts=[_fd.facing_yaw(shell_front[0])] * count,\n'
         '                                 extents=[_sl.shell_extents(glb)] * count)\n'),
        ('            {"id": f"b{i}", **source, "gameplay": gameplay,\n'
         '             "at": p["at"], "rot": p["rot"]}\n'
         '            for i, p in enumerate(placed["buildings"])\n'
         '        ]\n',
         '            {"id": f"b{i}", **source, "gameplay": gameplay,\n'
         '             "at": p["at"], "rot": p["rot"],\n'
         '             **({"street_reach": p["street_reach"]} if "street_reach" in p else {})}\n'
         '            for i, p in enumerate(placed["buildings"])\n'
         '        ]\n'),
        ('        span_x, span_y = ground_size(count, spacing=spacing, footprint=footprint)\n',
         '        span_x, span_y = ground_size(\n'
         '            count, spacing=spacing, footprint=footprint,\n'
         '            ys=([p["at"][1] for p in placed["buildings"]]\n'
         '                if any("street_reach" in p for p in placed["buildings"]) else None))\n'),
    ])
    shutil.copyfile(SRC / "street_line.py", LF / "packages" / "pipeline" / "street_line.py")
    shutil.copyfile(SRC / "test_street_line.py", LF / "tests" / "unit" / "test_street_line.py")
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    assert s.startswith("## [0.134.0]"), "changelog head"
    ch.write_text((SRC / "CHANGELOG_0.135.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.135.0", encoding="utf-8", newline="\n")
    print("Level Factory 0.135.0 applied")


if __name__ == "__main__":
    main()
