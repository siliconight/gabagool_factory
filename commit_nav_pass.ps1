# Commit the navmesh/walker pass across the repos it touched.
#
# Dry run by default: prints `git status --short` per repo and stops. Add
# -Commit to actually commit. Nothing is pushed either way.
#
# Commit messages are plain per CLAUDE.md -- no co-authorship trailers, no
# generated-by footers, no assistant references.
param([switch]$Commit, [string]$Branch = "nav-walker-pass")

$root = "C:\Projects\gabagool_studios\gabagool_factory"

# Editor backups this pass created. They exist so a bad change is one copy away
# from undone; they are not history.
$junk = @(
  "lot\godot\addons\heist_nav_qa\nav_qa_director.gd.pre_wp",
  "lot\godot\addons\heist_nav_qa\nav_qa_director.gd.pre_wpdefault"
)

# Scratch this pass created, or that predates it. `git add -A` would take all of
# it: _bridge holds COPIES of files already tracked elsewhere in the tree (it
# exists only because the device mount served stale bytes and a never-staged
# path was the workaround), and committing a second copy of lot.py is how the
# next reader ends up patching the wrong one.
$ignore = @("_bridge/", "__pycache__/", "*.pre_wp", "*.pre_wpdefault")

# build.py writes seven sidecars beside each .glb. Lot reads exactly two of them
# -- gameplay.json (13 references) and lights.json (7). It reads none of the
# rest, and slots.json alone is ~118 KB per building, so committing all 57 would
# add several megabytes of JSON nothing in the pipeline opens. The .glb files
# themselves ARE tracked and DO get committed: the 20/20 sweep is not
# reproducible from a clean checkout without them.
$ignoreLot = @(
  "specs/*/buildings/*.manifest.json",
  "specs/*/buildings/*.slots.json",
  "specs/*/buildings/*.navigation.json",
  "specs/*/buildings/*.validation.json",
  "specs/*/buildings/*.combat_audit.json"
)

$msgDeli = @'
stairs: land the collision ramp on the floor at the foot of a flight

The ramp is set half a step proud so its surface rides the step nosings, which
is right along the run and wrong where the run meets the floor: the surface
started step_rise/2 above it, plus half the slab's thickness through the tilt.
That is a riser at the first step -- the thing a smooth ramp exists to remove.
Measured 0.26 m on apartment_walkup_a01 against 0.117 that a capsule walks up
unassisted, and the walktest walkers parked against it.

Extend the ramp downhill until its top surface reaches floor level, and shift
the centre by half the extension so the head of the flight does not move. All
three emission sites: straight/switchback/scissor, and both legs of an L.

The geometry lands in stairwell.ramp_foot_extension so it can be tested without
Blender; deli_counter imports bpy at module scope. Eight stair test modules
existed and none mentioned the ramp collider, which is why this shipped.

contract: agent_max_climb 0.5 -> 0.15, cell_size 0.15 -> 0.10

agent_max_climb was letting the bake promise climbs a body cannot make -- a
0.49 m stair stringer and a 0.16 m kerb, against 0.117 that a capsule walks.
Lowering it severed every stair steeper than 45 deg, because the same number
also governs how a continuous slope is discretised: Recast joins adjacent voxel
columns only within walkableClimb, and on a ramp that gap is
cell_size * tan(pitch). Finer cells separate the two jobs -- 0.10 carries the
declared 55 deg slope limit while keeping the step ceiling at 0.15.
'@

$msgLot = @'
nav-qa: stop the walker eating the waypoint that rounds a corner

Waypoints were consumed by proximity against a hardcoded 0.6 m. On
warehouse_district the corner waypoint sat 0.45 m away -- inside that radius --
so it was marked reached while the body was still on the wrong side of the
corner, and the body then steered at the far waypoint straight into the
building's north wall. Four walkers on two sites, on_wall with a horizontal
normal, on a path every leg of which is clear for a body.

Consume on WP_RADIUS or on having PASSED the waypoint. Both are load-bearing:
a radius alone cannot tell near from behind, and passed alone stalls at the
first waypoint where the projection is exactly zero.

WP_RADIUS is derived, not chosen: the clearance a funnelled corner offers is
(bake radius) - (walker radius), the walker is 0.7 * AGENT_RADIUS, so the
margin is 0.3 * AGENT_RADIUS and this takes 60% of it. A pinned 0.15 was right
at cell_size 0.15 and clipped at 0.10.

walktest: --timeout, threaded into the call that kills Godot

