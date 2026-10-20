---
name: github-push-and-releases
description: "Walker 2026-10-10: push the root repo to github.com/siliconight/gabagool_factory and put the standalone package on GitHub Releases (the repo itself unchanged); the auto-mode classifier blocks git push / gh release as out-of-place publication, so the walker allows it or runs the commands"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-15T03:57:29.916Z
---

The walker, 2026-10-10: "I also want to start pushing to this GIT Repo:
https://github.com/siliconight/gabagool_factory -- the standalone package as a
release ... not change what the repo of the gabagool_factory is, but use GIT
releases as the place where the package would go".

- The root repo's `origin` IS that URL (public, default branch main). Each
  tool repo has its own `siliconight/<tool>` remote; the walker named only
  the root. The tool sources reach a new user through the package, not the
  push.
- The package for a release is built AT THE CERTIFIED TAGS:
  `tools/make_factory_package.ps1 -Tag factory-vX.Y.Z` (added 2026-10-10)
  reads the manifest at that tag and archives each repo at its tag; the
  zip lands in `C:\Projects\gabagool_studios\` as
  `gabagool_factory_package_factory-vX.Y.Z.zip`. Release notes live in
  `docs/releases/factory-vX.Y.Z.md`.
- The push and `gh release create` were BLOCKED by the session's auto-mode
  classifier ("Out-of-Place Publication") the first time; the walker ran
  the three commands by hand (1.36.0 is on GitHub, 2026-10-10) and then
  chose a PROJECT-SCOPED allow list for the package push job:
  `.claude/settings.local.json` (gitignored) allows `git push origin main`,
  `gh release create/upload factory-v*` and `gh release view`. Nothing
  wider: no tool-repo pushes, no other remotes.

- 1.39.0 (2026-10-12) went through from the session with no block: tool
  tags pushed per repo (`git -C <tool> push origin refs/tags/vX`), root
  main + `factory-v1.39.0`, then `gh release create factory-v1.39.0 <zip>
  -R siliconight/gabagool_factory --title "Gabagool Factory 1.39.0"
  --notes-file docs/releases/factory-v1.39.0.md`; GitHub's asset digest
  matched the local sha256. Order as 1.38.0: tagged commit = promotion +
  roadmap; the notes commit ("release X prepared") AFTER the zip, because
  docs/releases TRAVELS in the package. Prove the release zip is the tested
  one: zipfile CRCs against the install test's zip (1.39.0: 4,797 of 4,800
  same, the other 3 the manifest/changelog/roadmap).
- 1.40.0 (2026-10-14) went the same way with no block (4,975 of 4,978
  same; digest matched). `verify-manifest` runs FROM THE FACTORY ROOT:
  `python -m level_factory verify-manifest --factory <root> --strict`
  (from inside level_factory/ it is "No module named level_factory").
  Afterwards `python tools/factory_retire.py` (dry run, then `--apply`)
  takes the previous release's zip, the tested zip and the older install
  test's unpack -- the walker's standing "package clean job" rule.

**Why:** the handoff (roadmap 202) now goes through GitHub: the repo for the
record, Releases for the thing a stranger downloads.

**How to apply:** build at tags, write the notes, then push main + the
`factory-v*` tags and create the release with the zip attached; never
publish a package built from HEADs ahead of the certified set.

Related: [[collaborator-handoff-around-2026-10-21]], [[no-attribution-covers-my-own-commits]].
