#!/usr/bin/env python3
"""patch_manifest_133.py -- pin pixelcoat 0.16.0 and zoo 0.47.0.

  --check / (apply) / --revert / --selftest

The selftest deliberately does MORE than verify-manifest: it resolves every
tool's `tag` field against a real git tag in that tool's repo. verify-manifest
never reads the `tag` field at all, which is how laser_tag came to pin a v0.8.0
that does not exist and stay unnoticed. Any pin whose tag is missing must be
named in the description or the selftest fails.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MP = os.path.join(ROOT, "factory.manifest.json")
SIDE = ".pre_manifest133"

OLD_FV, NEW_FV = "1.32.0", "1.33.0"
BUMPS = {
    "pixelcoat": ("0.15.0", "0.16.0"),
    "zoo": ("0.46.0", "0.47.0"),
}

NOTES = {
    "pixelcoat": (
        "0.16.0 gave five kinds a grammar for the first time (laminate, paper, "
        "carbon, tar, vegetation), retagged pebble_gravel from kind dirt to "
        "gravel on the evidence of its own aggregate block, and listed ten "
        "previously unmapped kinds in all nine theme profiles. The theme profile "
        "is the gate: a kind is built only if a theme names a profile for it, "
        "which is why canvas, dirt, leather and rubber had _delco profiles and "
        "zero packs. Libraries went 68 packs to 118, MISMATCHES=0. All five new "
        "grammars use only fbm and worley_f1, the two generators with worked "
        "examples on disk; weave and directional_grain exist and were not used "
        "because their parameters were not verified. paper and carbon were "
        "authored below the texel-density floor and an existing regression test "
        "caught it -- pixelcoat holds max/min of 512/meters_per_tile to 3.0, and "
        "they had taken it to 6.0. They were clamped into the band the other 55 "
        "profiles occupy rather than the invariant being widened."
    ),
    "zoo": (
        "0.47.0 adds tests/test_recipe_reads_its_genome.py: a recipe that calls "
        "make_material but never reads a material key cannot respond to its "
        "genome, which is what made flat_top_grill's genome inert and silent. "
        "Measured across 53 recipes and 79 calls, exactly one is in that state "
        "(cheesesteak, a composite food prop with no single body surface); it is "
        "exempt with a written reason and the test also fails if an exempt "
        "recipe starts reading its genome, so the exemption cannot rot. Every "
        "inert genome offers a single option, so nothing renders wrong today -- "
        "the exposure is that a second option would be ignored in silence. All "
        "ten new pixelcoat kinds resolve through skins.find_pack in all five "
        "built themes, tintable true for laminate and paper only."
    ),
}

NEW_DESC = (
    "1.33.0 pins pixelcoat 0.16.0 and zoo 0.47.0, on closing the ten material "
    "kinds that no theme mapped. WHAT THIS SET DOES NOT CERTIFY, SAID FIRST: "
    "there is still no end-to-end chain, the art-unlit export is still blocked "
    "on collision_fingerprint, laser_tag still pins v0.8.0 which is a tag that "
    "does not exist, and nobody has looked at the five new grammars rendered in "
    "an engine. They build, they resolve, and that is the whole claim. The "
    "evidence here is pixelcoat 215 passed, zoo 548 passed / 11 skipped, 118 "
    "packs every one stamped tool_version 0.16.0, MISMATCHES=0 across five "
    "libraries, and skins.find_pack returning a pack for all ten kinds in all "
    "five themes. TWO CORRECTIONS ARE RECORDED HERE RATHER THAN BURIED. First: "
    "an earlier pass in this session flagged seven recipe literals as shadowing "
    "their genome and proposed replacing them; six were false positives, because "
    "the body already passed plan[\"material\"] and the literal sat on a sub-part "
    "with its own fixed colour -- a bottle cap, a safe's trim, the paper boat "
    "under the fries. Making that change would have tinted the boat with the fry "
    "colour. The weak discriminator was \"literal names a kind this genome also "
    "names\"; the correct one is whether the module consults its genome at all. "
    "Second: the zoo 0.45.0 entry claims that with ensure_ascii=False all 53 "
    "genomes round-trip. It is 49 of 53 -- litter_scrap, pebble, rubble_frag and "
    "weed_tuft do not -- and that is corrected in the zoo 0.47.0 entry rather "
    "than by rewriting the published one."
)

MODE = "apply"
for a in sys.argv[1:]:
    if a in ("--check", "--revert", "--selftest"):
        MODE = a[2:]
    else:
        print("unknown argument %r" % a)
        sys.exit(2)


def read():
    with open(MP, "rb") as fh:
        raw = fh.read()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    return raw, raw.decode("utf-8").replace("\r\n", "\n"), eol


def detect(text, data):
    for indent in (2, 4, 1):
        for ea in (False, True):
            body = json.dumps(data, indent=indent, ensure_ascii=ea)
            for suf in ("\n", ""):
                if body + suf == text:
                    return (indent, ea, suf)
    return None


def git_tag_exists(repo_dir, tag):
    if not os.path.isdir(os.path.join(repo_dir, ".git")):
        return None
    r = subprocess.run(["git", "-C", repo_dir, "rev-parse", "-q", "--verify",
                        "refs/tags/" + tag],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0


if MODE == "revert":
    s = MP + SIDE
    if os.path.isfile(s):
        shutil.copyfile(s, MP)
        os.remove(s)
        print("REVERTED %s" % os.path.basename(MP))
    else:
        print("no sidecar %s" % s)
    sys.exit(0)

raw, text, eol = read()
m = json.loads(text)
tools = m.get("tools") or {}

if MODE == "selftest":
    fails = []
    if m.get("factory_version") != NEW_FV:
        fails.append("factory_version is %r, expected %r"
                     % (m.get("factory_version"), NEW_FV))
    desc = m.get("description") or ""
    print("%-16s %-10s %-10s %-8s %s" % ("tool", "pinned", "tag", "tag?", "VERSION file"))
    print("-" * 74)
    for name in sorted(tools):
        e = tools[name]
        ver, tag = e.get("version"), e.get("tag")
        d = os.path.join(ROOT, name)
        ok = git_tag_exists(d, tag) if tag else None
        vf = os.path.join(d, "VERSION")
        installed = ""
        if os.path.isfile(vf):
            with open(vf, "r", encoding="utf-8") as fh:
                installed = fh.read().strip()
        state = "ok" if ok else ("MISSING" if ok is False else "no repo")
        print("%-16s %-10s %-10s %-8s %s" % (name, ver, tag, state, installed))
        if ok is False and name not in desc:
            fails.append("%s pins %s which does not exist and is NOT named in "
                         "the description" % (name, tag))
        if installed and ver and ver not in installed:
            fails.append("%s pins %s but its VERSION file says %r"
                         % (name, ver, installed))
    for name, (_, new) in BUMPS.items():
        if tools.get(name, {}).get("version") != new:
            fails.append("%s not pinned at %s" % (name, new))
    if "DOES NOT CERTIFY" not in desc:
        fails.append("the not-certified language is gone from the description")

    if fails:
        print("")
        print("SELFTEST FAILED")
        for f in fails:
            print("      %s" % f)
        sys.exit(1)

    # falsification: the tag check must FAIL on a pin that cannot resolve
    probe = git_tag_exists(os.path.join(ROOT, "zoo"), "v99.99.99")
    if probe is not False:
        print("")
        print("SELFTEST FAILED -- the tag resolver returned %r for a tag that"
              % probe)
        print("                   cannot exist, so its 'ok' results mean nothing")
        sys.exit(1)

    print("")
    print("SELFTEST OK -- factory %s, every pin's tag resolved against its own" % NEW_FV)
    print("               repo (not just the VERSION file, which is the check")
    print("               verify-manifest does not do), every unresolvable pin is")
    print("               named in the description, and the resolver was shown to")
    print("               return False for a tag that cannot exist")
    sys.exit(0)

problems = []
if m.get("factory_version") != OLD_FV:
    if m.get("factory_version") == NEW_FV:
        print("NOTHING TO DO -- already at %s" % NEW_FV)
        sys.exit(0)
    problems.append("factory_version is %r, expected %r"
                    % (m.get("factory_version"), OLD_FV))
for name, (old, new) in BUMPS.items():
    e = tools.get(name)
    if e is None:
        problems.append("no tools entry for %r" % name)
        continue
    if e.get("version") != old:
        problems.append("%s pins %r, expected %r" % (name, e.get("version"), old))
    if e.get("tag") != "v" + old:
        problems.append("%s tag is %r, expected %r" % (name, e.get("tag"), "v" + old))
    d = os.path.join(ROOT, name)
    if git_tag_exists(d, "v" + new) is not True:
        problems.append("%s: tag v%s does not exist in %s -- commit and tag first"
                        % (name, new, name))

fmt = detect(text, m)
if fmt is None:
    problems.append("factory.manifest.json does not round-trip in any known "
                    "format -- refusing to reformat it")

print("PRE-FLIGHT")
for name, (old, new) in sorted(BUMPS.items()):
    print("  %-12s %s -> %s   (tag v%s -> v%s)" % (name, old, new, old, new))
print("  factory_version %s -> %s" % (OLD_FV, NEW_FV))
print("  description %d chars -> %d chars (new entry prepended)"
      % (len(m.get("description") or ""),
         len(NEW_DESC) + 2 + len(m.get("description") or "")))
if problems:
    print("")
    print("REFUSING -- %d precondition(s) failed, nothing written:" % len(problems))
    for p in problems:
        print("      %s" % p)
    sys.exit(1)
if MODE == "check":
    print("")
    print("CHECK OK -- run without --check to apply")
    sys.exit(0)

new_m = dict(m)
new_m["factory_version"] = NEW_FV
new_tools = dict(tools)
for name, (old, new) in BUMPS.items():
    e = dict(new_tools[name])
    e["version"] = new
    e["tag"] = "v" + new
    e["note"] = NOTES[name]
    new_tools[name] = e
new_m["tools"] = new_tools
new_m["description"] = NEW_DESC + "\n\n" + (m.get("description") or "")

indent, ea, suf = fmt
body = json.dumps(new_m, indent=indent, ensure_ascii=ea) + suf
if not os.path.exists(MP + SIDE):
    with open(MP + SIDE, "wb") as fh:
        fh.write(raw)
with open(MP, "wb") as fh:
    fh.write(body.replace("\n", eol).encode("utf-8"))
print("")
print("APPLIED -- factory.manifest.json now %s (%d bytes). Run --selftest."
      % (NEW_FV, len(body)))
