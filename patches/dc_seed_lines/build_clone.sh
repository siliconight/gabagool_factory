#!/usr/bin/env bash
# Build the proven 0.264.0 clone from a fresh clone of deli_counter at 0.263.0. Usage: bash build_clone.sh <dest>
set -e
W=/c/Projects/gabagool_studios/gabagool_factory/_scratch/wip_dc_seed_lines
D="$1"
rm -rf "$D"
git clone -q /c/Projects/gabagool_studios/gabagool_factory/deli_counter "$D"
cd "$D"
python $W/edit_dc_lines.py .
cp $W/migrate_seed_lines.py $W/test_seed_lines.py $W/arrangement.py $W/test_arrangement.py .
python $W/edit_dc_grid.py .
for i in 1 2 3; do python migrate_seed_lines.py | tail -1; python migrate_shelter.py | tail -1; done
python migrate_seed_lines.py --check | tail -1
