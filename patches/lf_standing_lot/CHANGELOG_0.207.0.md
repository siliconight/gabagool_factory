## [0.207.0] - A package carries the buildings its scene stands, and no others

**The waste.** The compose stage themes every Empty the brief was given, and an urban brief is given every corner
block and mid-rise; a candidate stands some. The export copied the composed root whole, so every composed
`lot/<id>/` shipped. Measured on cold run 9297's package:
- sixteen `lot/` packages, while its assembly scene named thirteen;
- the three extra -- `gs_cornershop_a`, `gs_cornershop_b` and `gs_midrise_g` -- hold 12.2 MB of 210 and 95 `.glb`;
- they are 95 of the 711 model imports the light bake sets to Static Lightmaps, each unwrapped for a lightmap at
  import, for scenes nothing instances (a grep of every `.tscn` finds them named only by their own).

**What changes:**
- **`_standing_lot_ids`** reads the assembly scene's `lot/<id>/site.tscn` references, the same `_LOT_SITE_REF` the
  single-shell path reads.
- **The composed copy leaves out a composed `lot/<id>/` that no scene stands,** and says which:
  `[export] N composed building(s) no scene stands, left out: ...`.
- **`_copy_tree`'s `skip_lot` matches a relative path's first two parts, never a name.** A name matches anywhere
  in the tree, which is the failure `skip_rel` was written for.
- **Nothing is left out** where there is no assembly scene to ask, where it names no package, or on a single-shell
  mission (whose root moves under `lot/<id>/` and has no packages of its own). Absence of evidence decides toward
  including.
- **`tests/unit/test_export_standing_lot.py`:** fails on 0.206.1 on the two defect cases, every composed `lot/<id>/` shipping (`['b1', 'b2', 'b3', 'idle_a', 'idle_b']` where three stood; `['b1', 'b10']` where `b1` stood), while its three controls pass there; 5 of 5 pass on 0.207.0
- **The suite:** `python -m pytest -q`: exit 0, 2,406 passed (0.206.1's 2,400, the new file's 5, and `test_sibling_locator`'s guard over the new file), 14 skipped (the real-tool smoke), 1 xfail, counted off the progress marks, in 6 min 0 s.
