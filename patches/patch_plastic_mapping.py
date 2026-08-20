#!/usr/bin/env python
"""patch_plastic_mapping.py -- pixelcoat 0.13.0 -> 0.14.0, zoo 0.42.0 -> 0.42.1

WHAT
  Maps `plastic -> plastic_neutral` in all nine theme profiles, and retracts
  the `UNVERIFIED` note on `materials._tint_multiply` now that the export
  boundary has been measured.

  THIS ONE DOES CHANGE WHAT RENDERS. After the theme libraries are rebuilt,
  the 17 species that can wear `plastic` stop being flat colour and take the
  pack's grain, sheen and roughness -- while KEEPING their own hue, because
  `plastic_neutral` is tintable. Rebuild command is printed on success.

  Touches TWO repos. The pre-flight sweep spans both: if either refuses,
  neither is written.

USAGE   (run from anywhere; paths are absolute)
  pwsh:  python patch_plastic_mapping.py --check
         python patch_plastic_mapping.py
         python patch_plastic_mapping.py --selftest
         python patch_plastic_mapping.py --revert

CONTRACT
  * refuses on drift (sha256 per target, recorded at generation time)
  * all-or-nothing across both repos
  * every anchor must occur EXACTLY ONCE
  * .pre_plastic sidecars for --revert
  * __pycache__ purged after any write
"""
import argparse, hashlib, io, json, os, shutil, sys, tempfile

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
TAG = "plastic"
M = json.loads(r"""{
 "tool": "multi",
 "from_version": "pixelcoat 0.13.0 / zoo 0.42.0",
 "to_version": "pixelcoat 0.14.0 / zoo 0.42.1",
 "tag": "plastic",
 "edits": [
  {
   "path": "pixelcoat/profiles/themes/bank.json",
   "anchor": "  \"materials\": {\n",
   "after": "  \"materials\": {\n    \"plastic\": \"plastic_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/casino.json",
   "anchor": "  \"materials\": {\n",
   "after": "  \"materials\": {\n    \"plastic\": \"plastic_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/delco.json",
   "anchor": " \"materials\": {\n",
   "after": " \"materials\": {\n  \"plastic\": \"plastic_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/rockay.json",
   "anchor": " \"materials\": {\n",
   "after": " \"materials\": {\n  \"plastic\": \"plastic_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/rockay_civic.json",
   "anchor": " \"materials\": {\n",
   "after": " \"materials\": {\n  \"plastic\": \"plastic_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/rockay_retail.json",
   "anchor": " \"materials\": {\n",
   "after": " \"materials\": {\n  \"plastic\": \"plastic_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/rockay_service.json",
   "anchor": "  \"materials\": {\n",
   "after": "  \"materials\": {\n    \"plastic\": \"plastic_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/stadium.json",
   "anchor": "  \"materials\": {\n",
   "after": "  \"materials\": {\n    \"plastic\": \"plastic_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/street.json",
   "anchor": "  \"materials\": {\n",
   "after": "  \"materials\": {\n    \"plastic\": \"plastic_neutral\",\n"
  },
  {
   "path": "pixelcoat/pixelcoat/version.py",
   "anchor": "__version__ = \"0.13.0\"\n",
   "after": "__version__ = \"0.14.0\"\n"
  },
  {
   "path": "zoo/zoo_keeper/bpylayer/materials.py",
   "anchor": "    UNVERIFIED AT THE EXPORT BOUNDARY -- read this before trusting it.\n    glTF computes base colour as ``baseColorFactor * baseColorTexture *\n    COLOR_0``. This node is the Blender spelling of the FACTOR term, and the\n    exporter has to fold it back into one. There is now one more node between\n    the image and Base Color than there was when `tools/wear_probe.py`\n    verified the texture still exported, and the exporter is free to give up\n    quietly and drop the factor -- which would render every tinted prop in\n    the pack's own near-white, with no error anywhere. That is the same shape\n    of silent failure that hid the flat wear for a whole art pass.\n\n    `tools/tint_probe.py` exports a specimen and reads baseColorFactor and\n    baseColorTexture back out of the GLB. Run it before shipping a tintable\n    pack. If the factor is dropped, the fallback is to multiply the tint into\n    the loaded image pixels once per colour -- slower and heavier, but a plain\n    texture cannot be dropped.\n",
   "after": "    VERIFIED AT THE EXPORT BOUNDARY on Blender 5.1.1 (hash b70da489d7f4).\n    glTF computes base colour as ``baseColorFactor * baseColorTexture *\n    COLOR_0``. This node is the Blender spelling of the FACTOR term, and the\n    exporter has to fold it back into one. It does. `tools/tint_probe.py`\n    exported two materials off one tintable pack and read the GLB back:\n\n        M_Probe_red   baseColorFactor [0.620, 0.140, 0.140, 1.000]  texture yes\n        M_Probe_blue  baseColorFactor [0.140, 0.260, 0.550, 1.000]  texture yes\n\n    Those are the genome colours to three decimals, and baseColorTexture\n    survived the extra node. This was written down as UNKNOWN until it was\n    measured, because the failure mode -- exporter silently drops the factor,\n    every tinted prop renders in the pack own near-white, nothing logs -- is\n    the same shape that hid the flat wear for a whole art pass.\n\n    RE-RUN THE PROBE ON A BLENDER UPGRADE. The fold is the exporter choice,\n    not a guarantee of the format. If a future version drops it, the fallback\n    is to multiply the tint into the loaded image pixels once per colour --\n    slower and heavier, but a plain texture cannot be dropped.\n"
  }
 ],
 "whole": {
  "pixelcoat/VERSION": "Pixelcoat 0.14.0\n",
  "zoo/VERSION": "Zoo 0.42.1\n"
 },
 "new": {},
 "changelogs": {
  "pixelcoat/CHANGELOG.md": "## [0.14.0] - plastic joins the vocabulary\n\nEvery theme mapped the same 11 architectural kinds. Zoo's `KNOWN_KINDS` has\n22, and the gap was not evenly distributed: `plastic` is named by 17 of the 53\nspecies and hard-coded as a literal in 6 recipe bodies, so it was the largest\nsingle hole in the library by a wide margin. It stayed open because the only\nplastic profile was `plastic_delco`, a dark red -- and Zoo shares one material\nper kind, so mapping it would have turned every ATM shroud, vending machine\ntrim, CRT bezel, condiment bottle and car bumper the same red in all nine\nthemes. Worse than flat.\n\n0.13.0 gave a grammar a way to say its albedo is a surface and not a paint\njob. Zoo 0.42.0 reads it, and `tools/tint_probe.py` measured that the tint\nreaches the exported GLB intact. So the mapping is now safe to make.\n\n### Changed\n- All nine themes map `plastic -> plastic_neutral`. Because that pack is\n  tintable, this does NOT make 17 species share a colour: each mesh keeps the\n  hue its genome or style declares and gains the pack's grain, sheen and\n  roughness response.\n\n### Note\n`plastic_delco` is untouched and unmapped. It is a red plastic, correct for a\nspecific object and wrong for a shared kind slot; it stays available for a\ntheme that wants exactly that.\n\nStill unmapped, in demand order: laminate (6 species, no profile), paper (5,\nno profile), leather (3, profile exists), dirt (3, profile exists), gravel (2,\nno profile), rubber (1 genome + hard-coded in simple_car and boots, profile\nexists), tar (1 -- the `roof` species, no profile, unmapped since it shipped),\ncanvas, carbon, vegetation.\n\n",
  "zoo/CHANGELOG.md": "## [0.42.1] - the export boundary was measured, so the note comes down\n\n0.42.0 shipped `_tint_multiply` with an `### UNVERIFIED` block: the shader\ngraph gained a node between the image and Base Color, and the glTF exporter\nwas free to drop the resulting baseColorFactor silently. That was the honest\nstate of knowledge, and it is no longer the state of knowledge.\n\n### Verified\n`tools/tint_probe.py`, Blender 5.1.1 (hash b70da489d7f4), two materials built\nfrom one tintable pack and read back out of the exported GLB:\n\n    M_Probe_red   baseColorFactor [0.620, 0.140, 0.140, 1.000]  texture yes\n    M_Probe_blue  baseColorFactor [0.140, 0.260, 0.550, 1.000]  texture yes\n\nThe genome colours to three decimals, both textures intact, and the two did\nnot collapse into one material. The pixel-bake fallback is not needed.\n\n### Changed\n- The docstring on `_tint_multiply` now records the measurement instead of the\n  doubt, and says to re-run the probe on a Blender upgrade -- the fold is the\n  exporter's choice, not a guarantee of the format.\n\n"
 },
 "pre_sha": {
  "pixelcoat/profiles/themes/bank.json": "e6c741a7b09495411c72c17e4c33e1195333ddd417db3da26fd14bca58bfe233",
  "pixelcoat/profiles/themes/casino.json": "905c821e5348430dee3acf31bc44c5325f8c3f54f4c8e038d95b2050580bd8f8",
  "pixelcoat/profiles/themes/delco.json": "d03f93e44185e512ce197a650fa9fa40dccd72363f26fd4e867af5547f396f2e",
  "pixelcoat/profiles/themes/rockay.json": "54ed4fb48fe0aa8763b68a3a562fbb73ac5d507d0467787fe915cdb44088cd7f",
  "pixelcoat/profiles/themes/rockay_civic.json": "ad2b78a73a23f83086394af76885ab4ac1ee5dcd38f5253537c9528a02ad09a4",
  "pixelcoat/profiles/themes/rockay_retail.json": "1560a74dfdcf5e399bc1aa7a5491356126b96c08e546064c77b30936c621a2fb",
  "pixelcoat/profiles/themes/rockay_service.json": "7c999332b88cdc2dfba36c870fe8cf388e6b573d75121eb730db8e36588ee317",
  "pixelcoat/profiles/themes/stadium.json": "e610dab1d75beadd5622415bc5cc79b95599e59e2972faec77eaf8474630df66",
  "pixelcoat/profiles/themes/street.json": "3a6e6bd6572c5df0e078ba13b01adced2422f21b87d4e34c751cd8d83b803b92",
  "pixelcoat/pixelcoat/version.py": "11d88befa1340c1798c8fb0722caf097ce96600d79cfb21af4d4f29611732190",
  "zoo/zoo_keeper/bpylayer/materials.py": "11a6579f3836fc8f80bbba8e4111bfc38b37adcf5af2495a5095495c503b2fdd",
  "pixelcoat/VERSION": "88649f34113708f07b2c53caae6da816df746524048e31c8a40366e1e0d8362c",
  "zoo/VERSION": "0d25c76340a67f81ce4b587b555f793da5aaca8e62de8e57ffa01d8c7db44bb5",
  "pixelcoat/CHANGELOG.md": "8f1999c7a41b693cd39ab989ab665701c0a8d307d0082accc901ec16efff9269",
  "zoo/CHANGELOG.md": "c40163f6380a51c92ce6ee26acc93053f0c95058785eb555d131aa3d035df4ee"
 }
}""")


