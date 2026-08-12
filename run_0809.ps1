# run_0809.ps1 -- verify the six, then apply the two held patches.
#
# NOT a script to run in one go. Run it a REGION AT A TIME and read the output
# between them; steps 1-3 are the verification the state-of-the-tree note asks
# for, and step 3's result decides whether step 5 is worth doing at all.
#
# Flags below were read out of the source this session, not remembered:
#   run/walk/cache      level_factory/apps/cli/main.py
#   --sweep --builds    module_extents.py main()
#   build.py            deli_counter/build.py argparse
# Two that are easy to get wrong and are called out where they appear:
#   * --sweep takes the PREVIEW LOT DIR, not the workspace.
#   * the DC rebuild needs DC_MODULAR, or no slots are written.

#region 0 -- environment  (a fresh PowerShell opens in System32)
$FACTORY = "C:\Projects\gabagool_studios\gabagool_factory"
$WS      = "$FACTORY\lot-demo-ws"
$LF      = "$FACTORY\level_factory\apps\cli\main.py"
$PREVIEW = "$WS\.level_factory\preview\lot_demo_001_walk"
$LOTDIR  = "$PREVIEW\lot"

$env:BLENDER = "C:\blender\blender.exe"          # not on PATH
# DC_GODOT makes deli_counter's pre-commit hook run the nav gate. Unset here so
# this shell can never surprise you at commit time; set it deliberately in 5b.
Remove-Item Env:\DC_GODOT -ErrorAction SilentlyContinue

Set-Location $FACTORY
python patch_lf_source_library.py --check        # reads and hashes, writes nothing
python patch_dc_roof_voids.py --check            # ditto
#endregion


#region 1 -- verify the six that landed 2026-08-09.  NOTHING PATCHED YET.
# Keep a before-image of both bot reports so step 6 has something to diff.
Copy-Item "$PREVIEW\walkbot.json" "$FACTORY\walkbot.before.json" -Force
Copy-Item "$PREVIEW\shotbot.json" "$FACTORY\shotbot.before.json" -Force

Set-Location $WS
python $LF run lot_demo_001 --art
# EXPECT: five zoo_kit_build jobs, one per placed building; all succeed;
#         "blockers open: 0"; no un-suffixed kit job.

Set-Location $FACTORY
# --sweep wants the PREVIEW LOT DIR (a dir of building dirs, each with art/zoo).
# Zoo's core/kit.py is found by walking up from here, so no --zoo needed.
python module_extents.py --sweep $LOTDIR --builds deli_counter\build
# EXPECT: depot_a01, pharmacy_a02 and bank_branch_a04 still disagreeing; every
#         rebuilt building "ok"; bank_branch_a04's one line now reading
#         "MATCHES NO PLANNED MODULE" for prop_rockay_01_w160, not a dim fault.
#
# The DENOMINATOR will not be 8. $LOTDIR currently holds nine building dirs and
# only five are placed -- depot_a01, final_stand, pharmacy_a02 and
# lf_lot_demo_001_5017 are leftovers from earlier runs. That is the content-dir
# accumulation finding, not a sweep fault; do not read it as new damage.
#endregion


#region 2 -- `lf cache forget` on hardware for the first time.
Set-Location $WS

# Jobs that actually have a fingerprint receipt (forget reads the digest from it):
Get-ChildItem .level_factory\jobs -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'fingerprint.last.json') } |
    Select-Object -ExpandProperty Name | Sort-Object

python $LF cache inspect

# Pick a CHEAP one from that list (a patina_* or lot_build, not a zoo_* bake).
$JOB = "lot_demo_001.<pick-a-cheap-stage>"

python $LF cache forget $JOB     # EXPECT forgotten: true
python $LF cache forget $JOB     # again, WITHOUT re-running in between:
                                 # EXPECT forgotten: false,
                                 # "nothing was cached under that digest"
python $LF cache forget lot_demo_001.no_such_stage
$LASTEXITCODE                    # EXPECT non-zero + "no fingerprint receipt"

python $LF run lot_demo_001 --art
# EXPECT: that one job re-runs, everything else cache-hits. Compare its outputs
# to the previous run's -- forget should cost a rebuild, not change a result.
# If they DIFFER, the entry it dropped was poisoned, and that is the first
# direct evidence of it.
#endregion


