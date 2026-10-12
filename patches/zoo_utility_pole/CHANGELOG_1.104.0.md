## [1.104.0] - a wooden utility pole: the cobra-head, the crossarm, the wires' attachments and a transformer can by form

**Roadmap 240, the walker's Philly comps** (`docs/reference/PHILLY_STREET_COMPS.md`
at the factory root): in two of the three photographs the overhead network is
the strongest line in the frame -- a wooden pole at the corner carrying a
cobra-head on a long arm, cobra-heads on poles along the rowhouse street, wires
everywhere -- and the factory stood none of it. The walker's calls of
2026-10-12 (`docs/proposals/POLE_LINE_DESIGN.md`): one side of every street,
the full wire set without house drops, a transformer can every third or fourth
pole, a cobra-head on EVERY pole. This release is the pole; Lot places the
line and draws the wires next.

- **`utility_pole`**, laid out in pure Python by `core/utility_pole_forms.py`
  and built vertex for vertex by `recipes/utility_pole.py` through
  `bpylayer.prim_mesh`, the sign post's pattern. A 40 ft class 4 wood pole
  standing 10.4 m (0.30 m at grade, 0.19 m at the top), an 8 ft crossarm a
  foot under the top on two steel braces, three pin insulators for the
  primaries, the neutral's and the secondary's spools and two communication
  cables' bolts behind it, a number tag, and the cobra-head on a 6 ft arm
  climbing to 7.5 m over the road with its lens hung under the head --
  `M_UtilityPole_Lens`, which Lux's emissive binder powers with the street's
  lamps. US distribution practice fills the blanks (the module's docstring
  has the figures); the comps and the walker decide.
- **Two forms** (`params.form`): `auto`, the pole as above, and `transformer`,
  which adds a pole-mount can under the neutral with its two bushings. The
  lamp is not a form, because every pole carries one. No street-name blade:
  Lot has no road names to letter one with (`site_furniture.BLADE_AT_JUNCTION`).
- **Four materials whatever it carries** -- the genome's wood (creosote, the
  one thing a style tints), galvanised steel, brown porcelain and the lit lens
  -- so a pole draws four times. Collision is the pole's own column: a body
  walks under an arm.
- **The numbers Lot mirrors**, since neither repo can import the other:
  `MODULE_DIMS` (`auto` 0.30 x 3.67 x 10.4 m, `transformer` 0.46 x 3.67 x
  10.4), `POLE_AT` (the pole stands 0.615 m behind the module's centre,
  away from the road: the cobra-head reaches 2.45 m toward it and the
  crossarm 1.22 m the other way, and `fit_exact` maps the drawing's bounds
  onto the slot's), `LENS_AT` (2.171 m toward the road, 7.401 m up, where
  Lot hangs the light) and `WIRES` (each wire's attachment). Pinned to
  literals by `test_the_numbers_lot_mirrors_are_these`.

**Measured, Blender 5.1.1:** `tools/coplanar_census.py --species
utility_pole` -- 3 builds, 0 with coincident pairs, 0 that did not build, 496
tris at every corner; both forms through the kit path a `zoo_kit_build` job
takes (`zoo_cli --build-kit` on two slots shaped as Lot writes them):
`prop_utility_pole_delco_01_w30_d367_h1040` and `..._w46_d367_h1040_ftransformer`,
PASS, 496 and 592 tris, 4 visual meshes and 4 submissions each by
`docs/findings/fixture_merge/layer_count.py` (`M_UtilityPole_wood`, `_steel`,
`_porcelain`, `_Lens`).

**Tests:** `tests/test_utility_pole.py`, seventeen, pure: the species is
discovered and validates; each form plans at its module dims and keeps its
form (`auto` reads as none, as `kit.honour_dressing` makes it); the numbers
Lot mirrors; the plan fills its slot exactly; no two faces coincide; four
materials; the collision is the pole alone; the lens hangs under the head
toward the road and hovers clear of it; the wires stack so the lowest cable
clears 4.7 m at the middle of a 36 m span; the triangle budget; an unknown
form says so. `test_coincident_faces.CENSUS_BUILDS` 387 -> 390, the census
line above it. On 1.103.0 the new file fails to collect -- no `core.utility_pole_forms` to import -- and all seventeen with it; the census and the kit build above are its Blender half

**Suite:** 4,192 passed, 448 skipped, 1 xfailed in 5 min 40 s, where 1.103.0 passed 4,172: the new file's seventeen and the three material-option checks the sweep runs on every genome. The one new skip is `test_recipe_reads_its_genome[utility_pole]`, which sees only a direct `make_material` call, so it skips a recipe that builds through `prim_mesh` as it does one that builds no materials (59 recipes skip it); this one reads `plan['material']` for its wood
