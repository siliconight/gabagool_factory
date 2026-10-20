#!/bin/sh
# The zoo_screens clone's arm alone, rebuilt after a fix; arm a (Zoo 1.114.1) stands as run_ab.sh first built it.
F=/c/Projects/gabagool_studios/gabagool_factory
S=/c/Users/Brannen/AppData/Local/Temp/claude/C--Projects-gabagool-studios-gabagool-factory/27f14f8b-7ce5-44c0-a704-178a824035d7/scratchpad
SK=$F/workspaces/cold-9349-ws/.level_factory/jobs/restaurant_row_001.pixelcoat_build/out
cd $F/_runs/desk_ab || exit 1
rm -rf b
/c/blender/blender.exe --background --python $S/zoo_screens/tools/zoo_cli.py -- --build-kit desk.slots.json --out b \
    --theme delco --skins "$SK" --no-blend < /dev/null > b.log 2>&1
echo "b exit $?" > b.done
