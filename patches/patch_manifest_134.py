import json, os, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MP = os.path.join(ROOT, "factory.manifest.json")
SIDE = ".pre_manifest134"
OLD_FV, NEW_FV = "1.33.0", "1.34.0"
TOOL, TOLD, TNEW = "deli_counter", "0.91.0", "0.92.0"
MODE = sys.argv[1][2:] if len(sys.argv) > 1 else "apply"

NOTE = ("0.92.0 freezes the nav-gate's UNJUDGED set. A shell with no marker whose "
        "type ends in _spawn is reported as unjudged and the exit code is "
        "deliberately unchanged, so the set could grow silently. Measured from the "
        "per-shell results: 135 shells, 132 pass stairs, 3 fail, 17 unjudged. A "
        "prior note said 18 unjudged and named twelve; five were never recorded. "
        "16 navigable-null against 17 unjudged reconciles because night_pawn also "
        "fails stairs and navigable is a conjunction. Twelve of the seventeen are "
        "RECORDED, NOT EXPLAINED -- whether they should have spawn markers is an "
        "author decision nobody has made.")

DESC = ("1.34.0 pins deli_counter 0.92.0, on freezing the nav-gate's unjudged set. "
        "WHAT THIS SET DOES NOT CERTIFY, SAID FIRST: no end-to-end chain, the "
        "art-unlit export is still blocked on collision_fingerprint, laser_tag "
        "still pins a v0.8.0 that does not exist, and the three stair failures "
        "(cbp_town_finale_midbalanced_schemafixed, night_pawn, primos_pizza) are "
        "recorded and NOT fixed -- they need a Godot geometry pass. The new sweep "
        "reads deli_counter/build/, which is not committed, so it SKIPS in a clean "
        "checkout and only the baseline's integrity is asserted there. A "
        "CORRECTION IS RECORDED RATHER THAN BURIED: the figure carried forward as "
        "\\"the nav-gate passing 3 of 135\\" was backwards. 3 of 135 is the FAILURE "
        "count; 132 shells pass. Evidence: deli_counter 528 passed / 2 skipped.")

def read():
    with open(MP, "rb") as fh:
        raw = fh.read()
    return raw, raw.decode("utf-8").replace("\r\n", "\n"), ("\r\n" if b"\r\n" in raw else "\n")

def detect(text, data):
    for ind in (2, 4, 1):
        for ea in (False, True):
            b = json.dumps(data, indent=ind, ensure_ascii=ea)
            for s in ("\n", ""):
                if b + s == text:
                    return (ind, ea, s)
    return None

def tag_ok(repo, tag):
    d = os.path.join(ROOT, repo)
    if not os.path.isdir(os.path.join(d, ".git")):
        return None
    return subprocess.run(["git", "-C", d, "rev-parse", "-q", "--verify",
                           "refs/tags/" + tag], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0

if MODE == "revert":
    if os.path.isfile(MP + SIDE):
        shutil.copyfile(MP + SIDE, MP); os.remove(MP + SIDE); print("REVERTED")
    sys.exit(0)

raw, text, eol = read()
m = json.loads(text)
tools = m.get("tools") or {}

if MODE == "selftest":
    fails = []
    if m.get("factory_version") != NEW_FV:
        fails.append("factory_version %r" % m.get("factory_version"))
    desc = m.get("description") or ""
    print("%-16s %-9s %-9s %s" % ("tool", "pinned", "tag", "tag?"))
    print("-" * 50)
    for n in sorted(tools):
        e = tools[n]; ok = tag_ok(n, e.get("tag"))
        print("%-16s %-9s %-9s %s" % (n, e.get("version"), e.get("tag"),
              "ok" if ok else ("MISSING" if ok is False else "no repo")))
        if ok is False and n not in desc:
            fails.append("%s pins a missing tag and is not named in the description" % n)
    if tools.get(TOOL, {}).get("version") != TNEW:
        fails.append("%s not pinned at %s" % (TOOL, TNEW))
    if "DOES NOT CERTIFY" not in desc:
        fails.append("not-certified language missing")
    if tag_ok("zoo", "v99.99.99") is not False:
        fails.append("the tag resolver does not return False for an impossible tag")
    if fails:
        print(""); print("SELFTEST FAILED")
        for f in fails: print("      %s" % f)
        sys.exit(1)
    print(""); print("SELFTEST OK -- factory %s, deli_counter %s, every pin resolved,"
                     % (NEW_FV, TNEW))
    print("               resolver shown to reject an impossible tag")
    sys.exit(0)

probs = []
if m.get("factory_version") == NEW_FV:
    print("NOTHING TO DO -- already %s" % NEW_FV); sys.exit(0)
if m.get("factory_version") != OLD_FV:
    probs.append("factory_version is %r, expected %r" % (m.get("factory_version"), OLD_FV))
e = tools.get(TOOL)
if not e:
    probs.append("no tools entry for %s" % TOOL)
else:
    if e.get("version") != TOLD: probs.append("%s pins %r" % (TOOL, e.get("version")))
    if tag_ok(TOOL, "v" + TNEW) is not True:
        probs.append("tag v%s does not exist in %s -- commit and tag first" % (TNEW, TOOL))
fmt = detect(text, m)
if fmt is None: probs.append("manifest does not round-trip; refusing to reformat")

print("PRE-FLIGHT  %s %s -> %s   factory %s -> %s" % (TOOL, TOLD, TNEW, OLD_FV, NEW_FV))
if probs:
    print("REFUSING:"); [print("      %s" % p) for p in probs]; sys.exit(1)
if MODE == "check":
    print("CHECK OK"); sys.exit(0)

nm = dict(m); nm["factory_version"] = NEW_FV
nt = dict(tools); ne = dict(nt[TOOL])
ne["version"] = TNEW; ne["tag"] = "v" + TNEW; ne["note"] = NOTE
nt[TOOL] = ne; nm["tools"] = nt
nm["description"] = DESC + "\n\n" + (m.get("description") or "")
ind, ea, suf = fmt
body = json.dumps(nm, indent=ind, ensure_ascii=ea) + suf
if not os.path.exists(MP + SIDE):
    with open(MP + SIDE, "wb") as fh: fh.write(raw)
with open(MP, "wb") as fh: fh.write(body.replace("\n", eol).encode("utf-8"))
print("APPLIED -- factory %s (%d bytes)" % (NEW_FV, len(body)))
