#!/usr/bin/env bash
# Fresh-copy import of cold run 9214's package from the state the export hands Godot:
# no sidecars but the ones the package copies in with Lux's runtime (SkyMint's 140),
# restored to their source text. Repeated; each run's output kept.
cd /c/Projects/gabagool_studios/gabagool_factory || exit 1
mkdir -p _scratch/2026-10-09_import_9214
SRC="workspaces/cold-9214-ws/.level_factory/exports/LF_bank_block_001.portable-godot"
GODOT="/c/Godot/4.7/Godot_v4.7-stable_win64.exe"
N="${1:-2}"
for i in $(seq 1 "$N"); do
  D="_scratch/2026-10-09_import_9214/faithful$i"
  rm -rf "$D"
  cp -r "$SRC" "$D"
  restored=0
  while IFS= read -r f; do
    rel="${f#$D/runtime/skymint/}"
    src="lux/addons/skymint/$rel"
    if [ -f "$src" ]; then
      cp "$src" "$f"
      restored=$((restored + 1))
    else
      rm -f "$f"
    fi
  done < <(find "$D/runtime/skymint" -name "*.import")
  find "$D" -name "*.import" -not -path "$D/runtime/skymint/*" -delete
  rm -rf "$D/.godot"
  start=$(date +%s)
  timeout 900 "$GODOT" --headless --path "$D" --import > "_scratch/2026-10-09_import_9214/faithful$i.log" 2>&1 < /dev/null
  code=$?
  glb=$(find "$D" -name "*.glb.import" | wc -l)
  all=$(find "$D" -name "*.import" | wc -l)
  echo "faithful $i: $restored sky sidecars restored; exit $code after $(( $(date +%s) - start )) s, glb sidecars $glb of 425, all sidecars $all"
  rm -rf "$D"
done
