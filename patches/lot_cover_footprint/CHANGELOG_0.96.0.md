## 0.96.0 - a standing piece keeps dressing out of its own footprint

`site_surfaces.exclusions` gave every cover piece a `cover_edge` exclusion
of `site_cover.MARKER_CLEARANCE` (3 m) from its centre: "a cover piece
whose base is buried in scatter stops reading as cover". The rule never ran
in the pipeline -- the surfaces job read the authored spec, which carries no
cover -- until 0.95.0 made it read the site as drawn. On cold run 9143 it met
164 pieces (lamps, trees, benches, hydrants, bins, the kerb lane's cars and
the fields'), exclusion refusals went 493 -> 2,061, and every kerb line
became a 3 m clear ring: the sidewalk under each lamp bare in the frames
where 9141's carried litter.

The premise does not hold for dressing: a dressing piece is at most the
`low` band (0.30 m) and the shortest cover piece is `site_cover.
MIN_COVER_HEIGHT` (1.3 m), so scatter cannot bury cover. What a standing
piece needs is no dressing INSIDE it. Its exclusion is now its own
footprint (`size` in plan, as `assemble` stands it; `lot.COVER` when it
carries none), no radius; the markers keep `MARKER_CLEARANCE`.

MEASURED by re-running cold run 9143's surfaces and dressing jobs on its own
inputs with this (`_runs/dressing_096`), beside what 9142 and 9143 shipped:

                              9142        9143        this
    pieces                    5,232       2,226       3,566
    on another zone's ground  1,430       0           0
    sidewalks                 1,822       351         1,421
    roads (low)               1,071       331         477
    fields, a m2              0.288       0.065       0.080
    exclusion refusals        493         2,061       540

What remains of the drop from 9142 is the double dressing Patina 0.23.0
stopped: open ground's scatter on roads, sidewalks, the perimeter and the
fields.

`tests/test_site_surfaces.py`: the markers keep site_cover's circle and a
cover piece is a footprint; a 4.3 x 1.75 m car excludes a point on its
roof and not one 0.5 m off its side, which the 3 m circle reached
(literals).
