---
name: greybox-owner-census
description: Library-wide census of base greybox nothing skins -- run it when Deli Counter adds a new kind of base geometry; LF's export refuses any greybox in a themed package since 0.218.0
metadata:
  type: reference
---

`docs/findings/base_greybox_owners/census.py` reads every `deli_counter/build/<spec>.glb` node by node: collider, slot node (`themed_tscn.owns_node`), a worldskin pass's name test (prefixes READ from `level_factory/assets/godot/zoo_worldskin.gd`), or UNOWNED. Control: on cold 9342's four buildings it named exactly the engine census's two surfaces. It can over-report (the package also drops nodes inside a themed roof's box) but not miss; it cannot see a kit gap (a slot left on its greybox fallback).

**Why:** Level Factory 0.218.0 refuses ANY greybox surface in a themed package; a cold run only finds an unowned kind in the buildings its lot happens to draw. Cold 9342 was refused on DC's legacy fire escape; the census then found vehicle ramps in four garages before any run drew one. LF 0.220.0 owns both.

**How to apply:** when Deli Counter (or LF's lf_ transients) adds base geometry outside a slot, run the census, then check the themed pool with `building_library.themed_report` -- only shells it admits matter. A new kind needs a worldskin pass (the slab pass's shape) or a slot. See [[open-work-2026-10-09]].
