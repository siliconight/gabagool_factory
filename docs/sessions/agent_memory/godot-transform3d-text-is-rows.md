---
name: godot-transform3d-text-is-rows
description: "A .tscn Transform3D's nine basis numbers are ROWS, then the origin; reading them as columns has bitten DC, Lot and LF -- use tools/godot_transform.py"
metadata:
  node_type: memory
  type: reference
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-19T15:42:43.147Z
---

Godot 4.7 writes and parses `Transform3D(a..i, ox, oy, oz)` with the nine basis numbers as the matrix's ROWS. Column k (where the basis sends local axis k) is `f[k], f[3+k], f[6+k]`; per-axis scale is that column's length.

Engine-measured three times: Deli Counter 0.120.1 (cold run 9013), Lot 0.72.1 / `site_furniture.plate_facing` (str_to_var, 2026-09-13), and `tools/module_pose_census.py` on cold run 9324 (2026-10-19). Reading columns hides on pure turns of centred boxes and shows on turned + non-uniformly scaled modules (swapped extents) or points off a turned instance's origin (mirrored).

It recurred anyway: DC's z-fight gate (fixed DC 0.230.0 -- its "last two pairs" of roadmap 177 were this), LF's ground_contact (0.218.2), and five root tools (fixed 2026-10-19). The factory's tools read through `tools/godot_transform.py`, held by `tools/test_godot_transform.py`; `docs/findings/zfight_rows_177/` has the evidence.

**How to apply:** any new code that parses `.tscn` transforms uses that helper (or reads rows), and a test pins it to the measured case. Before trusting a geometry finding on rotated modules, check which reading the instrument uses. See [[open-work-2026-10-09]].
