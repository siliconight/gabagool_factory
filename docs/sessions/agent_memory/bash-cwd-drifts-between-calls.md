---
name: bash-cwd-drifts-between-calls
description: "The Bash tool's working directory persists and drifts across calls (a `cd` in one call sets the next call's cwd); a bare `git add -A && git commit` has landed in the wrong repo twice"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4bb794c9-c366-4613-95bd-3c61e9a0d0f9
  modified: 2026-10-15T11:13:01.274Z
---

In this workspace every Bash call must begin with an explicit absolute `cd`
to the repo it means to touch. The cwd persists between calls, including
across parallel calls in one batch, and "Environment update" notes only
report it after the fact.

**Why:** On 2026-09-12 a `git add -A && git commit && git push` meant for
`level_factory` ran in `zoo` (committed the Zoo species under the LF
message; fixed by amend + force-with-lease), and later one meant for
`pixelcoat` ran in the factory ROOT and committed every untracked
workspace, overwrote the root VERSION, and pushed.

**How to apply:** Never rely on the previous call's cwd. Start each command
with `cd /c/Projects/gabagool_studios/gabagool_factory/<repo> &&`. Before
any `git commit`, print `git rev-parse --show-toplevel` in the same
command, or use `git -C <abs path>`.

**An absolute `cd` is NOT enough when calls run in parallel** (2026-10-05,
twice in one session): the calls share ONE cwd, so another call's later
`cd ..` moves this one mid-command. A `git add` meant for `deli_counter`
ran in the root ("pathspec 'VERSION' did not match"), and a root `git add
patches/...` failed the same way. Failed safe both times. So: use `git -C
<abs>` and absolute paths for anything that may run beside another call,
and never send commit commands in a parallel batch.

**A leading `cd /abs && ...` can silently not take effect** (2026-10-15,
twice in one session): the commands after it ran in the PREVIOUS call's cwd
(`cat VERSION` read nothing in deli_counter; a root `grep docs/...` ran in
level_factory). Both failed safe, as reads. So: absolute paths for every
file in every command (`$D/layout_lint.py`, `python /abs/script.py`,
`git -C /abs`), and treat a `cd` as a hint, never as the frame.

**Background jobs race too** (2026-10-09). A background `cd level_factory
&& python -m pytest` shared the shell with the next foreground call's `cd`
to the root. pytest started at the factory root, collected
`_runs/_lf_tools`, and errored with 0 tests. Two earlier background suites
had passed by luck of timing. Run a background job in its own process:
`bash -c 'cd <abs> && cmd'`. A `bash script.sh` is safe the same way.
