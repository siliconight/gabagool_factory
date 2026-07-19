# Factory Changelog

Versions of the CERTIFIED SET. Individual tool detail lives in each tool's
own CHANGELOG.

## [factory-v1.3.0] - 2026-07-19

The art/material pass, certified. pixelcoat 0.10.0 -> 0.11.0 (procedural
material library: voronoi_cells + wave primitives, aggregate/emissive/
transparency grammars, ~23 tiling grammars + 6 textured glass + 3 opaque
glass_facade, theme-library CLI + street/delco/casino/stadium/bank profiles);
zoo 0.34.0 -> 0.35.0 (glass_facade kind, pack transparency import -> BSDF
alpha/blend, themed glazing routing kit->build->arch); deli_counter 0.79.0 ->
0.80.0 (facade windows tag glazing=facade -- resolves the 1.2.0 drift
known-issue); level_factory 0.10.5 -> 0.11.1 (pixelcoat stage builds the themed
skins library the Zoo kit resolves from; 0.11.1 realigns the fast-suite stub).
Verified on hardware: theme-library resolution (street/casino library_report),
real Blender kit build (glass<-glass_circles, 13 modules / 0 failed),
transparent window GLB in Blender 5.1, orchestrator out/ subdir preservation,
LF fast suite green. Pins: deli_counter 0.80.0, dispatch 0.3.0, lot 0.19.0,
lux 0.15.4, patina 0.18.0, pipeline 0.1.1, pixelcoat 0.11.0, zoo 0.35.0,
level_factory 0.11.1, laser_tag unpinned.

## [factory-v1.0.0] - 2026-07-15

First certified lockstep set. The emitter-marker light pipeline verified
end-to-end on hardware (DC 0.75.0 -> Zoo 0.30.1 markers -> Lux 0.15.2 spawner
-> LF 0.9.0 gates): 20/20 markers spawned, co-location 0.049-0.051 m, powered
kill/restore exact. Pins: deli_counter 0.75.0, dispatch 0.3.0, lot 0.18.0,
lux 0.15.2, patina 0.18.0, pixelcoat 0.9.0, zoo 0.30.1, level_factory 0.9.0,
laser_tag unpinned.