def _abs(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _write(path, text):
    """Never truncate the target before the content is known good."""
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    os.close(fd)
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def _purge_bytecode(rels):
    """Delete __pycache__ for every package dir we just rewrote a .py in.

    Found the hard way: rewriting version.py in the same wall-clock SECOND
    that its .pyc was written left the .pyc valid by Python's (mtime, size)
    check -- both were 366 bytes and both stamped the same second -- so the
    interpreter kept serving the OLD constant and the selftest reported the
    change had not landed. It had. A patch tool that edits live Python must
    invalidate bytecode or it can silently appear to do nothing.
    """
    seen = set()
    for rel in rels:
        if not rel.endswith(".py"):
            continue
        d = os.path.join(os.path.dirname(_abs(rel)), "__pycache__")
        if d in seen or not os.path.isdir(d):
            continue
        seen.add(d)
        shutil.rmtree(d, ignore_errors=True)
        print("  purged " + os.path.relpath(d, ROOT))
    return len(seen)


# --------------------------------------------------------------------------- #
# pre-flight
# --------------------------------------------------------------------------- #

def preflight(expect_patched=False):
    """Returns (ok, list of problem strings). Writes nothing, ever."""
    bad = []
    targets = set(M["pre_sha"])
    for rel in sorted(targets):
        p = _abs(rel)
        if not os.path.isfile(p):
            bad.append("MISSING  " + rel)
            continue
        got = _sha(p)
        want = M["pre_sha"][rel]
        if got != want and not expect_patched:
            bad.append("DRIFT    %s\n           on disk %s\n           expect  %s"
                       % (rel, got[:16], want[:16]))
    # anchors must be present exactly once
    for e in M["edits"]:
        p = _abs(e["path"])
        if not os.path.isfile(p):
            continue
        src = _read(p)
        n = src.count(e["anchor"])
        if n != 1 and not expect_patched:
            bad.append("ANCHOR   %s occurs %d times (need exactly 1)"
                       % (e["path"], n))
    for rel in M["new"]:
        p = _abs(rel)
        if os.path.isfile(p) and not expect_patched:
            bad.append("EXISTS   %s (refusing to overwrite a file this "
                       "patch claims to create)" % rel)
    return (not bad), bad


# --------------------------------------------------------------------------- #
# apply
# --------------------------------------------------------------------------- #

def apply():
    ok, bad = preflight()
    if not ok:
        print("REFUSED -- nothing written:")
        for b in bad:
            print("  " + b)
        return 1

    # Build every output IN MEMORY first. Only then touch the disk.
    out = {}

    by_file = {}
    for e in M["edits"]:
        by_file.setdefault(e["path"], []).append(e)
    for rel, edits in by_file.items():
        src = _read(_abs(rel))
        for e in edits:
            src = src.replace(e["anchor"], e["after"], 1)
        out[rel] = src

    for rel, text in M["whole"].items():
        out[rel] = text
    for rel, text in M["new"].items():
        out[rel] = text

    head = "# Changelog\n\n"
    for cl_rel, entry in M["changelogs"].items():
        cl = _read(_abs(cl_rel))
        if not cl.startswith(head):
            print("REFUSED -- %s does not start with the expected header"
                  % cl_rel)
            return 1
        out[cl_rel] = head + entry + cl[len(head):]

    # sidecars, then write
    for rel in sorted(out):
        p = _abs(rel)
        if os.path.isfile(p):
            shutil.copy2(p, p + ".pre_" + TAG)
    for rel in sorted(out):
        _write(_abs(rel), out[rel])
        print("  wrote  %-52s %8d bytes" % (rel, len(out[rel].encode("utf-8"))))

    _purge_bytecode(out)

    print("")
    print("%s %s -> %s" % (M["tool"], M["from_version"], M["to_version"]))
    return 0


def revert():
    n = 0
    for rel in sorted(set(list(M["pre_sha"]) + list(M["new"]))):
        p = _abs(rel)
        side = p + ".pre_" + TAG
        if os.path.isfile(side):
            shutil.copy2(side, p)
            os.remove(side)
            print("  restored " + rel)
            n += 1
        elif rel in M["new"] and os.path.isfile(p):
            os.remove(p)
            print("  removed  " + rel)
            n += 1
    _purge_bytecode(set(list(M["pre_sha"]) + list(M["new"])))
    print("reverted %d file(s)" % n)
    return 0 if n else 1


# --------------------------------------------------------------------------- #
# selftest -- must FAIL if the change is backed out
# --------------------------------------------------------------------------- #

def selftest():
    sys.path.insert(0, os.path.join(ROOT, "pixelcoat"))
    sys.path.insert(0, os.path.join(ROOT, "zoo"))
    fails = []
    try:
        return _selftest(fails)
    except Exception as exc:
        print("SELFTEST FAILED -- %s: %s" % (type(exc).__name__, exc))
        for f in fails:
            print("  - " + f)
        return 1


def _selftest(fails):
    import glob as _glob
    import json as _json
    import re as _re
    import tempfile as _tf

    prof = os.path.join(ROOT, "pixelcoat", "profiles")
    themes = sorted(_glob.glob(os.path.join(prof, "themes", "*.json")))

    # ---- 1. every theme maps plastic, and maps it to the TINTABLE profile --
    if len(themes) != 9:
        fails.append("expected 9 theme profiles, found %d" % len(themes))
    for t in themes:
        d = _json.load(open(t, encoding="utf-8"))
        got = d.get("materials", {}).get("plastic")
        if got != "plastic_neutral":
            fails.append("theme %r maps plastic -> %r, want 'plastic_neutral'"
                         % (d.get("theme"), got))

    # ---- 2. the profile it points at is real, is kind=plastic, IS tintable -
    #         (build_theme_library raises on a kind mismatch; catching it here
    #          gives a readable failure instead of a traceback mid-build)
    gp = os.path.join(prof, "materials", "plastic_neutral.json")
    if not os.path.isfile(gp):
        fails.append("profiles/materials/plastic_neutral.json is missing -- "
                     "every theme now points at nothing")
    else:
        g = _json.load(open(gp, encoding="utf-8"))
        if g.get("kind") != "plastic":
            fails.append("plastic_neutral is kind %r; the theme maps it to the "
                         "'plastic' slot and the build would raise" % g.get("kind"))
        if g.get("tintable") is not True:
            fails.append("plastic_neutral is NOT tintable -- mapping it would "
                         "paint 17 species the same colour, which is the whole "
                         "thing this change exists to avoid")

    # ---- 3. THE END-TO-END FALSIFICATION -----------------------------------
    #         Build a real theme library through Pixelcoat, then resolve it
    #         through Zoo. This is the only check that crosses both tools.
    from pixelcoat.core import material_grammar as mg
    from zoo_keeper.core import skins

    with _tf.TemporaryDirectory() as td:
        res = mg.build_theme_library(os.path.join(prof, "themes", "delco.json"),
                                     os.path.join(prof, "materials"),
                                     td, size=32)
        if "plastic" not in res["packs"]:
            fails.append("build_theme_library produced no plastic pack")
        else:
            pack = skins.find_pack(td, "plastic", "delco")
            if pack is None:
                fails.append("Zoo cannot resolve the plastic pack Pixelcoat "
                             "just wrote (layout mismatch: %r)"
                             % res["packs"]["plastic"])
            else:
                if pack.get("tintable") is not True:
                    fails.append("Zoo resolved the plastic pack but reads "
                                 "tintable=%r -- the flag does not survive the "
                                 "round trip" % pack.get("tintable"))
                if "albedo" not in pack.get("maps", {}):
                    fails.append("the plastic pack has no albedo map")
        # and the control: a NON-tintable kind must still come back False, or
        # this patch has repainted the architecture too.
        brick = skins.find_pack(td, "brick", "delco")
        if brick is None:
            fails.append("brick pack vanished from the rebuilt library")
        elif brick.get("tintable") is not False:
            fails.append("brick resolved tintable=%r -- walls would be "
                         "repainted by mesh colour" % brick.get("tintable"))

    # ---- 4. the retraction actually landed in the source -------------------
    msrc = os.path.join(ROOT, "zoo", "zoo_keeper", "bpylayer", "materials.py")
    text = open(msrc, encoding="utf-8").read()
    if "UNVERIFIED AT THE EXPORT BOUNDARY" in text:
        fails.append("materials.py still claims the export boundary is "
                     "unverified; it was measured")
    for token in ("VERIFIED AT THE EXPORT BOUNDARY", "0.620, 0.140, 0.140",
                  "0.140, 0.260, 0.550", "RE-RUN THE PROBE ON A BLENDER UPGRADE"):
        if token not in text:
            fails.append("materials.py docstring is missing %r" % token)

    # ---- 5. versions -------------------------------------------------------
    for tool, want in (("pixelcoat", "0.14.0"), ("zoo", "0.42.1")):
        vf = open(os.path.join(ROOT, tool, "VERSION"), encoding="utf-8").read().strip()
        if not vf.endswith(want):
            fails.append("%s/VERSION is %r, want it to end %r" % (tool, vf, want))
    vsrc = open(os.path.join(ROOT, "pixelcoat", "pixelcoat", "version.py"),
                encoding="utf-8").read()
    mm = _re.search(r'__version__\s*=\s*"([^"]+)"', vsrc)
    if not mm or mm.group(1) != "0.14.0":
        fails.append("pixelcoat/version.py says %r, not '0.14.0' -- pack "
                     "manifests would be misstamped again"
                     % (mm.group(1) if mm else None))

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("SELFTEST OK -- 5 groups, including a real theme library built "
          "through Pixelcoat and resolved back through Zoo (plastic tintable, "
          "brick not)")
    return 0


def check():
    ok, bad = preflight()
    print("targets:")
    for rel in sorted(M["pre_sha"]):
        p = _abs(rel)
        state = "ok" if os.path.isfile(p) and _sha(p) == M["pre_sha"][rel] else "DRIFT/MISSING"
        print("  %-14s %s" % (state, rel))
    for rel in M["new"]:
        print("  %-14s %s" % ("create" if not os.path.isfile(_abs(rel)) else "EXISTS", rel))
    print("")
    if ok:
        print("PRE-FLIGHT CLEAN -- apply would write %d file(s)"
              % (len(M["pre_sha"]) + len(M["new"])))
        return 0
    print("PRE-FLIGHT REFUSED:")
    for b in bad:
        print("  " + b)
    return 1


def main():
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
