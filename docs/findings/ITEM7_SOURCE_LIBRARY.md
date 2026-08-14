# Item 7 — the pipeline reads its own output as source

Built, tested, **held**. `patch_lf_source_library.py` is not applied to your
tree. The state-of-the-tree note says do not stack onto six unverified changes,
and the runbook at the bottom is the order that respects it.

Grounded per `CLAUDE.md`: every file read this session byte-matched what the
device reported — `SESSION_0808.md` 33,695; `CLAUDE.md` 17,020;
`NAV_GATE_FINDINGS.md` 14,661; `building_library.py` 18,467; `planner.py`
23,502; `apps/cli/commands/__init__.py` 102,298; `library_census.py` 5,856;
`library_themed_fit.py` 5,962; `marker_scope_census.py` 14,653; plus 138 of the
141 `*.validation.json` in `deli_counter/build/`. No mismatches, nothing
reconstructed.

---

## Three corrections to the doc, each measured

**1. `index` is NOT the one place every count enters from.** The handoff says
`library_census.py`, `library_themed_fit.py`, `marker_scope_census.py` and
`lot_for` "all pass through it". Measured: only `library_themed_fit.py` does
(`bl.index`, line 75). `library_census.py:82` and `marker_scope_census.py:215`
both `root.glob("*.glb")` directly.

This matters because the plan rested on it — *"One place, cannot drift, and
every count above corrects itself."* A fix at `index` alone would have left
**"103 navigable, 15 holed, 17 unjudged"** — printed by `marker_scope_census.py`
— counted over the polluted library, while `library_themed_fit.py` reported a
corrected denominator for the same directory. Two instruments disagreeing about
what is in a folder.

So the rule lives in `building_library.source_exclusion` and all three readers
**import** it. None restates it.

**2. The facades don't need naming — Deli Counter already says so.**
`<id>.validation.json` carries a `facade` flag written by
`deli_counter/evidence.py`. Read across all 138 validation manifests in the
library: `facade: true` on exactly `gs_facade_rowhome` and
`gs_facade_storefront`, `false` on every other, and **the key is present on all
138** — no shell is silent about it.

So the rule reads a field rather than matching a name — the same discipline
`scoped_verdict` states two functions down. You picked "name them explicitly"
over "derive from geometry"; this is neither, and it is better than both: it is
Deli Counter's own answer, and it generalises to facade twelve. The eleven are
still named explicitly, in `test_source_library.py`, each with its reason. If
you'd rather hardcode the two ids, it is one line.

Measured beside the flag, so it isn't taken on faith: both facades carry 0
markers, 0 rooms and a six-polygon navmesh of three 2-poly islands — three
floor plates with nothing joining them.

**3. The themed lot does not move. Only the greybox draw does.**

This is the one that changes the sequencing, and it refutes the concern I
opened with. `REQUIRED`'s docstring warns that narrowing the pool reshuffles
every draw already graded — true, but not for the themed path. Read off the
real manifests, **all eleven report `navigable: null` with
`interior_checked: 0`**, so `themed_fitness` already refuses every one as
UNJUDGED. `require_themed_shells` had removed exactly these eleven before
`index` ever learned to.

    lf_art_probe_001_5017              navigable=None  interior_checked=0
    lf_category5_baie_dore_001_5017    navigable=None  interior_checked=0
    lf_category5_baie_dore_001_5118    navigable=None  interior_checked=0
    lf_category5_baie_dore_001_5219    navigable=None  interior_checked=0
    lf_category5_baie_dore_001_5320    navigable=None  interior_checked=0
    lf_category5_baie_dore_001_5421    navigable=None  interior_checked=0
    lf_lot_demo_001_5017               navigable=None  interior_checked=0
    lf_lot_demo_001_5118               navigable=None  interior_checked=0
    lf_lot_demo_001_5219               navigable=None  interior_checked=0
    gs_facade_rowhome                  navigable=None  interior_checked=0
    gs_facade_storefront               navigable=None  interior_checked=0

