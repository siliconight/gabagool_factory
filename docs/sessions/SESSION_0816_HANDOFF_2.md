# Handoff — 2026-08-16, second

*Read this first. It is written so a session that has never seen this project
can start work without asking anything. It replaces
`SESSION_0816_HANDOFF.md`, which is still accurate about the three defects it
diagnosed and is now wrong about line endings — its rule there carries a
SUPERSEDED note in place.*

---

## 1. The next task, and what is known about it

**Re-export `lot_demo_001` under level_factory 0.40.0 and lot 0.42.0.**

It has been the second-ranked open item for days and it is now the first,
because three separate changes have shipped that have never been seen on more
than two buildings:

1. **level_factory 0.40.0** — one resource manifest per package instead of two.
   Tagged 2026-08-16, and it sat UNCERTIFIED until `factory-v1.26.0` today.
2. **lot 0.42.0, `clear_crew_spawn` before the cover plan** — `assemble` used
   to plan cover from a crew spawn the scene does not ship.
3. **lot 0.42.0, crew-first cover ordering** — the opening cover budget is now
   spent on the crew's sightlines before the rest of the map's.

Every measurement behind 2 and 3 was taken on `tests/test_site_cover.py`'s
yard fixture: **two 16 × 16 buildings on a 220 × 140 plate, no real collision
reading.** `lot_demo_001` is five buildings with 959 colliders. Nothing about
the cover work has met that.

### What to watch, specifically

