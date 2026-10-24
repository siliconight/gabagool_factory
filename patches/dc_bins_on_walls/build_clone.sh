#!/usr/bin/env bash
# Build the proven 0.266.0 clone from a fresh clone of deli_counter at 0.265.0. Usage: bash build_clone.sh <dest>
set -e
W=/c/Projects/gabagool_studios/gabagool_factory/patches/dc_bins_on_walls
D="$1"
rm -rf "$D"
git clone -q /c/Projects/gabagool_studios/gabagool_factory/deli_counter "$D"
cd "$D"
python $W/edit_dc_bins.py .
cp $W/test_bins_on_walls.py tests/
cp $W/migrate_bins_on_walls.py migrations/
python migrations/migrate_bins_on_walls.py
python migrations/migrate_bins_on_walls.py --check
