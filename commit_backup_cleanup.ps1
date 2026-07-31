# Untrack the editor backups that just got committed, and stop enumerating.
#
# WHAT HAPPENED. commit_walkable_pass.ps1 ignores backups by listing suffixes:
#
#     "*.pre_step", "*.pre_walkable", "*.pre_paths", "*.pre_manifest"
#
# Tonight's patches created *.pre_source, *.pre_bind, *.pre_bindtext and
# *.pre_threshold, none of which that list had heard of, so five backups went
# into history:
#
#     lot.py.pre_source
#     library_walk.py.pre_bind, .pre_bindtext, .pre_source, .pre_threshold
#
# These are copies of files already tracked in the same commit. Committing them
# means the next reader can open the wrong one, and it is exactly what the
# original ignore comment says it exists to prevent.
#
# THE SAME LESSON, THIRD TIME. GATE_SEVERITY enumerated codes and missed
# `moderate`. check_freshness deliberately uses a RULE for build inputs -- every
# root .py except test_* -- rather than a curated list, and says why. This list
# should have been `*.pre_*` from the start: the suffix is generated per patch, so
# any enumeration of it is a list that will be wrong the next time someone writes
# a patch.
#
# Dry run by default. Add -Commit to commit. Nothing is pushed either way.
param([switch]$Commit)

$root = "C:\Projects\gabagool_studios\gabagool_factory"

$repos = @(
  @{ Path = "$root\lot"; Label = "lot" },
  @{ Path = $root;       Label = "factory root" }
)

$msg = @'
untrack editor backups, and ignore them by rule rather than by list

Five *.pre_* files went into the previous commit: lot.py.pre_source and four
library_walk.py backups. They are copies of files tracked in the same commit, and
the next person to open one is patching a file that is not the file.

The ignore list enumerated suffixes -- pre_step, pre_walkable, pre_paths,
pre_manifest -- and each patch invents a new one, so the list was guaranteed to
fall behind the thing it describes. `*.pre_*` is the rule the enumeration was
approximating.

Third instance of the same shape in one pass. A severity lookup table missed a
level the emitters use; a build-input list would have missed the agent contract
had it not been written as a rule. Where the set is generated, describe it.
'@

foreach ($r in $repos) {
  Write-Host ""
  Write-Host "=========== $($r.Label) ===========" -ForegroundColor Cyan
  Push-Location $r.Path

  $tracked = @(git ls-files "*.pre_*")
  if (-not $tracked) {
    Write-Host "  no tracked *.pre_* files"
  } else {
    Write-Host "  tracked backups to untrack:"
    $tracked | ForEach-Object { Write-Host "    $_" }
  }

  $gi = Join-Path $r.Path ".gitignore"
  $existing = if (Test-Path $gi) { Get-Content $gi } else { @() }
  $needsRule = $existing -notcontains "*.pre_*"
  if ($needsRule) { Write-Host "  .gitignore needs: *.pre_*" }
  else { Write-Host "  .gitignore already has *.pre_*" }

  if ($Commit) {
    if ($needsRule) {
      Add-Content -Path $gi -Value ""
      Add-Content -Path $gi -Value "# editor backups from patch_*.py -- copies of tracked files, not history."
      Add-Content -Path $gi -Value "# A RULE, not a list: each patch invents its own suffix, so any enumeration"
      Add-Content -Path $gi -Value "# of them falls behind the next patch that gets written."
      Add-Content -Path $gi -Value "*.pre_*"
    }
    if ($tracked) {
      foreach ($f in $tracked) { git rm --cached -q -- $f }
      Write-Host "  untracked $($tracked.Count) file(s); they stay on disk"
    }
    $status = git status --short
    if (-not $status) {
      Write-Host "  nothing to commit"
    } else {
      $status | ForEach-Object { Write-Host "  $_" }
      $tmp = [System.IO.Path]::GetTempFileName()
      Set-Content -Path $tmp -Value $msg -Encoding UTF8
      git commit -F $tmp
      Remove-Item $tmp -Force
    }
  }
  Pop-Location
}

Write-Host ""
if (-not $Commit) {
  Write-Host "Dry run. Nothing changed. Re-run with -Commit when the list looks right." -ForegroundColor Yellow
  Write-Host "The backups stay on disk either way -- this only stops them being tracked." -ForegroundColor Yellow
} else {
  Write-Host "Committed. Nothing pushed." -ForegroundColor Green
  Write-Host "Backups remain on disk; they are just no longer in history." -ForegroundColor Green
}
