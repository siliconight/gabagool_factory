---
name: addon-swap-needs-import-pass
description: "Swapping a Godot addon version into a staged project needs `godot --headless --path P --import`, or `-s` runs miss new class_name types and the arm reads BROKEN"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-15T03:57:23.586Z
---

An A/B that copies one Laser Tag version's addon into a project another version staged must then run `godot --headless --path <project> --import`, as Level Factory's staging does (`level_factory/packages/staging/godot_project.py`, whose comment says `-s` honours only the class types an import scan registered). Without it, Laser Tag 0.32.0 on install test 8's project read BROKEN 20, every run logging "Trying to assign value of type 'Node' to a variable of type 'LT_EnemyMovement.gd'". `LT_Steering` (0.31.0) was missing from the old `.godot/global_script_class_cache.cfg`. The other direction (old addon into a new project) happened to run.

**Why:** it cost one A/B round on 2026-10-14 (install test 9, `docs/findings/stranger_install/lt_share_ab.sh` keeps the account). A broken arm prints a grade and a report, so it reads like a measurement.

**How to apply:**
- Give every arm the same import pass, controls included. A control that still reproduces its job in every field proves the pass moved nothing.
- Print each arm's class-cache count before trusting it.
- Related: [[laser-tag-rabbit-hole]], [[grader-speed-cap-three]].
