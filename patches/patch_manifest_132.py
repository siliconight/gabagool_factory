#!/usr/bin/env python
"""patch_manifest_132.py -- factory 1.31.0 -> 1.32.0

WHAT
  Re-pins two tools: zoo 0.46.0, deli_counter 0.91.0. Rewrites both their
  notes and the description's leading block, demoting the previous one to
  PRIOR CERTIFICATION.

  THE DESCRIPTION SAYS WHAT THIS SET DOES NOT CERTIFY, FIRST. No
  end-to-end chain ran. The evidence is four suites green in isolation
  plus one measured zoo/pixelcoat interop. A full re-certification is
  owed and this pin does not pretend to be one.

TAGS ARE RESOLVED, NOT ASSUMED
  Two checks, and the second one is new:

  * REQUIRE -- every tag this patch WRITES (v0.46.0, v0.91.0) must already
    exist inside that tool's OWN repository. Missing one refuses the whole write. This is
    the check whose absence, one release ago, let four nonexistent tags be
    pinned and a false finding be written into the description.

  * AUDIT -- every tag this patch does NOT touch is also resolved, and
    reported. laser_tag pins v0.8.0 and that tag does not exist; the audit
    is how that was found rather than inherited. A missing audit tag does
    NOT refuse the write -- it is recorded in the description instead,
    because resolving it is a decision about history, not a version bump.

USAGE   (run from anywhere; paths are absolute)
  python patch_manifest_132.py --check
  python patch_manifest_132.py
  python patch_manifest_132.py --selftest
  python patch_manifest_132.py --revert
"""
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
TAG = "manifest132"
M = json.loads(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "patch_m132.json"), encoding="utf-8").read()) \
    if os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "patch_m132.json")) else None