`run lot_demo_001 --art` is the themed path, so the patch **cannot** disturb the
08-09 sweep baseline. It is safe to apply before the verification run. It is
still held, because the state-of-the-tree note is about stacking in general and
because this claim is a property of today's *data*, not of the code — a future
re-bake that makes one of the eleven navigable silently ends it.
`test_the_themed_pool_does_not_move` pins it so that stops being silent.

What does move is the **greybox** pool, which nothing narrowed. That is how
`lf_lot_demo_001_5017` came to be placed as a building and measured as an
archetype in the 08-09 sweep.

---

## What the patch does

`building_library.source_exclusion(build_dir, aid)` — one definition, returns
the sentence or `""`. Two kinds, found two different ways because they are two
different things:

* **Composed outputs**, by the `lf_` prefix. Not a name guess:
  `apps/cli/commands/__init__.py:264` writes `f"lf_{model.mission_id}"` and
  `DeliCounterAdapter._level_name` appends `_{seed}`. It is a label this
  pipeline printed on its own output, one grep from the line that prints it.
* **Facades**, by Deli Counter's flag. An absent or unreadable validation
  manifest is **not** a facade — it fails open, because exactly one complete
  shell has no validation manifest (`cbp_town_finale_midbalanced_schemafixed`)
  and it is a building.

`index()` now returns **three** lists — `(complete, incomplete, non_source)`.
The arity change is the mechanism, not an accident: a filter that merely
shortened `complete` would be the silent narrowing this module refuses
everywhere else. Breaking the signature obliged every reader to say what it
does with the third list, and that is what surfaced correction 1 above.

A non-source entry never lands in `incomplete`. Reporting a composed site as
"missing a manifest" sends the reader to Deli Counter to rebuild a file that
should never have been indexed.

**Measured over a faithful reconstruction of `deli_counter/build/`** — exact
filenames, real validation manifests:

    complete     134  ->  123
    incomplete     4      bank, kitbash_demo, rarity_demo, survival_demo
    NOT SOURCE     0  ->   11      (the eleven, and only the eleven)

### The fixture carried the defect too

`test_fanout.py::ARCHETYPES` listed `lf_lot_demo_001_5017` as one of its eight
stand-in buildings — a faithful copy of the polluted directory, so the fixture
agreed with the code and neither said so. It is `rail_station_a02` now, with
the reason recorded above it. Same in `test_archetype_axis.py`. This is the
trap already written down as *"a fixture is a claim about the world"*, hit
again in the same file.

### Tests

22 new in `test_source_library.py`, **all demonstrated failing first** (21 of
22 fail on the pre-patch tree; the 22nd is the arity guard). The facade rule is
put wrong on purpose in **both** directions — a building merely *named*
`gs_facade_*` stays in, a plainly-named shell flagged `facade: true` goes out —
because "it flagged the known offender" cannot tell you it would not also flag
a good one. Replacing the flag read with a name rule fails that test and fails
`marker_scope_census.py --selftest`.

    571 passed, 1 skipped     before          (the tree as it stands today)
    593 passed, 1 skipped     after           (+22)
     72 passed                tests/ root     (unchanged)

`tests/test_presentation_fingerprint.py` still fails to import on
`_COMPOSER_SOURCES`, identically before and after — the pre-existing one.

### The censuses refuse rather than under-report

`library_census.py` and `marker_scope_census.py` now import the rule and
**refuse to run** if they cannot, because an unfiltered count here is not a
rougher truth, it is the defect. `--unfiltered` prints it anyway with a banner,
for comparing against a figure taken before this landed.
`marker_scope_census.py --selftest` now proves the source split alongside
`_outside`, in both directions, before every census.

---

## Runbook — the order, and why

The three open items come first. None of them can run here; all three need your
machine.

### 1. Verify the six against the current tree — nothing applied

    cd C:\Projects\gabagool_studios\gabagool_factory\lot-demo-ws
    python ..\level_factory\apps\cli\main.py run lot_demo_001 --art

Confirming, against the 08-09 figures: five `zoo_kit_build` jobs planned, one
per placed building; all succeed; `blockers open: 0`; no un-suffixed kit job.

    cd ..
    python module_extents.py --sweep lot-demo-ws --builds deli_counter\build

