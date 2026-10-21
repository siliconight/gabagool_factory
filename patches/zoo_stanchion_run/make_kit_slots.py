"""Stanchion runs for `zoo_cli --build-kit`: the default run, the shortest and the longest the genome holds, and a
lane's 3.0 m, as Deli Counter writes a species that owns its collision (`fit.collision` "none")."""
import json
import sys

slots = []
for i, (w, d, h) in enumerate(((4.6, 0.356, 0.97), (1.1, 0.3, 0.9), (12.0, 0.42, 1.05), (3.0, 0.356, 0.97))):
    slots.append({"slot_id": "stanchion_run_%d" % i, "role": "prop", "size_mod": "full", "style": 10,
                  "material": "metal_painted", "species": "stanchion_run", "kit_axis": "material",
                  "transform": {"translation": [0.0, 2.0 * i, h / 2], "rot_y": 0.0, "scale": [1.0, 1.0, 1.0]},
                  "fit": {"dims": [w, d, h], "pivot": "center", "openings": [], "collision": "none"}})
json.dump({"building_id": "stanchion_runs", "slots": slots}, open(sys.argv[1], "w"), indent=1)
print("wrote", len(slots))
