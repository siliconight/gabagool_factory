---
name: check-a-name-before-write
description: Write silently replaces an existing file; check a new patch/findings file name is free first -- patch_roadmap_234_floaters.py was overwritten 2026-10-13 and restored from git
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-13T18:55:05.039Z
---

Before writing a NEW file under `patches/` or `docs/findings/`, look for the name first (`ls patches | grep <item>`). Roadmap patch names repeat by item number and topic (`patch_roadmap_<item>_<topic>.py`), and the Write tool replaces an existing tracked file without warning. Its result says "updated successfully" instead of "created successfully".

**Why:** on 2026-10-13 I wrote `patches/patch_roadmap_234_floaters.py` over the 2026-10-11 patch that had filed item 234, the committed record of that change. Only `git status` showing ` M` caught it, and it was restored with `git checkout`.

**How to apply:** read the Write result -- "updated" on a file meant to be new is the alarm. Give new patches a distinguishing word (`_floater_helper`) and check the folder before writing. Related: [[gate-commits-on-the-patch]].