#region 3 -- the walk, BEFORE the roof patch.  This is the falsifier.
python $LF walk lot_demo_001 --play
Get-Content "$PREVIEW\walkbot.json"
# EXPECT, unchanged:
#   "blocker": "Roof", "blocker_rel_y": 3.9, "aperture_z": [],
#   "climb": false, "top_exit": false
#
# If `blocker` is no longer "Roof", the roof diagnosis is WRONG and step 5
# should not be run -- come back with the new value instead.
#
# While you are in there, by eye:
#   * bank_branch_a04 -- the ladder, and whether you can get onto its roof
#   * b2 = construction_site_a03 -- item 3's stair; F3 overlay names the
#     collider and its height
#   * item 2's premise -- do the rebuilt buildings still show odd proportions
#     and floating lintels, or did the kit fan-out remove them
#endregion


#region 4 -- apply the two patches.  Independent; either order.
Set-Location $FACTORY
python patch_lf_source_library.py
Set-Location "$FACTORY\level_factory"
python -m pytest tests\unit
# EXPECT: 593 passed, 1 skipped   (571 before, +22 new)

Set-Location $FACTORY
python patch_dc_roof_voids.py
Set-Location "$FACTORY\deli_counter"
python test_roofs.py
# EXPECT: 11 [ok] lines, "all roof tests passed"
#endregion


#region 5a -- rebuild bank_branch_a04 so the roof fix reaches geometry.
Set-Location "$FACTORY\deli_counter"
# REQUIRED. bank_branch_a04.json carries no `modular` key, so _modular_on()
# falls back to this env var -- without it the build writes no slots at all and
# the roof slot (with or without its void) never appears.
$env:DC_MODULAR = "1"
python build.py specs\bank_branch_a04.json --blender $env:BLENDER
# writes deli_counter\build\bank_branch_a04.{glb,gameplay.json,slots.json,...}

# THE ONE CHECK THAT SETTLES IT, no Godot needed:
python -c "import json; d=json.load(open('build/bank_branch_a04.slots.json')); [print(s['slot_id'], s['fit'].get('voids')) for s in d['slots'] if s['role']=='roof']"
# EXPECT exactly:
#   roof_footprint [{'x0': 15.45, 'y0': 10.9, 'x1': 16.55, 'y1': 12.2}]
# which is the rectangle already measured in the shipped slab_col_2-colonly.
# An empty list means the ordering half of the patch did not take.
#endregion


#region 5b -- re-judge the rebuilt shell (needs Godot; sets DC_GODOT)
# The rebuild makes bank_branch_a04.navgate.json stale, and themed selection
# READS that verdict rather than recomputing it. Re-bake before the next --art
# run or selection is deciding on a manifest that describes the old geometry.
$env:DC_GODOT = "C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
python nav_gate.py --help        # I have NOT read this CLI -- check for a
                                 # single-shell form before running --all,
                                 # which bakes the whole library and is slow.
Remove-Item Env:\DC_GODOT
#endregion


#region 6 -- the run and the walk that prove it
Set-Location $WS
python $LF run lot_demo_001 --art
python $LF walk lot_demo_001 --play
Get-Content "$PREVIEW\walkbot.json"
# EXPECT: Ladder_ladder_0 -> "climb": true, "top_exit": true, "ok": true
#         and no "stall" key at all.

Compare-Object (Get-Content "$FACTORY\walkbot.before.json") `
               (Get-Content "$PREVIEW\walkbot.json")

# And by eye, the thing none of this replaces: climb it and come out on the roof.
#endregion


#region 9 -- revert, if either patch misbehaves
Set-Location $FACTORY
python patch_lf_source_library.py --revert
python patch_dc_roof_voids.py --revert
# Both restore from their .pre_source / .pre_roofvoid sidecars and refuse if a
# sidecar is not the pre-image they recorded. Reverting the DC patch does NOT
# undo a rebuilt bank_branch_a04 -- rebuild it again from 5a if you need the
# old geometry back.
#
# Sidecars are session-scoped (item 8): delete them once this is committed.
#   Get-ChildItem $FACTORY -Recurse -Include *.pre_source,*.pre_roofvoid
#endregion
