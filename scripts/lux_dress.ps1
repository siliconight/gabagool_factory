# Build a site and drop Lux into it, so a greybox has a look.
#
# WHY THIS IS THE FIRST ART STEP AND NOT THE LAST. Of the four tools that make a
# level look finished, Lux is the only one that is certified clean
# (verify-contracts: lux 0.15.4 matches), needs no Blender, needs no rebuild of
# any art asset, and applies to geometry that already exists. Zoo, Pixelcoat and
# Patina all change what is IN the .glb, so they need the drift in roadmap item
# 21 closed first. Lux changes how it is lit and displayed, which is additive.
#
# WHAT IT SHOULD LIGHT ITSELF WITH. Lot already emits <site>.site.lights.json --
# 7 anchors on the pawn job, 12 on the kerb probe -- and Lux ships
# lux_light_loader.gd and lux_fixture_spawner.gd to consume exactly that. Deli
# Counter decides where a light belongs, Lot merges the manifests, Zoo bakes the
# visible fixture, Lux spawns the Light3D. One contract, no second source of
# truth. This is the step where that chain gets exercised end to end for the
# first time.
#
# SKYMINT is copied too when present: Lux's Sun Link borrows a SkyMint sun if it
# finds one, and the sky shader lives there rather than in addons/lux.
#
# Dry run by default. -Apply to build and copy.
param(
  [string]$Spec = "specs\coldrun_pawn_job.json",
  [string]$Dest = "C:\Projects\gabagool_studios\gabagool_factory\_runs\lux_dressed",
  [switch]$Apply
)

$ErrorActionPreference = "Continue"
$PSNativeCommandUseErrorActionPreference = $false
$root = "C:\Projects\gabagool_studios\gabagool_factory"
$lux  = Join-Path $root "lux\addons"

Write-Host ""
Write-Host "=========== plan ===========" -ForegroundColor Cyan
Write-Host "  1. cater  $Spec  ->  $Dest"
Write-Host "     (rebuilds with the flat surfaces; buildings are already built so no Blender)"
Write-Host "  2. copy addons\lux      -> $Dest\addons\lux"
if (Test-Path (Join-Path $lux "skymint")) {
  Write-Host "     copy addons\skymint  -> $Dest\addons\skymint"
}
Write-Host "  3. enable the Lux plugin in $Dest\project.godot"
Write-Host ""
Write-Host "  Then in Godot, three clicks the script cannot do for you:" -ForegroundColor DarkGray
Write-Host "    open the project, add a LuxRoot node to the walk scene (Create Node," -ForegroundColor DarkGray
Write-Host "    sun icon), open the Lux dock, pick a preset, Apply / Preview." -ForegroundColor DarkGray
Write-Host "    Presets: Delco Summer Afternoon, Gas Station Fluorescent, Blue Hour," -ForegroundColor DarkGray
Write-Host "    Heavy Rain, Mission Goes Hot." -ForegroundColor DarkGray

if (-not $Apply) {
  Write-Host ""
  Write-Host "Dry run. Re-run with -Apply." -ForegroundColor Yellow
  exit 0
}

# --- 1. build -------------------------------------------------------------
Push-Location (Join-Path $root "lot")
python cater.py $Spec "$Dest"
$built = $LASTEXITCODE
Pop-Location
if ($built -ne 0) {
  Write-Host "  cater failed ($built). Nothing copied." -ForegroundColor Red
  exit 1
}

# --- 2. addons ------------------------------------------------------------
New-Item -ItemType Directory -Force -Path (Join-Path $Dest "addons") | Out-Null
foreach ($a in @("lux", "skymint")) {
  $src = Join-Path $lux $a
  if (-not (Test-Path $src)) { continue }
  Copy-Item -Path $src -Destination (Join-Path $Dest "addons") -Recurse -Force
  $n = (Get-ChildItem (Join-Path $Dest "addons\$a") -Recurse -File).Count
  Write-Host ("  copied addons\{0}  ({1} files)" -f $a, $n) -ForegroundColor Green
}

# --- 3. enable the plugin -------------------------------------------------
# Godot reads this from project.godot; without it the LuxRoot node type and the
# dock never appear, and the copy above looks like it did nothing.
$pg = Join-Path $Dest "project.godot"
$txt = Get-Content $pg -Raw
if ($txt -match 'res://addons/lux/plugin\.cfg') {
  Write-Host "  project.godot already enables Lux" -ForegroundColor DarkGray
} else {
  if ($txt -match '(?m)^\[editor_plugins\]') {
    $txt = $txt -replace '(?m)^\[editor_plugins\][^\[]*',
      "[editor_plugins]`n`nenabled=PackedStringArray(`"res://addons/lux/plugin.cfg`")`n`n"
  } else {
    $txt = $txt.TrimEnd() +
      "`n`n[editor_plugins]`n`nenabled=PackedStringArray(`"res://addons/lux/plugin.cfg`")`n"
  }
  Set-Content -Path $pg -Value $txt -Encoding UTF8
  Write-Host "  project.godot: Lux plugin enabled" -ForegroundColor Green
}

# --- what the lighting chain has to work with -----------------------------
$lights = Get-ChildItem $Dest -Filter "*.site.lights.json" -ErrorAction SilentlyContinue
Write-Host ""
if ($lights) {
  foreach ($l in $lights) {
    $j = Get-Content $l.FullName -Raw | ConvertFrom-Json
    $n = if ($j.anchors) { $j.anchors.Count } else { "?" }
    Write-Host ("  {0}: {1} light anchor(s) for lux_light_loader to spawn" `
                -f $l.Name, $n) -ForegroundColor Green
  }
} else {
  Write-Host "  NO *.site.lights.json in the build -- Lux has no anchors to read," -ForegroundColor Yellow
  Write-Host "  so you get the look but not the lights. That is roadmap item 19." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Open it:" -ForegroundColor Green
Write-Host "  Start-Process `"<godot.exe>`" -ArgumentList '--path','$Dest'" -ForegroundColor Green
