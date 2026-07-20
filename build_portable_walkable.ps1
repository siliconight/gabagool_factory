# ============================================================================
#  build_portable_walkable.ps1  --  ONE command: spec + theme -> a dependency-
#  free, walkable, themed Godot building package a stranger can drop into their
#  own project (no Blender / Level Factory / zoo / deli / pixelcoat / addon).
#
#    powershell -ExecutionPolicy Bypass -File build_portable_walkable.ps1 `
#        -Spec pvp_station_ref -Theme street [-Godot C:\path\Godot_console.exe]
#
#  Pipeline: pixelcoat theme-library -> deli build (shell+slots+markers) ->
#  zoo kit (themed modules) -> portable_building (package + closure) ->
#  optional Godot clean-project portability check.
# ============================================================================
param(
  [string]$Spec  = "pvp_station_ref",
  [string]$Theme = "street",
  [string]$Godot = $env:DC_GODOT
)
$ErrorActionPreference = "Stop"
$root    = "C:\Projects\gabagool_studios\gabagool_factory"
$blender = "C:\blender\blender.exe"
$env:BLENDER = $blender
# build-time dep for the greybox floors+collision strip (not in the handoff).
# pip logs to stderr; under -ErrorActionPreference Stop that aborts the script,
# so relax the error mode for just this call.
$ErrorActionPreference = "Continue"
python -m pip install pygltflib --quiet 2>&1 | Out-Null
$ErrorActionPreference = "Stop"
$dc   = Join-Path $root "deli_counter"
$zoo  = Join-Path $root "zoo"
$pix  = Join-Path $root "pixelcoat"
$runs = Join-Path $root "_runs"
$skins = Join-Path $runs "skins_$Theme"
$kit   = Join-Path $runs "kit_${Spec}_${Theme}"
$pkg   = Join-Path $runs "portable_${Spec}_${Theme}"
$slots    = Join-Path $dc "build\$Spec.slots.json"
$gameplay = Join-Path $dc "build\$Spec.gameplay.json"

function Step($n, $msg) { Write-Host "`n=== [$n] $msg ===" -ForegroundColor Cyan }

Step 1 "pixelcoat theme-library ($Theme)"
Push-Location $pix
python -m pixelcoat.cli.main theme-library --theme $Theme --out $skins --json
Pop-Location

Step 2 "deli build $Spec (shell + slots.json + gameplay.json)"
Push-Location $dc
python build.py "specs\$Spec.json"
Pop-Location
if (-not (Test-Path $slots)) { throw "no slots.json at $slots (is $Spec a modular/pvp_heist spec?)" }

Step 3 "zoo kit build (themed modules -> $kit)"
& $blender --background --python (Join-Path $zoo "tools\zoo_cli.py") -- `
    --build-kit $slots --theme $Theme --skins $skins --out $kit
if ($LASTEXITCODE -ne 0) { Write-Host "zoo exited $LASTEXITCODE (advisory: some modules may WARN)" -ForegroundColor Yellow }

Step 4 "package dependency-free handoff (-> $pkg)"
$grey = Join-Path $dc "build\$Spec.glb"   # greybox shell -> floors+collision base
Push-Location $dc
python portable_building.py $slots --gameplay $gameplay --modules $kit --theme $Theme --greybox $grey --out $pkg
Pop-Location
$manifest = Get-Content (Join-Path $pkg "portable_resource_manifest.json") -Raw | ConvertFrom-Json
$portable = $manifest.closure.portable
Write-Host ("closure: absolute_paths={0}, dangling={1}, PORTABLE={2}" -f `
  $manifest.closure.absolute_path_count, $manifest.closure.dangling_refs.Count, $portable) `
  -ForegroundColor ($(if ($portable) {"Green"} else {"Red"}))

Step 5 "Godot clean-project portability check"
if ($Godot -and (Test-Path $Godot)) {
  & $Godot --headless --path $pkg --import 2>&1 | Out-Null
  $out = & $Godot --headless --path $pkg -- --lf-portability-check 2>&1
  $ok = ($out -join "`n") -match "scene instantiated ok"
  Write-Host ("portability run: scene instantiated ok = {0}" -f $ok) -ForegroundColor ($(if ($ok) {"Green"} else {"Red"}))
  if (-not $ok) { $out | Select-Object -Last 20 | Out-Host }
} else {
  Write-Host "no Godot path (-Godot or `$env:DC_GODOT); skipping the engine check." -ForegroundColor Yellow
  Write-Host "To walk it: open the folder as a Godot project and press F5:"
  Write-Host "  $pkg"
}

Write-Host "`nDONE. Portable package:" -ForegroundColor Green
Write-Host "  $pkg"
Write-Host "Hand off that folder (or zip it). Recipient opens/instances res://$Spec.tscn -- no toolchain needed."
