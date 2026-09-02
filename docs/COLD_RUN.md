# Cold Run Runbook — measuring interventions-per-level

Roadmap **item 17**. Everything else in `PIPELINE_ROADMAP.md` measures a defect
and closes it. This measures the toolchain itself: *hand the tools a spec, run
one command, and does a walkable, gated package come out with nobody touching
anything on the way?*

The deliverable is **a number** — how many times a human had to reach into the
machine — and item 17 states what the number means:

> A run needing zero is the first real evidence. A run needing four is a list of
> four defects, which is worth more than another guardrail. Repeat on several
> specs before believing either result.

All paths assume the factory root `C:\Projects\gabagool_studios\gabagool_factory`.

---

## The instrument

`tools\cold_run.py` keeps the count so nobody has to remember it. It hashes the
source of all ten tool repos at `--begin` and again at `--end`; **a file that
changed during the run is an intervention whether or not anybody wrote it
down.** The journal records intent, the hashes record fact, and `--end` prints
both and flags any disagreement between them.

```powershell
python C:\Projects\gabagool_studios\gabagool_factory\tools\cold_run.py --selftest
```

Prove the detector before trusting it. It should report build output ignored,
source edit / version bump / new file all caught.

## What the run is, and the compromise in it

Item 17 asks for *a spec that has never been through the pipeline*. There is a
tension in satisfying that literally: a brief written today, by anyone who has
been inside this pipeline this month, is not cold either — it would be written
around what is known to work, and would measure the author rather than the
tools.

So **run 1 holds the spec fixed and makes the geometry new**: the existing
`category5_baie_dore_001` brief, byte-for-byte unchanged, at a **`seed_base`
the factory has never drawn**. Seeds already spent are 1997, 2199, 5017, 5118,
5219, 5320 and 5421. `seed_base 7001` with the brief's `candidate_count: 5`
derives **7001, 7102, 7203, 7304, 7405** (`derive_seeds` is `seed_base + i*101`,
`packages/pipeline/planner.py:137`), none of which collide.

Every building, every site layout, every candidate is geometry the toolchain has
never seen. What is *not* cold is the brief's vocabulary — archetype, theme,
site shape — which the tools have been taught. State that limitation when
quoting the number: **run 1 measures the pipeline on unseen geometry, not on an
unseen vocabulary.** Run 2 (below) attacks the other half.

## Where the spec lives, and why not in a tool repo

`docs\cold_runs\cold_7001\` — `batch.json` plus a verbatim copy of the brief
under `briefs\`. Two constraints fix that location:

- **Outside the ten tool repos.** `cold_run.py` hashes `deli_counter`, `lot`,
  `zoo`, `lux`, `patina`, `pixelcoat`, `level_factory`, `dispatch`, `lasertag`
  and `pipeline`. A spec authored under `level_factory\examples\` would register
  as an *added file* and count as an intervention it is not.
- **Version-controlled.** `_runs\` is gitignored, so a spec parked there could
  not be re-run later to reproduce the measurement.

`batch create` resolves briefs as `<batch.json's folder>\briefs\<mission_id>.json`
(`apps/cli/commands/__init__.py:116`), so the two files must stay together.

**The spec is authored before `--begin`.** Writing it is not an intervention;
editing it after the clock starts is the exact failure mode item 17 is named
after — hand-editing the input until the output works.

---

## Prerequisites — all of this happens BEFORE the clock starts

Setup is not what is being measured. A missing Blender path is a laptop problem,
not a pipeline defect, and counting it would slander the tools. Get `doctor`
green first, then begin.

```powershell
$env:BLENDER  = "C:\blender\blender.exe"
$env:DC_GODOT = "C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
cd C:\Projects\gabagool_studios\gabagool_factory
```

### P1 — a FRESH workspace

