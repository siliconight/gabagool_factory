# Move this pass's one-shots out of the factory root. Dry run unless -Apply.
#
# Nothing is deleted and nothing git tracks is touched. The tracked check asks
# `git ls-files -- <path>` and tests whether it printed anything: the first
# version used `--error-unmatch`, which reports "not tracked" by writing to
# stderr, and PowerShell turns native stderr into an error record that
# ErrorActionPreference=Stop then treats as fatal. A query that answers "no" by
# failing is a bad shape for a query.
#
# _runs/ is deliberately NOT archived. It holds the teed run logs, and the whole
# reason seed 5320 went unexplained for an evening is that there was no record
# of what a run actually did.
param([switch]$Apply)

$ErrorActionPreference = "Continue"
$PSNativeCommandUseErrorActionPreference = $false
$root = "C:\Projects\gabagool_studios\gabagool_factory"
$dest = Join-Path $root ("_scratch_archive\" + (Get-Date -Format yyyyMMdd_HHmmss))

$files = @(
  # this pass
  "commit_anchor_work.ps1", "commit_anchors.ps1", "commit_fixup.ps1",
  "commit_route_gate.ps1", "commit_snapdown.ps1", "commit_item5.ps1",
  "commit_lasertag_version.ps1", "commit_session.ps1", "commit_walktest.ps1",
  "patch_route_gate.py", "patch_run_summary.py", "rerun_5320.ps1",
  "run_anchor_fix.ps1", "navbake_experiment.ps1", "split_swept_commits.ps1",
  # earlier passes
  "commit_gate_hardening.ps1", "commit_pass.ps1", "commit_placement_gate.ps1",
  "undo_smoke_out.ps1", "lf_patch.ps1", "guardrail_regate.ps1",
  "recertify.ps1", "reconcile_version.ps1"
)
$dirs = @("_fresh", "_navbake", "_navgate")

Push-Location $root
$moved = 0; $kept = 0; $absent = 0

foreach ($f in ($files + $dirs)) {
  $p = Join-Path $root $f
  if (-not (Test-Path $p)) { $absent++; continue }

  $tracked = @(git ls-files -- $f 2>$null)
  if ($tracked.Count -gt 0) {
    Write-Host ("  KEEP    {0}  -- git tracks it" -f $f) -ForegroundColor Yellow
    $kept++
    continue
  }

  $size = if (Test-Path $p -PathType Container) {
    $s = (Get-ChildItem $p -Recurse -File -ErrorAction SilentlyContinue |
          Measure-Object Length -Sum).Sum
    "{0:N1} MB" -f (($s | ForEach-Object { $_ }) / 1MB)
  } else { "{0:N0} B" -f (Get-Item $p).Length }

  if ($Apply) {
    New-Item -ItemType Directory -Force $dest | Out-Null
    Move-Item $p (Join-Path $dest $f) -Force
    Write-Host ("  MOVED   {0}  ({1})" -f $f, $size) -ForegroundColor DarkGray
  } else {
    Write-Host ("  would move  {0}  ({1})" -f $f, $size)
  }
  $moved++
}

Write-Host ""
if ($Apply) {
  Write-Host ("{0} moved to {1}; {2} kept because git tracks them; {3} already gone." `
      -f $moved, $dest, $kept, $absent) -ForegroundColor Green
  Write-Host "Delete that folder yourself once you have looked in it." -ForegroundColor DarkGray
} else {
  Write-Host ("{0} would move, {1} kept (tracked), {2} already gone. Re-run with -Apply." `
      -f $moved, $kept, $absent) -ForegroundColor Cyan
}

Write-Host "`n=========== still untracked at the root ===========" -ForegroundColor Green
git status --short | Where-Object { $_ -match '^\?\?' }
Pop-Location
