r"""Re-pin the lockstep set on the surface-dressing chain and the A/B.

    python patch_manifest_130_dressing.py --check
    python patch_manifest_130_dressing.py
    python patch_manifest_130_dressing.py --selftest
    python patch_manifest_130_dressing.py --revert

Run from the FACTORY ROOT.

## What moves

    factory_version   1.29.0 -> 1.30.0
    level_factory     0.42.0 -> 0.46.0     915 passed, 11 skipped
    lot               0.44.0 -> 0.47.0     377 passed
    patina            0.19.0 -> 0.21.0     326 passed, 1 skipped
    zoo               0.36.0 -> 0.38.0     294 passed, 2 skipped

and the description gains a 2026-08-19 certification, with the 2026-08-18 one
relabelled PRIOR in the pattern this file already uses.

## The tag question, and the first answer being wrong

Version 1 of this script asked `git tag --list` at the FACTORY root. That
repository's 21 tags are all `factory-v1.x` -- it tags the factory_version, not
the tools. Finding none of `v0.42.0 / v0.44.0 / v0.19.0 / v0.36.0` there, it
concluded the tag field was a naming convention rather than a record, said so
in a confident paragraph, wrote that paragraph into the certified description
as a FINDING, and pinned four tags that do not exist.

EVERY TOOL IS ITS OWN GIT REPOSITORY nested in the factory tree. All four of
those tags were real. The manifest was reverted byte-exact from its sidecar.

So this version asks each tool's own repo, and:

  * every tag present  -> proceed, printing each repo's tag count and its
                          numerically-newest tag.
  * any tag missing    -> REFUSE, and print the `git -C <tool> tag -a` command
                          for each one.
  * any repo unaskable -> REFUSE. An unasked question is not a yes.

There is no override flag. The previous version had one for the unaskable
case; a flag that lets the manifest claim an untagged release is the defect
with a switch on it.

The lesson is not that the check was wrong -- checks are wrong sometimes. It
is that a check pointed at the wrong source does not fail quietly. It returns
a finding, in the same tone as a true one, and findings get written down.

## What the description records as NOT verified

The dressing has never been loaded as part of a real site, nobody has looked at
it in a windowed level, `mesh_paths` remains untested end to end, and `certify`
reported dispatch 0.3.0 against a manifest pinning 0.3.1 -- recorded, not
reconciled. A lockstep record is only worth the gaps it admits to.

The manifest is never written unless the result parses as JSON and the pins
read back as intended. A truncated manifest is the failure mode that costs the
most to notice later.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

SIDECAR = ".pre_130dressing"
TARGET = "factory.manifest.json"

PRE_SHA = "b94ec9b7309f69cac8c232f661630980400e3a4f3b4a2685e531d05879777154"
POST_SHA = "4eae37b0bc7725a125d05a91a4836fe89d59b979d440a5912771667af2fd0a77"
PRE_BYTES = 16788
POST_BYTES = 22293

OLD_TAGS = {"level_factory": "v0.42.0", "lot": "v0.44.0",
            "patina": "v0.19.0", "zoo": "v0.36.0"}
NEW_TAGS = {"level_factory": "v0.46.0", "lot": "v0.47.0",
            "patina": "v0.21.0", "zoo": "v0.38.0"}

EXPECTED = {"level_factory": "0.46.0", "lot": "0.47.0",
            "patina": "0.21.0", "zoo": "0.38.0"}

DESC_OLD = ("The certified lockstep set: these tool versions were verified "
            "TOGETHER. Re-certified 2026-08-18,")

DESC_NEW = """The certified lockstep set: these tool versions were verified TOGETHER. Re-certified 2026-08-19, on the Layer 3 surface-dressing chain and the first Godot A/B this repo has run. WHAT WAS RUN: the whole chain end to end on coldrun_pawn_job -- `shape_metrics` over zoo/_preview_dressing, `lot/site_surfaces.py` on the coldrun_pawn_job spec (FOOTPRINTS_MERGED: read footprints for 4 of 4 buildings), `patina.surface_dressing --audit`, and `packages.exporting.dressing_scene` in both modes. 4,374 instances of 4 meshes over 22,180.76 m2 (0.1972 per m2), 568,220 triangles, 176 placements refused. As MultiMeshes that is 4 draw calls; as nodes it is 4,374, which is the load hitch this layer was told not to cause. THE BUFFER LAYOUT IS NOW MEASURED RATHER THAN ASSUMED, AND IT WAS WRONG. `tools/dressing_ab.ps1` loads the multimesh scene and the node scene in a real windowed Godot (4.7.stable, Vulkan, RTX 2060) and compares MultiMesh.get_instance_transform(i) against the node Transform3D. First run: 4372 of 4374 instances disagreed, and the 2 that agreed were at zero yaw. `multimesh_floats()` had been reading godot_transform's three tuples as basis COLUMNS; they are ROWS, which lot.py:_godot_transform says in its own comment. For a pure yaw a transpose is the inverse rotation, so every dressed object faced the mirrored way in a scatter layer where no one direction is expected -- it loaded, it rendered, and it looked like gravel. level_factory 0.46.0 fixes it, and the A/B now reports AB OK at worst deviation 0.00000000 across all 4,374 instances. The nodes path was correct throughout, being Lot's own ordering. FOUR TESTS COVERED THE BROKEN FUNCTION AND NONE COULD SEE IT, which is the more useful finding. Three used a yaw of zero, where the identity basis is symmetric and a transpose changes nothing. The fourth used a real yaw and compared sorted(floats) against sorted(literal), because it believed the two forms used different orderings -- and a transpose is a permutation, which no multiset comparison can ever detect. Measured rather than argued: the original 23-test file passes all green against the transposed module AND against the fixed one. The replacements are stated at yaws whose sine is not zero, and the patch selftest reinstates the transpose in memory and requires them to fail. SUITES, each on its own tree: level_factory 0.46.0 915 passed 11 skipped; Lot 0.47.0 377 passed; Patina 0.21.0 326 passed 1 skipped; Zoo 0.38.0 294 passed 2 skipped; real-tool smoke 9 passed 1 skipped with LF_TOOLS_DIR set. `certify` was run against workspaces/rockay-ws. WHAT WAS NOT RUN, and is therefore NOT covered by this set: the dressing scene has never been loaded as part of a real site. The A/B built its own throwaway project with placeholder BoxMeshes, and that was deliberate -- how a .glb becomes an addressable Mesh resource is a SEPARATE unknown, and tangling it in would have given one experiment that answered neither question. `mesh_paths` is still supplied by the caller, and no value of it has been tested end to end. Nobody has looked at the dressing in a windowed level: AB OK is a statement about twelve floats, not about how anything looks. One A/B run, one plan, one machine. Also not run: the walk sweep, the pack load check, deli_counter's suite, and no mission has been re-exported since this fix. EVERY _dressing.tscn WRITTEN BY level_factory 0.45.0 IS TRANSPOSED. The one under _dress was regenerated at 0.46.0 and its first instance transform re-read off disk to confirm it matches the node scene; any other copy is wrong, and this set does not know where they are. AND A PIN THIS SET DOES NOT RECONCILE: `certify` reported dispatch 0.3.0 while this manifest pins 0.3.1. That disagreement is recorded rather than resolved -- nothing in this certification touched dispatch, so the pin is left where it stood rather than moved on a guess. THE FOUR TOOLS WERE COMMITTED AND TAGGED BEFORE THIS PIN WAS WRITTEN: level_factory v0.46.0, lot v0.47.0, patina v0.21.0, zoo v0.38.0, each in its OWN repository. That is enforced rather than asserted -- patch_manifest_130_dressing.py runs git tag --list inside each tool's own repo and refuses to write if any tag it would name is missing. THE FIRST ATTEMPT AT THIS RE-PIN GOT THAT WRONG, AND IT IS RECORDED HERE BECAUSE IT IS THE EXACT FAILURE THIS FILE EXISTS TO CATCH. The check asked the FACTORY repository, whose 21 tags are all factory-v1.x; it found none of the four it was looking for, concluded that the tag field was a naming convention rather than a record of anything, wrote that conclusion into this description as a FINDING, and pinned four tags that did not exist. Every tool is its own git repository nested in the factory tree, and all four previously-pinned tags -- v0.42.0, v0.44.0, v0.19.0, v0.36.0 -- were real and had been all along. The manifest was reverted byte-exact from its sidecar and re-pinned only once the tags existed. A check that asks the wrong source is worse than no check, because it does not return silence, it returns a finding, and a finding gets written down. ONE STATE THIS SET RECORDS RATHER THAN RESOLVES: before that commit, verify-manifest reported level_factory STALE and the other nine OK. VERSION was last committed 2026-08-18 17:20 against schemas/surface_dressing.v1.json at 18:39 (fdc363b), with packages/exporting/dressing_scene.py still UNTRACKED -- so neither the 0.45.0 dressing module nor the 0.46.0 fix to it had ever been in a commit. Whether that STALE clears is a question for the next verify-manifest, not a claim made here. PRIOR CERTIFICATION, 2026-08-18 --"""

EDITS = [
    ("factory_version 1.29.0 -> 1.30.0",
     '"factory_version": "1.29.0",', '"factory_version": "1.30.0",'),
    ("level_factory 0.42.0 -> 0.46.0",
     '"version": "0.42.0",\n      "tag": "v0.42.0",',
     '"version": "0.46.0",\n      "tag": "v0.46.0",'),
    ("lot 0.44.0 -> 0.47.0",
     '"version": "0.44.0",\n      "tag": "v0.44.0",',
     '"version": "0.47.0",\n      "tag": "v0.47.0",'),
    ("patina 0.19.0 -> 0.21.0",
     '"version": "0.19.0",\n      "tag": "v0.19.0",',
     '"version": "0.21.0",\n      "tag": "v0.21.0",'),
    ("zoo 0.36.0 -> 0.38.0",
     '"version": "0.36.0",\n      "tag": "v0.36.0",',
     '"version": "0.38.0",\n      "tag": "v0.38.0",'),
    ("description: 2026-08-19 certification prepended", DESC_OLD, DESC_NEW),
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _transform(text: str) -> str:
    """The six edits, each required to match exactly once."""
    out = text
    for label, old, new in EDITS:
        n = out.count(old)
        if n != 1:
            raise ValueError(f"expected 1 occurrence, found {n}: {label}")
        out = out.replace(old, new, 1)
    return out


def _validate(text: str) -> dict:
    """Parse and check the pins. Raises rather than returning a bad manifest."""
    doc = json.loads(text)
    if doc["factory_version"] != "1.30.0":
        raise ValueError(f"factory_version is {doc['factory_version']}")
    for tool, want in EXPECTED.items():
        got = doc["tools"][tool]
        if (got["version"], got["tag"]) != (want, "v" + want):
            raise ValueError(f"{tool} reads {got['version']} / {got['tag']}")
    if doc["tools"]["dispatch"]["version"] != "0.3.1":
        raise ValueError("dispatch pin moved; this patch does not touch it")
    d = doc["description"]
    if not d.startswith("The certified lockstep set"):
        raise ValueError("description lost its opening")
    for marker in ("Re-certified 2026-08-19,",
                   "PRIOR CERTIFICATION, 2026-08-18 --",
                   "PRIOR CERTIFICATION, 2026-08-16",
                   "PRIOR CERTIFICATION, 2026-07-28"):
        if marker not in d:
            raise ValueError(f"description lost {marker!r}")
    return doc


# --- the tag question, asked of the right repository this time --------------

def _tool_dirs(root: Path) -> dict:
    """tool -> its own directory, honouring the manifest's `path` override.

    EVERY TOOL IS ITS OWN GIT REPOSITORY nested inside the factory tree. The
    first version of this file did not know that. It ran `git tag --list` at
    the FACTORY root, whose tags are all `factory-v1.x`, found none of the
    four it was looking for, and concluded the tag field was decorative. All
    four were real, in repositories it never opened. Hence this function: so
    the question is asked where the answer lives.
    """
    doc = json.loads((root / TARGET).read_text(encoding="utf-8"))
    tools = doc.get("tools", {})
    return {t: root / str(tools.get(t, {}).get("path", t)) for t in NEW_TAGS}


def _tags_in(repo: Path):
    """Every tag in ONE repo, or None if that repo cannot be asked."""
    if not (repo / ".git").exists() or shutil.which("git") is None:
        return None
    try:
        r = subprocess.run(["git", "-C", str(repo), "tag", "--list"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}


def _newest(tags) -> str:
    """The highest vX.Y.Z, compared NUMERICALLY.

    `git tag --list` sorts lexically, which puts v0.5.0 after v0.43.0 -- which
    is exactly how a human skimming that output misjudges where a repo is.
    """
    best, best_key = None, ()
    for t in tags:
        if not t.startswith("v"):
            continue
        parts = t[1:].split(".")
        if not all(p.isdigit() for p in parts):
            continue
        key = tuple(int(p) for p in parts)
        if key > best_key:
            best, best_key = t, key
    return best or "(none)"


def _tag_reality(root: Path) -> int:
    """0 to proceed, 1 to refuse. There is no override, deliberately.

    The previous version had an --assume-convention flag for the case where
    git could not be asked. It is gone. A flag that lets the manifest claim an
    untagged release is this whole defect with a switch on it.
    """
    unknown, missing = [], {}
    dirs = _tool_dirs(root)
    for tool, want in sorted(NEW_TAGS.items()):
        repo = dirs[tool]
        tags = _tags_in(repo)
        if tags is None:
            unknown.append(tool)
            print(f"[tags] {tool:<14} UNREADABLE at {repo}")
            continue
        here = want in tags
        print(f"[tags] {tool:<14} {len(tags):>3} tags, newest "
              f"{_newest(tags):<10} {want} "
              f"{'present' if here else 'MISSING'}")
        if not here:
            missing[tool] = want

    if unknown:
        print("[tags] REFUSING: cannot read the repository for "
              + ", ".join(unknown) + ".")
        print("[tags] An unasked question is not a yes.")
        return 1
    if missing:
        print("[tags] REFUSING: the manifest would name tags that do not exist:")
        for tool, tag in sorted(missing.items()):
            print(f"           {tag:<10} ({tool})")
        print("[tags] Commit the work, then tag each tool IN ITS OWN REPO:")
        for tool, tag in sorted(missing.items()):
            msg = f"{tool} {tag[1:]}"
            print(f'           git -C {tool} tag -a {tag} -m "{msg}"')
        return 1
    print("[tags] all four tags exist in their own repositories.")
    return 0


# --- selftest ---------------------------------------------------------------

MINI = """{
  "schema": "gabagool.factory.manifest.v1",
  "factory_version": "1.29.0",
  "description": "@DESC_OLD@ on the first LIT package. PRIOR CERTIFICATION, 2026-08-16 -- x. PRIOR CERTIFICATION, 2026-07-28: y.",
  "tools": {
    "dispatch": {
      "version": "0.3.1",
      "tag": "v0.3.1",
      "repo": "siliconight/dispatch"
    },
    "level_factory": {
      "version": "0.42.0",
      "tag": "v0.42.0",
      "repo": "siliconight/level_factory"
    },
    "lot": {
      "version": "0.44.0",
      "tag": "v0.44.0",
      "repo": "siliconight/lot"
    },
    "patina": {
      "version": "0.19.0",
      "tag": "v0.19.0",
      "repo": "siliconight/patina"
    },
    "zoo": {
      "version": "0.36.0",
      "tag": "v0.36.0",
      "repo": "siliconight/zoo"
    }
  }
}"""


def _selftest() -> int:
    bad = 0

    # 1. the new prose cannot break the JSON it is going into.
    hostile = sorted({c for c in DESC_NEW if ord(c) > 126 or c in '"\\'})
    print(f"[selftest] non-ASCII or JSON-hostile characters in the new "
          f"description: {hostile or 'none'}")
    bad |= 1 if hostile else 0

    # 2. the edits apply to a miniature manifest and it still parses.
    mini = MINI.replace("@DESC_OLD@", DESC_OLD)
    try:
        doc = _validate(_transform(mini))
        print("[selftest] edits apply to a miniature manifest and it parses; "
              f"description {len(doc['description']):,} chars")
    except (ValueError, KeyError) as exc:
        print(f"[selftest] FAIL: {exc}")
        bad = 1

    # 3. FALSIFICATION -- drop one edit and _validate must catch it.
    leaked = False
    for label, old, new in EDITS:
        partial = mini
        for l2, o2, n2 in EDITS:
            if l2 != label:
                partial = partial.replace(o2, n2, 1)
        try:
            _validate(partial)
        except (ValueError, KeyError):
            continue
        print(f"[selftest] FAIL: skipping {label!r} produced a manifest that "
              f"_validate accepted. It is not checking that edit.")
        bad = 1
        leaked = True
    if not leaked:
        print("[selftest] falsified: omitting any one of the six edits is "
              "caught by _validate")

    # 4. refusing to write unparseable JSON is the point, so prove it refuses.
    try:
        _validate(mini.replace('"tools": {', '"tools": {{', 1))
        print("[selftest] FAIL: broken JSON was accepted")
        bad = 1
    except (ValueError, KeyError, json.JSONDecodeError):
        print("[selftest] broken JSON is refused rather than written")

    # 5. every anchor is unique WITHIN the replacement it makes.
    for label, old, new in EDITS:
        if old in new and label.startswith("description"):
            continue
        if new.count(old) and not label.startswith("description"):
            print(f"[selftest] FAIL: {label} is not idempotent-safe")
            bad = 1

    print("[selftest] " + ("PASS" if not bad else "FAILED"))
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="say what would change, write nothing")
    ap.add_argument("--revert", action="store_true",
                    help="restore the manifest from its sidecar")
    ap.add_argument("--selftest", action="store_true",
                    help="check the edits and falsify them; needs no repo")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    root = Path.cwd()
    path = root / TARGET
    if not path.is_file():
        print(f"cannot find {TARGET} -- run this from the factory root")
        return 1
    side = path.with_suffix(path.suffix + SIDECAR)

    if args.revert:
        if not side.is_file():
            print(f"  no sidecar at {side.name}")
            return 1
        path.write_bytes(side.read_bytes())
        print(f"  reverted     {TARGET}")
        return 0

    raw = path.read_bytes()
    got = _sha(raw)
    if got == POST_SHA:
        print(f"  already applied  {TARGET}")
        return 0
    if got != PRE_SHA:
        print(f"REFUSING: {TARGET} is not the file this patch was built "
              f"against.\n    expected sha {PRE_SHA[:12]}  ({PRE_BYTES:,} "
              f"bytes)\n    found    sha {got[:12]}  ({len(raw):,} bytes)")
        return 1

    if _tag_reality(root):
        return 1

    try:
        out = _transform(raw.decode("utf-8"))
        _validate(out)
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"REFUSING: {exc}")
        return 1
    data = out.encode("utf-8")
    if _sha(data) != POST_SHA:
        print(f"REFUSING: the result is not the reviewed post-image\n"
              f"    expected {POST_SHA[:12]}  found {_sha(data)[:12]}")
        return 1

    if args.check:
        print(f"  would patch  {TARGET}  {len(raw):,} -> {len(data):,} "
              f"({len(data) - len(raw):+,})")
        for label, _o, _n in EDITS:
            print(f"                 {label}")
        return 0

    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {TARGET}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha {_sha(data)[:12]}")
    print()
    print("  Verify:  python patch_manifest_130_dressing.py --selftest")
    print("           cd level_factory; python -m apps.cli.main verify-manifest --factory ..")
    print()
    print("  The four DRIFTs this closes were deliberate. Anything still")
    print("  reported after this is new information.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
