# Factory Changelog

Versions of the CERTIFIED SET. Individual tool detail lives in each tool's
own CHANGELOG.

## [factory-v1.19.0] - 2026-08-14

level_factory 0.26.0 -> 0.27.0. The other nine tools are unchanged from
factory-v1.18.0: deli_counter 0.89.0, dispatch 0.3.1, laser_tag 0.8.0, lot
0.41.0, lux 0.16.0, patina 0.19.0, pipeline 0.6.0, pixelcoat 0.12.0, zoo
0.36.0.

Stage 1 of `docs/EXPORT_NAMING.md` is closed. All three names it specifies
now exist:

    exports/LF_lot_demo_001.portable-godot/       the build dir      (0.26.0)
    LF_lot_demo_001/                              inside the archive (0.27.0)
    LF_lot_demo_001_s5219_<utc>_f1.19.0_portable-godot.zip            (0.27.0)

THIS PIN IS NOW SHIPPED, NOT JUST RECORDED

0.27.0 writes `LF_MANIFEST.json` into every package, and its `tools` block is
the certified set read out of `factory.manifest.json`. The pin therefore
travels inside every export. Before this bump, an export built from 0.27.0
code wrote `"level_factory": "0.26.0"` there -- correct, because 0.27.0 was
not certified yet, and confusing to anyone who did not know why. After it,
exports self-describe.

WHAT WAS RUN

    export lot_demo_001 --mode portable-godot --format zip
      -> LF_lot_demo_001_s5219_20260814T211037Z_f1.18.0_portable-godot.zip
    portability-test lot_demo_001 --mode portable-godot
      -> PASS, engine_check passed, 0 parser errors, 0 shader errors,
         scene_instantiated true, 0 missing resources, resource_count 35
    level_factory unit suite: 579 passed, 1 skipped

AND THE ARCHIVE WAS OPENED AND ITS MANIFEST READ, which is the only reason
0.27.0 is correct. Its selftest passed 40 of 40 against a package whose
manifest said `"candidate": "...seed_XXXX"` and `"tools": {"lot": "0.4.0"}`
-- the adapter version, where lot is 0.41.0. Both checks asserted that the
plumbing carried what it was handed. It did. What it was handed was wrong.
A check that follows the data instead of reading the artifact will pass on a
deliverable that is false, and this one did.

WHAT WAS NOT RUN

No mission re-run and no re-grade; the 40 / 55 / 60 grades in the manifest
description are still 1.16.0's, and it is not rewritten. No walk sweep, no
pack load check. `pure-shell` has still not been re-exported since 0.26.0
renamed the build directory.

`pytest tests` still aborts during collection on
`tests/test_presentation_fingerprint.py`, which imports a `_COMPOSER_SOURCES`
that no longer exists in `adapters.presentation`. Confirmed against an
unpatched checkout, so it predates this work -- but it means the four test
modules outside `tests/unit` have not run in some time, and nothing said so.

OPEN, AND THE FIRST IS THE SERIOUS ONE

The `candidate_selected` marker for `lot_demo_001` holds the literal template
`lot_demo_001.candidate.seed_XXXX`; `cmd_approve` writes `--candidate`
verbatim and nothing validates it. `_selected_lot_out` derives a job path
from it, so `graybox_dir` points at a directory that does not exist and
exports have been succeeding on the Dispatch handoff alone. The same function
feeds the post-art functional-regression check a `site.site.gameplay.json`
that is not there.

AND THAT GATE HAS NOW BEEN MEASURED, WHICH FOUND SOMETHING LARGER

`tools/probe_selection_drift.py` compares the lock's three protected
signatures computed three ways: as the gate resolves them today, from the
REAL site file, and from no site file at all. All three ways agree, on all
three signatures. The site file changes nothing. Repairing the marker
would not have changed a single hash.

The cause is a vocabulary mismatch, not a path. `_merged_gameplay` reads
eleven keys; `site.site.gameplay.json` publishes twenty top-level keys and
none of the eleven -- buildings, collision, cover_plan, encounters,
enterability, ground, ground_extent, loot, markers, objectives, openings,
pacing, rooms, site, site_markers, surface_roles, surfaces, tactical,
vertical_links, zones. Lot and Deli name the same concepts differently and
the extraction is written in Deli's vocabulary. Four of the eleven get
backfilled from Deli by `setdefault`, which is what hid this: the
signature is never empty, so it never looked broken.

It is worse than the site being unguarded. `anchors` is absent from BOTH
files, so `anchor_registry_hash` -- the one whose drift message reads
"gameplay-anchor registry changed after art pass" -- has been hashing an
empty list. `route`, `route_graph` and `nav_hints` are absent from both,
so `route_graph_hash` is the hash of two empty dicts. `collision_hulls`
and `doorways` are absent from both. What remains protected is Deli's
`stair_systems`, a list of 2.

