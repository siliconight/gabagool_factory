## 0.95.0 - the dressing reads the site as drawn, and a field is its own zone

TWO FIXES, ONE CAUSE: the surface dressing was planned on a site that is
not the one in the scene.

THE SITE AS DRAWN. Level Factory's surfaces job runs `site_surfaces.py` on
the AUTHORED spec, while `assemble` draws something else -- walks
re-routed to real doors and some not drawn at all (0.88.0-0.91.0), the pads
(0.93.0), the fields and driveways (0.94.0). Measured on cold run 9142's
shipped site: the dressing was told of 6 walk slabs at the old
centre-to-centre stations (`path_0` at (30.5, 7.5), a walk between two
buildings 0.91.0 stopped drawing); the scene holds 9, none at those
stations; no pad or field reached `tops` or `zones`. So 54 low-density walk
zones dressed ground that is not a walk, and the real walks took open
ground's scatter. `assemble` now writes the spec it drew,
`<name>.site.drawn.json`, beside the scene, and `site_surfaces.py`'s CLI,
handed that out dir as `--base-dir` (Level Factory already passes it), reads
it in place of the authored spec and says so (`LOT_SURFACE_SPEC_AS_DRAWN`,
info). An out dir with none -- an older assembly, a probe -- reads as before.

A FIELD IS ITS OWN ZONE. 0.94.0 gave the fields no zone, so the ground
scatter dressed them as open ground at MEDIUM: on cold run 9141 all 256
pieces on the fields came from `open_ground` (0.29 a m2), the walker's
"pebbles on the aisles". A lot's aisle is a carriageway, and the guide's
reading of a road's centre is LOW. Each field now declares a `parking`
zone at its own top (`FIELD_THICK`), LOW, ranked after the road and ahead
of the courtyard, the perimeter and open ground. With Patina 0.23.0 (a zone
dresses only the ground it owns) the field's own zone is the one that
decides. Measured on cold run 9143 (`docs/cold_runs/cold_9143/NOTES.md`).

`tests/test_site_surfaces_field_zone.py`: a field declares a low zone at
its own height over its own rect; it owns its aisle ahead of open ground; a
site with no fields declares none; `assemble` writes the site it drew (the
fields, driveways, cover and footprints the authored spec lacks); and the
CLI plans on it and says so -- the control, the same spec with no drawn
site beside it, reads as before.
