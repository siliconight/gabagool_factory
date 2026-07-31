# Commit the 2026-07-27 pipeline-integrity work, one repo at a time.
# Review each `git status` before it commits; nothing is pushed.
#
# Staging rule: this script stages tracked modifications only, plus the new
# files a caller names. `git add -A` was used here once and swept four repos'
# untracked work into README commits -- dispatch got 28 files of Level Factory
# smoke-test output, and deli_counter, pixelcoat and patina each got real source
# work committed under a message that described a README banner. A commit that
# does not say what is in it is worse than no commit, so new files are opt-in.
$root = "C:\Projects\gabagool_studios\gabagool_factory"

function Commit-Repo {
  param(
    [string]$path,
    [string]$message,
    [string[]]$include = @()    # new (untracked) files this commit intends
  )
  Push-Location $path
  Write-Host "`n=== $path ===" -ForegroundColor Cyan
  git status --short
  if (-not (git status --porcelain)) { Write-Host "  (nothing to commit)"; Pop-Location; return }

  git add -u                                  # tracked modifications and deletions
  foreach ($f in $include) { git add -- $f }  # named new files, nothing else

  # Anything still untracked was NOT part of this commit. Say so out loud
  # rather than letting it ride along or vanish unnoticed.
  $left = git ls-files --others --exclude-standard
  if ($left) {
    Write-Host "  left untracked (not in this commit):" -ForegroundColor Yellow
    $left | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
  }

  git diff --cached --quiet
  if ($LASTEXITCODE -eq 0) { Write-Host "  (nothing staged)"; Pop-Location; return }
  git commit -m $message | Out-Host
  git show --stat --oneline HEAD | Select-Object -First 8
  Pop-Location
}

Commit-Repo "$root\lot" @"
Cover guardrails: route placement, derived clearance, emitted-geometry read-back

- site_cover: place cover along the crew's route, not only between marker
  pairs, on a budget that scales with route length. Marker pairs describe the
  opening and say nothing about the ground the crew has to cross.
- site_cover: derive building clearance from deli_counter/agent_contract.json
  (2*ceil(radius/cell)*cell + 2*cell) instead of a flat 2.0 measured to a
  piece's centre, which left a 0.5 m lane against a bake that needs 1.2 m.
- site_cover: read back the emitted rectangles and report LOT_COVER_PINCH for
  any lane the site's own cover closes below that minimum, measured against
  the buildings and the perimeter walls.
- lot: emit LT_CoverTestPoints from the cover actually placed. They were a
  hardcoded rosette 5 m around the objective, so the bot's cover-seek has
  never once pointed at real cover.
- cater: needs_build compares a spec digest against a <glb>.spec.sha256 stamp
  rather than mtimes, which tie inside a single coarse clock tick.
"@

Commit-Repo "$root\level_factory" @"
Runs that can account for themselves

- adapters/laser_tag: hash the addon sources into fingerprint_inputs. Laser Tag
  publishes no VERSION, so probe() contributed nothing and a patched addon kept
  serving the previous grade while reporting success.
- jobs/scheduler: exclude *.provenance.json from a job's output set. Sidecars
  re-entered it every run and added a level of nesting each time; at seventeen
  the path passed MAX_PATH and killed the run before any stage did work.
- staging/godot_project: replace staged sibling subtrees instead of keeping the
  first one forever.
- validation/lasertag_report: gate on the enemy's first shot rather than the
  both-sides contact metric, and demote LT_NO_SURVIVABLE_OPENING to
  non-blocking. Laser Tag is not the authority on the combat model it measures;
  the owned guardrail is LOT_ROUTE_EXPOSED, offline, before the scene is written.
"@

Commit-Repo "$root\lasertag" @"
Measure on the physics clock; publish per-side openings

- LT_RunState: tick elapsed_seconds in _physics_process. Every combat event
  that reads it is produced on the physics frame, so a render-frame clock
  stamped shots at 0.0 and made the timings unusable.
- LT_MetricsCollector: publish avg_time_to_first_enemy_shot and
  avg_time_to_first_player_shot. Both were tracked per run and discarded at
  aggregation, leaving every consumer reading the combined figure as if it
  were the enemy's.
- LT_ScoreCalculator: judge pacing and exposure by the enemy's opening rather
  than the run's first shot from either side, which marked down the maps whose
  placement worked.
- LT_BotPlayerController: bound cover-seek by reachability so the bot stops
  abandoning its route for cover it cannot reach.
"@

Commit-Repo $root -include @("PIPELINE_MAP.md") -message @"
Add PIPELINE_MAP.md: the authority boundary and the standalone contract

The deliverable is a level shell that must work in someone else's Godot
project with none of these tools present, and these tools are not the
authority on gameplay or networking. Documents every repo's role, what it
owns and what it must not decide, the job DAG, artifact locations, the
collision contract, and a procedure for deciding where a change belongs.
Both READMEs point at it; PIPELINE_ROADMAP.md carries the live state.
"@

foreach ($tool in @("deli_counter","zoo","pixelcoat","patina","lux","dispatch")) {
  Commit-Repo "$root\$tool" @"
README: point at PIPELINE_MAP.md, and state what this repo owns

Says what this repo decides and what it must not, so a change starts from the
boundary rather than discovering it. The map covers the DAG, the standalone
package contract, and the rule that runtime findings are requests for
guardrails upstream.
"@
}

Write-Host "`n=== manifest lockstep ===" -ForegroundColor Cyan
# verify-manifest resolves tool paths relative to the factory root, so the
# factory root is the cwd it has to run from -- not level_factory.
Push-Location $root
python -m level_factory verify-manifest --factory $root
Pop-Location
