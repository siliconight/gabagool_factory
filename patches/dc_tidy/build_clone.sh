#!/usr/bin/env bash
# Build the proven 0.265.0 clone from a fresh clone of deli_counter at 0.264.0. Usage: bash build_clone.sh <dest>
set -e
W=/c/Projects/gabagool_studios/gabagool_factory/_scratch/wip_dc_tidy
rm -rf "$1"
git clone -q /c/Projects/gabagool_studios/gabagool_factory/deli_counter "$1"
python $W/tidy.py "$1"
python $W/tidy_hook.py "$1"
cp $W/test_root_is_the_builder.py "$1/tests/"
