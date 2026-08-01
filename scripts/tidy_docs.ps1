# Repo hygiene, pass 1: documents and editor backups. NO code moves here.
#
# WHY THIS PASS IS SEPARATE. Moving the checkers is not a file move, it is a
# code change: check_all.py computes ROOT from __file__ and uses it for two
# different jobs -- finding its sibling scripts AND defining the tree to scan.
# Drop it into tools\ and gd_files() scans tools\ instead of the factory,
# reporting clean over four files instead of 104. A tidy that silently narrows
# what a guardrail looks at is worse than an untidy root. That work needs
# FACTORY_ROOT split from SCRIPT_DIR and a before/after file count, so it is
# pass 2. This pass touches nothing any script reads.
#
# WHAT MOVES
#   root *.md   -> docs\        every markdown except the keepers below
#   *.pre_*     -> _scratch_archive\pre_patch\   editor backups, already
#                                                gitignored and redundant with
#                                                git history
#
# Both are RULES rather than lists, for the reason this repo has now learned
# four separate times: a set that something generates cannot be described by
# enumerating it. `*.pre_*` in particular is generated one suffix per patch.
#
# WHAT STAYS, and why each one earns it -- see $keep below. Two of them are not
# a matter of taste: PIPELINE_MAP.md and PIPELINE_ROADMAP.md are linked 22 times
# by `../` from five independently-versioned repos (zoo, pixelcoat, patina,
# level_factory, lot). Moving them tidies one directory and breaks five repos'
# documentation.
#
# THE GUARD. Before moving a document this scans every root script, every root
# document, and every sub-repo top-level markdown for inbound references to it.
# Anything referenced is held back and reported rather than moved. That check is
# the whole reason to trust this script: the keep-list above was DISCOVERED by
# running exactly this scan by hand, not decided in advance.
#
# Dry run by default. -Commit to move and commit. Nothing is pushed.
param([switch]$Commit)

$ErrorActionPreference = "Continue"
$PSNativeCommandUseErrorActionPreference = $false

$root    = "C:\Projects\gabagool_studios\gabagool_factory"
$docsDir = Join-Path $root "docs"
$bakDir  = Join-Path $root "_scratch_archive\pre_patch"

# Documents that stay at the root, each with the reason it earns the spot.
$keep = [ordered]@{
  "README.md"           = "repo convention -- the first thing a visitor opens"
  "CLAUDE.md"           = "read from the root by tooling; moving it changes behaviour"
  "CHANGELOG.md"        = "repo convention"
  "PIPELINE_MAP.md"     = "12 ../PIPELINE_MAP.md links from five sub-repos"
  "PIPELINE_ROADMAP.md" = "10 ../PIPELINE_ROADMAP.md links from five sub-repos"
}

function Tracked($rel) {
  $r = @(git ls-files -- $rel 2>$null)   # answers 'no' by printing nothing,
  return $r.Count -gt 0                  # not by failing -- see archive_scratch
}

Push-Location $root

# ---------------------------------------------------------------- documents
$docs = @(Get-ChildItem -Path $root -File -Filter "*.md" |
          Where-Object { $_.Name -like "*.md" -and -not $keep.Contains($_.Name) })

# Everything that could plausibly link to a document.
$scan = @()
$scan += @(Get-ChildItem -Path "$root\*" -File -Include *.md, *.py, *.ps1 -ErrorAction SilentlyContinue)
foreach ($d in Get-ChildItem -Path $root -Directory) {
  if ($d.Name -match '^[._]') { continue }
  $scan += @(Get-ChildItem -Path "$($d.FullName)\*" -File -Include *.md -ErrorAction SilentlyContinue)
}

$move = @(); $held = @()
foreach ($doc in $docs) {
  $refs = @()
  foreach ($f in $scan) {
    if ($f.FullName -eq $doc.FullName) { continue }
    if (Select-String -Path $f.FullName -SimpleMatch $doc.Name -Quiet -ErrorAction SilentlyContinue) {
      $refs += (Resolve-Path -Relative $f.FullName)
    }
  }
  if ($refs.Count -gt 0) { $held += [pscustomobject]@{ Doc = $doc; Refs = $refs } }
  else                   { $move += $doc }
}

