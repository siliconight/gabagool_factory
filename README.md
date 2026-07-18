# gabagool_factory

The Siliconight tool factory: nine standalone tools that build DD
missions, plus the coordination layer that versions them as a SET.

## Two-layer versioning

**Layer 1 - each tool** is a standalone git repo with its own semver, VERSION
file, CHANGELOG, and tags. Tools ship as versioned paste-over packages and are
pushed/tagged independently. Code changes ALWAYS land in a tool repo - never
at this level.

**Layer 2 - the factory** versions the *combination*. `factory.manifest.json`
pins the tool versions that were certified together (built, gated, and smoked
as a set). This repo tracks only that manifest and its docs; every tool
directory is gitignored. Bump `factory_version` when the certified set
changes, tag `factory-vX.Y.Z`.

## Lockstep check

The checking code lives in Level Factory (code stays in tools):

    level-factory verify-manifest --factory C:\Projects\gabagool_studios\gabagool_factory

OK = installed VERSION matches the pin. DRIFT = same major, re-certify the
set and bump the manifest. INCOMPATIBLE = major bump, adapters likely broken.
UNKNOWN = no VERSION source (see notes on patina / pixelcoat / lasertag in
the manifest).

## Release flow for a tool change

1. Paste the tool's versioned package over its repo root; commit, tag, push
   in THAT repo.
2. Run the relevant gates (zoo\tools\walkabout.ps1, lux\tools\headless_walk.ps1,
   LF fast suite / real-tool smoke).
3. Update `factory.manifest.json` to the new pin, bump `factory_version`,
   note it in CHANGELOG.md, commit + tag here (`factory-vX.Y.Z`).
