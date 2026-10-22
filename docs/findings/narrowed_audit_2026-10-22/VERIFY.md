# Brief: refute proposed roadmap closes (read-only)

A first pass audited the NARROWED items of `C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md` and
proposed changing some of their statuses to CLOSED, SUPERSEDED or ANALYSIS. Before any of that is written into the
roadmap, you try to BREAK each proposal. A wrong close buries undone work; that is the failure you are here to catch.

## Input

`all_results.json` in this folder holds every first-pass result. Your prompt names the item numbers you check. For
each, read: its result object (`remainder`, `per_piece`, `proposed_status`, `notes`), and the item itself in the
roadmap -- its heading `**N. ` and the status block directly above it (`grep -n "^\*\*N\. "` on the roadmap; the
status is the paragraph just above).

## For each item

1. List every factual claim the proposed status makes: each file:line, commit, version, figure, quotation and
   cross-reference to another item.
2. Check each one yourself by opening it. A file:line must say what is claimed; a figure must be in the cited record;
   a quoted line must be verbatim; an item said to be CLOSED must be CLOSED in the roadmap, and an item said to carry
   something must actually say so.
3. Then ask the question the first pass may have skipped: does what was found do the specific thing the item's
   remainder asks for -- on the path the item names, proven where the item asks for proof (a package, a cold run,
   the walker's eye)? A similar feature, a partial cover, or code that exists but never ran where the item asks, is
   NOT a close.
4. Verdict: `UPHELD` (every claim checks and the remainder is genuinely done/taken over/not a task), `UPHELD_WITH_FIXES`
   (the conclusion stands but some claims are wrong or loose -- give the corrected status text), or `REFUTED` (the
   item should stay NARROWED -- say exactly what is still undone and how you know).

## Rules

- **The factory root's `.gitignore` excludes every tool repo** (`lot`, `level_factory`, `deli_counter`, `zoo`, `lux`,
  `patina`, `pixelcoat`, `dispatch`, `lasertag`). A search started at the root silently skips them. Search inside
  each tool repo's own folder (Grep with `path` set to it), or `git -C <repo> grep`.
- Read-only. Edit nothing anywhere except your output file. No builds, tests, Godot, Blender, or scripts that write.
  Read, Grep, Glob and read-only git/`ls` only. Absolute paths in every shell command; `C:/...` for Windows Python.
- Cite only what you opened in this run.

## Output

Write `verify_<your letter>.json` in this folder (letter in your prompt), rewriting it after each item: a list of

```json
{"n": 17, "verdict": "UPHELD | UPHELD_WITH_FIXES | REFUTED",
 "checked": ["claim -> what the file actually says (file:line)"],
 "problems": ["each wrong or unsupported claim, and what is true instead"],
 "corrected_status": "full corrected *STATUS: ...* text when UPHELD_WITH_FIXES, else empty",
 "why": "one paragraph"}
```

Final reply: under 200 words -- one line per item with its verdict and the reason.