**The crew's lines should close, and `open_lines` should be 0 or small.** On
the yard, crew-first closed all seven crew lines with 3 of the 12 opening
pieces. Five buildings means more marker pairs and more competition for the
same budget (`plan_cover`'s `limit` is 12 and `assemble` does not override it).
If `LOT_SIGHTLINE_OPEN` fires, read it before treating it as a regression —
`site_cover.findings` grades it **minor** and its own message says "it is a
design note, not a broken level". A crew line left open is the thing that
matters; an objective-to-enemy line left open may be correct.

**`cover_points["LT_PlayerSpawn"]` must equal the `LT_PlayerSpawn` in the
shipped walk scene.** That equality is the whole of fix 2. On the yard it was
(-70.0, 30.0) against (-60.5, 30.0) — cover planned for a crew standing inside
a building.

**The two `place_enemies` calls should agree.** See roadmap item 3, below.

### The instrument exists but does not fit yet

`lot/tools/probe_r51_cover_enemies.py` wraps `place_enemies` and `plan_cover`
for one real `lot.assemble` run and reports every call that fired — caller,
inputs, occluder source, outputs — then re-runs the failing assertion against
each candidate set. It is READ-ONLY apart from a temp dir.

It imports its fixture from `tests/test_site_cover.py`, so **it will not run
against `lot_demo_001` unmodified.** Point it at the real mission rather than
rebuilding the fixture by hand; rebuilding inputs by hand is the defect it was
written to investigate.

### What is NOT known

The command to re-export `lot_demo_001` is not recorded here, because nobody
has run it this month and the workspace it lives in was not located. The shape
is the one `run_3b_unlit.ps1` uses:

```powershell
python level_factory\apps\cli\main.py -C <workspace> export lot_demo_001 --mode <mode> --format folder
```

Find the workspace before assuming it. `workspaces\unlit-3b-ws` is the
`unlit_probe_001` bed, not this one.

---

## 2. State as of this handoff

Everything is committed and pushed. All three trees are clean — verified, not
assumed.

| repo | version | tag | HEAD | clean |
|---|---|---|---|---|
| level_factory | 0.40.0 | `v0.40.0` | `5bd29d1` | yes |
| factory (coordination) | 1.26.0 | `factory-v1.26.0` | `9b25111` | yes |
| lot | 0.42.0 | `v0.42.0` | `df848df` | yes |

**`factory-v1.26.0` is at `8c7db41`, four commits behind HEAD.** Those four —
`.gitattributes`, the handoff supersede note, roadmap item 3, and the
`roadmap_status.py` fix — change no tool version, so the certified SET is
unchanged and the tag is where it belongs. Do not "fix" it by re-tagging.

`lot` suite: **336 passed, 0 failed** in 3.59s.

Roadmap: **48, 49, 50, 51 CLOSED.** **3 NARROWED.** 25 of 51 items still have
no explicit status line — `python tools\roadmap_status.py --unclassified`.

### What changed today

1. **Roadmap 51 closed — three defects, and the item's own diagnosis was right
   about one of them.** Defect one (six stale test callers) was as written.
   Defect three was NOT "the scene loses the plan" and not 48's family; a test
   planned from a route the tool never uses, and the scene carried its plan to
   0 of 18 failing coordinate pairs. Defect two was NOT "the search or the
   check"; cover was planned for a crew standing inside a building, and then
   the opening budget never reached the crew at all — 12 pieces, 0 touching the
   crew, 6 breaking enemy-to-enemy sightlines. `test_site_cover.py` was never
   modified; it asserted the right contract throughout.
2. **level_factory 0.40.0 was shipped but not certified.** `factory-v1.25.0`
   pinned 0.39.0 while `v0.40.0` had been tagged and pushed, so the certified
   set omitted the fix the roadmap recorded as closing item 50. Certified in
   `factory-v1.26.0`, with the gap recorded in the manifest's own note.
3. **~30 patch scripts and probes from prior sessions were never tracked.**
   `git commit -a` stages modified tracked files and silently skips new ones,
   so every one of those commits looked clean. The roadmap cited
   `patch_lf_038/039/040` by filename as the record for items 48–50; that
   provenance existed only on one disk. Recovered in `333e276`.
4. **LF is canonical now.** `core.autocrlf = input` had been storing every blob
   as LF and never converting back, so the working copy and the repository
   disagreed on every text file and nobody could see it. `.gitattributes` sets
   `* text=auto eol=lf` (`f2713e9`) and the working copy was renormalised.
5. **`roadmap_status.py --write` was rewriting all 4,525 line endings** on every
   run, invisibly. Fixed in `9b25111`.

---

## 3. Conventions this project runs on

**Every code change ships as a patch script** in `patches\`, with `--check`,
`--revert`, `--selftest`. Anchored text edits that **refuse on drift** rather
than fuzzy-matching. `.pre_<tag>` sidecars for revert. Print byte counts and
sha256. Check every file it touches exists BEFORE editing any of them.

**Gate the apply on the selftest.** PowerShell does not stop on a non-zero
exit, so a failing `--selftest` will sail straight into a write unless you say
otherwise. This happened today.

```powershell
python patches\<patch>.py --selftest
if ($LASTEXITCODE -ne 0) { throw "selftest failed - not applying" }
python patches\<patch>.py --check
if ($LASTEXITCODE -ne 0) { throw "check failed - not applying" }
python patches\<patch>.py
```

**`_eol()` is keyed off the FILE, never off an anchor** — and never off a
remembered constant. LF is canonical repo-wide as of `f2713e9`, but read the
file anyway; that is the rule that made today's renormalisation a non-event.
`.pre_*` sidecars are gitignored byte copies, so older ones are still CRLF and
are supposed to be.

**`Path.read_text()` normalises newlines on the way in; `Path.write_text()`
denormalises on the way out.** The round trip looks lossless in Python and
rewrites every line ending on disk. Use `newline=""` when writing, or
`read_bytes`/`write_bytes` throughout.

**Selftests must be able to fail.** Recurring mistakes, all caught:
- `A and B or C` — `and` binds tighter, so a loose `C` swallows the test.
- Searching for a string that spans a line break. Match whitespace-normalised.
- **Counting a bare name that the patch's own comment also contains.** This
  happened SEVEN times in one session and a selftest caught it every time.
  Count the call form (`site_spawns.clear_crew_spawn(`), or count on
  non-comment lines, and print the naive count alongside so the gap is visible.
- **Prove a new check can fail** by removing the evidence and re-running it.

**Selftests run `tests/unit` whole and read pytest's RETURN CODE**, not its
text. `rc=5` (collected nothing) is a FAILURE — it is what a broken import
looks like.

**`level_factory/pyproject.toml` sets `addopts = "-q"`.** Passing `-q` again
makes it `-qq` and pytest drops the count line. `lot` has no such setting.

**After any roadmap edit:**

```powershell
python tools\roadmap_status.py --write
python tools\roadmap_status.py --check
```

The status table is DERIVED. Items carry `*STATUS: <VERB> <date> -- <evidence>*`
one line above them. Vocabulary: `OPEN` / `CLOSED` / `RETRACTED` / `NARROWED` /
`SUPERSEDED` / `ANALYSIS`.

**`level_factory\` and `lot\` are their own git repos** and are gitignored by
the factory repo. Commit their changes from inside them; commit
`PIPELINE_ROADMAP.md`, `patches\`, `tools\`, `docs\` and `factory.manifest.json`
from the factory root. **`git add -A`, not `git commit -a`** — the latter skips
new files silently and cost this project 30 untracked artifacts.

---

## 4. Hard-won working rules

**Do not reason ahead of a verified read.** Item 49 got three mechanisms before
the right one. Today, four of five confident mechanisms were refuted by one
measurement each: the ordering hypothesis for defect three, the `solids`
hypothesis for defect two, "the roadmap is CRLF so the handoff will have
shrunk", and "`--renormalize` will stage the roadmap". Each took one command to
disprove and would have taken a paragraph to argue.

**SEARCH THE ROADMAP FOR THE BEHAVIOUR, NOT JUST THE CODE FOR THE SYMBOL.**
Roadmap item 3 — "Lot places enemies twice, and nothing checks the two agree" —
names both call sites and had an explicit OPEN status line re-confirmed on
2026-08-12. An item-51 investigation grepped `lot.py` for `place_enemies`,
found both sites, diagnosed the divergence from scratch, and presented it as a
new finding. The roadmap already knew. Before writing up anything as new, grep
`PIPELINE_ROADMAP.md` for the behaviour in plain words.

**The device bridge serves stale files, sometimes at the correct byte count.**
Have a FRESH scratch file written — a file with no previous version cannot be
served stale — stamped with the source's size and sha256:

```powershell
$f = "<path>"
$lines = [System.IO.File]::ReadAllLines((Resolve-Path $f))
$out = Join-Path (Get-Location) "_scratch\<name>.txt"
$hdr = @("FILE   : $f",
         "BYTES  : $((Get-Item $f).Length)",
         "SHA256 : $((Get-FileHash $f -Algorithm SHA256).Hash)",
         "LINES  : $($lines.Count)", "")
[System.IO.File]::WriteAllLines($out, ($hdr + $lines))
```

Then reconstruct the body and check it lands EXACTLY on the reported byte
count. A delta of zero at six significant figures is not a coincidence.

**But that dump destroys line-ending information.** `ReadAllLines` +
`WriteAllLines` normalises, so the dump cannot tell you what the source used.
You can INFER the mix from arithmetic — `.gitignore` reconstructed to 1,209 as
all-LF and 1,267 as all-CRLF against a reported 1,241, which is 32 CRLF and 26
LF and nothing else — but you cannot recover which lines. If endings matter,
measure them on the machine.

**`git status` can be silent while the disk and the repository differ.** Git
compares through the clean filter, so a file that is CRLF on disk and LF in the
repo reads as unmodified. A 4,529-byte difference sat there today reporting
clean. Do not use `git status` as evidence about bytes.

**Working style the user asked for:** *"either give me the PS to run in shell
or don't give me a verb."* Any action addressed to them arrives as runnable
PowerShell. `pwsh`, not `powershell` — 5.1 writes a BOM and tools refuse it.
No bash heredocs. Watch escaping in `Select-String -Pattern`: use
`[regex]::Escape()` rather than hand-escaping quotes.

---

## 5. Everything else still open, ranked

1. **`lot_demo_001` re-exported under 0.40.0 / lot 0.42.0** — section 1.
2. **Roadmap item 3, NARROWED.** The two `place_enemies` calls now agree, but
   item 3 asked to "place once, thread the result through, or assert the two
   agree" and got NEITHER. They agree by determinism from identical inputs,
   which is exactly the "same inputs, same answer" claim item 3 calls untested.
   `assemble` and `write_walk_scene` still derive the mission points twice.
3. **Cover planning is coupled to `place_enemies`.** `plan_cover` ranks
   everything by marker pairs that include enemy spawns. If enemy placement
   moves to the gameplay layer — the stated intent — `plan_cover` loses the
   input it prioritises by. Decide the shape before that move, not after.
4. **Enemy-to-enemy pairs still consume opening cover budget** once the crew is
   served. Excluding them outright measured 7 opening pieces and 18 total
   against 12 and 23, with the same zero open lines — fewer pieces, same
   result. Separate decision about what `open_sightlines` should return.
5. **Lux is decoupled in the DAG but coupled by filename.**
   `lux.applied.tscn`, `lux.quality.json`, `lux.validation.json` are string
   literals across 8 modules / 27 sites. Change a Lux output name and
   `walk_preview`'s `has_lux` reads False and silently renders unlit.
   `_preset_for` also hardcodes Lux preset DISPLAY names where a wrong name is
   a silent no-op.
6. **Three version sources disagree.** `doctor` reports drift against
   `packages/tools/contracts.py`'s `GROUNDED` (e.g. lot "certified 0.18.3")
   while `factory.manifest.json` pins lot 0.42.0. Plus `tools.lock.json`. The
   manifest-versus-shipped-tag instance was fixed today; this one is untouched.
7. **`roadmap_status.py` reads with `errors="replace"` and writes the result
   back.** Any byte that fails to decode becomes U+FFFD and is then PERSISTED
   over the original on the next `--write`. Nothing has hit it. It is a lossy
   read-then-write-back on the project's largest document.
8. **25 of 51 roadmap items have no explicit status line.** Half the roadmap is
   inferred. `--unclassified` lists them; 15 infer OPEN.
9. **Roadmap 44 / 45 / 46** — Zoo collision substitutes, non-collision surface
   dressing, interactive state machines. Specified, nothing built.
10. **Dispatch real-tools test is skipped** for missing
    `build/lux/lux.profile.json` fixture data. 9 real_tools, 1 skipped.
11. **The `--unlit` interface shape.** The planner has a real fourth layer
    (`LAYER_LIGHT`, `_LAYER_REQUIRES = {LAYER_LIGHT: LAYER_ART}`) but the CLI
    expresses it by subtraction: `--art` means art AND light, `--unlit` removes
    light. There is no positive `--light`.

---

## 6. Artifacts and known-good hashes

New this session:

- `lot/tools/probe_r51_cover_enemies.py` — read-only; wraps `place_enemies` and
  `plan_cover` for one real `assemble` and reports what actually fired. It
  refuted its own author's hypothesis twice.
- `patches/patch_lot_stale_spawn_callers.py`, `patch_lot_hook_plan.py`,
  `patch_lot_cover_ships_spawn.py`, `patch_lot_cover_crew_first.py` — item 51.
- `patches/patch_r52_lot_release.py`, `patch_r52_factory_certify.py` — releases.
- `patches/patch_r52_gitattributes.py`, `patch_r52_gitattributes_cite.py`,
  `patch_r52_handoff_eol_note.py`, `patch_roadmap_status_lf.py` — endings.
- `patches/patch_roadmap_51_mechanism.py`, `patch_roadmap_51_defect_two.py`,
  `patch_roadmap_03_narrowed.py` — roadmap.

**Known-good hashes** (2026-08-16, after all of the above; first 12 of sha256):

```
lot/lot.py                                103,033 B  998C3D27ED56
lot/site_cover.py                          40,013 B  56C56597C324
lot/site_spawns.py                         53,893 B  619F4C3C178D
PIPELINE_ROADMAP.md                       272,806 B  B5EE33245664
tools/roadmap_status.py                     9,967 B  9722A0EA70A8
level_factory/packages/exporting/export.py 37,159 B  979BF39F07FE
level_factory/packages/exporting/closure.py 12,146 B 1467E73D1326
```

Regenerate with:

```powershell
foreach ($f in @("lot\lot.py","lot\site_cover.py","lot\site_spawns.py",
                 "PIPELINE_ROADMAP.md","tools\roadmap_status.py",
                 "level_factory\packages\exporting\export.py",
                 "level_factory\packages\exporting\closure.py")) {
  "{0,-46} {1,8} B  {2}" -f $f, (Get-Item $f).Length,
    (Get-FileHash $f -Algorithm SHA256).Hash.Substring(0,12)
}
```

**A note on this session's error rate, because it is the useful part.** Seven
selftest assertions were wrong on first write — every one a count of a token
the patch's own documentation contained. Four confident mechanisms were refuted
by a single measurement each. One patch was applied over a failing selftest
because the PowerShell had no gate. One finding was re-derived from scratch
that the roadmap already held. Every one of these was caught by an instrument
rather than by thinking harder, and none of them reached a shipped artifact.
That is the case for the conventions in section 3, stated as evidence rather
than as advice.
