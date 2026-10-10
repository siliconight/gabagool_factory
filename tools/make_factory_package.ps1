# make_factory_package.ps1 -- one zip a stranger can make levels with: every TRACKED file of
# every factory repo, Deli Counter's built building library, and no run record unless asked.
#
#     powershell -ExecutionPolicy Bypass -File tools\make_factory_package.ps1 [-WithRecord]
#
# WHAT TRAVELS (roadmap 202, docs\findings\stranger_install\):
#   - Every tracked file of the eleven repos at their checked-out HEADs. `git archive` is the
#     packager, so untracked and ignored state (workspaces\, _runs\, _scratch\, _archive\,
#     caches, .pre_ snapshots) never enters a git object and cannot enter this zip.
#   - Deli Counter's library: build\ less floorplans\, the shells and sidecars a lot draws its
#     buildings from. Git ignores the meshes, so a zip of tracked files alone carried 0 of 146
#     shells, and every level a stranger made would have placed one generated shell N times
#     (`building_library.index` starts from the GLBs it finds). It travels only when Deli
#     Counter has no uncommitted change and its own `build_freshness.py` calls it up to date,
#     and it is stamped later than the sources: `git archive` stamps every tracked file with its
#     commit's time, and Level Factory's freshness check compares times.
#   - Not the run record -- docs\cold_runs, docs\findings, patches, _runs and workspaces,
#     824 of 987 MB on 2026-10-07 -- which a level maker never reads. -WithRecord includes it.
#
# Two caveats, stated so nobody learns them from the recipient:
#   - UNCOMMITTED work does not travel. Commit first, or it is not in the zip.
#   - tracked-but-scratchy files DO travel (anything committed by accident).
#     If the zip looks fat, `git ls-files` in the offending repo names them.
#   -Tag factory-vX.Y.Z (roadmap 202, the GitHub release): package the CERTIFIED set rather than
#   the checkouts' HEADs. The root is archived at that tag, and each tool at the tag the
#   manifest AT THAT TAG names for it, so the zip is the set verify-manifest read all OK and
#   the install test ran, whatever has been committed since. A tag that does not exist refuses,
#   and so does a Deli Counter whose HEAD is not its tag, since the library beside the code is
#   built from HEAD and would not match. The zip is named by the tag.
param([switch]$WithRecord, [string]$Tag = "")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$tagged = @{}
if ($Tag) {
  $null = git -C $root rev-parse -q --verify "refs/tags/$Tag"
  if ($LASTEXITCODE -ne 0) { throw "no tag $Tag on the factory root" }
  $manifestText = git -C $root show "${Tag}:factory.manifest.json" | Out-String
  $manifest = $manifestText | ConvertFrom-Json
  $tagged["."] = $Tag
  foreach ($prop in $manifest.tools.PSObject.Properties) {
    $folder = if ($prop.Value.path) { $prop.Value.path } else { $prop.Name }
    $toolTag = $prop.Value.tag
    $null = git -C (Join-Path $root $folder) rev-parse -q --verify "refs/tags/$toolTag"
    if ($LASTEXITCODE -ne 0) { throw "no tag $toolTag in $folder (named by the manifest at $Tag)" }
    $tagged[$folder] = $toolTag
  }
  Write-Host ("packaging the certified set {0} (factory {1})" -f $Tag, $manifest.factory_version)
}
$stage = Join-Path ([System.IO.Path]::GetTempPath()) "gabagool_pkg_$stamp"
New-Item -ItemType Directory -Force -Path $stage | Out-Null
# The run record. `_runs` and `workspaces` hold 48 tracked files (5.2 MB on 2026-10-10):
# measurements, an attic, and three old workspaces' files, none of which a level reads.
$record = @("docs/cold_runs", "docs/findings", "patches", "_runs", "workspaces")
$tar = Join-Path $env:SystemRoot "System32\tar.exe"
if (-not (Test-Path $tar)) { throw "no ${tar}: this script packages with Windows' own tar" }
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) "gabagool_repo_$stamp.tar"
# Whatever happens below, the staging folder and the tar do not outlive the run: the first
# failed run of this version left both in the temp folder.
try {

# The factory root repo itself, then every child directory that is its own
# repo. Nested repos are invisible to the root's git, so there is no overlap.
$repos = @(@{ name = "."; path = $root })
Get-ChildItem -Directory $root |
  Where-Object { Test-Path (Join-Path $_.FullName ".git") } |
  ForEach-Object { $repos += @{ name = $_.Name; path = $_.FullName } }

Write-Host ("packaging {0} repo(s) from {1}{2}" -f $repos.Count, $root,
  $(if ($WithRecord) { ", with the run record" } else { ", without the run record" }))
foreach ($r in $repos) {
  $dest = if ($r.name -eq ".") { $stage } else { Join-Path $stage $r.name }
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  # the tree to archive: HEAD, or the certified tag when -Tag names the set
  $ref = "HEAD"
  if ($Tag) {
    if (-not $tagged.ContainsKey($r.name)) { throw "the manifest at $Tag names no tag for $($r.name)" }
    $ref = $tagged[$r.name]
  }
  $head = git -C $r.path rev-parse --short $ref
  $dirty = git -C $r.path status --porcelain
  $flag = if ($dirty -and -not $Tag) { "  (UNCOMMITTED CHANGES NOT INCLUDED)" } else { "" }
  Write-Host ("  {0,-16} @ {1} ({2}){3}" -f $r.name, $head, $ref, $flag)
  # ARCHIVE TO A FILE, NEVER THROUGH A PIPE: PowerShell pipes are text
  # pipes, and binary tar data through one arrives mangled. This script's
  # first run did exactly that -- eleven "Unrecognized archive format"
  # errors under a printed success line, because nothing checked an exit
  # code. Both lessons are below.
  if ($r.name -eq "." -and -not $WithRecord) {
    $paths = @(".") + ($record | ForEach-Object { ":(exclude)$_" })
    git -C $r.path archive --format=tar -o $tmp $ref -- @paths
  } else {
    git -C $r.path archive --format=tar -o $tmp $ref
  }
  if ($LASTEXITCODE -ne 0) { throw "git archive failed for $($r.name)" }
  # WINDOWS' OWN tar, by path: from a shell that puts Git's /usr/bin first,
  # `tar` is GNU tar, which reads `C:\...` as a remote host and stops with
  # "Cannot connect to C: resolve failed" (2026-10-10, run from Git Bash).
  & $tar -xf $tmp -C $dest
  if ($LASTEXITCODE -ne 0) { throw "tar extract failed for $($r.name)" }
  Remove-Item $tmp
}

# THE LIBRARY. Refused rather than shipped stale or mismatched: a library built from code that
# is not the code in the zip is a level nobody here has seen.
$dc = Join-Path $root "deli_counter"
if (git -C $dc status --porcelain) {
  throw "deli_counter has uncommitted changes: the library may not match the code that travels"
}
if ($Tag -and (git -C $dc rev-parse HEAD) -ne (git -C $dc rev-parse "refs/tags/$($tagged['deli_counter'])^{commit}")) {
  throw "deli_counter's HEAD is not its certified tag $($tagged['deli_counter']): the library beside it is built from HEAD and would not match the code that travels"
}
python (Join-Path $dc "build_freshness.py")
if ($LASTEXITCODE -ne 0) {
  throw "deli_counter's build_freshness.py calls the library stale: rebuild it (python build.py --all in deli_counter) first"
}
$lib = @(git -C $dc ls-files --others --ignored --exclude-standard build |
  Where-Object { $_ -notlike "build/floorplans/*" })
$shells = @($lib | Where-Object { $_ -like "build/*.glb" }).Count
if ($shells -lt 1) { throw "deli_counter\build holds no shells: there is no library to carry" }
$now = Get-Date
foreach ($rel in $lib) {
  $dst = Join-Path (Join-Path $stage "deli_counter") $rel
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
  Copy-Item -LiteralPath (Join-Path $dc $rel) -Destination $dst
  (Get-Item -LiteralPath $dst).LastWriteTime = $now
}
Write-Host ("library: {0} files, {1} shells, stamped {2}" -f $lib.Count, $shells, $now)

$n = (Get-ChildItem -Recurse -File $stage).Count
if ($n -lt 50) { throw "staging holds only $n file(s) -- refusing to zip a hollow package" }
Write-Host ("staged {0} files" -f $n)
$zipName = if ($Tag) { "gabagool_factory_package_$Tag.zip" } else { "gabagool_factory_package_$stamp.zip" }
$zip = Join-Path (Split-Path -Parent $root) $zipName
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip -Force
Write-Host "package: $zip"
Write-Host "point the recipient at START_HERE.md first."

} finally {
  if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
  if (Test-Path $tmp) { Remove-Item -Force $tmp }
}
