# Commit the step-gate pass: the accessor, the player capsule, the derived slab
# stack, the angle-aware kerb cut, and the gate's on-route test.
#
# Dry run by default: prints `git status --short` per repo and stops. Add
# -Commit to commit. Nothing is pushed either way.
#
# Messages are plain per CLAUDE.md -- no co-authorship trailers, no generated-by
# footers, no assistant references. -Branch is OPT-IN: every repo here commits
# straight to main, which is the only branch any of them has.
param([switch]$Commit, [string]$Branch = "")

$root = "C:\Projects\gabagool_studios\gabagool_factory"

# Scratch and editor backups. `_bridge` holds COPIES of files tracked elsewhere
# in the tree; committing a second lot.py is how the next reader patches the
# wrong one. The *.pre_* files exist so a bad change is one copy away from
# undone -- they are not history.
$ignore = @("_bridge/", "__pycache__/", "_scratch_archive/",
            "*.pre_wp", "*.pre_wpdefault", "*.pre_gate", "*.pre_visible",
            "*.pre_accessor", "*.pre_angle")
$ignoreLot = @(
  "specs/*/buildings/*.manifest.json",
  "specs/*/buildings/*.slots.json",
  "specs/*/buildings/*.navigation.json",
  "specs/*/buildings/*.validation.json",
  "specs/*/buildings/*.combat_audit.json"
)

$msgDeli = @'
contract: the step limit comes off the BODY, not the bake radius

clearances.unassisted_step_max_m was derived from nav_bake.agent_radius_m (0.4),
giving 0.117. But the bake radius is not a body: the contract's own note calls it
"fattest navigating character + 0.05 safety", so it is deliberately larger than
anything that walks. The step a body walks up is a property of the body --
characters.player.radius_m, 0.35, giving 0.1025.

site_steps already read the player radius, so the gate enforcing this field
reported 0.103 while the field said 0.117: two numbers for one quantity, live at
the same time. The derivation is recorded alongside the value so the next change
to a body re-derives instead of re-picking.
'@

$msgLot = @'
lot: let _agent() return the contract it claims to be the source of truth for

    for sec in merged:
        merged[sec].update(data.get(sec, {}))

iterated the DEFAULTS' keys, not the file's. _AGENT_DEFAULTS carried nav_bake and
qa, so `characters` and `clearances` were read off disk and discarded -- by a
function whose docstring calls it one source of truth for character metrics and
derived clearances while carrying neither. The step gate died on
KeyError: 'characters' every build, and the walk-scene player capsule was a
string literal three lines under an agent_radius that reads the contract
properly, because the accessor could not reach characters.player at all.

Merge what the file has. A section added to the contract tomorrow then reaches
callers without editing this function, which is the point of having one source of
truth. The missing-file fallbacks are refreshed to today's ratified values; they
still said climb 0.5 and cell 0.15 after both had changed, so a build with no
contract present would have silently used the numbers that severed the
staircases.

lot: the walk-scene player capsule reads the contract

It was 0.4 radius against a contract player of 0.35, so the body a human walks
was wider than the body every clearance was derived for.

lot: derive the outdoor slab thicknesses instead of picking them

PATH_THICK 0.10, COURT_THICK 0.12, ROAD_THICK 0.08 were chosen against
max_step_up_m (0.5) -- what a controller can LIFT itself over -- rather than
against what a capsule walks up. Every adjacent pair has to clear the walk limit
in BOTH directions, and the sidewalk is on the other side of each slab:

    ground 0.00  -> slab                  slab <= step
    slab         -> sidewalk SIDEWALK_H   SIDEWALK_H - slab <= step

so a walkable slab is squeezed into [SIDEWALK_H - step, step], today
[0.0575, 0.1025]. COURT_THICK had drifted out of it: ground -> courtyard was
0.12 m, a wall, and ballpark_block's own circulation crosses it. PATH_THICK was
inside by 2.5 mm. The three now sit at fixed fractions of the band and move
together when the gameplay team picks a different body. SIDEWALK_H is NOT derived
and does not move -- a kerb is meant to be a wall, which is the whole reason kerb
cuts exist. An empty band is reported rather than clamped quietly.

lot: size the kerb cut to the crossing, not to the path's width

