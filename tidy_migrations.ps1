# Guardrails phase 3: move the one-shot migrations out of the factory root.
#
# WHY. The root holds ~30 patch*.py and ~13 commit_*.ps1, every one of which
# already ran, alongside the six or seven things you actually run. Nothing
# distinguishes "run this weekly" from "this ran once in July", so the tools are
# lost among the history.
#
# WHAT MOVES, and it is a RULE rather than a list, for the reason the *.pre_*
# ignore taught tonight: `patch*.py` and `commit_*.ps1`. Both name-spaces are
# generated -- a new patch appears every time something gets fixed -- so any
# enumeration of them is a list that is already out of date.
#
# WHAT STAYS: everything else. The checkers (check_*.py, gdcheck.py), the
# harnesses (library_walk.py, rebuild_buildings.py), the standing tools
# (factory_clean.ps1, promote_factory.ps1, archive_scratch.ps1,
# build_portable_walkable.ps1, guardrail_regate.ps1, reconcile_version.ps1,
# render_kit_sheets.ps1, lf_patch.ps1), and the documents.
#
# THESE ARE NOT DELETED, and that matters more than the tidying. Twice tonight a
# file the device bridge served stale was recovered by applying a patch script to
# an older backup and confirming the result landed on the device's byte count.
# That only worked because each patch records the exact before-and-after text it
# applied. They are the only record of how the current source came to be.
#
# `git mv` is used where a file is tracked, so history follows it.
#
# THE ONE EXCEPTION, and it is passed in rather than hardcoded. A patch that has
# not run yet is not history, it is pending work, and filing it under
# migrations/ with "already ran" written above it would be a lie the next reader
# has no way to catch. Name any such file with -Keep. The default is empty on
# purpose: a built-in exception list is an enumeration, and enumerations in this
# repo have now fallen behind the thing they describe four separate times. The
# exception belongs at the call site where somebody can see it.
#
# Dry run by default. Add -Commit to move and commit. Nothing is pushed.
param([switch]$Commit, [string]$Bucket = "2026-07", [string[]]$Keep = @())

$root = "C:\Projects\gabagool_studios\gabagool_factory"
$dest = Join-Path $root "migrations\$Bucket"

function Summarise($path) {
  # First meaningful line of the docstring or header comment -- what it did.
  $lines = Get-Content -Path $path -TotalCount 40 -ErrorAction SilentlyContinue
  foreach ($l in $lines) {
    $t = $l.Trim()
    if ($t -match '^"""(.+)') { return $Matches[1].Trim().TrimEnd('"') }
    if ($t -match '^#\s*(\S.+)') {
      $c = $Matches[1].Trim()
      if ($c -notmatch '^-{3,}$' -and $c -notmatch '^={3,}$') { return $c }
    }
  }
  return ""
}

Push-Location $root
# -Filter goes to the filesystem, which still matches 8.3 short names, so
# "patch*.py" can catch a patch_foo.py.pre_something whose short name ends .py.
# The -like re-check tests the real name. Costs nothing; the alternative is a
# backup silently swept into migrations/ and read later as the live patch.
$items = @()
foreach ($p in @(Get-ChildItem -Path $root -File -Filter "patch*.py")) {
  if ($p.Name -like "patch*.py") { $items += $p }
}
foreach ($p in @(Get-ChildItem -Path $root -File -Filter "commit_*.ps1")) {
  if ($p.Name -like "commit_*.ps1") { $items += $p }
}
$items = $items | Sort-Object Name

if ($Keep) {
  $held = @($items | Where-Object { $Keep -contains $_.Name })
  $missing = @($Keep | Where-Object { $items.Name -notcontains $_ })
  if ($missing) {
    # A -Keep name that matches nothing is almost always a typo, and a typo here
    # moves the file it was meant to protect. Refuse rather than proceed.
    Write-Host ""
    Write-Host "  -Keep names nothing in the move set: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "  Check the spelling. Nothing moved." -ForegroundColor Red
    Pop-Location
    exit 2
  }
  $items = @($items | Where-Object { $Keep -notcontains $_.Name })
  Write-Host ""
  Write-Host "  Held back at the root (not history -- has not run yet):" -ForegroundColor Yellow
  $held | ForEach-Object { Write-Host "    $($_.Name)" -ForegroundColor Yellow }
}

if (-not $items) {
  Write-Host "  nothing to move -- the root is already tidy"
  Pop-Location
  exit 0
}

Write-Host ""
Write-Host "=========== $($items.Count) one-shot migration(s) ===========" -ForegroundColor Cyan
foreach ($i in $items) {
  $tracked = (git ls-files --error-unmatch $i.Name 2>$null)
  $mark = if ($tracked) { "git mv" } else { "move  " }
  Write-Host ("  {0}  {1,-34} {2,7} bytes  {3}" -f $mark, $i.Name, $i.Length,
              $i.LastWriteTime.ToString("yyyy-MM-dd HH:mm"))
}

