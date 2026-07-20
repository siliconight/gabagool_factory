# ============================================================================
#  render_kit_sheets.ps1  --  render the themed kit's hero modules into review
#  sheets using the existing (tested) deli_counter/review_render.py + Blender.
#  Shows the street theme's materials on real geometry: glass window, cinderblock
#  wall, concrete doorway, breach state, roof. Outputs contact sheets under
#  _runs\kit_street\review\<module>\sheet.png.
# ============================================================================
$ErrorActionPreference = "Continue"
$blender = "C:\blender\blender.exe"
$root    = "C:\Projects\gabagool_studios\gabagool_factory"
$rr      = Join-Path $root "deli_counter\review_render.py"
$kit     = Join-Path $root "_runs\kit_street"

# Hero modules covering the theme's material variety.
$heroes = @(
  "window_street_01_w160.glb",           # glass pane + frame + cinderblock surround (the star)
  "wall_street_01_w200.glb",             # cinderblock wall
  "doorway_street_01_w125.glb",          # concrete doorway
  "breach_street_01_w140_breached.glb",  # breached state
  "roof_street_01_w3400.glb"             # roof slab
)

foreach ($m in $heroes) {
  $glb = Join-Path $kit $m
  if (-not (Test-Path $glb)) { Write-Host "skip (missing): $m" -ForegroundColor Yellow; continue }
  Write-Host "==== rendering $m ====" -ForegroundColor Cyan
  & $blender --background --python $rr -- $glb --fast
}

Write-Host "`nSheets written under:" -ForegroundColor Green
Write-Host "  $kit\review\<module>\sheet.png"
