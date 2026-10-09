#!/usr/bin/env bash
# Fresh-copy import of cold run 9214's package, repeated, each run's output kept.
# Counts the .glb.import sidecars each first pass leaves (425 GLBs in the package).
cd /c/Projects/gabagool_studios/gabagool_factory || exit 1
mkdir -p _scratch/2026-10-09_import_9214
SRC="workspaces/cold-9214-ws/.level_factory/exports/LF_bank_block_001.portable-godot"
GODOT="/c/Godot/4.7/Godot_v4.7-stable_win64.exe"
for i in 1 2 3 4; do
  D="_scratch/2026-10-09_import_9214/run$i"
  rm -rf "$D"
  cp -r "$SRC" "$D"
  find "$D" -name "*.import" -delete
  rm -rf "$D/.godot"
  start=$(date +%s)
  timeout 900 "$GODOT" --headless --path "$D" --import > "_scratch/2026-10-09_import_9214/run$i.log" 2>&1 < /dev/null
  code=$?
  glb=$(find "$D" -name "*.glb.import" | wc -l)
  all=$(find "$D" -name "*.import" | wc -l)
  echo "run $i: exit $code after $(( $(date +%s) - start )) s, glb sidecars $glb of 425, all sidecars $all"
  rm -rf "$D"
done
