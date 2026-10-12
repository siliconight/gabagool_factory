# Level Factory's suite: where its seven minutes go (roadmap 239)

The factory's iteration loop is a tool's test suite and a cold run. After
roadmap 239 brought the cold run's drive to 6.9 minutes (cold run 9259),
Level Factory's suite was as long as the run it gates: 443.1 s on 0.193.1
(`_scratch/lf_01931_suite.xml`, the run that shipped 0.193.1). Every Level
Factory change waits for it. This folder finds where that time goes, by the
same rule as the cold run's: measure, cut the largest thing that can be cut
without changing a result, measure again.

## Where the time goes (0.193.1's JUnit, every test's own `time`)

    443.1 s   the suite, 2,348 tests (16 skipped); 439.6 s inside tests, 3.5 s outside
    394.6 s   in the 53 tests that take a second or more
     16.8 s   in the 2,201 that take under a tenth of a second

    118.8 s   tests/test_archetype_resolution.py   58.3 + 30.4 + 30.1 s in its three corpus tests
    166.8 s   tests/integration/ (142.4 s in 15 tests: end_to_end 42.2, batch_production 35.8,
              advanced_review 34.2, presentation_export 30.2) and tests/service/test_facade.py
              (24.4 s in 13) -- the pipeline run end to end on stand-in tools
     91.7 s   tests/unit/test_worldskin_{ladders,slabs,stairs,lit_faces}.py -- 32 tests, each a
              real headless Godot import of a small fixture project
     11.8 s   tests/unit/test_setup_venv.py -- real virtual environments

## The corpus walk (Level Factory 0.193.2)

`test_archetype_resolution.py`'s three corpus tests each called
`_brief_paths()`, which walked the WHOLE factory with `rglob("*.json")` and
only then dropped what lies under `_SKIP_DIRS` (`_runs`, `build`,
`node_modules`, `.git`). `brief_walk_probe.py` times that walk against
`os.walk` pruning the same directories before descending, the arms
alternated so the filesystem cache favours neither
(`brief_walk_probe.out.txt`):

    round 1   the test's walk   59.14 s   487 briefs     (the suite's first corpus test: 58.3 s)
              the pruned walk   19.04 s   487 briefs
    round 2   the test's walk   29.95 s   487 briefs     (its second and third: 30.4, 30.1 s)
              the pruned walk   18.85 s   487 briefs
    every walk the same list, in the same order

The tree is 1,524,870 entries: 69 % under `workspaces/`, 17 % under `_runs/`
(every one under a skipped directory), 10 % under `_scratch/`; 384,372 of
them under a skipped directory, which the old walk listed and the new one
never enters. It grows with every cold run. The briefs are 487: 262 in the
recorded cold runs under `docs/`, 148 under `_scratch/`, 73 in workspaces'
own sources, 4 in Level Factory's examples.

**Shipped:** Level Factory 0.193.2 -- `_corpus_walk` prunes, the same
predicate decides every path, and `_brief_paths` walks once a session.
Its three tests fail on 0.193.1; against the old walk given the new names,
two fail on its behaviour (the spy saw it list `_runs/x` and the other
skipped directories; it walked twice) and the identity test passes, as a
guard should. The suite then ran 355.1 s against 443.1 (0.193.2's JUnit
against 0.193.1's), this module 22.0 s against 118.8 -- 21.74 s in the first
corpus test, 0.07 and 0.08 s in the other two; 2,335 passed, 16 skipped, 0
failed.

**Then the walker paused the loop**, 2026-10-12: "our optimization for time
is good enough for now". The two items below are where it would resume
(roadmap 239's status lists the rest).

**Not changed, a question:** 148 of the 487 briefs are under `_scratch/`,
gitignored scratch (`docs/FILING.md`). The corpus depends on what a checkout
happens to hold, and a collaborator's holds none of them; `_SKIP_DIRS`' own
rule ("scratch, not corpus") would exclude it. That narrows what the tests
read, so it waits for a change of its own.

## Next, not started

- **The worldskin imports, 91.7 s:** each test imports its own fixture
  project in a real Godot, about 3 s apiece; the tests are independent, so
  they would run side by side under `pytest-xdist` -- a download, which needs
  the walker's yes -- or in fewer imports, which would change what each test
  isolates.
- **The integration tests, 166.8 s:** the pipeline end to end on stand-in
  tools, a few seconds a run; not yet looked into.
