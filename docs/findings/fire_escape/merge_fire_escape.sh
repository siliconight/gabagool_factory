#!/bin/bash
# Level Factory 0.209.0's merge rule on cold run 9303's package, before it ships (roadmaps 156 and 241).
# 9303's export merged every Empty's sided slots already (0.208.0's `merge_empties.gd`) and left each walk-up's
# fire escape whole: `fire_escape_<storey>` and `fire_escape_drop` give no side. Three runs over one mirror,
# each report kept beside this script:
#
#   merge_fire_escape_0208.out.json   0.208.0's script (`git show b8fe4f7:...` in level_factory, 0.208.0's
#                                     commit; the export unlinks its copy, so the package carries none) over the
#                                     walk-ups' scenes: THE CONTROL. Nothing is left that it takes, so each scene
#                                     should report "no side to merge" and stay unsaved.
#   merge_fire_escape_0209.out.json   0.209.0's over the same scenes: what it takes in and how many groups it
#                                     makes a scene.
#   merge_fire_escape_others.out.json 0.209.0's over the package's other Empties, which stand no fire escape:
#                                     each should report "no side to merge", the rule taking nothing else.
#
# The mirror is removed after. Run after `patches/patch_lf_merge_fire_escape.py` has been applied, so that
# level_factory's working copy is 0.209.0.
#
#     bash docs/findings/fire_escape/merge_fire_escape.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/findings/fire_escape"
SCR="_scratch/merge_9303"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
PKG="LF_urban_row_001.portable-godot"
SRC="workspaces/cold-9303-ws/.level_factory/exports/$PKG"
[ -f "$SRC/mission.tscn" ] || { echo "no package at $SRC"; exit 1; }
grep -q 'begins_with("fire_escape_")' level_factory/assets/godot/merge_empties.gd \
  || { echo "level_factory's merge_empties.gd has no fire escape rule: apply the patch first"; exit 1; }
rm -rf "$SCR"
mkdir -p "$SCR"
git -C level_factory show b8fe4f7:assets/godot/merge_empties.gd > "$SCR/merge_0208.gd" || exit 1
grep -q 'begins_with("fire_escape_")' "$SCR/merge_0208.gd" \
  && { echo "0.208.0's merge_empties.gd has the rule: it is not the control"; exit 1; }
cp level_factory/assets/godot/merge_empties.gd "$SCR/merge_0209.gd"
cp -r "$SRC" "$SCR/$PKG" || exit 1
timeout 1800 "$G" --headless --path "$SCR/$PKG" --import < /dev/null > "$SCR/import.log" 2>&1
echo "import exit $?"
WALKUPS=""
OTHERS=""
for d in "$SCR/$PKG"/lot/gs_*; do
  id=$(basename "$d")
  [ -f "$d/site.tscn" ] || continue
  if grep -q 'node name="fire_escape_' "$d/site.tscn"; then
    WALKUPS="$WALKUPS res://lot/$id/site.tscn"
  elif grep -q 'node name="Merged' "$d/site.tscn"; then
    OTHERS="$OTHERS res://lot/$id/site.tscn"
  fi
done
echo "walk-ups:$WALKUPS"
echo "others:  $OTHERS"
run() {  # <script copy> <report> <scenes...>
  local script="$1" report="$2"; shift 2
  cp "$SCR/$script" "$SCR/$PKG/merge_empties.gd"
  timeout 900 "$G" --headless --path "$SCR/$PKG" --script res://merge_empties.gd -- \
    "$F/$OUT/$report" "$@" < /dev/null > "$SCR/${report%.out.json}.log" 2>&1
  echo "$script over $# scene(s): exit $?"
}
run merge_0208.gd merge_fire_escape_0208.out.json $WALKUPS
run merge_0209.gd merge_fire_escape_0209.out.json $WALKUPS
run merge_0209.gd merge_fire_escape_others.out.json $OTHERS
python - "$OUT" <<'PY'
import json, sys
for name in ("0208", "0209", "others"):
    d = json.load(open("%s/merge_fire_escape_%s.out.json" % (sys.argv[1], name), encoding="utf-8"))
    print("%-7s ok %s  error %s  scenes %d" % (name, d["ok"], d["error"], len(d["scenes"])))
    for s in d["scenes"]:
        print("  %-34s meshes_in %3d  surfaces_in %3d  merged %2d  unwrapped %2d  colliders %3d  error %s" % (
            s["scene"], s["meshes_in"], s["surfaces_in"], s["merged"], s["unwrapped"], s["colliders"], s["error"]))
PY
rm -rf "$SCR"
