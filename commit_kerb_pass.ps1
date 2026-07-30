# Commit the kerb-cut and step-gate work. Second pass; the navmesh/walker
# commits already landed.
#
# Dry run by default. Add -Commit to commit. Nothing is pushed either way.
# Messages are plain per CLAUDE.md -- no trailers, no footers, no assistant
# references. -Branch is opt-in: these repos commit straight to main.
param([switch]$Commit, [string]$Branch = "")

$root = "C:\Projects\gabagool_studios\gabagool_factory"
$ignore = @("_bridge/", "__pycache__/", "_scratch_archive/",
            "*.pre_wp", "*.pre_wpdefault")
$ignoreLot = @(
  "specs/*/buildings/*.manifest.json",
  "specs/*/buildings/*.slots.json",
  "specs/*/buildings/*.navigation.json",
  "specs/*/buildings/*.validation.json",
  "specs/*/buildings/*.combat_audit.json"
)

$msgLot = @'
sidewalks: drop the kerb where a path crosses it

SIDEWALK_H is 0.16 and a capsule walks up 0.103 unassisted, so stepping off the
ground onto a sidewalk was a wall. Reported from play: walking from a spawn
toward the street stops dead and needs a jump.

A kerb is SUPPOSED to be a wall -- that is what keeps you out of traffic -- so
this does not flatten it. It drops the kerb where people are meant to cross, the
way a real street does, and Lot already knows where that is: `paths` are the
site's designed circulation and they run through the sidewalks either side of
any road they cross. A sidewalk stops being one long box and becomes the
segments between crossings plus a `kerbcut_` section at each crossing, flush
with the road. Every transition on a route is then legal:

    ground  0.00 -> kerbcut  0.08   walkable
    kerbcut 0.08 -> sidewalk 0.16   walkable
    road    0.08 -> kerbcut  0.08   flush

and the kerb stays a kerb everywhere else, which is correct rather than
convenient. 36 dropped sections on ballpark_block; 42 outdoor transitions
measured, none of them blocking a route.

site_steps: gate the step at build time, not in play

Wires site_steps.findings into assemble(), so a rise a body cannot walk is
reported when the site is built. Two codes, and the distinction is the point:
LOT_STEP_BLOCKS_A_ROUTE is major and fires when a designed route crosses the
rise; LOT_STEP_NEEDS_ASSIST is minor and fires off-route, which is what a kerb
away from a crossing correctly is. The check reads back the .tscn Lot just
WROTE rather than re-deriving from the constants that produced it.

Library after both: 20 of 20 walk clean, zero stranded anchors, zero blocked
routes, zero stuck walkers.
'@

$msgDeli = @'
contract: record the step a capsule actually walks up

clearances.unassisted_step_max_m, with its derivation. A capsule meets a low
step on its bottom hemisphere, so the contact normal is sloped rather than
horizontal and the engine calls the contact a floor only while that angle stays
inside floor_max_angle. The tallest step a body WALKS up with no step-up code is
radius * (1 - cos(floor_max_angle)).

characters.player.max_step_up_m (0.5) is what a controller can LIFT itself over,
and it had been standing in for this number. Every outdoor surface height in Lot
was chosen against it, which is why SIDEWALK_H ended up at 0.16 and the
courtyard at 0.12 -- one a wall, the other three millimetres over.

The deliverable ships into projects with none of this toolchain present, so a
transition above this line requires the consumer to have implemented step-up
themselves. That is why it belongs in the contract rather than in one tool.
'@

$repos = @(
  @{ Path = "$root\deli_counter"; Msg = $msgDeli; Label = "deli_counter" },
  @{ Path = "$root\lot";          Msg = $msgLot;  Label = "lot"; Extra = $ignoreLot }
)

foreach ($r in $repos) {
  Write-Host ""
  Write-Host "=========== $($r.Label) ===========" -ForegroundColor Cyan
  Push-Location $r.Path
  Write-Host "  branch: $((git rev-parse --abbrev-ref HEAD).Trim())"
  $status = git status --short
  if (-not $status) { Write-Host "  clean, nothing to commit"; Pop-Location; continue }
  $status | ForEach-Object { Write-Host "  $_" }

  if ($Commit) {
    if ($Branch) {
      Write-Host "  branching to $Branch"
      git checkout -b $Branch
      if ($LASTEXITCODE -ne 0) {
        git checkout $Branch
        if ($LASTEXITCODE -ne 0) {
          Write-Host "  could not switch to $Branch -- NOT committing" -ForegroundColor Red
          Pop-Location; continue
        }
      }
    }
    $patterns = $ignore
    if ($r.ContainsKey("Extra")) { $patterns = $ignore + $r.Extra }
    $gi = Join-Path $r.Path ".gitignore"
    $existing = if (Test-Path $gi) { Get-Content $gi } else { @() }
    $added = @($patterns | Where-Object { $existing -notcontains $_ })
    if ($added) {
      Add-Content -Path $gi -Value ""
      Add-Content -Path $gi -Value "# scratch and unread build sidecars"
      $added | ForEach-Object { Add-Content -Path $gi -Value $_ }
      Write-Host "  .gitignore += $($added -join ', ')"
    }
    git add -A
    $tmp = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $tmp -Value $r.Msg -Encoding UTF8
    git commit -F $tmp
    Remove-Item $tmp -Force
  }
  Pop-Location
}

Write-Host ""
if (-not $Commit) {
  Write-Host "Dry run. Nothing committed. Re-run with -Commit when the status looks right." -ForegroundColor Yellow
} else {
  Write-Host "Committed. Nothing pushed." -ForegroundColor Green
}
