# ============================================================
#  guardrail_regate.ps1 -- rebuild touched specs, re-gate the
#  geometry changes, refresh + re-verify every mission site.
#  After it finishes: open _runs\<site>_proj\project.godot in
#  Godot 4.7 and run <site>_walk.tscn to WALK the level yourself.
# ============================================================
$ErrorActionPreference = "Continue"
cd C:\Projects\gabagool_studios\gabagool_factory\deli_counter
$env:BLENDER  = "C:\blender\blender.exe"
$env:DC_GODOT = "C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"

# -- 1) offline rebuild of the 30 guard-rail-touched specs --
$specs = @("airport_terminal_a01","arena_a02","auto_shop_a02","bank_tower_a03","brewery_a03","casino_a01","clinic_a01","construction_site_a01","courthouse_a03","depot_a01","freight_terminal_a01","gas_station_a01","gas_station_a02","gas_station_a03","landmark_hall_a01","large_warehouse_a01","marina_a03","market_hall_a01","museum_a03","parking_garage_a01","pawn_shop_a01","pharmacy_a01","rail_station_a01","stadium_a02","strip_club_a01","strip_retail_a02","supermarket_a01","train_yard_a01","warehouse_a01","warehouse_a02")
foreach ($s in $specs) {
  python build.py "specs\$s.json"
  python evidence.py "specs\$s.json"
  python roundtrip.py "build\$s.glb"
}

# -- 2) engine gates for the two geometry changes --
foreach ($s in @("warehouse_a02","gas_station_a02")) {
  python nav_gate.py "build\$s.glb"
  python godot_gate.py "build\$s.glb"
}

# -- 3) guard rails, library-wide --
python layout_lint.py --all

# -- 4) refresh buildings into every mission site, re-assemble,
#       re-gate (walktest + 4-player smoke) --
cd ..\lot
$sites = [ordered]@{
  "ballpark_block" = @("warehouse_a02","stadium_a01","stadium_a04")
  "bank_tower_block" = @("credit_union_a01","bank_tower_a01","bank_tower_a03")
  "brewery_block" = @("apartment_walkup_a02","brewery_a02","pawn_shop_a02")
  "central_vault" = @("bank_branch_a04","deli_a01","warehouse_a02","parking_garage_a02")
  "deli_block" = @("warehouse_a01","deli_a01","parking_garage_a01")
  "independence_mall" = @("landmark_hall_a03","landmark_hall_a01","landmark_hall_a02")
  "mainline_mansion" = @("funeral_home_a01","mansion_a03","country_club_a01")
  "museum_row" = @("construction_site_a01","museum_a02","courthouse_a03")
  "phl_airport" = @("freight_terminal_a01","airport_terminal_a01","airport_terminal_a02")
  "port_row" = @("marina_a03","freight_terminal_a03","depot_a02")
  "reading_terminal" = @("clinic_a01","market_hall_a01","market_hall_a02")
  "ref_pvp_site" = @("bank_job","pvp_station_ref","bank_job")
  "rivers_casino" = @("parking_garage_a02","casino_a01","casino_a02")
  "septa_station" = @("strip_retail_a01","rail_station_a02","gas_station_a03")
  "septa_yard" = @("depot_a01","train_yard_a01","train_yard_a02")
  "storage_row" = @("auto_shop_a02","self_storage_a01","strip_club_a01")
  "strip_mall" = @("gas_station_a01","strip_retail_a02","pharmacy_a01")
  "walkup_siege" = @("auto_shop_a01","apartment_walkup_a01","pawn_shop_a01")
  "warehouse_district" = @("supermarket_a03","large_warehouse_a03","depot_a01")
  "xfinity_center" = @("arena_a02","arena_a01","arena_a03")
}
foreach ($site in $sites.Keys) {
  New-Item -ItemType Directory -Force "specs\$site\buildings" | Out-Null
  foreach ($b in $sites[$site]) {
    Copy-Item "..\deli_counter\build\$b.glb"           "specs\$site\buildings\" -Force
    Copy-Item "..\deli_counter\build\$b.gameplay.json" "specs\$site\buildings\" -Force
  }
  python lot.py "specs\$site\${site}_site.json" "..\_runs\${site}_proj" --walkable --navqa
  xcopy /E /I /Y "specs\$site\buildings" "..\_runs\${site}_proj\buildings" | Out-Null
  python walktest.py "..\_runs\${site}_proj" --all
  python mp_smoke.py "..\_runs\${site}_proj" "specs\$site\${site}_site.json" --players 4
}

# -- 5) site guard rails + status --
python site_layout_lint.py --all
python phase4m_status.py
Write-Host ""
Write-Host "WALK IT: open _runs\<site>_proj\project.godot in Godot 4.7" -ForegroundColor Green
Write-Host "         and run <site>_walk.tscn (first-person spawn->objective->extraction)." -ForegroundColor Green
