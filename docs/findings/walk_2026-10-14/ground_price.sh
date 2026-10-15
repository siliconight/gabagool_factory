#!/bin/bash
# Price the backdrop's ground (roadmap 252; Level Factory 0.211.0's BackdropGround, the walk's finding 2).
#
# What it compares. Cold run 9308's package (urban_row_001, the ground as shipped) against itself with the
# ground removed -- ground_strip.py none, whose result is 9305's backdrop scene byte for byte -- and, as a
# second arm, with the ground unshaded (ground_strip.py unshaded), the cheaper alternative 252 names.
# One package, so the stations, the bake and every other file are the same, and the arms differ in
# site_backdrop.tscn alone (checked below before anything runs).
#
# How. Level Factory's fixed-station harness through docs/findings/horizon_glow/price_glow.py: control_1
# (no ground), the subject (the harness's name for it is "glow"), control_2 (no ground again). Per heading
# against the controls' mean; the controls' spread is the noise floor. Two prices, one after the other:
#   ground_shaded/    the ground as shipped
#   ground_unshaded/  the ground unshaded
# The copies go to _scratch/price_ground/ and are deleted once the JSONs exist (about 200 MB each).
#
# NOT DURING A WALK OR A DEMO: it opens Godot windows for many minutes. Nothing else runs beside a price.
#
#     bash docs/findings/walk_2026-10-14/ground_price.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
# the workspace named in full, so tools/factory_retire.py sees which one this reads
PKG="workspaces/cold-9308-ws/.level_factory/exports/LF_urban_row_001.portable-godot"
OUT="docs/findings/walk_2026-10-14"
SCR="_scratch/price_ground"
[ -f "$PKG/site_backdrop.tscn" ] || { echo "no package at $PKG"; exit 1; }
mkdir -p "$SCR"
rm -rf "$SCR/none" "$SCR/shaded" "$SCR/unshaded"
for arm in none shaded unshaded; do
  cp -r "$PKG" "$SCR/$arm" || exit 1
done
python "$OUT/ground_strip.py" none "$SCR/none/site_backdrop.tscn" || exit 1
python "$OUT/ground_strip.py" unshaded "$SCR/unshaded/site_backdrop.tscn" || exit 1
for arm in shaded unshaded; do
  extra=$(diff -rq "$SCR/none" "$SCR/$arm" | grep -vc "site_backdrop.tscn")
  [ "$extra" = "0" ] || { echo "THE ARMS DIFFER beyond site_backdrop.tscn: none against $arm"; exit 1; }
done
for arm in shaded unshaded; do
  mkdir -p "$OUT/ground_$arm"
  python docs/findings/horizon_glow/price_glow.py "$SCR/none" "$SCR/$arm" "$OUT/ground_$arm" \
    > "$OUT/ground_$arm/price.txt" 2>&1
  echo "$arm price exit $?"
  tail -8 "$OUT/ground_$arm/price.txt"
done
rm -rf "$SCR/none" "$SCR/shaded" "$SCR/unshaded"
