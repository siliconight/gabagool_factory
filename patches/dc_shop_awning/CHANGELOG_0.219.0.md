## [0.219.0] - the corner blocks hang an awning over the shop

**Factory roadmap 241, the corner shop.** The comps: "Corners carry the life. The corner building has the shop at
grade (lit, awning), homes above." 0.218.0 built the shop; Zoo 1.108.0 draws the awning (`shop_awning`); this hangs
one over each corner block's storefront, in its shop's canvas.

- **`shop_awning.py`** (new, pure) says where the awning hangs, in the building's frame:
  - across the front, 0.3 m short of either end;
  - 1.2 m out, its back 8 mm inside the front wall's face, so no face of Zoo's awning lies on the wall's;
  - its valance's bottom 0.1 m over the storefront's head, and its top 0.85 m over that.

  CHOSEN, not read. 1.2 m stays inside Level Factory's 2.0 m terrace frontage, off the sidewalk, and the top
  stands more than 0.3 m under the first floor's sills. A form Zoo does not draw is refused.
- **`LevelSpec.awning`,** a form or None. The schema carries it: 0.218.0's lesson, a spec field the schema does not
  carry fails the build's own gate.
- **A facade calls `_awning` after `_stoop`.** It writes a `prop` slot -- `shop_awning`, canvas, the form the
  shop's colour -- and a visual greybox box.
  - No collider: the awning hangs over a frontage nobody walks at its height.
  - Level Factory reads an Empty's street edge off its colliders, so the awning moves no line.
- **`empty_midrise(..., awning=None)`** declares canvas when it hangs one. The four corners hang a deli's red, a
  bar's black, a laundromat's navy and a grocery's green.
- **`material_kind.KIND_BY_MATERIAL` carries canvas,** a skin kind already. The suite's `test_every_spec_material_has_a_kind` found the row missing after the first build.
- **`build_freshness.py`** counts `shop_awning.py` among a shell's sources. The four corner specs are regenerated,
  and the nine mid-rises are byte for byte as they were.
- **Built:** `build.py --all`, 6 min 59 s, 159 shells. The four corner blocks moved -- their spec and glb, each now carrying the awning's slot and visual box -- and each validates clean; every other shell's outputs are byte-identical to 0.218.0's by its manifest's `outputs_sha256_16`, 155 of 155. Read off `build/gs_cornershop_a.slots.json`: one `shop_awning` slot, `shed_red`, 14.4 x 1.2 x 0.85 m centred at (0, -8.242, 3.075) -- its back 8 mm inside the front wall's face at y -7.65, its valance's bottom 0.1 m over the storefront's head.
- **`test_corner_awning.py` and the suite:** 1,516 passed, 2 skipped, exit 0: 0.218.0's 1,508 and `test_corner_awning.py`'s 8, which fails to import on 0.218.0 (no `shop_awning`). Its `test_every_built_corner_carries_its_awning_slot` reads all four built slots. The suite's `test_every_spec_material_has_a_kind` failed on the first run, canvas having no kind row, and passes with it.
