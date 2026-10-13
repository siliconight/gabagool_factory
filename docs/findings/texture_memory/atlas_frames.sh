#!/bin/bash
# What a smaller reflection atlas costs the look (roadmap 238's first lever). Cold run 9273's package, copied
# four times; the reflection atlas's face size set by an `override.cfg` beside each copy's project.godot
# (read at start, before the renderer sizes the atlas), its count left at the default 64, which holds the
# level's 23 probes:
#   s256    no override: the package as it ships
#   s256b   no override again: THE CONTROL -- two renders of one package, the floor every diff is read against
#   s128    reflection_size=128
#   s64     reflection_size=64
# Each copy: `look_shots.py` with the derived stations and twelve interiors (rooms are where the probes
# are), then `texture_split_probe.gd -- mission` for its texture memory. Diffs against s256; a sheet of the
# interiors. Prints what it measured. The package copies are removed at the end; the shots stay in _scratch.
#
#     bash docs/findings/texture_memory/atlas_frames.sh
F=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$F" || exit 1
OUT="docs/findings/texture_memory"
S="_scratch/atlas_9273"
G="C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
PKG="workspaces/cold-9273-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"
[ -f "$PKG/mission.tscn" ] || { echo "no package at $PKG"; exit 1; }
rm -rf "$S"
mkdir -p "$S"
for v in s256 s256b s128 s64; do
  cp -r "$PKG" "$S/$v" || exit 1
  case $v in
    s128) printf '[rendering]\n\nreflections/reflection_atlas/reflection_size=128\n' > "$S/$v/override.cfg" ;;
    s64) printf '[rendering]\n\nreflections/reflection_atlas/reflection_size=64\n' > "$S/$v/override.cfg" ;;
  esac
  cp "$OUT/texture_split_probe.gd" "$S/$v/"
  timeout 1800 "$G" --headless --path "$S/$v" --import < /dev/null > "$S/import_$v.log" 2>&1
  echo "import $v exit $?"
  timeout 900 python tools/look_shots.py "$S/$v" --scene mission.tscn --interiors 12 --out "$S/shots_$v" --json \
    > "$S/shots_$v.json" 2> "$S/shots_$v.err" < /dev/null
  echo "shots $v exit $?"
  timeout 600 "$G" --path "$S/$v" -s res://texture_split_probe.gd -- mission < /dev/null > "$S/mem_$v.txt" 2>&1
  echo "memory $v: $(grep '^\[split\] mission' "$S/mem_$v.txt" | tr '\n' ' ')"
done
ARGS=()
for p in "$S"/shots_s256/*.png; do
  s=$(basename "$p" .png)
  for v in s256b s128 s64; do
    [ -f "$S/shots_$v/$s.png" ] && python docs/cold_runs/cold_9244/frame_diff.py "$p" "$S/shots_$v/$s.png" | sed "s/^/$v /"
  done
  # interiors are look_shots' `in_<skin>` stations
  case "$s" in
    in_*) ARGS+=("256 (as shipped) $s=$p" "128 $s=$S/shots_s128/$s.png" "64 $s=$S/shots_s64/$s.png") ;;
  esac
done
# every interior at the three sizes, 17 MB: kept in scratch, not the repo
python docs/findings/edge_menu/sheet.py "$S/atlas_frames_all.png" 3 "${ARGS[@]}" && echo "sheet: $S/atlas_frames_all.png"
# the record: the two rooms the diffs moved most on cold run 9273's package
W="in_drywall_delco_1997_2"; C="in_concrete_delco_1997"
python docs/findings/edge_menu/sheet.py "$OUT/atlas_frames.png" 3 \
  "256 (as shipped) $W=$S/shots_s256/$W.png" "128=$S/shots_s128/$W.png" "64=$S/shots_s64/$W.png" \
  "256 $C=$S/shots_s256/$C.png" "128=$S/shots_s128/$C.png" "64=$S/shots_s64/$C.png" \
  && echo "sheet: $OUT/atlas_frames.png"
# the package copies go; the shots stay under $S until read
rm -rf "$S/s256" "$S/s256b" "$S/s128" "$S/s64"
