# run_3b_unlit.ps1 -- roadmap 47 stage 3b: a real --art --unlit run.
#
#     pwsh -File tools\run_3b_unlit.ps1
#
# `pwsh`, not `powershell`. Windows PowerShell 5.1 and pwsh 7 disagree
# about whether `-Encoding utf8` writes a BOM; the JSON here is written
# through .NET so either host works, but pwsh is what the rest of this
# session ran under and is what these paths were tested against.
#
# Run from the FACTORY ROOT. Writes everything under _runs\3b\ and a fresh
# workspace at workspaces\unlit-3b-ws, so nothing existing is touched.
#
# WHY A NEW MISSION AND A NEW WORKSPACE
#
# lot_demo_001 and art_probe_001 both already have `lux_apply` output on disk.
# Exporting either one as art-unlit proves export-time subtraction -- which
# stage 3a already proved -- and says nothing about a mission where Lux NEVER
# RAN. That is the whole of 3b, so it needs a mission id that has never seen
# the light layer.
#
# WHY THE BRIEF CARRIES lot_library
#
# art_probe_001's own notes: "The planner gates the whole Art layer on that
# key's PRESENCE: `plan art_probe_001 --art` ... produced DAGs containing zero
# art jobs." A 3b run on a brief without it would plan no art at all and
# report success, which is precisely the kind of empty green this whole arc
# has been about. One building and one candidate keep it fast; the library key
# keeps it real.
#
# EVERY STEP STOPS ON FAILURE. A run that carries on past a failed stage is
# how eight downstream absences got mistaken for eight findings.

$ErrorActionPreference = "Stop"

$root    = (Get-Location).Path
$src     = Join-Path $root "_runs\3b\src"
$ws      = Join-Path $root "workspaces\unlit-3b-ws"
$log     = Join-Path $root "_runs\3b\run.log"
$mission = "unlit_probe_001"
$seed    = 5017
$cand    = "$mission.candidate.seed_$seed"
$cli     = "level_factory\apps\cli\main.py"
$library = Join-Path $root "deli_counter\build"

# BOM-FREE, IN EITHER HOST. `Out-File -Encoding utf8` writes a BOM under
# Windows PowerShell 5.1 and does not under pwsh 7, and the first run of this
# script hit exactly that: `batch create` refused with "Unexpected UTF-8 BOM
# (decode using utf-8-sig)". The tool was right to refuse. Writing through
# .NET with an explicit no-BOM encoder removes the host from the question.
function Write-Utf8NoBom($path, $text) {
    $enc = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($path, $text, $enc)
}

function Step($label, $block) {
    Write-Host ""
    Write-Host "=== $label ===" -ForegroundColor Cyan
    "" | Tee-Object -FilePath $log -Append | Out-Null
    "=== $label ===" | Tee-Object -FilePath $log -Append | Out-Null
    & $block 2>&1 | Tee-Object -FilePath $log -Append
    if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
        throw "$label exited $LASTEXITCODE -- stopping. See $log"
    }
}

# ---------------------------------------------------------------- 0. setup
New-Item -ItemType Directory -Force -Path (Join-Path $src "briefs") | Out-Null
Remove-Item -Force -ErrorAction SilentlyContinue $log
Write-Utf8NoBom $log "3b run started $(Get-Date -Format o)`r`n"

@{
    schema       = "level_factory.batch.v0.1"
    batch_id     = "unlit_3b"
    name         = "Roadmap 47 stage 3b -- a mission that never ran Lux"
    seed_base    = $seed
    theme_family = "rockay"
    missions     = @($mission)
} | ConvertTo-Json -Depth 5 | ForEach-Object {
    Write-Utf8NoBom (Join-Path $src "batch.json") $_
}

@{
    schema                  = "level_factory.mission_brief.v0.1"
    mission_id              = $mission
    display_name            = "Unlit probe"
    archetype               = "bank"
    building_count          = 1
    candidate_count         = 1
    # THE KEY THAT GATES THE ART LAYER. Without it the planner produces a DAG
    # with zero art jobs and the run reports success -- see art_probe_001's
    # notes. A 3b that proved nothing would look exactly like a 3b that
    # passed.
    lot_library             = $library
    landmark                = "unlit_probe"
    site_shape              = "street_row"
    route_shape             = "along_the_street"
    extraction_relationship = "street_exit"
    objective_hypotheses    = @("cross_the_block")
    target_minutes          = @(6, 10)
    theme                   = "rockay"
    time_of_day             = "night"
    weather                 = "clear"
    verticality             = "medium"
    notes                   = "Roadmap 47 stage 3b. Purpose: run a mission with --art --unlit through the real tools so that lux_apply NEVER runs, then export art-unlit and portability-test it. Everything before this proved export-time subtraction from a mission that HAD run Lux. One building, one candidate: the point is the layer set, not the scale."
} | ConvertTo-Json -Depth 5 | ForEach-Object {
    Write-Utf8NoBom (Join-Path $src "briefs\$mission.json") $_
}

