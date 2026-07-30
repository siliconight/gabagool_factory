# Commit the tooling pass: the site_steps CLI, the build-freshness gate, and the
# CLAUDE.md amendment.
#
# Dry run by default. Add -Commit to commit. Nothing is pushed either way.
# Messages are plain per CLAUDE.md -- no trailers, no footers, no assistant
# references. -Branch is opt-in: these repos commit straight to main.
param([switch]$Commit, [string]$Branch = "")

$root = "C:\Projects\gabagool_studios\gabagool_factory"

$ignore = @("*.pre_cli", "*.pre_stamp", "*.pre_endings")

$msgLot = @'
site_steps: make the CLI able to report its own worst finding

Three defects that compounded into a check which could not fail.

It never passed site_spec, and findings() builds on_route only when it has one --
so the set was always empty and LOT_STEP_BLOCKS_A_ROUTE, the only major code and
the one that means a body following the site's own circulation is stopped, was
unreachable from the command line. Every standalone run reported at most the minor
off-route code and read as reassuring.

It measured the wrong body:

    r = float(((contract.get("qa") or {}).get("walker_capsule_radius_m")) or 0.4)

The QA walker is deliberately narrower than the player and the 0.4 fallback is the
BAKE radius, deliberately wider than any body. What a capsule walks up is a
property of the player, so it reported a 0.117 m limit for a body that walks
0.1025 while the build gate two files away reported 0.103 from the same contract.

And it only read a contract if handed one, so with no argument every number fell
back and the output looked authoritative while being derived from nothing. It now
searches $DC_AGENT_CONTRACT then the deli_counter sibling, the order lot.py
already uses, and refuses to report at all rather than reporting fallbacks.

The spec is found by matching spec["name"] against the scene's stem before falling
back to the directory, because Lot names a scene from the name FIELD --
specs/ref_pvp/ref_pvp_site.json builds ref_pvp_site.tscn, and a directory called
ref_pvp_site also exists, so a single pass accepting either would resolve by
listing order rather than by intent.

Exit codes distinguish the three outcomes: 0 checked and clean, 1 checked and
found a major finding, 2 COULD NOT check. A run whose major branch was unreachable
must not exit 0, or every wrapper reads "could not check" as "passed", which is
the whole reason this needed fixing.
'@

$msgRoot = @'
check_freshness: does the geometry the library walks match what made it

library_walk stages a site by copying lot/specs/<site>/buildings/ into a throwaway
project, so the .glb in each site folder IS the geometry that gets walked, and
nothing checked that it corresponded to anything. deli_a01.json was three days
newer than its export and no gate noticed; the sweep walked geometry that did not
match its spec and came back green.

The worse case is a BUILDER edit, not a spec edit. The stair ramp foot fix changed
deli_counter/stairwell.py and staled every .glb in the library at once with no
spec contents changing, so a check comparing each .glb only against its own spec
would have reported all 57 as fresh.

Hashes, not mtimes: mtimes do not survive a git checkout, so an mtime rule reports
either everything stale or nothing depending on clone order. rebuild_buildings now
writes <stem>.buildstamp.json beside each export recording the SHA-256 of the spec
that fed it, of the build inputs that produced it, and of the .glb itself. The
stamp is written at the moment of export, because writing it any other time
records a claim instead of checking one.

What counts as a build input is a RULE, not a list: every root-level .py in
deli_counter except test_*, plus agent_contract.json. A curated list of builder
modules is precisely the thing that stops matching reality quietly. The contract
is in there because it is an input and not just a document -- agent_contract.py
reads it, so a clearance change moves geometry with no source file touched, and it
changed after the last rebuild. It over-reports: editing a status script stales
everything. Over-reporting costs a rebuild; under-reporting ships a level that
does not match its spec.

Two exit codes for two different failures. 1 means the geometry is KNOWN not to
match. 2 means it cannot be checked -- no stamp yet, or a .glb with no
deli_counter spec. Collapsing them would leave the gate permanently red for every
building without a spec, and a gate that is always red gets ignored, which ends
the same place as a gate that is always green. A .glb with no stamp never reports
fresh.

CLAUDE.md: compare bytes, not characters

The reconstruction procedure added last commit verifies a rebuilt file by byte
count, and that verification fails for a reason unrelated to staleness. Python
reads text with universal newlines, so len(text) on a CRLF file is short by
exactly one byte per line -- lot.py.pre_accessor read as 81,669 characters against
83,419 bytes, a 1,750-byte gap that is precisely its 1,750 CRLFs, and for a few
minutes it looked like the rebuild had failed. Read the ancestor as bytes, or
restore the endings before measuring. Git's autocrlf also means on-disk endings
can change between sessions with no content change, so a byte count is evidence
about one working tree at one moment.
'@

$repos = @(
  @{ Path = "$root\lot"; Msg = $msgLot;  Label = "lot" },
  @{ Path = $root;       Msg = $msgRoot; Label = "factory root" }
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
      # No 2>$null. Swallowing git's stderr is how a "branching to ..." line got
      # printed while the checkout failed and the commit landed on main anyway.
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
    $gi = Join-Path $r.Path ".gitignore"
    $existing = if (Test-Path $gi) { Get-Content $gi } else { @() }
    $added = @($ignore | Where-Object { $existing -notcontains $_ })
    if ($added) {
      Add-Content -Path $gi -Value $added
      Write-Host "  .gitignore += $($added -join ', ')"
    }
    git add -A
    # -F avoids PowerShell re-parsing a message that contains quotes and $null
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
