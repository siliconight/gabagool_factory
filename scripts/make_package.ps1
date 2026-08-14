<#
.SYNOPSIS
    Build the shareable Level Factory package for lot_demo_001, end to end.

.DESCRIPTION
    Run from the FACTORY ROOT. Stops at the first failure rather than
    carrying on, because every step here depends on the one before it.

    Without -Candidate it runs as far as the candidate comparison and stops,
    because choosing which candidate ships is a person's call. Re-run with
    -Candidate <id> to finish.

        .\make_package.ps1
        .\make_package.ps1 -Candidate lot_demo_001.candidate.seed_5118

.NOTES
    The proof is the portability test, not the export. `export` writes a
    package; `portability-test` opens it in a CLEAN Godot project with no
    Level Factory, no addons, and nothing else on disk, and reports whether
    the engine could actually parse and instantiate it. A package that
    exports and fails that test is not portable, it is just a folder.
#>
[CmdletBinding()]
param(
    [string]$Candidate = "",
    [string]$Mission   = "lot_demo_001",
    [string]$Workspace = "lot-demo-ws"
)

$ErrorActionPreference = "Stop"

function Step($n, $text) {
    Write-Host ""
    Write-Host "=== [$n] $text" -ForegroundColor Cyan
}

function Assert-LastExit($what, [int[]]$Allow = @(0)) {
    if ($Allow -notcontains $LASTEXITCODE) {
        Write-Host ""
        Write-Host "STOPPED: $what exited $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

if (-not (Test-Path ".\level_factory")) {
    Write-Host "run this from the factory root (the folder holding level_factory\)" -ForegroundColor Red
    exit 1
}

$lf = @("-m", "level_factory", "-C", $Workspace)

Step 1 "run the mission (art + gameplay layers)"
# --art is not optional for this package. `grade what ships` keys the Lot
# grade off the themed_site_assemble stage, so a graybox-only run grades a
# draw the package will not contain -- which is the exact defect that
# invalidated the previous candidate selection.
python @lf run $Mission --art --gameplay
# exit 1 means findings, not failure. Only 2+ is a stop.
Assert-LastExit "run" @(0, 1)

Step 2 "compare the candidates on the numbers"
python .\compare_candidates.py $Workspace $Mission
Assert-LastExit "compare_candidates" @(0, 1)

if (-not $Candidate) {
    Write-Host ""
    Write-Host "Pick a candidate from the table above, then re-run:" -ForegroundColor Yellow
    Write-Host "  .\make_package.ps1 -Candidate <id>" -ForegroundColor Yellow
    exit 0
}

Step 3 "select the candidate"
python @lf approve $Mission candidate_selected --candidate $Candidate
Assert-LastExit "approve"

Step 4 "export the portable package (folder + zip)"
# --format zip writes the folder AND zips it; portability-test needs the
# folder, and the zip is what you send.
python @lf export $Mission --format zip
Assert-LastExit "export"

Step 5 "portability test -- open it in a clean Godot project"
python @lf portability-test $Mission
Assert-LastExit "portability-test"

$exportDir = Join-Path $Workspace ".level_factory\exports\$Mission.portable-godot"
# NOT "$exportDir.zip". `zip_export` names the archive with
# Path.with_suffix(".zip"), and pathlib reads ".portable-godot" as the
# suffix -- so the mode is REPLACED rather than appended and the archive
# lands at <mission>.zip. Beyond this script: exporting two modes of one
# mission writes both archives to that same name, and the second silently
# overwrites the first.
$zipPath   = Join-Path $Workspace ".level_factory\exports\$Mission.zip"

Step 6 "what came out"
if (Test-Path $zipPath) {
    $zip = Get-Item $zipPath
    Write-Host ("  package : {0}  ({1:N1} MB)" -f $zip.FullName, ($zip.Length / 1MB))
} else {
    Write-Host "  no zip at $zipPath" -ForegroundColor Yellow
}
foreach ($f in @("mission.tscn", "project.godot", "HANDOFF.md",
                 "export_closure_scan.json", "output_layers.json",
                 "portable_resource_manifest.json", "LICENSES.json")) {
    $p = Join-Path $exportDir $f
    if (Test-Path $p) { Write-Host "  $f" } else { Write-Host "  MISSING $f" -ForegroundColor Yellow }
}

Write-Host ""
Write-Host "Send the .zip plus PACKAGE_README.md. The portability report above" -ForegroundColor Green
Write-Host "is the claim; everything else is decoration." -ForegroundColor Green
