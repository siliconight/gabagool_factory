# Commit the factory-root half of the step pass. The lot and deli_counter halves
# are already in (97366fc and a478863); this is the root repo, which
# commit_step_pass.ps1 did not cover.
#
# Dry run by default. Add -Commit to commit. Nothing is pushed either way.
# Messages are plain per CLAUDE.md -- no trailers, no footers, no assistant
# references. -Branch is opt-in: this repo commits straight to main.
param([switch]$Commit, [string]$Branch = "")

$root = "C:\Projects\gabagool_studios\gabagool_factory"

# The root .gitignore already excludes every tool repo, _runs/, _bridge/,
# __pycache__/ and _scratch_archive/, so the rebuilt scenes and the staged copies
# stay out on their own. Only the editor backup this pass created is new.
$ignore = @("*.pre_rules")

$msg = @'
check_steps: ask the built scenes whether a route is walkable

library_walk forwards the step gate's [lot] lines as each site builds, so
confirming 20 sites are clean meant scrolling an hour of output and trusting that
the ABSENCE of a line meant the check ran. It has not meant that four times in
this pass -- Write-Host is not pipeable, git's stderr went to $null while a
checkout failed, walktest's inner timeout hid behind an outer one, and the gate's
own prints were indented past the filter that forwards them.

This reads the gate back off every scene under _runs in about two seconds and
separates the three answers that matter: clean, blocks a route, and NO SCENE TO
CHECK. The third is the one an absence of output cannot express, and it earned
itself immediately: the first run reported ref_pvp as having no scene, because Lot
names a scene from the spec's `name` field rather than the directory the spec
lives in, and specs/ref_pvp declares ref_pvp_site. A site nobody looked at was
about to read as passing. Scene resolution now tries the declared name, the
directory name, then a single unambiguous non-navqa scene, and still returns
nothing rather than guessing between two.

Also cross-checks that clearances.unassisted_step_max_m still equals what
site_steps enforces, since those two were separately 0.117 and 0.103 for a while.
Exits 1 on any block or missing scene, so it can gate a build rather than only
inform one.

Not fixed here, and worth naming: `python site_steps.py <scene>` cannot produce
the major finding at all. It never passes site_spec, so on_route is empty and
LOT_STEP_BLOCKS_A_ROUTE is unreachable, and it defaults the radius to
qa.walker_capsule_radius_m or 0.4 -- reporting a 0.117 m limit for a body that
walks 0.1025. Every standalone run of that CLI this pass was measuring the wrong
body through a path with the major branch switched off.

CLAUDE.md: four rules earned in this pass

Three are refinements of rules already in the file rather than new ideas, which is
the finding: they were right and not specific enough to fire.

Grounding gets a recovery procedure. The rule said a staged file whose byte count
disagrees with the device is not the file; it did not say what to do next, so the
honest reading was to stop. The staleness is per-path -- lot.py served 68,904
against a reported 85,287 while its .pre_accessor backup staged clean in the same
call. Every patch script records the exact text it applied, so a live file can be
rebuilt from the nearest clean ancestor and VERIFIED, because a byte count landing
exactly on the device's figure is not coincidence at four significant figures.
Both stale files reconstructed to delta zero.

Instruments gets the box-inflation trap: a margin allowed per axis inflates a
polygon along its own axes and over-reports near a corner by up to sqrt(2)*margin.
Same family as the polygon centroids and the level line already listed there.

Two new sections. Attribute every item in a gate's output before patching it --
7 transitions on one site were three separate defects, and fixing the obvious one
would have left 3 findings after a 58-minute sweep and looked like a failed fix.
And an unused parameter is an unfinished thought: _kerb_crossings had accepted the
kerb band's depth since it was written and never read it, which is exactly why the
crossing width was short by up to 5.99 m.

Library after the pass: 20 of 20 walk clean, and 20 of 20 report no rise on a
designed route that a body cannot walk up. Two independent instruments agreeing.
'@

Write-Host ""
Write-Host "=========== factory root ===========" -ForegroundColor Cyan
Push-Location $root
Write-Host "  branch: $((git rev-parse --abbrev-ref HEAD).Trim())"
$status = git status --short
if (-not $status) {
  Write-Host "  clean, nothing to commit"
  Pop-Location
  Write-Host ""
  Write-Host "Nothing to do." -ForegroundColor Yellow
  exit 0
}
$status | ForEach-Object { Write-Host "  $_" }

if ($Commit) {
  if ($Branch) {
    # No 2>$null. Swallowing git's stderr is how a "branching to ..." line got
    # printed while the checkout failed and the commit landed on main anyway.
    Write-Host "  branching to $Branch"
    git checkout -b $Branch
    if ($LASTEXITCODE -ne 0) {
      git checkout $Branch
      if ($LASTEXITCODE -ne 0) {
        Write-Host "  could not switch to $Branch -- NOT committing" -ForegroundColor Red
        Pop-Location; exit 1
      }
    }
  }
  $gi = Join-Path $root ".gitignore"
  $existing = if (Test-Path $gi) { Get-Content $gi } else { @() }
  $added = @($ignore | Where-Object { $existing -notcontains $_ })
  if ($added) {
    Add-Content -Path $gi -Value $added
    Write-Host "  .gitignore += $($added -join ', ')"
  }
  git add -A
  # -F avoids PowerShell re-parsing a message that contains quotes and $null
  $tmp = [System.IO.Path]::GetTempFileName()
  Set-Content -Path $tmp -Value $msg -Encoding UTF8
  git commit -F $tmp
  Remove-Item $tmp -Force
}
Pop-Location

Write-Host ""
if (-not $Commit) {
  Write-Host "Dry run. Nothing committed. Re-run with -Commit when the status above looks right." -ForegroundColor Yellow
} else {
  Write-Host "Committed. Nothing pushed." -ForegroundColor Green
}
