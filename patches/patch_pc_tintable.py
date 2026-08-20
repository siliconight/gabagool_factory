#!/usr/bin/env python
"""patch_pc_tintable.py -- Pixelcoat 0.12.0 -> 0.13.0

WHAT
  Adds `tintable` to the material grammar and writes it into every pack
  manifest, plus the first achromatic-by-intent profile (`plastic_neutral`),
  plus the version.py/VERSION reconciliation (version.py was left at 0.11.0
  by the 0.12.0 release, so every pack on disk is misstamped).

  This patch changes NOTHING that renders. No theme maps `plastic`, so no
  pack resolves for it. Mapping it is held until Zoo reads `tintable`.

USAGE   (run from anywhere; paths are absolute)
  pwsh:  python patch_pc_tintable.py --check
         python patch_pc_tintable.py --selftest
         python patch_pc_tintable.py
         python patch_pc_tintable.py --revert

CONTRACT
  * refuses on drift: every target file's sha256 is checked against the
    sha recorded when this script was generated
  * all-or-nothing: a full pre-flight sweep of every target runs BEFORE the
    first byte is written. A single refusal writes nothing at all.
  * every edit is anchored, and every anchor must occur EXACTLY ONCE
  * .pre_tintable sidecars are written for --revert
"""
import argparse, hashlib, io, json, os, shutil, sys, tempfile

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
TAG = "tintable"
M = json.loads(r"""{
 "tool": "pixelcoat",
 "from_version": "0.12.0",
 "to_version": "0.13.0",
 "tag": "tintable",
 "edits": [
  {
   "path": "pixelcoat/pixelcoat/core/material_grammar.py",
   "anchor": "    emit: dict = field(default_factory=lambda: {\"roughness\": True, \"normal\": False})\n",
   "after": "    emit: dict = field(default_factory=lambda: {\"roughness\": True, \"normal\": False})\n    # ACHROMATIC-BY-INTENT. True means \"my albedo is a surface, not a paint\n    # job -- the consumer supplies the hue\". Zoo multiplies the mesh's own\n    # base colour into a tintable pack and skips it for every other pack, so\n    # a rusted-metal facade keeps its rust while a plastic shroud takes the\n    # genome's red. Keyed here and not on `kind` because one kind (metal)\n    # legitimately serves both cases.\n    tintable: bool = False\n"
  },
  {
   "path": "pixelcoat/pixelcoat/core/material_grammar.py",
   "anchor": "        \"meters_per_tile\": float(grammar.meters_per_tile),\n        \"seed\": int(seed),\n",
   "after": "        \"meters_per_tile\": float(grammar.meters_per_tile),\n        \"seed\": int(seed),\n        \"tintable\": bool(grammar.tintable),\n"
  },
  {
   "path": "pixelcoat/pixelcoat/version.py",
   "anchor": "__version__ = \"0.11.0\"\n",
   "after": "__version__ = \"0.13.0\"\n"
  }
 ],
 "whole": {
  "pixelcoat/VERSION": "Pixelcoat 0.13.0\n"
 },
 "new": {
  "pixelcoat/profiles/materials/plastic_neutral.json": "{\n  \"id\": \"plastic_neutral\",\n  \"kind\": \"plastic\",\n  \"tintable\": true,\n  \"base_colors\": [\n    \"#e9e9e6\",\n    \"#f2f1ed\"\n  ],\n  \"meters_per_tile\": 1.5,\n  \"bands\": {\n    \"macro\": 0.12,\n    \"meso\": 0.22,\n    \"micro\": 0.2\n  },\n  \"macro\": {\n    \"generator\": \"fbm\",\n    \"cells\": 3,\n    \"octaves\": 2\n  },\n  \"meso\": {\n    \"generator\": \"directional_grain\",\n    \"cells_along\": 3,\n    \"cells_across\": 40,\n    \"axis\": \"y\"\n  },\n  \"micro\": {\n    \"generator\": \"fbm\",\n    \"cells\": 140,\n    \"octaves\": 2\n  },\n  \"detail_strength\": 0.05,\n  \"albedo_pattern\": 0.55,\n  \"posterize\": 12,\n  \"roughness\": {\n    \"base\": 0.34,\n    \"variation\": 0.09\n  },\n  \"height_strength\": 0.12,\n  \"emit\": {\n    \"roughness\": true,\n    \"normal\": false\n  }\n}\n"
 },
 "changelog": "## [0.13.0] - a pack can now say it wants to be painted\n\nZoo's `make_material` drops the genome's per-specimen colour the moment a\npack resolves: every object of a kind shares one cached material named for\nthe pack, and the only thing modulating it is COLOR_0, which carries\ngreyscale wear. That is right for a brick wall and wrong for a bumper. The\nfix cannot key on material KIND, because `metal` serves both a rusted\nstorefront facade and 42 prop species. So it keys on the PACK.\n\n### Added\n- **`tintable` on the material grammar**, written into the pack manifest. A\n  grammar sets it when its albedo is deliberately achromatic and the\n  consumer is expected to supply the hue. `metal_rusted_street` does not set\n  it and never should; `plastic_neutral` does.\n- **`plastic_neutral`** - an injection-moulded plastic in near-white, with\n  flow-direction grain and a low-variance sheen. It carries the surface and\n  nothing else, so a red vending machine and a black ATM shroud can share\n  it. This is the first profile authored to be multiplied rather than used.\n\n### Fixed\n- **`version.py` still said 0.11.0** while `VERSION` said 0.12.0. The 0.12.0\n  release bumped one and not the other, so every pack built since - including\n  the five theme libraries rebuilt today - is stamped\n  `\"tool_version\": \"0.11.0\"`. That file's own docstring calls itself the\n  single source of truth \"baked into every manifest so output is traceable to\n  the exact tool revision\"; for one release it was not. Both now read 0.13.0.\n\n### Note\nNothing renders differently yet. No theme maps `plastic`, so no pack resolves\nfor it and every plastic prop stays on the flat tinted path. Mapping it is a\nseparate change, deliberately held until Zoo reads `tintable`.\n\n",
 "pre_sha": {
  "pixelcoat/pixelcoat/core/material_grammar.py": "3966c67be13077d588a591cb1af56ceddc17caf67d80d2202cd2bde8eb194bf0",
  "pixelcoat/pixelcoat/version.py": "1682c249e359a381f17915750fa88a2e9ec672d666bc3f907ade43e37a7e2e88",
  "pixelcoat/VERSION": "aae64ce7f92c932d0a6836921d07fa2b603562893d5eb711005363bf3b1f9105",
  "pixelcoat/CHANGELOG.md": "fa5e5f55356a5396090bf296682d13843fee8905c49ed8be57d1a39b1c212424"
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

    cl_rel = M["tool"] + "/CHANGELOG.md"
    cl = _read(_abs(cl_rel))
    head = "# Changelog\n\n"
    if not cl.startswith(head):
        print("REFUSED -- %s does not start with the expected header" % cl_rel)
        return 1
    out[cl_rel] = head + M["changelog"] + cl[len(head):]

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
    fails = []
    try:
        return _selftest(fails)
    except Exception as exc:
        print("SELFTEST FAILED -- %s: %s" % (type(exc).__name__, exc))
        for f in fails:
            print("  - " + f)
        return 1


def _selftest(fails):

    from pixelcoat.core import material_grammar as mg
    from pixelcoat.version import __version__

    # 1. the field exists and defaults to False
    if "tintable" not in mg.MaterialGrammar.__dataclass_fields__:
        fails.append("MaterialGrammar has no `tintable` field")
    else:
        g = mg.MaterialGrammar(id="x", kind="plastic")
        if g.tintable is not False:
            fails.append("tintable does not default to False (got %r)" % g.tintable)

    # 2. from_dict actually carries it (the field filter drops unknown keys,
    #    so this fails loudly if the field was never added)
    g2 = mg.MaterialGrammar.from_dict({"id": "x", "kind": "plastic",
                                       "tintable": True})
    if getattr(g2, "tintable", None) is not True:
        fails.append("from_dict dropped tintable=True")

    # 3. THE FALSIFICATION: build two real packs and read the manifests back.
    #    Remove the manifest line and this test fails.
    import tempfile as _tf
    prof = os.path.join(ROOT, "pixelcoat", "profiles", "materials")
    with _tf.TemporaryDirectory() as td:
        m_t = mg.build_material_pack(
            os.path.join(prof, "plastic_neutral.json"),
            os.path.join(td, "tinted"), size=32)
        m_f = mg.build_material_pack(
            os.path.join(prof, "metal_rusted_street.json"),
            os.path.join(td, "flat"), size=32)
        if m_t.get("tintable") is not True:
            fails.append("plastic_neutral pack manifest: tintable=%r, want True"
                         % m_t.get("tintable"))
        if m_f.get("tintable") is not False:
            fails.append("metal_rusted_street pack manifest: tintable=%r, "
                         "want False" % m_f.get("tintable"))
        # and it must survive the round trip to disk
        onto = json.load(open(os.path.join(td, "tinted",
                                           "plastic_neutral.pack.json"),
                              encoding="utf-8"))
        if onto.get("tintable") is not True:
            fails.append("tintable did not survive the write to pack.json")

    # 4. plastic_neutral must actually be achromatic and bright, or the
    #    multiply produces mud. Measured, not asserted by eye.
    g3 = mg.MaterialGrammar.load(os.path.join(prof, "plastic_neutral.json"))
    for hexc in g3.base_colors:
        r, gg, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
        if max(r, gg, b) - min(r, gg, b) > 12:
            fails.append("plastic_neutral base colour %s is not achromatic "
                         "(chroma spread %d > 12)" % (hexc, max(r, gg, b) - min(r, gg, b)))
        if min(r, gg, b) < 200:
            fails.append("plastic_neutral base colour %s is too dark to tint "
                         "(min channel %d < 200)" % (hexc, min(r, gg, b)))

    # 5. the version drift this patch also fixes
    vfile = open(os.path.join(ROOT, "pixelcoat", "VERSION"),
                 encoding="utf-8").read().strip()
    # Read the SOURCE, not the import: a stale .pyc can serve the old
    # constant (see _purge_bytecode) and would make this check lie.
    vsrc = open(os.path.join(ROOT, "pixelcoat", "pixelcoat", "version.py"),
                encoding="utf-8").read()
    import re as _re
    mm = _re.search(r'__version__\s*=\s*"([^"]+)"', vsrc)
    vpy = mm.group(1) if mm else "?"
    if not vfile.endswith(vpy):
        fails.append("VERSION says %r but version.py says %r -- the drift is "
                     "back" % (vfile, vpy))
    if vpy != __version__:
        fails.append("version.py on disk says %r but the imported module says "
                     "%r -- stale bytecode" % (vpy, __version__))

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("SELFTEST OK -- 5 checks, including two real pack builds read back "
          "from disk")
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
