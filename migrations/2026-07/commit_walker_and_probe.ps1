# Lot 0.32.0 + factory 1.15.0, then the probe that settles item 16.
$ErrorActionPreference = "Continue"
$PSNativeCommandUseErrorActionPreference = $false
$root = "C:\Projects\gabagool_studios\gabagool_factory"

function Commit-Repo {
  param([string]$Path, [string[]]$Files, [string]$Message, [string]$Tag)
  Push-Location $Path
  Write-Host "`n=========== $Path ===========" -ForegroundColor Cyan
  foreach ($f in $Files) { git add -- $f }
  $staged = git diff --cached --name-only
  if (-not $staged) { Write-Host "  nothing staged" -ForegroundColor DarkGray; git log -1 --oneline; Pop-Location; return }
  $staged | ForEach-Object { Write-Host "  + $_" -ForegroundColor DarkGray }
  $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("msg_" + [guid]::NewGuid().ToString() + ".txt")
  [System.IO.File]::WriteAllText($tmp, $Message, (New-Object System.Text.UTF8Encoding($false)))
  git commit -F $tmp
  $rc = $LASTEXITCODE
  Remove-Item $tmp -Force
  if ($rc -ne 0) { Write-Host "  commit failed ($rc)" -ForegroundColor Red; Pop-Location; return }
  if ($Tag) { git tag -f $Tag | Out-Null; Write-Host "  tagged $Tag" -ForegroundColor DarkGray }
  git log -1 --oneline
  Pop-Location
}

Commit-Repo -Path "$root\lot" -Tag "v0.32.0" -Files @(
  "godot/addons/heist_nav_qa/nav_qa_director.gd", "VERSION", "CHANGELOG.md"
) -Message @'
nav QA: let the walker diagnostics out, and let the walker climb

Two fixes found by re-walking the twenty registered mission sites.

_conclude built each walker's report entry from a hand-written list of five
keys, so everything 0.30.0 recorded about a stuck capsule -- every slide
collision with collider name and contact normal, the waypoint it was steering
to, is_on_floor / is_on_wall -- was written to the walker and dropped on the way
out. All three failing sites came back with blocked_by absent from a director
that had measured it. The keys are named in one place now, beside a note that
_conclude has to copy them: a serializer with a fixed key list silently discards
whatever is added later, which is the same defect as measuring the wrong thing,
one layer further out. `at` gets the same treatment -- it was set for a walker
that ran out the clock and not for one that gave up, so a stuck position lived
only inside the status prose.

And two genuine walker defects, neither of which turned out to be the cause:

Gravity was applied every frame regardless of is_on_floor. A waypoint on a stair
flight usually sits at the same height as the body, so the climbing branch never
fires and the flat branch has to walk the slope while accumulating a downward
component that pins the capsule into the junction where ramp meets floor. It now
applies only while airborne.

The step-up probe was a single 0.5 m lift, which assumed the only thing that can
stop a body at a stair mouth is the riser in front of it. It tries 0.5, 0.35 and
0.2 before giving up, and says WHICH probe failed: no headroom to lift is a
finding about the stairwell against clearances.min_headroom_m, no room ahead is a
finding about the obstacle, and a walker that cannot tell them apart sends the
reader to the wrong repo.

floor_snap_length is set to the step height so a walker stays glued to a
descending slope instead of launching off its crest into frames where the step
probe cannot fire.

The remaining failure is not the walker: see roadmap item 16.
'@

Commit-Repo -Path $root -Files @("PIPELINE_ROADMAP.md", "factory.manifest.json") -Message @'
factory 1.15.0: seventeen of twenty walk, and the last three are one defect

The twenty registered mission sites re-walked with the fixed Lot, bypassing
Level Factory entirely. Seventeen clean. Zero stranded anchors, zero rooms that
failed to bake, zero barrier resolutions outside the casino, every mission spine
walkable across twenty different site geometries -- the anchor work generalises
rather than fitting the one casino it was found on.

The three that fail do so identically, and roadmap item 16 records it with the
numbers: every path proof passing, all four walkers pressed against a stair ramp
with a HORIZONTAL contact normal, on a route the navmesh produced. The ramp is
39.2 degrees with its foot exactly on the slab -- no step to mount, no slope to
fail. The walker is walking into the side of the staircase, 3.4 m of wall,
because the route says it can. The bake and the colliders disagree about the
same staircase.

Also recorded: the twenty runtime_walktest `pass` stamps in the mission registry
predate every fix in this set, and should not be trusted until re-earned.
'@

Write-Host "`n=========== item 16: is the navmesh inside the stairs? ===========" -ForegroundColor Green
Copy-Item "$root\navmesh_solid_probe.gd" "$root\_runs\walkup_siege_proj\" -Force
$env:LOT_GODOT = "C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
& $env:LOT_GODOT --headless --path "$root\_runs\walkup_siege_proj" --script res://navmesh_solid_probe.gd