A cold run must not inherit a warm cache, a prior approval, or a stale
`shared\` asset. Level Factory fingerprints on seed so a new seed busts the
cache anyway, but a clean workspace removes the argument.

```powershell
python -m level_factory init C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws
```

Do **not** reuse `rockay-ws`. It is evidence, it is read-only, and it is warm.

### P2 — point it at the repos

Copy the known-good file rather than hand-authoring one:

```powershell
copy C:\Projects\gabagool_studios\gabagool_factory\workspaces\rockay-ws\tools.local.json C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws\tools.local.json
```

### P3 — doctor, until green

```powershell
python -m level_factory -C C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws doctor
```

`-C` must name the **workspace** (the folder holding `.level_factory\`), not the
factory root — it searches at and above that path and never below.

Fix anything red here freely; none of it counts. When `doctor` is green, stop
touching things.

---

## The run

### Step 1 — start the clock

```powershell
python tools\cold_run.py --begin cold_7001
```

Prints the file count and every tool's VERSION. **Copy that version block into
the report** — it is what the number is a measurement *of*.

From this point on, every keystroke that changes a tool repo, a brief, a theme
or a genome is an intervention.

### Step 2 — create the batch

```powershell
python -m level_factory -C C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws batch create docs\cold_runs\cold_7001\batch.json
```

Expect `created batch 'cold_7001' with 1 mission(s): category5_baie_dore_001`.

### Step 3 — plan, and read the plan before running it

```powershell
python -m level_factory -C C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws plan category5_baie_dore_001
```

Reading a plan is observation, not intervention. Check it names 5 candidates at
the seeds above and `output=graybox`.

### Step 4 — the graybox base

```powershell
python -m level_factory -C C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws run category5_baie_dore_001
```

The long one: 5 candidates × 4 buildings through Deli Counter in Blender, then
Lot, then Laser Tag nav QA. Budget hours, not minutes, and expect the console to
sit silent through Blender. **If it looks hung, check the window title for
`Select`** — Windows console QuickEdit pauses output when a click lands in the
buffer. Press Esc. That is not a retry and not an intervention.

### Step 5 — the three gates

```powershell
python -m level_factory -C C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws approve category5_baie_dore_001 brief_approved
python -m level_factory -C C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws approve category5_baie_dore_001 candidate_selected --candidate category5_baie_dore_001.candidate.seed_7001
python -m level_factory -C C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws approve category5_baie_dore_001 functional_shell_locked
```

**These three are not interventions.** Level Factory's approval model exists so
a human decides those three things; counting them would report every successful
run as needing three interventions and make the metric useless. *Choosing* which
candidate is a decision. *Making* a candidate work is an intervention.

Substitute a different `--candidate` if `seed_7001` is not the one you'd pick —
still a decision, still not counted. Record which you chose and why.

### Step 6 — the layers

```powershell
python -m level_factory -C C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws run category5_baie_dore_001 --art --gameplay
```

Zoo swaps + Pixelcoat + Patina + Lux, then Dispatch over the art scene.

### Step 7 — the package

```powershell
python -m level_factory -C C:\Projects\gabagool_studios\gabagool_factory\workspaces\cold-7001-ws export category5_baie_dore_001 --mode portable-godot
```

**The run ends when a gated package exists.** Anything after that point is not
counted, per the instrument's own definition.

### Step 8 — stop the clock

```powershell
python tools\cold_run.py --end
```

Writes `after.json` and `diff.json` beside the journal under
`_runs\cold\cold_7001\` and prints the verdict. `diff.json` carries the
attribution too — `attributed` with a reason per file, `unattributed` without.
Exit `0` means zero interventions; exit `1` means the run needed hands and the
report says where.

### Step 9 — grade the output (observation only)

```powershell
python tools\check_all.py
```

`0` checked-clean, `1` checked-found, `2` COULD NOT check. This answers *is the
level any good*, which is a different question from *how many hands did it take*.
Both belong in the report; neither substitutes for the other.

---

## Operating rules while the clock runs

**`--note` an intervention the moment you make it, not at the end.**

```powershell
python tools\cold_run.py --note "dc: widened wall_span tolerance, run 4 crashed on a 0.04 sliver"
```

Note it even when you are sure the hash will catch it — the hash says *a file
changed*, the note says *why*, and the report is worth little without both.
Notes are also the only record of interventions the hash cannot see: a
hand-edited workspace file, or a re-run with different arguments.

**`--retry` is for re-running the IDENTICAL command after a transient.**

```powershell
python tools\cold_run.py --retry "blender exited 1, no output written; same command second time worked"
```

Reported as its own figure, deliberately. A pipeline needing six retries is not
a pipeline needing six patches, and conflating them flatters one and slanders
the other.

**A re-run with different arguments, or with a flag the original did not carry,
is an intervention** — `--note` it, not `--retry`.

**Reading logs, running gates, taking measurements: not interventions.**
Observation never counts — but record it anyway, with `--observe`:

```powershell
python tools\cold_run.py --observe "all five candidates fail LT route completion at 0%"
```

Reported as its own figure and counted toward nothing. It exists because a
correction to an earlier journal line once had to be filed with `--note` for
want of it, and inflated `cold_7001`'s count by one (roadmap 70).

**The pipeline writing into a tool repo is not an intervention either.** Level
Factory writes one DC spec per candidate into `deli_counter\specs\`, and DC
regenerates the index beside them. `--end` attributes those against the
`GENERATED` table in `cold_run.py`, prints the reason next to each file, and
leaves them out of the count. Read the reasons — that table is a claim about
who writes where, and a wrong entry there hides a real edit. Anything the
table does not claim is counted.

**If the run dies unrecoverably, still `--end` it.** A run that could not finish
is a result, and an abandoned journal with a live `ACTIVE` marker blocks the
next label.

---

## What to do with the number

Write it into item 17's status line in `PIPELINE_ROADMAP.md`, with the tool
versions from Step 1 and a one-line summary per intervention. Then:

- **Zero.** The first real evidence, and item 17 says so. It does not close the
  item — one run proves less than it feels like it does. It licenses run 2.
- **Non-zero.** Each intervention is a defect with a reproduction already
  attached. File them as roadmap items, fix them **in the tool repos** (never in
  a workspace), and re-run at a new seed. The count going down across runs is
  the only progress this metric recognises.
- **DISAGREEMENT printed.** Files moved and nothing was noted. The hashes are
  the fact; read `diff.json` before quoting anything.

## Run 2 — the other half of the coldness

Run 1 holds the vocabulary fixed. Run 2 changes it: **`bank_block_001` at
`seed_base 7002`** — a different archetype (`urban_bank`), a different site
shape (`street_block`), a different theme family (`delco_1997`), 3 buildings
instead of 4.

Set it up the same way — `docs\cold_runs\cold_7002\` with `batch.json` and a
verbatim copy of `level_factory\examples\delco_batch\briefs\bank_block_001.json`
— in its own fresh workspace, under label `cold_7002`.

**Known risk, flagged rather than pre-solved:** the brief declares
`"theme": "delco_1997"`. Pixelcoat carries `profiles\themes\delco.json` and the
Zoo species carry a `delco` style; whether `delco_1997` resolves to those, or
falls through, is not established here. If it falls through, that is a real
finding of a different class from a pipeline defect — a spec naming a theme the
kit does not carry — and it should be recorded as such rather than quietly
patched mid-run.

Do not run 2 before run 1. Two unknowns at once cannot be told apart.