The cut centres were already right to the centimetre. The width assumed every
crossing was head-on: a strip of width w meeting a line at angle t leaves
w/sin(t) on that line, and a kerb is a band, not a line, so the strip also shears
along it by depth*cos(t)/sin(t). On ballpark_block a 6 m path meets the kerb at
35 degrees and needs 12.0 m; 7.2 m was dropped; so the route spilled onto the
sidewalk sections either side of each cut and met a 0.16 m wall on four of them.

The sidewalk depth was already a parameter of _kerb_crossings and had never been
used. A crossing shallow enough to drop more than three path widths of kerb is
reported, because the honest fix there is usually to re-route.

site_steps: an exact distance decides what is on a route

_point_in allowed `margin` of slack on each of a polygon's own axes, which
inflates it per-axis -- a box, not the set of points within `margin`. Near a
corner it over-reports by up to sqrt(2)*margin, and it did: two sidewalk sections
were reported as blocking a route whose exact clearance to them was 3.43 m
against a 3.00 m half-width. A body never reaches them. An instrument reporting a
wall nothing can touch is the same substitution defect it was written to catch,
so the slack test now rejects and an exact point-to-edge distance decides.

site_steps: the gate runs, and its output survives the filter

findings() is wired into assemble() and reported in the result. Two prints
mattered: the wiring guard keyed on the words "site_steps" appearing anywhere in
lot.py, and a comment already contained them, so the patch reported success and
skipped the wiring; and the gate's lines were indented, while library_walk
forwards on startswith("[lot]") and adds the indent itself, so every line it
produced -- findings and the STEP GATE DID NOT RUN notice alike -- was dropped.

ballpark_block before: LOT_STEP_BLOCKS_A_ROUTE, 7 transitions. Four were the cut
width, two were the gate over-reporting, one was the courtyard slab.
'@

$repos = @(
  @{ Path = "$root\deli_counter"; Msg = $msgDeli; Label = "deli_counter" },
  @{ Path = "$root\lot";          Msg = $msgLot;  Label = "lot"; Extra = $ignoreLot }
)

foreach ($r in $repos) {
  Write-Host ""
  Write-Host "=========== $($r.Label) ===========" -ForegroundColor Cyan
  Push-Location $r.Path
  Write-Host "  branch: $((git rev-parse --abbrev-ref HEAD).Trim())"
  $status = git status --short
  if (-not $status) { Write-Host "  clean, nothing to commit"; Pop-Location; continue }
  $status | ForEach-Object { Write-Host "  $_" }

  if ($Commit) {
    if ($Branch) {
      # No 2>$null anywhere. Swallowing git's stderr is how a "branching to ..."
      # line got printed while the checkout failed and the commit landed on main.
      Write-Host "  branching to $Branch"
      git checkout -b $Branch
      if ($LASTEXITCODE -ne 0) {
        git checkout $Branch
        if ($LASTEXITCODE -ne 0) {
          Write-Host "  could not switch to $Branch -- NOT committing" -ForegroundColor Red
          Pop-Location; continue
        }
      }
    }
    $patterns = $ignore
    if ($r.ContainsKey("Extra")) { $patterns = $ignore + $r.Extra }
    $gi = Join-Path $r.Path ".gitignore"
    $existing = if (Test-Path $gi) { Get-Content $gi } else { @() }
    $added = @($patterns | Where-Object { $existing -notcontains $_ })
    if ($added) {
      Add-Content -Path $gi -Value ""
      Add-Content -Path $gi -Value "# scratch and editor backups -- copies of tracked files, not history"
      $added | ForEach-Object { Add-Content -Path $gi -Value $_ }
      Write-Host "  .gitignore += $($added -join ', ')"
    }
    git add -A
    # -F avoids PowerShell re-parsing a message that contains quotes
    $tmp = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $tmp -Value $r.Msg -Encoding UTF8
    git commit -F $tmp
    Remove-Item $tmp -Force
  }
  Pop-Location
}

Write-Host ""
if (-not $Commit) {
  Write-Host "Dry run. Nothing committed. Re-run with -Commit when the status above looks right." -ForegroundColor Yellow
} else {
  Write-Host "Committed. Nothing pushed." -ForegroundColor Green
}
