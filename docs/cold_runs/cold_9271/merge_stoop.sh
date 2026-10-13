#!/bin/bash
# Level Factory 0.196.0's merge rule on cold run 9271's package, before it ships: 9271's export merged every
# Empty's sided slots already (0.195.0's `merge_empties.gd`) and left its stoop's three slot children whole
# -- `stoop_landing`, `stoop_tread_1`, `stoop_tread_2` give no side. Run 0.196.0's script over a mirror's
# twelve Empty scenes: what is left to merge is the stoop, and the report says how many meshes it took in
# and how many groups it made a scene. The mirror is removed after.
#
#     bash docs/cold_runs/cold_9271/merge_stoop.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/cold_runs/cold_9271"
SCR="_scratch/merge_9271"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
PKG="LF_restaurant_row_001.portable-godot"
rm -rf "$SCR"
mkdir -p "$SCR"
cp -r "workspaces/cold-9271-ws/.level_factory/exports/$PKG" "$SCR/$PKG" || exit 1
cp level_factory/assets/godot/merge_empties.gd "$SCR/$PKG/merge_empties.gd"
timeout 1800 "$G" --headless --path "$SCR/$PKG" --import < /dev/null > "$SCR/import.log" 2>&1
echo "import exit $?"
SCENES=$(ls -d "$SCR/$PKG"/lot/gs_empty_rowhome_* | sed "s#.*/lot/#res://lot/#; s#\$#/site.tscn#")
timeout 900 "$G" --headless --path "$SCR/$PKG" --script res://merge_empties.gd -- \
  "$F/$OUT/merge_stoop.out.json" $SCENES < /dev/null > "$SCR/merge.log" 2>&1
echo "merge exit $?"
python - "$OUT/merge_stoop.out.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print("ok", d["ok"], "error", d["error"], "scenes", len(d["scenes"]))
for s in d["scenes"]:
    print("%-44s meshes_in %3d  surfaces_in %3d  merged %2d  colliders %3d  error %s" % (
        s["scene"], s["meshes_in"], s["surfaces_in"], s["merged"], s["colliders"], s["error"]))
PY
rm -rf "$SCR"
