# The narrowed audit, 2026-10-22: what "NARROWED" was hiding

**The question**, the walker's, 2026-10-21: "the 107 narrowed...does that mean they are close to finishing?" (the
index said 108; one, item 42, has its status glued under a paragraph, which a one-line regex missed and
`roadmap_status.parse` does not). **The answer: mostly no.** Of 108, 15 were in fact finished, taken over or not a
task, and now say so; 93 stay NARROWED, and of the 91 audited among them 32 have a large remainder, 31 medium and 25
small. "NARROWED" has meant "something shipped", not "nearly done". This is roadmap hygiene, not a cut in
interventions-per-level: it makes the list honest so the next pick is a real one.

## Method

1. `extract.py` -- every NARROWED item, by the index's own parser, its newest status cut at "Earlier status kept:"
   and its body, balanced into ten batches (`batch_01..10.json`). 293 and 296 were kept out: the walker's answers
   on the drawings page (`docs/findings/walker_review_2026-10-21_drawings/verdicts_2026-10-22/`) decide them.
2. First pass, `BRIEF.md`: ten read-only auditors, one batch each, each remaining piece checked against today's
   repos with file:line evidence -- verdict DONE / OPEN / WALKER / SUPERSEDED / MOOT / ANALYSIS / UNCLEAR, the size
   left, what it bears on, and work done since the newest status (`result_01..10.json`, merged `all_results.json`).
3. Second pass, `VERIFY.md`: three adversarial verifiers took every proposed change of status and tried to break
   it -- every cited line opened, every quote and figure checked, and whether the thing found does the item's
   specific job where the item asks for proof (`verify_A/B/C.json`, merged `verify_all.json`).
4. `table.py` -> `table.out.md`: the per-item table and tallies.
5. The roadmap: `patches/patch_roadmap_narrowed_audit.py` (made by `patches/roadmap_narrowed_audit/`, dry-run on a
   scratch roadmap, a second run refused, the index regenerated and checked; outside the index only the 19 status
   blocks moved).

## What changed

| outcome | items |
|---|---|
| CLOSED (7) | 87, 90, 138, 139, 141, 144, 158 |
| SUPERSEDED (5) | 64 (by 79's step 6), 81 (84's decision), 127 (spawns provisional), 140 (by 238), 142 (by 147) |
| ANALYSIS (3) | 166 (load time is a trade), 222 (a shadow control that misses unexplained), 247 (Godot's own ids) |
| corrected | 14: its SUPERSEDED said the walk test walks the crew's body; it walks a 0.28 m capsule (below) |
| the walker's answers | 293, 296 stay NARROWED; 295 OPEN, now the rotatable view's home |

The second pass refuted none of the fifteen; nine went in with its corrections: 138 is CLOSED, not superseded, and
its rig's path was wrong; 139 credited a factory frame to the walker; 140 put a changelog's words in the walker's
mouth; 144 missed that item 250 carries the walker's own ask for a stair species; 158's walker verdict was on frames,
not a walk; 166 quoted a figure the changelog's prose has and its table does not; 222's figures were one night's,
not 0.77.0's; 64 had two items pointing at it; 90's null is opt-in.

**Held NARROWED, not closed:**

- **17**, the acceptance test for interventions-per-level: met in letter -- cold runs 9181 and 9191 and three before
  them, five never-run specs out first time, 0 interventions -- but every brief was written in-house, which
  `docs/COLD_RUN.md` says "would measure the author rather than the tools", and 9191 shipped with all three
  candidates out on `LT_MAP_ENEMY_PATHING_BROKEN`. Closing it means amending CLAUDE.md's "Nobody has measured this
  number yet": the walker's file and the walker's call (verify_A.json carries a drafted status).
- **117**: its proposed ANALYSIS rests on a census the first pass ran in memory and never filed, so nothing can
  re-check it; and no lint reports a wall standing on a link-only `floor_hole`/`hatch` hole -- the case it waits for
  would pass unnoticed. Arming that tripwire is the one cheap step left.

**Refuted on the way, item 14** (closed 2026-10-15): its status and `docs/findings/open_items_remeasure/README.md`
said "the walk test walks the crew's body over every leg of every candidate (208)". It does not:
`lot/godot/addons/heist_nav_qa/nav_qa_director.gd` walks `AGENT_RADIUS * 0.7`, 0.28 m (:40, :818), on 56 degrees
(:830), read again here; the crew's body walked once, on patched copies (208). Both texts corrected, the old kept.

## Left: what the 91 audited still-NARROWED items need

- **The walker's (7 items)**: 146 a re-walk of the per-room finishes; 153 whether the street reads as one to drive
  and cross; 186 the window neon behind the pane (cold 9191); 202 a Linux run; 215 the responder-arc rule (leave,
  open road ends, or soften); 239 resume the paused cold-run speed backlog or not; 250 three looks (the storey-1
  rail from below, the door sign in the band's colours, a corner shop's window depth). 28 OPEN items also carry a
  walker piece (`per_piece` state `walker`).
- **Small and the factory's (21)**: 36, 53, 58, 59, 78, 83, 85, 112, 118, 132, 143, 161, 162, 163, 174, 189, 192,
  206, 242, 243, 265. 83 has one breach panel one light over the cap; 145 one offset to derive; 242's own condition
  is met and only two Laser Tag grader leftovers hold it.
- **What they bear on (82 OPEN)**: quality 47, hygiene 15, gunfights 10 (10, 12, 22, 156, 171, 189, 199, 208, 230,
  288), performance 4, other 4, interventions 2 (59, 111).
- **Work done since a status and never recorded**: 34 OPEN items (`table.out.md`). This is first-pass evidence and
  NOT second-checked, so it is here and not in their statuses; re-narrowing each wants its pieces checked first.

## What this audit could get wrong

- **The root `.gitignore` excludes every tool repo**, so a search started at the root skips them silently (found by
  batch 10's auditor mid-run). An OPEN verdict resting on "a search found nothing" may be blind where an auditor
  searched from the root. Only the proposed status changes were second-checked; the OPEN verdicts were not.
- `extract.py`'s bodies sometimes ran past the item into the next one's status (87 into 88, 117 into 118, 152 into
  153: the auditors noticed and set it aside). The newest statuses were cut correctly.
- The auditors ran only read-only commands; three ran Python that read the libraries in memory (`python -B`); one
  import refreshed a gitignored `deli_counter/__pycache__/prop_species.cpython-314.pyc`; two made and deleted a
  scratch file in the audit folder; one was refused `tools/massing.py` and tallied by reading instead. No tracked
  file in any repo changed.
