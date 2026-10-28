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

HELD AGAIN 2026-10-27 evening: asked "do the interiors look really good?" I said no (empty lobby, flat plaster, plain teller line, flat light, bare vaults); the walker: "hold the release, do the interior pass first". The manifest patch `patches/patch_factory_manifest_1_42_0.py` is written (story through Zoo 1.139.0 / DC 0.284.0 / Lot 0.135.0) and must be re-read and its story/MOVED updated after the pass.

**Why:** last release 1.41.0 was 2026-10-20; ~40 tool releases since (authoring panel, supermarket, bake-only range, bank light/floor).
**How to apply:** follow 1.41.0's record (root commit ba472e2): promote `factory.manifest.json` with a `patches/patch_factory_manifest_1_42_0.py` (+ result file, `python -m level_factory verify-manifest --factory <root> --strict` from the factory root, all OK); tag each tool at its head (lightweight, tested commits; peel annotated tags with `^{commit}`); `tools/make_factory_package.ps1 -Tag factory-v1.42.0`; install test a fresh unpack (`docs/findings/stranger_install/install_test_12.sh` pattern: setup --venv, make, walk) until one certifies; notes `docs/releases/factory-v1.42.0.md` written AFTER the zip; zip CRCs against the tested zip; publish; then `tools/factory_retire.py`. Related: [[github-push-and-releases]], [[forge-mirrors-github]], [[bank-interior-next]].

2026-10-28: interior pass shipped -- DC 0.285.0 (panelling, bank storefront, vault steel), Zoo 1.140.0 (deposit boxes), Zoo 1.141.0 (chained pens); root ce1a506. Frames 17/18 sent; walker's verdict pending. The drafted manifest patch's STORY/MOVED/ENTRY must add these before it runs. Open before release if the walker wants: lobby officers' desks (DC recipe + migration), darker-than-comp deposit steel, storefront mullions dark from inside.

2026-10-28 later: the walker said "add the lobby desks and fix those two first", then "we need to make the cash! in the vault room!". Shipped Zoo 1.142.0 (9143115: shelving `vault` stock = money racks, glass storefront frames in aluminium, deposit wall painted) and DC 0.286.0 (d26f4e35: lobby desks, `shelf_cash` racks + carts anchored in bank vaults). The walker "agreed" brick/block shopfront frames stay as they are. The manifest patch's STORY/MOVED/ENTRY must add these too; release still waits on the walker seeing the frames.