Write-Host ""
Write-Host "  -> $dest"
Write-Host "  plus migrations\MIGRATIONS.md recording name, size, date and what each did."
Write-Host ""
Write-Host "  Staying at the root:" -ForegroundColor DarkGray
Get-ChildItem -Path $root -File | Where-Object {
  ($_.Extension -in ".py", ".ps1") -and
  ($_.Name -notlike "patch*.py") -and ($_.Name -notlike "commit_*.ps1")
} | ForEach-Object { Write-Host "    $($_.Name)" -ForegroundColor DarkGray }

if (-not $Commit) {
  Write-Host ""
  Write-Host "Dry run. Nothing moved. Re-run with -Commit when the split looks right." -ForegroundColor Yellow
  Pop-Location
  exit 0
}

New-Item -ItemType Directory -Force -Path $dest | Out-Null

$rows = @()
foreach ($i in $items) {
  $rows += [pscustomobject]@{
    Name = $i.Name
    Bytes = $i.Length
    When = $i.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
    What = (Summarise $i.FullName)
  }
  $tracked = (git ls-files --error-unmatch $i.Name 2>$null)
  if ($tracked) { git mv -- $i.Name "migrations/$Bucket/$($i.Name)" }
  else { Move-Item -Path $i.FullName -Destination (Join-Path $dest $i.Name) }
}

$md = @()
$md += "# Migrations"
$md += ""
$md += "One-shot scripts that have already run. **Do not delete them.**"
$md += ""
$md += "Twice in one session a file the device bridge served stale was recovered by"
$md += "applying the patches that followed an older backup and confirming the result"
$md += "landed on the byte count the device reported. That works only because each"
$md += "script records the exact before-and-after text it applied. These are the only"
$md += "record of how the current source came to be."
$md += ""
$md += "Moved here by ``tidy_migrations.ps1``. What stays at the root: the checkers"
$md += "(``check_*.py``, ``gdcheck.py``), the harnesses (``library_walk.py``,"
$md += "``rebuild_buildings.py``), the standing tools, and the documents."
$md += ""
$md += "The split is a RULE, not a list -- ``patch*.py`` and ``commit_*.ps1`` are"
$md += "generated name-spaces, so any enumeration of them is out of date the next time"
$md += "somebody fixes something."
$md += ""
$md += "## $Bucket"
$md += ""
$md += "| script | bytes | last written | what it did |"
$md += "| --- | ---: | --- | --- |"
foreach ($r in ($rows | Sort-Object Name)) {
  $what = $r.What -replace '\|', '\|'
  if ($what.Length -gt 110) { $what = $what.Substring(0, 107) + "..." }
  $md += "| ``$($r.Name)`` | $($r.Bytes) | $($r.When) | $what |"
}
$md += ""
$mdPath = Join-Path $root "migrations\MIGRATIONS.md"
Set-Content -Path $mdPath -Value $md -Encoding UTF8
git add -- "migrations/MIGRATIONS.md"

$msg = @'
move one-shot migrations out of the factory root

The root held ~30 patch*.py and ~13 commit_*.ps1, every one already run, mixed in
with the six things you actually run. Nothing distinguished "run this weekly" from
"this ran once in July", so the tools were lost among the history.

They are NOT deleted, and that is the important part. Twice in one session a file
the device bridge served stale was recovered by applying the patches that followed
an older backup and confirming the rebuilt file landed exactly on the byte count
the device reported. That works only because each script records the exact
before-and-after text it applied, so they are the only record of how the current
source came to be. migrations/MIGRATIONS.md indexes them with size, date and a
one-line description.

The split is a rule -- patch*.py and commit_*.ps1 -- not a list of names. Both are
generated name-spaces: a new one appears every time something gets fixed. An
enumeration would be stale by the next fix, which is exactly how the *.pre_*
ignore list fell four suffixes behind and let ten editor backups into history.
'@

$status = git status --short
if ($status) {
  $status | ForEach-Object { Write-Host "  $_" }
  $tmp = [System.IO.Path]::GetTempFileName()
  Set-Content -Path $tmp -Value $msg -Encoding UTF8
  git commit -F $tmp
  Remove-Item $tmp -Force
  Write-Host ""
  Write-Host "Committed. Nothing pushed." -ForegroundColor Green
  Write-Host "The root now holds tools and documents only; migrations/ holds the history." -ForegroundColor Green
} else {
  Write-Host "  nothing staged"
}
Pop-Location
