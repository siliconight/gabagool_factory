# Lot 0.30.0 + Level Factory 0.22.0 + factory 1.14.0.
# Also prints seed 5017's stuck detail from the real file -- the mount this
# session reads through has been serving stale bytes all day.
$ErrorActionPreference = "Continue"
$PSNativeCommandUseErrorActionPreference = $false
$root = "C:\Projects\gabagool_studios\gabagool_factory"

Write-Host "`n=========== what stopped seed 5017's walkers ===========" -ForegroundColor Green
$rep = "$root\rockay-ws\.level_factory\jobs\category5_baie_dore_001.walktest_navqa.candidate.seed_5017\out\site_navqa.walktest.json"
if (Test-Path $rep) {
  $j = Get-Content $rep -Raw | ConvertFrom-Json
  Write-Host ("  ok={0}  proof_failures={1}" -f $j.ok, $j._proof_failures)
  foreach ($w in $j.walkers) {
    if ($w.status -like "ok*") { continue }
    Write-Host ("  {0}: {1}   reached {2}/{3}" -f $w.name, $w.status,
        $w.targets_reached, $w.targets_total) -ForegroundColor Yellow
    if ($null -ne $w.waypoint) {
      Write-Host ("     steering to ({0}, {1}, {2}), {3} m short, waypoint {4}/{5}; on_floor={6} on_wall={7}" -f `
          $w.waypoint[0], $w.waypoint[1], $w.waypoint[2], $w.waypoint_dist_m,
          $w.path_index, $w.path_points, $w.on_floor, $w.on_wall)
    }
    if ($null -eq $w.PSObject.Properties['blocked_by']) {
      Write-Host "     blocked_by: ABSENT -- this report predates Lot 0.30.0; re-run to get it" -ForegroundColor DarkYellow
    } elseif (@($w.blocked_by).Count -eq 0) {
      Write-Host "     TOUCHING NOTHING -- the geometry did not block it. This is the walker's steering, not the level." -ForegroundColor Cyan
    } else {
      foreach ($c in $w.blocked_by) {
        Write-Host ("     pressing against {0}  normal ({1}, {2}, {3})  at ({4}, {5}, {6})" -f `
            $c.collider, $c.normal[0], $c.normal[1], $c.normal[2],
            $c.at[0], $c.at[1], $c.at[2]) -ForegroundColor Cyan
      }
    }
  }
} else { Write-Host "  no report at $rep" -ForegroundColor Yellow }

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

Commit-Repo -Path "$root\lot" -Tag "v0.30.0" -Files @(
  "godot/addons/heist_nav_qa/nav_qa_director.gd", "VERSION", "CHANGELOG.md"
) -Message @'
nav QA: a stuck walker records what it is stuck against

Seed 5017 put all four walkers on the same coordinate, (20.5, 0.9, -2.7), on the
same leg, with every path proof passing. The report said where and not what, so
settling it meant reconstructing the site colliders offline -- 1,475 of them --
and that could not answer it either: six metres of clear floor in both axes
around the point and an unobstructed straight line to the target. The obstacle
is whatever move_and_slide is touching, and only the engine knows that.

On giving up, _drive now captures every slide collision -- collider name, node
path, contact normal, contact point -- plus the waypoint it was steering to, how
far short it stopped, where that sits in the path, and is_on_floor/is_on_wall.

The empty case is the one worth having. A capsule wedged in geometry is a level
defect. A capsule stopped in open space touching NOTHING is this tool steering
itself into a corner, and blaming a level for that is how an afternoon goes
missing.
'@

Commit-Repo -Path "$root\level_factory" -Tag "v0.22.0" -Files @(
  "packages/jobs/scheduler.py",
  "apps/cli/commands/__init__.py",
  "adapters/walktest/__init__.py",
  "tests/unit/test_walktest_adapter.py",
  "tests/unit/test_candidate_scoped_failure.py",
  "tests/unit/test_lasertag_readiness.py",
  "VERSION", "CHANGELOG.md", "pyproject.toml"
) -Message @'
a candidate that fails is eliminated, not fatal

Five candidates are generated so the weak ones can be dropped. Mission-wide
fail-fast defeated exactly that: the first blocked job halted the whole DAG, so
a candidate was never eliminated -- it took its siblings down with it, their
jobs never dispatched, and their stable out/ directories kept the previous run
artifacts where the next reader mistook them for current answers. A Laser Tag
finding on seed 5320 is how seed 5320 own walktest came to be skipped for an
evening and read as a passing geometry check.

Job.candidate_id already carried the distinction; the scheduler was not using
it. A candidate-scoped failure now records the candidate in
RunSummary.eliminated_candidates and lets every other candidate finish. A
mission-level failure still stops the run, because nothing downstream of one can
be salvaged by carrying on.

Dependents needed no special handling: ready is only appended when a dependency
SUCCEEDS, so anything downstream of a failed job never becomes ready. What was
missing was saying so. RunSummary.not_run_reason gives every un-dispatched job
its sentence, and cmd_run prints both beside the job count that already read as
a complete account of the run.

0.21.0, folded in here: WALKTEST_WALKER_STUCK carries the walker contact and the
waypoint it was steering to, so a stuck finding names an obstacle instead of a
coordinate -- or says it was touching nothing, which points at this tool rather
than the level.

test_a_route_never_walked_on_a_full_clock_blocks is rewritten rather than
deleted. It asserted the contract 0.20.0 changed, and it was right about the old
one; the new version asserts non-blocking, keeps the reachability category, and
requires the message to name walktest_navqa -- a demoted finding that does not
point at the instrument which owns the verdict leaves the reader nowhere to go.

This is the precondition for WALKTEST_ENFORCED. Flipping it before this would
have turned one flawed candidate into a dead mission.
'@

Commit-Repo -Path $root -Files @("PIPELINE_ROADMAP.md", "factory.manifest.json") -Message @'
factory 1.14.0: enforcement is now a decision rather than a blocked one

Lot 0.30.0 + Level Factory 0.22.0. Roadmap item 15 closed: a candidate-scoped
failure eliminates the candidate and the run continues, which was the one thing
standing between the walktest and being a real gate.

Also restores the "Not to be worked on" heading, which I deleted when inserting
items 14 and 15 -- the section body has been sitting under item 15 since, which
reads as though the combat exclusions were part of it.

Item 14 stays open and is now instrumented rather than investigated: the next
run says what seed 5017 walkers were touching, and an empty contact list moves
it from the level to the walker steering.
'@

Write-Host "`n=========== left over ===========" -ForegroundColor Green
foreach ($p in @("$root\lot", "$root\level_factory", $root)) {
  Push-Location $p
  Write-Host "`n$p" -ForegroundColor Cyan
  git status --short | Where-Object { $_ -notmatch '^\?\?' }
  Pop-Location
}
