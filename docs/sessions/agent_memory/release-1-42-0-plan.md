---
name: release-1-42-0-plan
description: "Walker 2026-10-27 — cut factory 1.42.0 after the bank's step 2 (DC 0.281.0); publish to GitHub now, forge later by --backfill"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-27T18:30:11.074Z
---

Walker, 2026-10-27, asked "we are also probably due for a new release/package?". Chose: cut 1.42.0 AFTER the bank's step 2 (Deli Counter 0.281.0 check desk + cash carts, Zoo 1.135.0) is shipped and shown; publish to GitHub (`gh` is on the allow list); the forge gets it later with `tools/publish_release.py --backfill` once the walker has recreated BMONEY/gabagool_factory, pushed main once by hand (Git Credential Manager stores the token) and allowed the script. Bank step 4 (wall finishes) waits for the release. SUPERSEDED the same day: shown the furnished lobby, the walker said "fix it before we rush to the release" -- finish the bank (walls, dressing, identity) FIRST, then cut 1.42.0.

**Why:** last release 1.41.0 was 2026-10-20; ~40 tool releases since (authoring panel, supermarket, bake-only range, bank light/floor).
**How to apply:** follow 1.41.0's record (root commit ba472e2): promote `factory.manifest.json` with a `patches/patch_factory_manifest_1_42_0.py` (+ result file, `python -m level_factory verify-manifest --factory <root> --strict` from the factory root, all OK); tag each tool at its head (lightweight, tested commits; peel annotated tags with `^{commit}`); `tools/make_factory_package.ps1 -Tag factory-v1.42.0`; install test a fresh unpack (`docs/findings/stranger_install/install_test_12.sh` pattern: setup --venv, make, walk) until one certifies; notes `docs/releases/factory-v1.42.0.md` written AFTER the zip; zip CRCs against the tested zip; publish; then `tools/factory_retire.py`. Related: [[github-push-and-releases]], [[forge-mirrors-github]], [[bank-interior-next]].