Write-Host ""
Write-Host "=========== documents ===========" -ForegroundColor Cyan
if ($move.Count -eq 0) { Write-Host "  nothing to move" }
foreach ($d in ($move | Sort-Object Name)) {
  $how = if (Tracked $d.Name) { "git mv" } else { "move  " }
  Write-Host ("  {0}  {1,-24} {2,7} bytes -> docs\" -f $how, $d.Name, $d.Length)
}

if ($held.Count -gt 0) {
  Write-Host ""
  Write-Host "  HELD BACK -- something links to these:" -ForegroundColor Yellow
  foreach ($h in $held) {
    Write-Host ("    {0}" -f $h.Doc.Name) -ForegroundColor Yellow
    foreach ($r in $h.Refs) { Write-Host ("        <- {0}" -f $r) -ForegroundColor DarkYellow }
  }
  Write-Host "  Move these by hand once the links are updated." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Staying at the root by design:" -ForegroundColor DarkGray
foreach ($k in $keep.Keys) { Write-Host ("    {0,-22} {1}" -f $k, $keep[$k]) -ForegroundColor DarkGray }

# ------------------------------------------------------------------ backups
$baks = @(Get-ChildItem -Path $root -File | Where-Object { $_.Name -like "*.pre_*" })
Write-Host ""
Write-Host "=========== editor backups ===========" -ForegroundColor Cyan
if ($baks.Count -eq 0) { Write-Host "  none at the root" }
else {
  $tot = ($baks | Measure-Object Length -Sum).Sum
  foreach ($b in ($baks | Sort-Object Name)) {
    $t = if (Tracked $b.Name) { " TRACKED -- will not move" } else { "" }
    Write-Host ("  {0,-34} {1,7} bytes{2}" -f $b.Name, $b.Length, $t)
  }
  Write-Host ("  {0} file(s), {1:N0} bytes -> _scratch_archive\pre_patch\" -f $baks.Count, $tot)
  Write-Host "  They are copies of files git already has. Kept, not deleted." -ForegroundColor DarkGray
}

# --------------------------------------------------------------- the finding
Write-Host ""
Write-Host "=========== noted, not acted on ===========" -ForegroundColor Cyan
Write-Host "  archive_scratch.ps1 enumerates 23 filenames and the list has rotted:"
Write-Host "  it names lf_patch.ps1, guardrail_regate.ps1 and reconcile_version.ps1,"
Write-Host "  which are standing tools. Only its git-tracked check stops it archiving"
Write-Host "  them. tidy_migrations.ps1 now does the same job by rule. Retiring one of"
Write-Host "  the two is a decision, not a tidy, so this script leaves it alone."

if (-not $Commit) {
  Write-Host ""
  Write-Host "Dry run. Nothing moved. Re-run with -Commit when it looks right." -ForegroundColor Yellow
  Pop-Location
  exit 0
}

# ------------------------------------------------------------------- do it
if ($move.Count -gt 0) {
  New-Item -ItemType Directory -Force -Path $docsDir | Out-Null
  foreach ($d in $move) {
    if (Tracked $d.Name) { git mv -- $d.Name "docs/$($d.Name)" }
    else { Move-Item -Path $d.FullName -Destination (Join-Path $docsDir $d.Name) }
  }
}
$movedBaks = 0
foreach ($b in $baks) {
  if (Tracked $b.Name) { continue }
  New-Item -ItemType Directory -Force -Path $bakDir | Out-Null
  Move-Item -Path $b.FullName -Destination (Join-Path $bakDir $b.Name) -Force
  $movedBaks++
}

$msg = @'
move documents into docs/ and editor backups out of the root

The root held seventeen markdown files, fourteen .pre_* backups and the six
things you actually run, with nothing distinguishing them. Documents now live in
docs/; backups move to _scratch_archive/pre_patch/, which is gitignored, and are
kept rather than deleted because git already has their content and they cost
nothing to keep.

Both splits are rules -- every root *.md except five named keepers, and *.pre_*
-- not lists of names. The keepers are not taste: README, CLAUDE and CHANGELOG
are convention, and PIPELINE_MAP.md and PIPELINE_ROADMAP.md are linked 22 times
by ../ from zoo, pixelcoat, patina, level_factory and lot. Moving those two
would tidy one directory and break five repos' documentation.

Before moving anything the script scans every root script, every root document
and every sub-repo top-level markdown for inbound references, and holds back
whatever is referenced. The keeper list was found by that scan rather than
decided in advance.

No code moved. The checkers stay at the root until check_all.py and
check_freshness.py separate FACTORY_ROOT from SCRIPT_DIR -- both currently
derive the tree they scan from their own __file__, so relocating them would
quietly shrink what they look at while still reporting clean.
'@

$status = git status --short
if ($status) {
  $status | ForEach-Object { Write-Host "  $_" }
  $tmp = [System.IO.Path]::GetTempFileName()
  Set-Content -Path $tmp -Value $msg -Encoding UTF8
  git commit -F $tmp
  Remove-Item $tmp -Force
  Write-Host ""
  Write-Host ("Committed. {0} document(s) in docs\, {1} backup(s) archived. Nothing pushed." `
              -f $move.Count, $movedBaks) -ForegroundColor Green
} else {
  Write-Host "  nothing staged" -ForegroundColor Yellow
}
Pop-Location
