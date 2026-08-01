# Factory hygiene — auditing and clearing artifact bloat

The tools generate a lot of regenerable output (renders, previews, build dirs,
caches, skin packs). Left alone it grows without bound. This is the repeatable
way to see it and clear it safely.

## The one rule

**A file is either _source_ (tracked in git, kept forever) or a _regenerable
artifact_ (an output/cache, safe to delete and rebuild).** Keep artifacts in a
small, known set of directories so a script can find and clear them without ever
guessing at source.

## The job

`factory_clean.ps1` audits and clears a **curated allow-list** of artifact dirs
and junk files — nothing else:

```
build/  dist/  exhibits/  _preview/  _skins/  _runs/  _out/  .godot/
__pycache__/  .pytest_cache/  .mypy_cache/  .ruff_cache/  *.egg-info/
*.pyc  *.pyo  *.tmp  *.blend1
```

Usage:

```powershell
# AUDIT — report every artifact and its size, grouped by tool. Deletes nothing.
powershell -ExecutionPolicy Bypass -File factory_clean.ps1

# CLEAR — delete exactly what the audit listed.
powershell -ExecutionPolicy Bypass -File factory_clean.ps1 -Apply
```

Run the audit anytime; run `-Apply` when the numbers justify it. It's idempotent
— run it as often as you like.

## Why not `git clean -xfd`?

That's the usual answer, and it's a trap here: `git clean -x` deletes **all**
ignored files, which includes *precious* ignored files — `tools.local.json`,
`.env`, local settings. The allow-list approach only ever touches known
regenerable names, so local config and source are safe by construction. It also
doesn't depend on every repo's `.gitignore` being perfect.

## Stop the bloat at the source (.gitignore)

So artifacts never get *committed* in the first place, make sure each tool repo
ignores the same set. Safe baseline to merge into each repo's `.gitignore`:

```gitignore
# caches
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/

# regenerable outputs
build/
dist/
exhibits/
_preview/
_skins/
_runs/
_out/

# engine / dcc scratch
.godot/
*.tmp
*.blend1
```

**Do NOT** blanket-ignore `*.png` or `*.glb` — those are source in some tools
(Pixelcoat's `recipes/sources/*.png`, texture packs, fixtures). Ignore output
*directories*, not file types.

## Extending it

When the audit's per-tool total looks bigger than the dirs listed, some tool is
writing outputs to a name not on the allow-list. Add that dir name to
`$DirNames` at the top of `factory_clean.ps1` (and to the `.gitignore` baseline),
and it's covered from then on.

## Safety summary

- Dry-run by default; deletes only with `-Apply`.
- Removes only the curated allow-list — never source, never tracked files,
  never local config.
- Skips everything under `.git/`.
- Idempotent and repeatable.
