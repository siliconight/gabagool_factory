"""Lot 0.95.0, second half: the dressing reads the site as it was DRAWN.

Applied on top of `patch_lot_field_zone.py` (the same release). Found while
wiring that one: Level Factory's surfaces job runs `site_surfaces.py` on the
AUTHORED spec (`temp/<mission>/candidate_seed_<n>/site.json`), while
`assemble` draws something else -- walks re-routed to real doors and some
not drawn at all (0.88.0-0.91.0), the pads (0.93.0), the fields and their
driveways (0.94.0). Measured on cold run 9142's shipped site: the dressing
was told of 6 walk slabs, at the old centre-to-centre stations
(`path_0` at (30.5, 7.5), a walk between two buildings that 0.91.0 stopped
drawing); the scene holds 9, none of them at those stations; and no pad or
field reached `tops` or `zones`. So 54 low-density "walk" zones dressed
ground that is not a walk, the real walks took open ground's scatter, and
the fields could not be zoned at all.

`assemble` now writes the spec it drew, `<name>.site.drawn.json`, beside
the scene; `site_surfaces.py`'s CLI, given that out dir as `--base-dir`
(which Level Factory already passes), reads it in place of the spec it was
handed and says so (`LOT_SURFACE_SPEC_AS_DRAWN`, info). An out dir with no
drawn spec -- an older assembly, a probe -- is read exactly as before.

Anchored edits (every anchor once; refuses on a miss): `lot.py`
(`assemble` writes the drawn spec), `site_surfaces.py` (the CLI reads it),
`tests/test_site_surfaces_field_zone.py` (two tests appended).

    python patch_lot_drawn_spec.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_field_zone"


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
    assert "LOT_SURFACE_SPEC_AS_DRAWN" not in (LOT / "site_surfaces.py").read_text(encoding="utf-8"), \
        "already applied"
    _edit(LOT / "lot.py", [
        ('    tscn_out = os.path.join(out_dir, f"{site_spec[\'name\']}.tscn")\n'
         '    write_godot_scene(site_spec, merged, tscn_out, preview=preview,\n'
         '                      portable=portable, self_flooring=self_flooring)\n',
         '    tscn_out = os.path.join(out_dir, f"{site_spec[\'name\']}.tscn")\n'
         '    write_godot_scene(site_spec, merged, tscn_out, preview=preview,\n'
         '                      portable=portable, self_flooring=self_flooring)\n'
         '    # THE SPEC AS DRAWN (0.95.0): walks resolved to their doors, the pads,\n'
         '    # the fields and their driveways, the cover -- what the scene above\n'
         '    # holds, which the authored spec does not. `site_surfaces.py` reads it\n'
         '    # from here, so the dressing is planned on the ground that exists.\n'
         '    drawn_out = os.path.join(out_dir, f"{site_spec[\'name\']}.site.drawn.json")\n'
         '    with open(drawn_out, "w", encoding="utf-8") as f:\n'
         '        json.dump(site_spec, f, indent=1)\n'),
    ])
    _edit(LOT / "site_surfaces.py", [
        ('    base = a.base_dir if a.base_dir is not None else os.path.dirname(\n'
         '        os.path.abspath(a.spec))\n'
         '    out = surfaces(spec, nav_bake=nav, radius_m=a.radius_m,\n'
         '                   floor_max_angle_deg=a.floor_max_angle_deg,\n'
         '                   base_dir=base or None)\n',
         '    base = a.base_dir if a.base_dir is not None else os.path.dirname(\n'
         '        os.path.abspath(a.spec))\n'
         '    # THE SITE AS DRAWN (0.95.0). The spec handed in is the authored one;\n'
         '    # `assemble` resolves walks, adds pads and fields, and writes what it\n'
         '    # drew beside its scene. Planning dressing on the authored spec put\n'
         '    # walk zones on walks the scene does not have (cold run 9142: 6\n'
         '    # declared, 9 drawn, none at the same stations) and never saw a field.\n'
         '    drawn = (os.path.join(base, f"{spec.get(\'name\', \'site\')}.site.drawn.json")\n'
         '             if base else None)\n'
         '    as_drawn = bool(drawn and os.path.isfile(drawn))\n'
         '    if as_drawn:\n'
         '        with open(drawn, encoding="utf-8") as fh:\n'
         '            spec = json.load(fh)\n'
         '    out = surfaces(spec, nav_bake=nav, radius_m=a.radius_m,\n'
         '                   floor_max_angle_deg=a.floor_max_angle_deg,\n'
         '                   base_dir=base or None)\n'
         '    if as_drawn:\n'
         '        out["findings"].append(_finding(\n'
         '            CODE_SPEC_AS_DRAWN, "info",\n'
         '            f"planned on the site as assemble drew it ({drawn}), not on "\n'
         '            f"the authored spec {a.spec}"))\n'),
        ('CODE_FOOTPRINTS_MERGED = "LOT_SURFACE_FOOTPRINTS_MERGED"\n',
         'CODE_FOOTPRINTS_MERGED = "LOT_SURFACE_FOOTPRINTS_MERGED"\n'
         'CODE_SPEC_AS_DRAWN = "LOT_SURFACE_SPEC_AS_DRAWN"\n'),
    ])
    t = LOT / "tests" / "test_site_surfaces_field_zone.py"
    s = t.read_text(encoding="utf-8")
    assert "\r" not in s
    t.write_text(s.rstrip("\n") + "\n" + (SRC / "tests_drawn_append.py").read_text(encoding="utf-8"),
                 encoding="utf-8", newline="\n")
    print("Lot 0.95.0: the drawn spec applied")


if __name__ == "__main__":
    main()
