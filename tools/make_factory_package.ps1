# make_factory_package.ps1 -- one zip of every TRACKED file in every factory
# repo, and nothing else. git archive is the packager: untracked and ignored
# state (workspaces\, _runs\, _scratch\, _archive\, build\ outputs, caches,
# .pre_ snapshots) never enters a git object, so it cannot enter this zip.
# What the recipient gets is exactly what fresh clones of all eleven repos
# would give them, in one file, at the commits currently checked out here.
#
#     powershell -File tools\make_factory_package.ps1
#
# Two caveats, stated so nobody learns them from the recipient:
#   - UNCOMMITTED work does not travel. Commit first, or it is not in the zip.
#   - tracked-but-scratchy files DO travel (anything committed by accident).
#     If the zip looks fat, `git ls-files` in the offending repo names them.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$stage = Join-Path ([System.IO.Path]::GetTempPath()) "gabagool_pkg_$stamp"
New-Item -ItemType Directory -Force -Path $stage | Out-Null

# The factory root repo itself, then every child directory that is its own
# repo. Nested repos are invisible to the root's git, so there is no overlap.
$repos = @(@{ name = "."; path = $root })
Get-ChildItem -Directory $root |
  Where-Object { Test-Path (Join-Path $_.FullName ".git") } |
  ForEach-Object { $repos += @{ name = $_.Name; path = $_.FullName } }

Write-Host ("packaging {0} repo(s) from {1}" -f $repos.Count, $root)
foreach ($r in $repos) {
  $dest = if ($r.name -eq ".") { $stage } else { Join-Path $stage $r.name }
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  $head = git -C $r.path rev-parse --short HEAD
  $dirty = git -C $r.path status --porcelain
  $flag = if ($dirty) { "  (UNCOMMITTED CHANGES NOT INCLUDED)" } else { "" }
  Write-Host ("  {0,-16} @ {1}{2}" -f $r.name, $head, $flag)
  # ARCHIVE TO A FILE, NEVER THROUGH A PIPE: PowerShell pipes are text
  # pipes, and binary tar data through one arrives mangled. This script's
  # first run did exactly that -- eleven "Unrecognized archive format"
  # errors under a printed success line, because nothing checked an exit
  # code. Both lessons are below.
  $tmp = Join-Path ([System.IO.Path]::GetTempPath()) "gabagool_repo_$stamp.tar"
  git -C $r.path archive --format=tar -o $tmp HEAD
  if ($LASTEXITCODE -ne 0) { throw "git archive failed for $($r.name)" }
  tar -xf $tmp -C $dest
  if ($LASTEXITCODE -ne 0) { throw "tar extract failed for $($r.name)" }
  Remove-Item $tmp
}

$n = (Get-ChildItem -Recurse -File $stage).Count
if ($n -lt 50) { throw "staging holds only $n file(s) -- refusing to zip a hollow package" }
Write-Host ("staged {0} tracked files" -f $n)
$zip = Join-Path (Split-Path -Parent $root) "gabagool_factory_package_$stamp.zip"
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip -Force
Remove-Item -Recurse -Force $stage
Write-Host "package: $zip"
Write-Host "point the recipient at USING_THE_FACTORY.md first."
