## [0.138.1] - The drip's tools find Pixelcoat by searching

Two tools still counted their way to Pixelcoat. `test_sibling_locator`'s
guard (`test_nothing_reaches_above_this_repo_by_counting_parents`) has
failed on both since 2026-09-26, the full suite's only red besides a stale
row fixed in 0.138.0:
- `tools/drip_assets.py:38`, `DEFAULT_PIXELCOAT`;
- `tools/wet_ab_run.py:150`, the `--pixelcoat` default.

Both were `Path(__file__).resolve().parents[2] / "pixelcoat"`. That is the
factory from a checkout sitting beside its siblings, and `scratchpad` from a
git worktree, where there is no Pixelcoat. It is the arithmetic
`tests/siblings.py` removed from the suite.

`drip_assets.pixelcoat_root()` replaces it, and `drip_assets` is the one
place that knows, as its docstring already said:
- **Override first.** `LF_PIXELCOAT_ROOT` -- the name
  `tests/siblings.env_var` derives -- in either spelling, the repo or the
  directory holding it.
- **No fallback on a bad override.** One naming the wrong place answers
  None; it does not fall back to the walk.
- **Then a walk.** Otherwise it walks up for `pixelcoat/core/droplets.py`,
  the file `stage` actually imports, so a directory named `pixelcoat` is not
  mistaken for the repo.

These are `sibling_repo`'s rules, restated because a tool run as
`python tools/x.py` has only `tools/` on its path and cannot import `tests`
(the reason `adapters/zoo` inlines its own search too).

When nothing is found, `stage` refuses with a sentence naming the file and
the override, instead of importing from a directory that does not exist.
`wet_ab_run.py --pixelcoat` now defaults to None, so the one search answers
for it. `walk_export.py` already passed None.

`tests/unit/test_drip_pixelcoat_locator.py` loads a COPY of `drip_assets.py`
placed where a worktree puts it, under a factory that carries Pixelcoat. That
is the layout that broke the count; from this checkout both answer the same.
It checks:
- the copy finds the factory's Pixelcoat;
- the override takes either spelling;
- a wrong override is None, and `stage` names the file and the variable.

All three fail on 0.138.0, run on copies.
