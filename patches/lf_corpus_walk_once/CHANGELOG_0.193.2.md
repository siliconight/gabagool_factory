## [0.193.2] - The archetype corpus is walked once a session, and never into a directory it discards

**Why.** The suite's own clock (0.193.1's run, JUnit): 443.1 s, of which
`tests/test_archetype_resolution.py` took 118.8 s -- 58.3, 30.4 and 30.1 s in
its three corpus tests, each of which walked the whole factory with
`rglob("*.json")` and only then dropped what lies under `_SKIP_DIRS`. The tree
is 1,524,870 entries (69 % under `workspaces/`, 17 % under `_runs/`), 384,372
of them under a skipped directory, and it grows with every cold run; the
briefs are 487. The factory's iteration loop is this suite and a cold run
(roadmap 239), and the suite had become as long as the run.

**What changed.** `_corpus_walk(root)`: `os.walk`, pruning a directory named in
`_SKIP_DIRS` before descending, and `_keep`, the module's predicate unchanged,
asked of every path. The same list by construction: a path below a skipped
directory carries that directory's name in its parts, so the predicate refuses
it whether or not the walk went in; `os.walk` neither follows a link into a
directory nor stops at one it cannot read, as `rglob` does not; `normcase`
keeps `rglob`'s case rule for the extension; and a directory whose name
matches counts, as it does to `rglob`. `_brief_paths()` calls it once a
session (`functools.lru_cache`) and returns a tuple, so no test changes what
the next one reads. The corpus, the predicate, `_SKIP_DIRS` and
`_KNOWN_UNRESOLVABLE` are as they were.

**Measured** (the factory's `docs/findings/lf_suite_time/brief_walk_probe.py`,
the arms alternated): the old walk 59.14 s cold and 29.95 s warm, the new
19.04 and 18.85 s, the same 487 briefs in the same order all four times.
In the suite (JUnit, 0.193.2's run against 0.193.1's): 443.1 -> 355.1 s, this module 118.8 -> 22.0 s -- the corpus walked once, 21.74 s in the first corpus test and 0.07 and 0.08 s in the other two

**Not changed, and a question:** 148 of the 487 briefs are under `_scratch/`,
gitignored scratch by `docs/FILING.md`, so the corpus depends on what a
checkout happens to hold and a collaborator's holds none of them.
`_SKIP_DIRS`' own rule ("scratch, not corpus") would exclude it, but that
narrows what the tests read; it is left for a change of its own.

**Tests:** three in `tests/test_archetype_resolution.py` -- the walk finds what
`rglob` found on a tree with a brief under every skipped directory, a
`briefs` directory under one and a directory named like a brief; it never
lists a directory it discards (`os.scandir` spied, and asked to have listed
the root, so it cannot pass on a walk that listed nothing); and the corpus is
walked once a session. All three fail on 0.193.1 (two with no walk to call, one with no cache); given the old walk under the new names, two fail on its behaviour -- the spy saw it list `_runs/x` and the other skipped directories, and it walked twice -- and the identity passes, as a guard should

**Suite:** 2,335 passed, 16 skipped, 0 failed (JUnit, 2,351 tests): 0.193.1's 2,332 and the three new tests
