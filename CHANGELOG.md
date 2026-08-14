# Factory Changelog

Versions of the CERTIFIED SET. Individual tool detail lives in each tool's
own CHANGELOG.

## [factory-v1.16.0] - 2026-08-14

The art layer, certified, and the pins catch up to the tools they name.

deli_counter 0.88.0 -> 0.89.0, level_factory 0.22.0 -> 0.24.0, lot 0.32.0 ->
0.41.0, lux 0.15.4 -> 0.16.0, patina 0.18.0 -> 0.19.0. dispatch 0.3.0,
pipeline 0.5.0, pixelcoat 0.11.0, zoo 0.32.0 and laser_tag 0.8.0 were already
correct.

Four of those five pins were behind because VERSION moved and nothing moved
the pin. `lot` is the exception and the interesting one: its CHANGELOG
carried nine consecutive entries from 0.33.0 to 0.41.0 while its VERSION file
still said 0.33.0 and this manifest pinned 0.32.0 -- three different answers
to one question, none of them agreeing. `patch_version_reconcile.py` made
each tool agree with itself first; this makes the manifest agree with them.

WHAT WAS RUN FOR THIS CERTIFICATION

- The mission re-ran end to end on the themed draw and graded its three
  candidates 40 / 55 / 60, selecting `lot_demo_001.candidate.seed_5219`.
  That re-run overturned SESSION_0811's conclusion that the Laser Tag score
  was a plateau: the plateau was an artifact of grading the greybox draw
  while the themed draw shipped.
- `check_all`: gdscript clean, stairs clean, steps clean.
- The portable package opened in a clean Godot project -- zero plugins, zero
  autoloads, zero external references, 18.6 MB across 212 entries.
- Four deli_counter shell fixes engine-confirmed, taking nav_gate from 7 of
  135 shells failing to 3.

WHAT WAS NOT RUN, AND IS THEREFORE NOT COVERED

The walk sweep (`library_walk.py`, needs Godot, about an hour for 20 sites),
the pack load check, and the `lot` and `deli_counter` unit suites. A set that
does not say what it skipped reads as a set that skipped nothing.

WHAT IS KNOWN FAILING

- `check_all` freshness: 57 buildings whose geometry no longer matches the
  spec or builder that made them.
- Three demo shells still fail nav_gate: `cbp`, `night_pawn`, `primos_pizza`.
  None is in the `lot_demo_001` draw. `cbp` is not the same defect as the
  four that were fixed -- its first floor fragments across 63 islands, 32 of
  them 2 polygons or fewer, so no stair fix reaches it.

UNRESOLVED, AND RECORDED RATHER THAN PINNED PAST

This entry sits directly on top of `factory-v1.3.0`. Twelve certified sets
between them have no entry at all -- 1.4 through 1.15 were pinned without
being written down. They are not reconstructed here; there is nothing on disk
to reconstruct them from, and inventing twelve entries would put fiction in
the file whose only job is to be the record.

And `factory-v1.3.0` records "zoo 0.34.0 -> 0.35.0". Zoo's own CHANGELOG has
never contained a 0.33.0, 0.34.0 or 0.35.0 entry; before 2026-08-14 its
newest was 0.31.0, and that number appeared twice. Either zoo was renumbered
downward at some point, its entries were lost, or that line named versions
that never shipped. Nothing on disk says which, so this says so instead of
choosing.

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
