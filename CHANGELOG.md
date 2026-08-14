# Factory Changelog

Versions of the CERTIFIED SET. Individual tool detail lives in each tool's
own CHANGELOG.

## [factory-v1.17.0] - 2026-08-14

A bookkeeping release. Four of the five tools shipped no new code; they
finally have version numbers that name the code they were already running.

dispatch 0.3.0 -> 0.3.1, level_factory 0.24.0 -> 0.25.0, pipeline 0.5.0 ->
0.6.0, pixelcoat 0.11.0 -> 0.12.0, zoo 0.32.0 -> 0.36.0. deli_counter 0.89.0,
laser_tag 0.8.0, lot 0.41.0, lux 0.16.0 and patina 0.19.0 are unchanged from
factory-v1.16.0.

THE DISTINCTION THAT MATTERS HERE

`pixelcoat`'s eleven commits, `zoo`'s seventeen, `dispatch`'s README edit and
`pipeline`'s guard-rail stamp were all committed BEFORE factory-v1.16.0 was
cut. That code was on disk and inside the set when 1.16.0 was certified this
morning. Nothing about the running system changed between then and now.

What changed is that `verify-manifest` reported four tools STALE -- code
committed after the VERSION naming it -- so each got the version and the
CHANGELOG entry it was owed. The set being pinned is the set that was already
running, under names that are now accurate.

A certified set that does not separate bookkeeping from behaviour tells its
reader something was verified when nothing was. So: nothing new was verified
for this bump.

THE ONE PIECE OF NEW CODE

`level_factory` 0.25.0 teaches `verify-manifest` to read the CHANGELOG as a
third number, which 0.24.0's own entry had flagged as known and unaddressed.
Two statuses: UNRELEASED (the CHANGELOG ahead of VERSION) and UNDOCUMENTED
(VERSION ahead of the CHANGELOG), both outranking DRIFT, because a tool that
does not know its own version cannot be pinned by anyone.

It immediately found what it was built for -- `pipeline` documenting v0.1.0
against a VERSION of 0.5.0, five releases with no entries -- and it caught
its author twice inside an hour: once asserting `pipeline` would report
UNRELEASED when it reports UNDOCUMENTED, and once reporting `dispatch` as
disagreeing with itself because the first heading reader only understood
`## [0.3.0]` and dispatch writes `## v0.3.0`.

WHAT WAS RUN

Every patch's selftest, and level_factory 0.25.0's against the real factory:
eleven mechanism checks on fixtures that cannot drift, plus a live
`verify_manifest` over all ten tools. After this the run reads ten OK.

WHAT WAS NOT RUN

Everything engine-shaped. No mission re-run, no walk sweep, no pack load
check, no unit suites, since factory-v1.16.0 this morning. The evidence for
the SET is 1.16.0's evidence, unchanged, which is why the manifest
description still carries 1.16.0's date and is not rewritten here.

KNOWN FAILING, UNCHANGED FROM 1.16.0

`check_all` freshness still reports 57 buildings whose geometry no longer
matches the spec or builder that made them. Three demo shells still fail
nav_gate -- `cbp`, `night_pawn`, `primos_pizza` -- none of them in the
`lot_demo_001` draw.

ZOO JUMPED TO 0.36.0, AND WHY

`zoo`'s tags run to v0.35.0. Its VERSION had been reset backwards to 0.31.0
at some point, so every number written since was landing on history that
already existed. Today's release was drafted as 0.33.0 and `git tag` refused
it -- v0.33.0 has meant "Phase 1 structural species" since it was cut. The
refusal is the only reason this was noticed.

Worse, earlier the same day I had force-moved `v0.32.0` off `a944ccd`
("enriched kit index, missing-module gap report, slot-fit authority over
genome ranges") onto a CHANGELOG correction, having read it as a stale tag on
a bad entry. It was a real release, and a reset version number looks exactly
like a stale tag from the outside. The tag is restored to `a944ccd`; zoo's
work today is one release at 0.36.0, above everything; and the entry explains
the 0.32-0.35 gap rather than leaving a reader to assume the numbering is
arbitrary.

This also closes what factory-v1.16.0 recorded as unresolved -- that
factory-v1.3.0 reported "zoo 0.34.0 -> 0.35.0" while zoo's CHANGELOG had
never held a 0.33, 0.34 or 0.35 entry. It had held them. The entries were
lost in the reset; the tags survived.

STILL OPEN

`laser_tag` has no CHANGELOG at all. It is a Godot addon directory holding
VERSION and `addons/`, so it may never want one, but nothing has decided
that.

And two entries written today record what they could not establish rather
than filling it in: `pipeline` v0.6.0 names the 6 lines in
`building_configuration_registry.json` it did not read, and `zoo` 0.36.0
names the commit in its range -- `5bbe380`, "checkpoint: uncommitted working
tree" -- that says nothing about itself.

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