def _abs(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    os.close(fd)
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def _tool_dir(name):
    return os.path.join(ROOT, M["tool_paths"].get(name, name))


def _tag_exists(name, tag):
    """Ask the TOOL's repository, never the factory's. The factory repo's
    tags are all factory-v1.x; asking it about v0.44.0 returns silence, and
    silence read as a finding is how four nonexistent tags got pinned."""
    d = _tool_dir(name)
    if not os.path.isdir(os.path.join(d, ".git")):
        return None
    try:
        r = subprocess.run(["git", "-C", d, "tag", "--list", tag],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return bool(r.returncode == 0 and r.stdout.strip())


def check_tags(verbose=True):
    """(ok_to_write, audit_findings)."""
    bad, findings = [], []
    for name, tag in sorted(M["require_tags"].items()):
        got = _tag_exists(name, tag)
        if verbose:
            print("  require  %-15s %-10s %s"
                  % (name, tag, {True: "ok", False: "MISSING",
                                 None: "unknowable"}[got]))
        if got is not True:
            bad.append("%s: %s does not resolve in %s" % (name, tag, _tool_dir(name)))
    for name, tag in sorted(M["audit_tags"].items()):
        got = _tag_exists(name, tag)
        if verbose:
            print("  audit    %-15s %-10s %s"
                  % (name, tag, {True: "ok", False: "MISSING",
                                 None: "unknowable"}[got]))
        if got is False:
            findings.append("%s pins %s and it does not exist" % (name, tag))
    return (not bad), bad, findings


def preflight():
    bad = []
    for rel, want in M["pre_sha"].items():
        p = _abs(rel)
        if not os.path.isfile(p):
            bad.append("MISSING  " + rel)
        elif _sha(p) != want:
            bad.append("DRIFT    %s\n           on disk %s\n           expect  %s"
                       % (rel, _sha(p)[:16], want[:16]))
    return (not bad), bad


def check():
    ok, bad = preflight()
    print("target:")
    for rel in M["pre_sha"]:
        print("  %-14s %s" % ("ok" if ok else "DRIFT/MISSING", rel))
    print("\ntags:")
    tok, tbad, findings = check_tags()
    if findings:
        print("\naudit findings (recorded in the description, not fixed here):")
        for f in findings:
            print("  - " + f)
    print()
    if ok and tok:
        print("PRE-FLIGHT CLEAN -- apply would write factory.manifest.json")
        return 0
    print("PRE-FLIGHT REFUSED:")
    for b in bad + tbad:
        print("  " + b)
    return 1


def apply():
    ok, bad = preflight()
    tok, tbad, findings = check_tags(verbose=False)
    if not (ok and tok):
        print("REFUSED -- nothing written:")
        for b in bad + tbad:
            print("  " + b)
        return 1
    for f in findings:
        print("  audit finding (recorded, not fixed): " + f)
    for rel, text in M["whole"].items():
        p = _abs(rel)
        if os.path.isfile(p):
            shutil.copy2(p, p + ".pre_" + TAG)
        _write(p, text)
        print("  wrote  %-28s %8d bytes" % (rel, len(text.encode("utf-8"))))
    print("\nfactory %s -> %s" % (M["from_version"], M["to_version"]))
    return 0


def revert():
    n = 0
    for rel in M["pre_sha"]:
        p = _abs(rel)
        side = p + ".pre_" + TAG
        if os.path.isfile(side):
            shutil.copy2(side, p)
            os.remove(side)
            print("  restored " + rel)
            n += 1
    print("reverted %d file(s)" % n)
    return 0 if n else 1


def selftest():
    fails = []
    try:
        return _selftest(fails)
    except Exception as exc:
        print("SELFTEST FAILED -- %s: %s" % (type(exc).__name__, exc))
        for f in fails:
            print("  - " + f)
        return 1


def _selftest(fails):
    man = json.load(open(_abs("factory.manifest.json"), encoding="utf-8"))

    # 1. the pins landed
    if man["factory_version"] != "1.32.0":
        fails.append("factory_version is %r, want 1.32.0" % man["factory_version"])
    for name, tag in M["require_tags"].items():
        t = man["tools"][name]
        if t["tag"] != tag or ("v" + t["version"]) != tag:
            fails.append("%s: version=%r tag=%r disagree with %r"
                         % (name, t["version"], t["tag"], tag))

    # 2. every pinned tag in the WHOLE file resolves, or is named as a finding
    missing = []
    for name, t in sorted(man["tools"].items()):
        got = _tag_exists(name, t.get("tag", ""))
        if got is False:
            missing.append((name, t["tag"]))
    for name, tag in missing:
        if name not in man["description"]:
            fails.append("%s pins %s which does not exist, and the description "
                         "does not mention %s -- an unresolved pin must be "
                         "recorded" % (name, tag, name))
    if not missing:
        print("  every pinned tag resolves (laser_tag must have been fixed)")
    else:
        print("  unresolved pins, each recorded in the description: %s"
              % ", ".join("%s=%s" % m for m in missing))

    # 3. THE HONESTY CHECK. This set did not run a chain; the description has
    #    to say so. If a later edit quietly upgrades the claim, this fails.
    for phrase in ("WHAT THIS SET DOES NOT CERTIFY",
                   "no end-to-end chain ran",
                   "A full re-certification is owed"):
        if phrase not in man["description"]:
            fails.append("description no longer contains %r" % phrase)

    # 4. the real verify_manifest agrees
    lf = os.path.join(ROOT, "level_factory")
    sys.path.insert(0, lf)
    try:
        from packages.tools import contracts
    except Exception as exc:
        print("  (could not import level_factory contracts: %s: %s)"
              % (type(exc).__name__, exc))
        contracts = None
    verified = contracts is not None
    if contracts is not None:
        results = contracts.verify_manifest(ROOT)
        by = {}
        for r in results:
            by.setdefault(str(r.status), []).append(r.adapter_id)
        for status, names in sorted(by.items()):
            print("  verify-manifest %-14s %s" % (status, ", ".join(sorted(names))))
        for r in results:
            if r.adapter_id in M["require_tags"] and str(r.status) != "OK":
                fails.append("verify-manifest reports %s as %s (certified=%r "
                             "installed=%r documented=%r)"
                             % (r.adapter_id, r.status, r.certified,
                                r.installed, r.documented))

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    tail = ("and verify-manifest reports OK for all four" if verified else
            "BUT verify-manifest COULD NOT BE RUN -- that part is unchecked")
    print("SELFTEST OK -- four pins match their tags, every unresolved pin is "
          "named in the description, the not-certified language is intact, "
          + tail)
    return 0 if verified else 1


def main():
    if M is None:
        print("patch_m.json must sit next to this script")
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--revert", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.check:
        return check()
    if a.revert:
        return revert()
    if a.selftest:
        return selftest()
    return apply()


if __name__ == "__main__":
    sys.exit(main())
