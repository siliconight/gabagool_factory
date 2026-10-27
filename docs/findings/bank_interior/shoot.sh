cd /c/Projects/gabagool_studios/gabagool_factory || exit 9
PY=.venv/Scripts/python.exe; CLI=level_factory/apps/cli/main.py; WS=workspaces/bank-look-1027-ws
$PY $CLI -C $WS walk bank_block_001 > _scratch/bank_look_walk.log 2>&1; echo "walk=$?"; tail -3 _scratch/bank_look_walk.log
python - <<'PY'
import sys
sys.path.insert(0, "tools")
import look_shots
W = "workspaces/bank-look-1027-ws/.level_factory/preview/bank_block_001_walk"
# bank_branch_a02 is building b0 at Godot (-60, 0, 6.97), unrotated: plan (x, y) -> Godot (-60 + x, h, 6.97 - y).
# Its lobby is plan [-15, -11, 15, 2], the glass storefront on its south edge (plan y -11 -> Godot z 17.97); the teller
# counter is plan (0, -2), 12 m along x; the manager's office plan [-15, 2, 0, 11]; storey -1 is 3.6 m down, its vault
# plan [-8, -11, 0, -3] and vault_west plan [-15, -11, 0, 11].
ST = ["lobby_entry:-60,1.6,16.5,-60,1.3,8.5",
      "lobby_wide:-73.5,1.6,16.5,-52,1.3,7.0",
      "behind_line:-60,1.6,6.0,-60,1.3,16.0",
      "manager_office:-61,1.6,-3.0,-73,1.2,3.5",
      "vault:-61,-2.0,10.8,-67,-2.6,17.0",
      "vault_west:-61,-2.0,-3.0,-74,-2.6,10.0"]
for tag, extra in (("level", {}), ("inspect", {"inspect": "studio"})):
    try:
        got = look_shots.shoot(W, "_scratch/bank_look_shots_" + tag, stations=ST, timeout=900, **extra)
    except TypeError as e:
        print(tag, "skipped:", e)
        continue
    for s in got.get("shots", []):
        if s["name"] in [x.split(":")[0] for x in ST]:
            print(tag, s["name"], round(s["mean"], 1), s["p50"])
PY