run_one bounded Godot at a hardcoded 300 s while library_walk's --timeout only
bounded the outer python, so raising the sweep timeout changed nothing and a
1352 m spine on a dense navmesh reported NO REPORT instead of TIMEOUT.

site_steps: the step a capsule can actually walk up

A capsule meets a low step on its bottom hemisphere, so the contact normal is
sloped and the engine calls it floor only inside floor_max_angle. The tallest
step a body WALKS up with no step-up code is radius * (1 - cos(floor_max_angle))
-- 0.117 for the 0.4 body, against SIDEWALK_H of 0.16. max_step_up_m is what a
controller can LIFT itself over, which is a different number and was standing in
for this one.

Rebuilds every library building through Blender so the stair fix reaches the
geometry the sweep walks. Sidecars Lot does not read are gitignored rather than
committed.
'@

$msgRoot = @'
library walks 20/20 clean

Five defects, three of them in the instruments rather than the levels:
a stair ramp that started proud of its own floor, a bake that promised climbs
no body can make, a climb limit that also severed legal slopes, a QA walker
that consumed its corner waypoints, and a harness timeout that made a
connected site look broken.

Adds rebuild_buildings.py (re-export every building the library walks, in
place, matched to its deli_counter spec) and gdcheck.py (gdparse plus the
three GDScript traps a grammar cannot see). CLAUDE.md gains four rules earned
here: ground yourself in the repo before patching, report measurements rather
than causes, treat a null result as evidence about the wiring, and derive
constants instead of picking them.

Buildings re-exported: 57 across 62 site slots.
'@

$repos = @(
  @{ Path = "$root\deli_counter"; Msg = $msgDeli; Label = "deli_counter" },
  @{ Path = "$root\lot";          Msg = $msgLot;  Label = "lot"; Extra = $ignoreLot },
  @{ Path = $root;                Msg = $msgRoot; Label = "factory root" }
)

foreach ($r in $repos) {
  Write-Host ""
  Write-Host "=========== $($r.Label) ===========" -ForegroundColor Cyan
  Push-Location $r.Path
  $branch = (git rev-parse --abbrev-ref HEAD).Trim()
  $onDefault = $branch -in @("main", "master")
  if ($onDefault) {
    Write-Host "  branch: $branch  <- DEFAULT BRANCH" -ForegroundColor Yellow
  } else {
    Write-Host "  branch: $branch"
  }
  $status = git status --short
  if (-not $status) { Write-Host "  clean, nothing to commit"; Pop-Location; continue }
  $status | ForEach-Object { Write-Host "  $_" }

  if ($Commit) {
    if ($onDefault) {
      Write-Host "  branching to $Branch before committing to $branch"
      git checkout -b $Branch 2>$null
      if ($LASTEXITCODE -ne 0) { git checkout $Branch }
    }
    # keep the scratch out of history rather than out of the working tree
    $gi = Join-Path $r.Path ".gitignore"
    $existing = if (Test-Path $gi) { Get-Content $gi } else { @() }
    $patterns = $ignore
    if ($r.ContainsKey("Extra")) { $patterns = $ignore + $r.Extra }
    $added = @()
    foreach ($pat in $patterns) {
      if ($existing -notcontains $pat) { $added += $pat }
    }
    if ($added) {
      Add-Content -Path $gi -Value ""
      Add-Content -Path $gi -Value "# scratch and editor backups -- copies of tracked files, not history"
      $added | ForEach-Object { Add-Content -Path $gi -Value $_ }
      Write-Host "  .gitignore += $($added -join ', ')"
    }
    foreach ($j in $junk) {
      $full = Join-Path $root $j
      if ((Test-Path $full) -and $full.StartsWith($r.Path)) {
        Write-Host "  skipping backup $j"
      }
    }
    git add -A
    foreach ($j in $junk) {
      $full = Join-Path $root $j
      if ($full.StartsWith($r.Path)) { git reset -q -- $full 2>$null }
    }
    # -F avoids PowerShell re-parsing a message that contains quotes
    $tmp = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $tmp -Value $r.Msg -Encoding UTF8
    git commit -F $tmp
    Remove-Item $tmp -Force
  }
  Pop-Location
}

Write-Host ""
if (-not $Commit) {
  Write-Host "Dry run. Nothing committed. Re-run with -Commit when the status above looks right." -ForegroundColor Yellow
} else {
  Write-Host "Committed. Nothing pushed." -ForegroundColor Green
}