Write-Host "source written to $src"
if (-not (Test-Path $library)) {
    throw "lot_library does not exist: $library -- the art layer will not plan"
}

# THIS SCRIPT OWNS THIS PATH. A half-finished run leaves a workspace that
# `init` will not overwrite, and a 3b measured against leftovers from a
# previous attempt is not a measurement.
if (Test-Path $ws) {
    Write-Host "removing previous $ws"
    Remove-Item -Recurse -Force $ws
}
Step "init workspace" { python $cli init $ws }

# Tool paths come from the workspace that already runs the real tools. A 3b
# that resolved different binaries would be measuring a different toolchain.
Copy-Item (Join-Path $root "workspaces\lot-demo-ws\tools.local.json") `
          (Join-Path $ws "tools.local.json") -Force
Write-Host "copied tools.local.json from lot-demo-ws"

Step "doctor"       { python $cli -C $ws doctor }
Step "batch create" { python $cli -C $ws batch create (Join-Path $src "batch.json") }

# ------------------------------------------------- 1. graybox + lock
# --target functional-lock exits 1 when findings are open; both are fine here.
Write-Host ""
Write-Host "=== run functional-lock ===" -ForegroundColor Cyan
python $cli -C $ws run $mission --target functional-lock 2>&1 | Tee-Object -FilePath $log -Append

Step "approve brief"     { python $cli -C $ws approve $mission brief_approved }
Step "approve candidate" { python $cli -C $ws approve $mission candidate_selected --candidate $cand }
Step "approve lock"      { python $cli -C $ws approve $mission functional_shell_locked }

# ------------------------------------------------ 2. THE RUN. Unlit.
# Blender and headless Godot from here. This is the long part.
Write-Host ""
Write-Host "=== run --art --unlit --gameplay  (Blender/Godot; this is the long one) ===" -ForegroundColor Yellow
python $cli -C $ws run $mission --art --unlit --gameplay 2>&1 | Tee-Object -FilePath $log -Append

Step "plan, for the record" { python $cli -C $ws plan $mission --art --unlit --gameplay }

# ------------------------------------------------ 3. export + portability
Step "export art-unlit" {
    python $cli -C $ws export $mission --mode art-unlit --format folder
}
Step "portability art-unlit" {
    python $cli -C $ws portability-test $mission --mode art-unlit
}

# ------------------------------------------------ 4. what landed
Write-Host ""
Write-Host "=== job directories ===" -ForegroundColor Cyan
Get-ChildItem (Join-Path $ws ".level_factory\jobs") -Directory |
    Select-Object -ExpandProperty Name |
    Tee-Object -FilePath $log -Append

Write-Host ""
Write-Host "=== the two questions 3b exists to answer ===" -ForegroundColor Cyan
$luxDir = Join-Path $ws ".level_factory\jobs\$mission.lux_apply"
$msg = if (Test-Path $luxDir) {
    "LOOK  lux_apply ran -- --unlit did not take: $luxDir"
} else {
    "ok    lux_apply never ran"
}
$msg | Tee-Object -FilePath $log -Append
$gate = Join-Path $ws ".level_factory\jobs\$mission.lux_fixture_gate"
$msg2 = if (Test-Path $gate) {
    "ok    lux_fixture_gate DID run -- the fixture pass stayed in the art layer"
} else {
    "LOOK  lux_fixture_gate missing -- more than the render was dropped"
}
$msg2 | Tee-Object -FilePath $log -Append

Write-Host ""
Write-Host "log: $log"
Write-Host "workspace: $ws"
Write-Host ""
Write-Host "Then, for the record:" -ForegroundColor Cyan
Write-Host "  python $cli -C $ws export $mission --mode portable-godot --format folder"
Write-Host "  python tools\probe_unlit_ab.py $ws $mission"
Write-Host ""
Write-Host "That last pair is the interesting one: exporting portable-godot"
Write-Host "from a mission that never ran Lux. If it succeeds, portable-godot"
Write-Host "and art-unlit are the same package for this mission -- which is"
Write-Host "true and worth seeing stated by an artifact."
