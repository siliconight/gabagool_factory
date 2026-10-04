## [0.175.1] - The nav baseline check runs after the nav gate

`check.py` ran every pure test in one sweep, then `nav_gate.py --all`. But
`test_navgate_population.py` reads what the nav gate writes -- each shell's
`build/<name>.navgate.json` -- and compares it with `navgate_baseline.json`.
In the first sweep, a shell built for the commit being checked has no
`.navgate.json` yet, so it was never compared, and a new unjudged shell
always passed on the commit that added it.

Measured on this repo:
- 0.174.0 added six rowhome Empties and committed clean.
- 0.175.0's hook refused for those same six, whose nav results had first
  been written during that hook (11:00, 2026-10-04).

The check was one commit late, every time, for every new shell.

`AFTER_NAV_GATE` names the tests that read the nav gate's output; it is
`test_navgate_population.py` today. They are left out of the first sweep
(`--ignore`) and run as their own step straight after the nav gate.

The other files that mention `.navgate.json` (`test_headroom.py`,
`test_marker_scope.py`, `test_navgate_verdict.py`) were read: none opens
`build/`, so they stay in the first sweep.

`test_check_order.py` drives `check.main` with `run` recorded instead of
executed, so it needs neither Godot nor a build. It checks three things:
- the population check runs after the nav gate;
- the first sweep leaves it out, and it runs exactly once;
- every held-back file exists, so a rename cannot silently undo this.

All three fail against 0.175.0's `check.py`, run on a copy: the first two on
the order, the third because `AFTER_NAV_GATE` did not exist.
