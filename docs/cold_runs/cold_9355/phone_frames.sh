#!/bin/sh
# Cold run 9355's phone frames against 9351's: a walk copy of 9355's package, then the same stations shot in both --
# each street payphone from 4 m toward its road (the frame the walker judged, `docs/cold_runs/cold_9351/`) and from
# 1.5 m, into the booth's mouth. Stations are read off 9355's drawn site. 9351's level is the same seed and brief; its
# derivation lines (`_scratch/review/stop_stations_9351.txt`: each phone's place, yaw, kerb, look and eye) must equal
# 9355's before any frame is shot. 9351 is shot again here, beside 9355, rather than read from its earlier frames.
F=/c/Projects/gabagool_studios/gabagool_factory
G=/c/Godot/4.7/Godot_v4.7-stable_win64_console.exe
R=$F/_scratch/review
cd $F || exit 1
python tools/walk_export.py workspaces/cold-9355-ws/.level_factory restaurant_row_001 --out $R/walk_9355 || exit 1
python tools/cold_drive/wire_sky.py $R/walk_9355 || exit 1
$G --headless --path $R/walk_9355 --import > $R/walk_9355_import.log 2>&1
python docs/cold_runs/cold_9351/stop_stations.py workspaces/cold-9355-ws restaurant_row_001 \
    > $R/stop_stations_9355.txt 2> $R/stop_stations_9355.err || exit 1
python docs/cold_runs/cold_9351/stop_stations.py workspaces/cold-9355-ws restaurant_row_001 --back 1.5 \
    > $R/stop_stations_9355_close.txt 2> $R/stop_stations_9355_close.err || exit 1
if cmp -s $R/stop_stations_9351.txt $R/stop_stations_9355.err; then
    echo "stations: 9355's phones stand, face and look as 9351's"
else
    echo "STATIONS DIFFER from 9351's"
    exit 1
fi
for run in 9351 9355; do
    python tools/look_shots.py $R/walk_$run --out $R/phones_far_$run $(cat $R/stop_stations_9355.txt) \
        > $R/phones_far_$run.log 2>&1
    echo "far $run exit $?"
    python tools/look_shots.py $R/walk_$run --out $R/phones_close_$run $(cat $R/stop_stations_9355_close.txt) \
        > $R/phones_close_$run.log 2>&1
    echo "close $run exit $?"
done
