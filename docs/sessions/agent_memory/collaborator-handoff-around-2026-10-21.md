---
name: collaborator-handoff-around-2026-10-21
description: "Walker will hand a full export of the tools to a collaborator ~2026-10-21; they will make levels (tool changes = a fork), on Windows and Linux; roadmap 202 measures what a stranger hits"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-12T13:52:29.111Z
---

On 2026-10-07 the walker said they want to give "a full export of the tools
(package)" to a collaborator "in a couple weeks" -- around 2026-10-21 -- "for
them to start using". They asked whether to keep proving the level standard
with cold runs or improve the tools first.

**Why:** a stranger's first hour is the first real test of CLAUDE.md's
deliverable sentence ("somebody who has never seen this repo points these
tools at their own game"). Every zero-intervention run so far was earned on
the walker's machine with workarounds the driver knows.

**How to apply:**
- Recommended answer (given 2026-10-07): prove now and fix what proving
  finds (week 1), then make the install itself a cold run (week 2): unpack
  into a fresh path, follow one setup page, count every question as an
  intervention.
- Roadmap 202 holds the measured gaps: certified set six weeks stale
  (verify-manifest 8 DRIFT, 1 INCOMPATIBLE), `init` writes tool paths blank
  and the driver copies the previous run's, driver root hardcoded, 7 of 11
  repos declare no dependencies, no setup page, 824 MB of ~987 MB is the run
  record, briefs carry an absolute `lot_library` path.
- Answered by the walker, 2026-10-07: the collaborator will "likely just be
  making levels"; if they change the tools, "it will likely be a fork from
  this repo" -- so a zip at certified tags is the deliverable, not repo
  access. OS: "Windows and Linux" -- every driver and setup step must run on
  Linux too (today the drivers are bash with a hardcoded /c/ root, plus
  Windows-only PowerShell). The bar is [[consumers-need-only-blender-and-godot]].
- Still open: Replayability out of the pass rule.
- **Progress 2026-10-10 (roadmap 202 NARROWED):** the install path is built
  (LF 0.167.0-0.171.0, START_HERE.md, factory.cmd/.sh, a 72 MB package
  that carries the building library) and walked twice from a fresh unpack
  (docs/findings/stranger_install/). factory 1.35.0 certified from install
  test 2, every repo tagged locally. Left before the handoff: the real
  `setup --venv` (needs the walker's yes for the PyPI download), a Linux
  run (no Linux machine here), and an install test at whatever LF the
  handoff ships (0.172.0 fixed the walk's sparkle false-fail after 1.35.0).
  The handoff zip should be made at the certified tags.

- **Progress 2026-10-11 (roadmap 202 NARROWED):** the walker said yes to
  the PyPI download and has no Linux machine. Install tests 4 to 6 typed
  the page's own `setup --venv`; tests 4 and 5 found three defects a
  stranger would have met (the venv's sitecustomize error; `walk` stripping
  the bake from the package `make` shipped, since LF 0.144.0; the shot bot
  failing a level for a failing tube's flicker), all fixed in LF 0.178.1 and
  0.178.3. Install test 6 certified **factory 1.37.0**, released on GitHub
  with its zip. The handoff zip IS that release asset. Left: Linux.
- **2026-10-12: factory 1.39.0 is the latest release** (install test 8:
  make 7.9 min where 1.38.0's took 34.1, walk 5.6 vs 10.9; 0 deviations).
  A collaborator's first `make` is now about eight minutes. Left: Linux.

Related: [[level-excellence-standard-doc]], [[keep-it-rolling]].
