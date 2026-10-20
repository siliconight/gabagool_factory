#!/bin/sh
# Zoo 1.115.0 (the repo) against the zoo_phone clone (1.116.0 to be): four street payphones, variants 0 to 3, each
# arm in a fresh Blender process with cold run 9350's skins.
F=/c/Projects/gabagool_studios/gabagool_factory
S=/c/Users/Brannen/AppData/Local/Temp/claude/C--Projects-gabagool-studios-gabagool-factory/27f14f8b-7ce5-44c0-a704-178a824035d7/scratchpad
SK=$F/workspaces/cold-9350-ws/.level_factory/jobs/restaurant_row_001.pixelcoat_build/out
cd $F/_runs/phone_ab || exit 1
rm -rf a b
/c/blender/blender.exe --background --python $F/zoo/tools/zoo_cli.py -- --build-kit phones.slots.json --out a \
    --theme delco --skins "$SK" --no-blend < /dev/null > a.log 2>&1
echo "a exit $?" > ab.done
/c/blender/blender.exe --background --python $S/zoo_phone/tools/zoo_cli.py -- --build-kit phones.slots.json --out b \
    --theme delco --skins "$SK" --no-blend < /dev/null > b.log 2>&1
echo "b exit $?" >> ab.done
