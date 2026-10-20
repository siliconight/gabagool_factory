#!/bin/sh
# Zoo 1.114.1 (the repo) against the zoo_screens clone (1.115.0 to be), one office desk and one cubicle bank,
# cold run 9349's own skins. Each arm in a fresh Blender process; logs beside the outputs. Arm b was rebuilt
# alone after the footprint fix (run_b.sh); arm a is this script's.
F=/c/Projects/gabagool_studios/gabagool_factory
S=/c/Users/Brannen/AppData/Local/Temp/claude/C--Projects-gabagool-studios-gabagool-factory/27f14f8b-7ce5-44c0-a704-178a824035d7/scratchpad
SK=$F/workspaces/cold-9349-ws/.level_factory/jobs/restaurant_row_001.pixelcoat_build/out
cd $F/_runs/desk_ab || exit 1
rm -rf a b
/c/blender/blender.exe --background --python $F/zoo/tools/zoo_cli.py -- --build-kit desk.slots.json --out a \
    --theme delco --skins "$SK" --no-blend < /dev/null > a.log 2>&1
echo "a exit $?" > ab.done
/c/blender/blender.exe --background --python $S/zoo_screens/tools/zoo_cli.py -- --build-kit desk.slots.json --out b \
    --theme delco --skins "$SK" --no-blend < /dev/null > b.log 2>&1
echo "b exit $?" >> ab.done
