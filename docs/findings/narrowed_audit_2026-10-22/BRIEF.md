# Brief: audit of the roadmap's NARROWED items (read-only)

You are auditing part of `PIPELINE_ROADMAP.md` in the factory at `C:\Projects\gabagool_studios\gabagool_factory`.
108 of its 298 items are NARROWED: partly closed, with a remainder stated in the item. The owner asked whether
"narrowed" means "close to finishing". Your job is to settle that for YOUR batch, item by item, from the repos as
they stand TODAY (2026-10-22), with evidence. You change nothing in any repo.

## What the factory is

The factory root holds one git repo per tool, as subdirectories, plus the factory's own records:

- Tool repos (each its own git repo, each with `VERSION` and `CHANGELOG.md`): `lot` (site assembly),
  `level_factory` (orchestration, export, packaging, presentation), `deli_counter` (building shells, furnishing,
  stairs, agent contract), `zoo` (props/species), `lux` (lighting), `patina` (wear), `pixelcoat` (materials, signs),
  `dispatch` (packaging), `lasertag` (bots/gameplay QA).
- Factory records: `patches/` (every shipped change as a `patch_*.py` plus a folder of its evidence; the patch's
  docstring says what it did), `docs/findings/<topic>/` (investigations), `docs/cold_runs/cold_N/NOTES.md` (each
  cold run's record: a level built end to end with nobody touching it; "interventions" = hand-patches it needed),
  `tools/`, `CHANGELOG.md`, `PIPELINE_MAP.md`.
- `workspaces/` and `rockay-ws` are mission workspaces: generated output and vendored COPIES of tool addons. Read
  them as evidence of what a tool produced if useful, but a copied `.gd` there is not the tool's source.

`CLAUDE.md` at the root is the repo's judgment file. Read its sections "Verification", "Instruments" and "A null
result is not a refutation" before you start; they describe exactly how audits here have gone wrong before.

## Your input

`batch_NN.json` (your number is in the prompt) in this folder: a list of items, each with
`n`, `title`, `line` (the heading's line in `PIPELINE_ROADMAP.md`), `newest` (the item's newest status, up to
"Earlier status kept:"), `earlier_chars` (how much older status history follows -- read it in the roadmap at
`line` if you need it), and `body` (the item text).

The newest status is usually where the remainder is named ("LEFT:", "REMAINING:", "what did not get built", "the
gap is unchanged"). Older items have no "What would close it" section: then the remainder is whatever the body
asked for that the statuses do not report done.

## For each item

1. **State the remainder** in your own words, as concrete pieces (one per thing that is not done), each traceable to
   a sentence of the item. Quote the sentence briefly.
2. **Check every piece against today's repos.** The newest status has a date; work after that date may have done
   a piece without anyone updating this item. Look in: the owning tool's `CHANGELOG.md` and `git -C <repo> log`
   after that date; its source (grep the names the item uses: functions, codes like `LOT_DESTINATION_ABOVE_FLOOR`,
   files, knobs); `patches/` names and docstrings; `docs/cold_runs/*/NOTES.md`; and LATER roadmap items -- grep
   the roadmap for "item N", "roadmap N", "(N)" and the item's key terms, since a later item often takes over,
   answers or supersedes an earlier one. The generated index near the top of the roadmap lists every item's status.
3. **Decide a verdict**:
   - `DONE` -- every remaining piece is done now. One citation per piece, of code you READ in this run (file:line)
     or a commit/changelog line plus the code it names. If the item asks for proof in a package or cold run, the
     proof is part of done: code shipped but never run where the item asks is `OPEN`, and say which half is missing.
   - `OPEN` -- at least one piece is genuinely undone and is the factory's to do. Give the evidence it is undone
     (the grep that finds no such check; the file that still has the old shape). If some pieces have been done
     since the newest status, list those separately with evidence (`done_since`), so the item can be narrowed
     further.
   - `WALKER` -- the only thing left is a decision or taste call that belongs to the walker (the project owner, who
     plays the levels). Quote the question.
   - `SUPERSEDED` -- the remainder is now tracked by a later item, or the design it assumed was replaced. Name the
     item or change and quote the line that takes it over.
   - `MOOT` -- the remainder no longer applies: the code, feature or path it concerns was removed or rebuilt. Cite.
   - `ANALYSIS` -- what is left is not a task: a standing finding or constraint with no work to do.
   - `UNCLEAR` -- cannot be decided by reading; say exactly which run or measurement would decide it.
4. **Size** what is left: `small` (one patch in one repo), `medium` (a patch plus a cold run, or two repos),
   `large` (a new capability, several tools, or a design question first). Use `none` for DONE/MOOT/ANALYSIS.
5. **Bears on**: what doing the remainder would move -- `interventions` (a level that needs a hand-fix without it),
   `quality` (how a level looks/feels), `gunfights` (navigation, cover, sightlines), `performance`, `hygiene`
   (records, naming, tooling), or `other`.
6. If the verdict is DONE, SUPERSEDED, MOOT or ANALYSIS, draft `proposed_status`: one paragraph in the roadmap's
   voice -- `*STATUS: CLOSED 2026-10-22 -- <what proves it, with versions, figures and file:line>*` (or SUPERSEDED /
   ANALYSIS). No line breaks inside it. Figures over adjectives; cite what you read.

## Evidence rules (these are the ones this repo has been burned by)

- **Cite only what you read in this run.** A function's name is not its behaviour: open it. "There is a function
  called `check_anchor_floor`" is not evidence that anchors are checked; the lines that do the check are.
- **A similar feature is not the same feature.** Confirm the thing found does the specific job, on the specific
  path, the item asks for. If it covers part, say which part.
- **Name what produced an artefact** before using it as evidence: which tool, which job, which build.
- **Do not guess a schema**: if you read a JSON record, read a real instance and quote the key you used.
- **When you cannot tell, say UNCLEAR.** A wrong DONE costs more than an honest UNCLEAR: the item would be closed
  with its work undone. A wrong OPEN costs a re-check.
- Report what you measured; argue causes in `notes`, briefly.

## Hard limits

- **Read-only.** Do not edit, create or delete any file anywhere except your own result file (below). Do not run
  builds, tests, cold runs, Godot, Blender or any script that writes files. Allowed: Read, Grep, Glob, and
  read-only shell commands (`git -C <repo> log/show/grep/diff`, `ls`, a Python one-liner that only reads). No
  `git fetch/checkout/reset/stash`, nothing that touches the network.
- Use absolute paths in every shell command (the shell's working directory is shared and drifts). On Windows
  Python, write paths as `C:/Projects/...`. Prefer the Read and Grep tools to shell pipelines.

## Output

Write `result_NN.json` in this folder (same NN as your batch): a JSON list, one object per item, in batch order.
**Rewrite the whole file after finishing EACH item**, so work survives if you run long. Each object:

```json
{
  "n": 9,
  "title": "...",
  "remainder": ["piece 1, with a short quote of the sentence it comes from", "piece 2 ..."],
  "verdict": "DONE | OPEN | WALKER | SUPERSEDED | MOOT | ANALYSIS | UNCLEAR",
  "per_piece": [{"piece": "piece 1", "state": "done | undone | walker | superseded | moot | unclear",
                 "evidence": "file:line / commit / item -- what it shows", "checked": "how you checked"}],
  "done_since": ["piece done after the newest status, with evidence"],
  "size": "none | small | medium | large",
  "bears_on": "interventions | quality | gunfights | performance | hygiene | other",
  "proposed_status": "",
  "notes": "anything the reviewer must know; doubts; what would decide an UNCLEAR"
}
```

Your final reply (not the file) should be SHORT, under 300 words: the count per verdict, then one line per item
that is not OPEN saying why. The file carries the detail.