Expect 3 of 8 still disagreeing (`depot_a01`, `pharmacy_a02` — not placed, so
still on the old shared art — and `bank_branch_a04` on the
`prop_rockay_01_w160` orphan, which should now read `MATCHES NO PLANNED
MODULE`, not a dimension fault).

### 2. `cache forget` on hardware — four paths, one job re-run

Never run outside tests. Pick a cheap job with a receipt
(`dir .level_factory\jobs\*\fingerprint.last.json`), then:

    lf cache inspect
    lf cache forget lot_demo_001.<cheap_stage>     # expect forgotten: true
    lf cache forget lot_demo_001.<cheap_stage>     # again, WITHOUT re-running
                                                   # expect forgotten: false,
                                                   # "nothing was cached under
                                                   #  that digest"
    lf cache forget lot_demo_001.no_such_stage     # expect the receipt-missing
                                                   # message, non-zero exit
    python ..\level_factory\apps\cli\main.py run lot_demo_001 --art

That job re-runs; everything else hits cache. Compare its outputs to the
previous run's — `forget` should cost a rebuild, not change a result. If they
differ, the entry it dropped was poisoned and that is the first evidence of it.

### 3. Walk the corrected site by eye

    lf walk lot_demo_001 --play

The check none of the instruments replace, and how this started. Three things
to look at, in order:

* **The ladder.** The bot finds it every run —
  `Ladder_ladder_0: climb, top_exit — no opening at all at rel_y 3.90, the slab
  is solid over the ladder`. Only known gameplay-blocking defect. The report
  names the building; the overlay (F3, on by default) names the collider and
  its height when you stand under it.
* **Item 3, `construction_site_a03` (b2).** The stair into the slab. The
  overlay answers "how much headroom, and what is the ceiling" directly. A
  flight with 1.9 m of clearance proves a polygon path to a 1.8 m agent and
  still feels like a wall.
* **Item 2's premise.** Now worth a look, because the kit fan-out has landed:
  if the odd proportions and floating lintels were Deli Counter's greybox
  partitions at the real storey height standing beside Zoo modules pinned at
  3.300, the rebuilt buildings should read clean and item 2 closes as a symptom
  of item 1. `bank_branch_a04` is the one to check — all four species measure
  3.900 now.

### 4. Only then, apply

    python patch_lf_source_library.py --check     # reads and hashes, writes nothing
    python patch_lf_source_library.py
    cd level_factory && python -m pytest tests\unit        # 593 passed, 1 skipped

`--revert` restores from the `.pre_source` sidecars. Round-tripped here: apply →
593, revert → 571 with every file back to the device's exact byte count.

Refuses on any target whose bytes are not what it was written against — a
whole-file SHA-256, not an anchor, so a drifted file cannot be half-patched, and
nothing is written unless every target verifies. Tested by drifting one file:
it names it, prints both digests, and writes nothing at all.

### 5. Recount

    python library_themed_fit.py deli_counter\build
    python marker_scope_census.py deli_counter\build
    python library_census.py deli_counter\build

Every corrected figure in `SESSION_0808.md` — "6 of 134", "97 of 134 can carry a
theme", "103 navigable, 15 holed, 17 unjudged", "37 themeable families" — was
taken against the polluted library and none has been restated. The denominator
moves from 134 to 123 and each of those needs re-reading, not adjusting.

---

## Still open after this

**The composed package accumulates modules across runs.** Logged 08-09, not
touched. `prop_rockay_01_w160` is the cosmetic symptom; the mechanism is the
same family as `_bundle_asset`'s name-collision handling in
`exporting/localize.py`.

**Three more `lf_` residues with no `.glb`.** `lf_m1_1997`, `lf_m1_2098`,
`lf_m1_2199` have `.validation.json` in `deli_counter/build/` and no shell, so
`index` never saw them and this patch does not touch them. Item 8's sweep, not
a correctness question — but they say the feedback loop has been running longer
than the eleven suggest.

**Item 8 still waits**, and the connection the doc draws is real: *when
everything looks like it might be current, nothing reads as stale.* This patch
adds ten more `.pre_source` sidecars to a root that already has too many. They
are session-scoped; clean them when this commits.
