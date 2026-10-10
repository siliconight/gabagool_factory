## [0.176.1] - The site spec's draw takes the cluster template too

**Cold run 9231, roadmap 230.** The first level drawn by a template
(restaurant_row_001 with `cluster: auto`) stopped at the export: the
planner and the compose spec drew the template's lot through
`lot_for_brief` (deli, pharmacy, office) and the site spec drew its own
through `pick_lot`, anchored but untemplated (deli, office, rail station),
so the art leg dressed a pharmacy the site never placed, the station's
glb was unresolved, and the export's closure gate stopped the run
(`EXPORT_CLOSURE_BROKEN: 1 unresolved res:// reference(s)`). 0.176.0's own
note said "`grep lot_for` over the package names all three call sites";
the fourth draw was a `pick_lot`, and the planner's disagreement guard
compares the art jobs with the compose spec, not with the site spec, so
nothing before the export could see it.

- **`building_library.preferred_for_brief(model)`:** the one place the
  template is read off a brief; `lot_for_brief` and the site spec builder
  both ask it, so the four draws cannot disagree about the template.
- **A test walks `apps/` and `packages/`** for every `pick_lot(` outside
  the library and refuses one that does not say `preferred=`.
- Every brief that names no cluster keeps its draw byte for byte, as
  before; 9231's lot with the fix is deli, pharmacy and office in every
  stage, which cold run 9232 shows.

**Suite:** RESULT_SUITE.