This does not touch the grades, which come from the walk and scoring
stages. It does mean every "no functional drift after the art pass"
result this factory has recorded -- including the one inside
factory-v1.16.0's evidence -- was a weaker claim than it read as. The
description is still not rewritten, for the reason 1.17.0 gave; a reader
of it should know what that phrase covered.

Mapping Lot's vocabulary onto the signatures is a contract question
between two tools, and the obvious-looking pairs (`collision` ->
`collision_hulls`, `openings` -> `doorways`, `vertical_links` -> ladders
and stairs, `markers`/`site_markers` -> anchors) have not been opened and
checked. A guessed mapping would give a lock that hashes real data and
still protects the wrong thing, which is harder to notice than one that
hashes nothing. Not attempted here.

0.27.0 stopped the bad value reaching the shipped manifest and made
the disagreement print on every export. It did not change which directory a
job resolves from, and should not have.

`pyproject.toml` still says 0.22.0 against a VERSION of 0.27.0, still
invisible to `verify-manifest`. 57 buildings stale in `check_all` freshness.
`cbp`, `night_pawn` and `primos_pizza` still fail nav_gate. `laser_tag` still
has no CHANGELOG.

## [factory-v1.18.0] - 2026-08-14

level_factory 0.25.0 -> 0.26.0. The other nine tools are unchanged from
factory-v1.17.0: deli_counter 0.89.0, dispatch 0.3.1, laser_tag 0.8.0, lot
0.41.0, lux 0.16.0, patina 0.19.0, pipeline 0.6.0, pixelcoat 0.12.0, zoo
0.36.0.

NOT A BOOKKEEPING RELEASE, WHICH IS THE DISTINCTION 1.17.0 DREW

1.17.0 pinned code that was already running, under names that had gone
stale, and said plainly that nothing new was verified for it. This is the
other kind: new code, a behaviour change a recipient of a package can see,
and a run that earned it.

WHAT CHANGED

An export's directory name was composed in five places -- twice in
`packages/exporting/export.py`, three times in `apps/cli/commands`. One of
those five hardcoded `portable-godot` four lines after the block above it had
set the mode, so it was correct only for as long as the default never moved.
`ids.export_build_dir_name` is now the only definition, and it lives beside
`candidate_id` and `job_id` because those already own the rule that an id
which becomes a directory is refused rather than sanitised.

`lot_demo_001.portable-godot/` is now `LF_lot_demo_001.portable-godot/`.

THE ARCHIVE STOPS LOSING ITS PROFILE

`with_suffix(".zip")` reads `.portable-godot` as a file extension and
REPLACES it, which is the entire reason the archive was `lot_demo_001.zip`
with no profile in the name -- and why both profiles would have written to
the same archive. Nobody decided to drop it; a path helper ate it. Appending
instead of substituting gives `LF_lot_demo_001.portable-godot.zip`.

WHAT WAS RUN

    export lot_demo_001 --mode portable-godot
      -> .level_factory\exports\LF_lot_demo_001.portable-godot
    portability-test lot_demo_001 --mode portable-godot
      -> PASS. engine_check passed, parser_error_count 0,
         shader_error_count 0, scene_instantiated true,
         missing_resource_count 0, absolute_path_count 0,
         external_reference_count 0, resource_count 35, godot 4.7
    export ... --format zip
      -> LF_lot_demo_001.portable-godot.zip

The portability pass was re-earned, not assumed. The export directory moved,
and a package that loads in a clean Godot 4.7 project is exactly the claim a
directory rename could break.

WHAT WAS NOT RUN

No mission re-run and no re-grade: the 40 / 55 / 60 grades in the manifest
description are still 1.16.0's. No walk sweep, no pack load check, no unit
suites. `pure-shell` has not been re-exported since the rename.

The manifest description is not rewritten. One portability pass is evidence
for one claim, not a re-certification of the set.

STAGE 1 OF THREE

`docs/EXPORT_NAMING.md` specifies three names; this lands the build
directory. The full archive name needs the seed, the build time and the
factory version plumbed into `export_mission`, and `LF_MANIFEST.json` comes
with them. The interior renames (`lot/<building>/` -> `sites/<building>/`,
dropping `assets/lot.glb`) move `res://` paths and want their own
portability run.

A FOURTH VERSION NUMBER, WHICH THE CHECK CANNOT SEE

`level_factory/pyproject.toml` says `version = "0.22.0"` while VERSION and
the CHANGELOG both say 0.26.0. `verify-manifest` reports level_factory OK
because `installed_factory_versions` reads only the VERSION file. The check
is not wrong about what it measured -- it is silent about a source it never
looks at. This was noticed while working out how to invoke the CLI, not by
any check, which is the argument for recording it. Open.

KNOWN FAILING, UNCHANGED

57 buildings stale in `check_all` freshness. `cbp`, `night_pawn` and
`primos_pizza` still fail nav_gate; none are in the `lot_demo_001` draw.
`laser_tag` still has no CHANGELOG.

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
