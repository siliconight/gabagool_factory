r"""factory 1.19.0's entry, corrected with the measurement, BEFORE commit.

    python patch_manifest_119b.py --check
    python patch_manifest_119b.py
    python patch_manifest_119b.py --selftest
    python patch_manifest_119b.py --revert

Run from the FACTORY ROOT, AFTER patch_manifest_119.py and BEFORE the
factory-v1.19.0 commit. It does not touch factory.manifest.json -- the pin is
already right. It edits the CHANGELOG entry, and the one assertion in
patch_manifest_119.py that pinned the un-measured state.

WHY

1.19.0's entry says the regression gate "has NOT been measured". It was
measured immediately afterwards, by `tools/probe_selection_drift.py`, and
leaving a certified set's record saying otherwise would be the exact failure
this repo keeps finding: an answer that existed somewhere the record did not
read.

WHAT THE PROBE FOUND

    the gate passes today                    True
    the site file changes the signatures     False
    the lock itself was computed w/o site    True

The middle line is the finding, and it is not the marker bug. That compares
the REAL `site.site.gameplay.json` against NO site file at all -- all three
protected hashes identical. Repairing the marker would not have changed a
single one of them.

THE CAUSE, WHICH IS A VOCABULARY MISMATCH

`_merged_gameplay` reads eleven keys. `site.site.gameplay.json` publishes
twenty top-level keys and NONE of the eleven:

    buildings, collision, cover_plan, encounters, enterability, ground,
    ground_extent, loot, markers, objectives, openings, pacing, rooms, site,
    site_markers, surface_roles, surfaces, tactical, vertical_links, zones

Lot and Deli publish different vocabularies for the same concepts, and the
extraction was written in Deli's. Four of the eleven -- stair_systems,
ladders, platforms, fire_escapes -- get backfilled from the Deli side by
`setdefault`, which is what has been hiding this: the signature is never
empty, so it never looked broken.

IT IS WORSE THAN "THE SITE IS NOT GUARDED"

`anchors` is absent from BOTH files. So `_anchor_registry` hashes an empty
list, and `anchor_registry_hash` -- "gameplay-anchor registry changed after
art pass" -- has been protecting nothing on either side. `route`,
`route_graph` and `nav_hints` are absent from both, so `route_graph_hash` is
the hash of two empty dicts. `collision_hulls` and `doorways` are absent from
both.

Which leaves the entire functional lock protecting exactly one thing: Deli's
`stair_systems`, a list of 2. Three signatures, one of which has real content
and five-sixths of that one is empty lists.

WHAT THIS DOES AND DOES NOT INVALIDATE

It does NOT touch the grades. Those come from the walk and scoring stages,
not from here.

It DOES mean every "no functional drift after the art pass" result this
factory has recorded was a weaker claim than it read as -- including the one
in factory-v1.16.0's evidence. The manifest description is still not
rewritten, for the reason 1.17.0 gave, but a reader of that description
should know what the phrase covered.

NOT FIXED HERE, AND NOT BY A PATCH LIKE THIS ONE

Mapping Lot's vocabulary onto the protected signatures is a contract question
between two tools -- whether `collision` means `collision_hulls`, whether
`openings` means `doorways`, whether `vertical_links` covers ladders and
stairs, whether `markers`/`site_markers` are the anchors. Those look like
obvious pairs and I have not opened one of them to check its shape. Guessing
a mapping and writing it into a gate would produce a lock that hashes real
data and still protects the wrong thing, which is harder to notice than a
lock that hashes nothing.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CHANGELOG = "CHANGELOG.md"
P119 = "patches/patch_manifest_119.py"
SIDECAR = ".pre_119b"

OLD = (
    "The same function\n"
    "feeds the post-art functional-regression check a `site.site.gameplay.json`\n"
    "that is not there. Whether that gate still compares anything real has NOT\n"
    "been measured; `tools/probe_selection_drift.py` measures it without changing\n"
    "anything. ")

NEW = (
    "The same function\n"
    "feeds the post-art functional-regression check a `site.site.gameplay.json`\n"
    "that is not there.\n"
    "\n"
    "AND THAT GATE HAS NOW BEEN MEASURED, WHICH FOUND SOMETHING LARGER\n"
    "\n"
    "`tools/probe_selection_drift.py` compares the lock's three protected\n"
    "signatures computed three ways: as the gate resolves them today, from the\n"
    "REAL site file, and from no site file at all. All three ways agree, on all\n"
    "three signatures. The site file changes nothing. Repairing the marker\n"
    "would not have changed a single hash.\n"
    "\n"
    "The cause is a vocabulary mismatch, not a path. `_merged_gameplay` reads\n"
    "eleven keys; `site.site.gameplay.json` publishes twenty top-level keys and\n"
    "none of the eleven -- buildings, collision, cover_plan, encounters,\n"
    "enterability, ground, ground_extent, loot, markers, objectives, openings,\n"
    "pacing, rooms, site, site_markers, surface_roles, surfaces, tactical,\n"
    "vertical_links, zones. Lot and Deli name the same concepts differently and\n"
    "the extraction is written in Deli's vocabulary. Four of the eleven get\n"
    "backfilled from Deli by `setdefault`, which is what hid this: the\n"
    "signature is never empty, so it never looked broken.\n"
    "\n"
    "It is worse than the site being unguarded. `anchors` is absent from BOTH\n"
    "files, so `anchor_registry_hash` -- the one whose drift message reads\n"
    "\"gameplay-anchor registry changed after art pass\" -- has been hashing an\n"
    "empty list. `route`, `route_graph` and `nav_hints` are absent from both,\n"
    "so `route_graph_hash` is the hash of two empty dicts. `collision_hulls`\n"
    "and `doorways` are absent from both. What remains protected is Deli's\n"
    "`stair_systems`, a list of 2.\n"
    "\n"
    "This does not touch the grades, which come from the walk and scoring\n"
    "stages. It does mean every \"no functional drift after the art pass\"\n"
    "result this factory has recorded -- including the one inside\n"
    "factory-v1.16.0's evidence -- was a weaker claim than it read as. The\n"
    "description is still not rewritten, for the reason 1.17.0 gave; a reader\n"
    "of it should know what that phrase covered.\n"
    "\n"
    "Mapping Lot's vocabulary onto the signatures is a contract question\n"
    "between two tools, and the obvious-looking pairs (`collision` ->\n"
    "`collision_hulls`, `openings` -> `doorways`, `vertical_links` -> ladders\n"
    "and stairs, `markers`/`site_markers` -> anchors) have not been opened and\n"
    "checked. A guessed mapping would give a lock that hashes real data and\n"
    "still protects the wrong thing, which is harder to notice than one that\n"
    "hashes nothing. Not attempted here.\n"
    "\n")

P119_OLD = ('    check("it names the marker defect and refuses to call the gate measured",\n'
            '          "seed_XXXX" in cl and "has NOT\\nbeen measured" in cl)\n')
P119_NEW = ('    check("it names the marker defect and carries the measurement",\n'
            '          "seed_XXXX" in cl and "HAS NOW BEEN MEASURED" in cl\n'
            '          and "The site file changes nothing" in cl)\n')

EDITS: list[tuple[str, str, str]] = [
    (CHANGELOG, OLD, NEW),
    # The pair stays coherent. 119's check pinned "not measured", which was
    # true when it was written and is false now; a selftest that fails
    # because the world improved is the failure mode this repo has hit
    # before. Neither file is committed yet, so this is one edit, not a
    # rewrite of history.
    (P119, P119_OLD, P119_NEW),
]

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    if "## [factory-v1.19.0]" not in cl:
        print("REFUSING: no factory-v1.19.0 entry here -- run "
              "patch_manifest_119.py first")
        return 1

    for rel, old, new in EDITS:
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        raw = p.read_bytes()
        body = raw.decode("utf-8")
        if body.count(_CRLF):
            print(f"REFUSING: {rel} has CRLF line endings; these anchors are LF")
            return 1
        if new in body:
            print(f"  already applied  {rel}")
            continue
        if body.count(old) != 1:
            print(f"REFUSING: {rel} -- the anchor occurs {body.count(old)} "
                  f"time(s), expected 1")
            return 1
        out = body.replace(old, new, 1)
        if rel.endswith(".py"):
            try:
                compile(out, str(p), "exec")
            except SyntaxError as exc:
                print(f"REFUSING: {rel} -- does not parse after the edit: {exc}")
                return 1
        data = out.encode("utf-8")
        if check:
            print(f"  would patch  {rel}  {len(raw):,} -> {len(data):,} bytes "
                  f"({len(data) - len(raw):+,})")
            continue
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        p.write_bytes(data)
        print(f"  patched      {rel}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import json
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check("the entry no longer says the gate is unmeasured",
          "has NOT\nbeen measured" not in cl)
    check("it carries the measurement",
          "HAS NOW BEEN MEASURED" in cl
          and "The site file changes nothing" in cl)
    check("it names the cause, not just the symptom",
          "vocabulary mismatch" in cl and "vertical_links" in cl)
    check("it says which key hashes an empty list",
          "anchor_registry_hash" in cl and "hashing an\nempty list" in cl)
    check("it names what is actually still protected",
          "`stair_systems`, a list of 2" in cl)
    check("it separates this from the grades",
          "does not touch the grades" in cl)
    check("and says 1.16.0's evidence read stronger than it was",
          "factory-v1.16.0's evidence" in cl
          and "weaker claim than it read as" in cl)
    check("it refuses to guess the mapping",
          "guessed mapping" in cl and "Not attempted here" in cl)
    check("1.19.0 is still one entry and was not renumbered",
          cl.count("## [factory-v1.19.0]") == 1
          and "## [factory-v1.20.0]" not in cl)

    p119 = (root / P119).read_text(encoding="utf-8")
    check("patch_manifest_119's own check follows the entry",
          "HAS NOW BEEN MEASURED" in p119
          and 'has NOT\\nbeen measured' not in p119)

    # The claims about the probe are checked against the probe, not asserted.
    probe = (root / "tools" / "probe_selection_drift.py")
    check("the probe this entry cites exists", probe.is_file())
    if probe.is_file():
        src = probe.read_text(encoding="utf-8")
        check("and really does compare with-site against without-site",
              "without_site = signatures(" in src
              and "site_matters = with_site != without_site" in src)

    # And the manifest is untouched by this patch.
    m = json.loads((root / "factory.manifest.json").read_text(encoding="utf-8"))
    check("the pin is still 1.19.0 / level_factory 0.27.0",
          m.get("factory_version") == "1.19.0"
          and m["tools"]["level_factory"]["version"] == "0.27.0")

    print()
    print("  the record now says what was measured, and what was not"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel in (CHANGELOG, P119):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        return bad

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_manifest_119b.py --selftest")
        print("    python patches\\patch_manifest_119.py --selftest")
        print()
        print('    git commit -am "factory 1.19.0 -- stage 1 closed, and the '
              'functional lock measured"')
        print('    git tag -a factory-v1.19.0 -m "factory 1.19.0"')
        print("    git push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
