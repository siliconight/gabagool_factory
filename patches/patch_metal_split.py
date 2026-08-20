#!/usr/bin/env python
"""patch_metal_split.py -- pixelcoat 0.14.0 -> 0.15.0, zoo 0.42.1 -> 0.43.0

WHAT
  Registers two new material kinds -- `metal_painted` and `metal_bare` -- and
  authors a tintable Pixelcoat profile for each, mapped in all nine themes.

  `metal` stays exactly as it is. It is theme-owned: a rusted facade and a
  corrugated wall belong to the building. The two new kinds are object-owned:
  the mesh supplies the hue, the pack supplies the surface.

  TWO kinds and not one because Zoo looks up METALLIC per kind. Paint is a
  dielectric (0.0); bare metal is a conductor (0.90).

  THIS CHANGES NOTHING THAT RENDERS. No Zoo genome names either kind yet.

  SCOPE, MEASURED FIRST: of the 42 species that can wear `metal`, only 12
  declare a style colour with chroma >= 0.10. The other 30 -- including all
  ten architectural species -- are already near-grey and keep `metal`.

USAGE   (run from anywhere; paths are absolute)
  pwsh:  python patch_metal_split.py --check
         python patch_metal_split.py
         python patch_metal_split.py --selftest
         python patch_metal_split.py --revert

  Then rebuild the theme libraries:
         pwsh -File pixelcoat\\tools\\rebuild_theme_libraries.ps1

CONTRACT
  * refuses on drift (sha256 per target, recorded at generation time)
  * all-or-nothing across both repos
  * every anchor must occur EXACTLY ONCE
  * .pre_metalsplit sidecars for --revert
  * __pycache__ purged after any write
"""
import argparse, hashlib, io, json, os, shutil, sys, tempfile

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
TAG = "metalsplit"
M = json.loads(r"""{
 "tool": "multi",
 "from_version": "pixelcoat 0.14.0 / zoo 0.42.1",
 "to_version": "pixelcoat 0.15.0 / zoo 0.43.0",
 "tag": "metalsplit",
 "edits": [
  {
   "path": "zoo/zoo_keeper/core/skins.py",
   "anchor": "               \"gravel\", \"vegetation\")\n",
   "after": "               \"gravel\", \"vegetation\",\n               # PROP METAL vs ARCHITECTURAL METAL. `metal` is theme-owned:\n               # a rusted storefront facade and a corrugated wall belong to\n               # the building, and a tintable pack in that slot would repaint\n               # them by their greybox colour. These two are OBJECT-owned --\n               # the mesh supplies the hue and the pack supplies the surface.\n               # They are separate kinds and not one, because METALLIC is a\n               # per-kind lookup and paint is a dielectric (0.0) while bare\n               # metal is a conductor. Measured before splitting: of the 42\n               # species that can wear `metal`, only 12 declare a style colour\n               # with chroma >= 0.10; the other 30 are already near-grey and\n               # correctly keep `metal`.\n               \"metal_painted\", \"metal_bare\")\n"
  },
  {
   "path": "zoo/zoo_keeper/bpylayer/materials.py",
   "anchor": "             \"gravel\": 0.95, \"vegetation\": 0.85}\n",
   "after": "             \"gravel\": 0.95, \"vegetation\": 0.85,\n             # Prop metal (see skins.KNOWN_KINDS). Semi-gloss enamel sits\n             # duller than the bare sheet it covers; brushed/polished stock\n             # sits tighter than the generic `metal` average.\n             \"metal_painted\": 0.45, \"metal_bare\": 0.28}\n"
  },
  {
   "path": "zoo/zoo_keeper/bpylayer/materials.py",
   "anchor": "METALLIC = {\"metal\": 0.85, \"carbon\": 0.30}\n",
   "after": "# `metal_painted` is listed at 0.0 rather than left to the .get() default:\n# the whole reason it is a separate kind from `metal_bare` is this number, and\n# a value that matters should not be inferred from an omission.\nMETALLIC = {\"metal\": 0.85, \"carbon\": 0.30,\n            \"metal_painted\": 0.0, \"metal_bare\": 0.90}\n"
  },
  {
   "path": "pixelcoat/profiles/themes/bank.json",
   "anchor": "  \"materials\": {\n",
   "after": "  \"materials\": {\n    \"metal_painted\": \"metal_painted_neutral\",\n    \"metal_bare\": \"metal_bare_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/casino.json",
   "anchor": "  \"materials\": {\n",
   "after": "  \"materials\": {\n    \"metal_painted\": \"metal_painted_neutral\",\n    \"metal_bare\": \"metal_bare_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/delco.json",
   "anchor": " \"materials\": {\n",
   "after": " \"materials\": {\n  \"metal_painted\": \"metal_painted_neutral\",\n  \"metal_bare\": \"metal_bare_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/rockay.json",
   "anchor": " \"materials\": {\n",
   "after": " \"materials\": {\n  \"metal_painted\": \"metal_painted_neutral\",\n  \"metal_bare\": \"metal_bare_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/rockay_civic.json",
   "anchor": " \"materials\": {\n",
   "after": " \"materials\": {\n  \"metal_painted\": \"metal_painted_neutral\",\n  \"metal_bare\": \"metal_bare_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/rockay_retail.json",
   "anchor": " \"materials\": {\n",
   "after": " \"materials\": {\n  \"metal_painted\": \"metal_painted_neutral\",\n  \"metal_bare\": \"metal_bare_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/rockay_service.json",
   "anchor": "  \"materials\": {\n",
   "after": "  \"materials\": {\n    \"metal_painted\": \"metal_painted_neutral\",\n    \"metal_bare\": \"metal_bare_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/stadium.json",
   "anchor": "  \"materials\": {\n",
   "after": "  \"materials\": {\n    \"metal_painted\": \"metal_painted_neutral\",\n    \"metal_bare\": \"metal_bare_neutral\",\n"
  },
  {
   "path": "pixelcoat/profiles/themes/street.json",
   "anchor": "  \"materials\": {\n",
   "after": "  \"materials\": {\n    \"metal_painted\": \"metal_painted_neutral\",\n    \"metal_bare\": \"metal_bare_neutral\",\n"
  },
  {
   "path": "pixelcoat/pixelcoat/version.py",
   "anchor": "__version__ = \"0.14.0\"\n",
   "after": "__version__ = \"0.15.0\"\n"
  }
 ],
 "whole": {
  "pixelcoat/VERSION": "Pixelcoat 0.15.0\n",
  "zoo/VERSION": "Zoo 0.43.0\n"
 },
 "new": {
  "pixelcoat/profiles/materials/metal_painted_neutral.json": "{\n  \"id\": \"metal_painted_neutral\",\n  \"kind\": \"metal_painted\",\n  \"tintable\": true,\n  \"base_colors\": [\n    \"#ececea\",\n    \"#f3f2f0\"\n  ],\n  \"meters_per_tile\": 1.2,\n  \"bands\": {\n    \"macro\": 0.14,\n    \"meso\": 0.18,\n    \"micro\": 0.22\n  },\n  \"macro\": {\n    \"generator\": \"fbm\",\n    \"cells\": 3,\n    \"octaves\": 2\n  },\n  \"meso\": {\n    \"generator\": \"fbm\",\n    \"cells\": 26,\n    \"octaves\": 3\n  },\n  \"micro\": {\n    \"generator\": \"fbm\",\n    \"cells\": 160,\n    \"octaves\": 2\n  },\n  \"detail_strength\": 0.045,\n  \"albedo_pattern\": 0.5,\n  \"posterize\": 12,\n  \"roughness\": {\n    \"base\": 0.42,\n    \"variation\": 0.07\n  },\n  \"height_strength\": 0.1,\n  \"emit\": {\n    \"roughness\": true,\n    \"normal\": false\n  }\n}\n",
  "pixelcoat/profiles/materials/metal_bare_neutral.json": "{\n  \"id\": \"metal_bare_neutral\",\n  \"kind\": \"metal_bare\",\n  \"tintable\": true,\n  \"base_colors\": [\n    \"#eeedea\",\n    \"#f5f4f1\"\n  ],\n  \"meters_per_tile\": 1.0,\n  \"bands\": {\n    \"macro\": 0.1,\n    \"meso\": 0.3,\n    \"micro\": 0.24\n  },\n  \"macro\": {\n    \"generator\": \"fbm\",\n    \"cells\": 3,\n    \"octaves\": 2\n  },\n  \"meso\": {\n    \"generator\": \"directional_grain\",\n    \"cells_along\": 2,\n    \"cells_across\": 96,\n    \"axis\": \"x\"\n  },\n  \"micro\": {\n    \"generator\": \"hash_grain\"\n  },\n  \"detail_strength\": 0.07,\n  \"albedo_pattern\": 0.6,\n  \"posterize\": 14,\n  \"roughness\": {\n    \"base\": 0.28,\n    \"variation\": 0.11\n  },\n  \"height_strength\": 0.08,\n  \"emit\": {\n    \"roughness\": true,\n    \"normal\": false\n  }\n}\n"
 },
 "changelogs": {
  "pixelcoat/CHANGELOG.md": "## [0.15.0] - prop metal splits from architectural metal\n\n`metal` was doing two jobs. A rusted storefront facade and a corrugated wall\nbelong to the BUILDING, and the theme should own their look. A vending machine\nand a car body belong to the OBJECT, and the genome should own their colour.\nOne kind cannot serve both: making it tintable would repaint the architecture\nby its greybox colour, and leaving it fixed is what put a galvanized spangle on\na red vending machine.\n\nMeasured before splitting anything: of the 42 Zoo species that can wear\n`metal`, only 12 declare a style colour with chroma >= 0.10. The other 30 --\nincluding all ten architectural species -- are already near-grey and correctly\nkeep `metal`. This is a 12-species change, not a 42-species one.\n\n### Added\n- `metal_painted_neutral` (tintable) -- semi-gloss enamel over sheet steel.\n  Fine orange-peel at meso, tight grain at micro, roughness 0.42.\n- `metal_bare_neutral` (tintable) -- brushed stock. Directional grain along x,\n  hash grain at micro, roughness 0.28.\n\nTwo profiles and not one because Zoo looks up METALLIC per kind: paint is a\ndielectric and bare metal is a conductor. A single shared profile would have\nmade every painted prop render with a metallic sheen.\n\n### Changed\n- All nine themes map `metal_painted` and `metal_bare`.\n\n### Note\nNothing renders differently. No Zoo genome names either kind yet; that is the\nnext change and it is deliberately separate so each batch of species can be\nlooked at before the next one starts.\n\n",
  "zoo/CHANGELOG.md": "## [0.43.0] - two new kinds, and the measurement that scoped them\n\nThe skinned vending-machine render made the case: `plastic` trim took its own\nred correctly, and the BODY came out galvanized grey, because the body is\n`metal` and `metal` is theme-owned. Every ATM, HVAC unit, filing cabinet and\ncar body had the same defect -- 42 species sharing one grey.\n\nBefore splitting, the size of the problem was measured rather than assumed.\nFor each species that can wear `metal`, the chroma of every style colour whose\nmaterial is `metal`:\n\n    chroma >= 0.25   5 species   simple_car 0.64, gold_bar 0.61, helmet 0.57,\n                                 vending_machine 0.48, queue_stanchion 0.32\n    0.10 - 0.25      7 species   chair, filing_cabinet, water_tank,\n                                 flat_top_grill, shelving, atm, vault_door\n    < 0.10          30 species   streetlight 0.038, hvac_unit 0.058, ...\n\nThirty species need no change at all: their metal colours are already grey, so\nthe theme's metal is a fair answer. Ten of those thirty are architecture --\nwall, wallCorner, wallEnd, window, doorway, breach, prop, dress_cover, ceiling,\nroof -- and MUST stay theme-owned. That is the measured reason the kind could\nnot simply be made tintable.\n\n### Added\n- `metal_painted` and `metal_bare` in `skins.KNOWN_KINDS`, `ROUGHNESS`\n  (0.45 / 0.28) and `METALLIC` (0.0 / 0.90).\n\nTwo kinds and not one because METALLIC is a per-kind lookup. Paint is a\ndielectric; bare metal is a conductor. Folding them together would have put a\nmetallic sheen on matte paint, or killed the specular on a gold bar.\n\n`metal_painted` is written as an explicit 0.0 rather than left to the `.get()`\ndefault, because that number is the entire reason the two kinds are separate\nand a value that load-bearing should not be inferred from an omission.\n\n### Note\nNothing renders differently. No genome names either kind yet.\n\nWATCH OUT when the genomes are edited. `dna.resolve_plan` does:\n\n    if material not in genome[\"materials\"][\"options\"]:\n        material = genome[\"materials\"][\"default\"]\n\nsilently. A style that says `\"material\": \"metal_painted\"` is DISCARDED unless\nthe kind is also added to that species' `materials.options`. Every species edit\nis two places, and the failure mode is a render that looks unchanged.\n\n"
 },
 "pre_sha": {
  "zoo/zoo_keeper/core/skins.py": "c9cbc22e6e89d57ce479764e05616188c0ac4f54f7c3f994e1b5be9555b7e83e",
  "zoo/zoo_keeper/bpylayer/materials.py": "aefd21be07f232362465d3a6fc1377593ca39bcd22105cd30e8f084c6afcd8db",
  "pixelcoat/profiles/themes/bank.json": "83cd7d46962c67aeace3769862fe55aac469cf9658865d0339a9e5509e9c5255",
  "pixelcoat/profiles/themes/casino.json": "410487e14b008fefe57c30407a82ee18920bace1037904191f62f2476d6398a5",
  "pixelcoat/profiles/themes/delco.json": "68f5c17286a24f4fa2ba0b6792250f00ad9e0713914c0f2fcead46f2193ab55b",
  "pixelcoat/profiles/themes/rockay.json": "af3959d5968df33a48bce729317f7be60e98501e311989951eac65355b628391",
  "pixelcoat/profiles/themes/rockay_civic.json": "11c6a5f32bfbfcbc563d1c8bdfa044c596f27c7a134a438f30a29a448c5310d4",
  "pixelcoat/profiles/themes/rockay_retail.json": "28aec958f5748111c2175ae9a0666188b13a91ba3d6b16398cf54cc81c162ac9",
  "pixelcoat/profiles/themes/rockay_service.json": "31daa33d068da78f38b69105a7a40bf296ff3abf0c56ddf8f0ff0bdf0b542150",
  "pixelcoat/profiles/themes/stadium.json": "6e0ce115da31aedc2f377509d04044dc07956dc1505400cae44d418e7f160978",
  "pixelcoat/profiles/themes/street.json": "501b877ad8286a309ff56def8fffd9d781e1ab8b48eb14546a9e707d868c8442",
  "pixelcoat/pixelcoat/version.py": "969c391637e9cf97a9f7755d27750ef166da232b9ee80a8560b0b2e4e17c67ea",
  "pixelcoat/VERSION": "2d2b25b25365fa2a727f5a02aea2e7b2aa4dbd2b983a525521f2b6640b106ca9",
  "zoo/VERSION": "067b99a2ad8a54bce3a3d0dfe47aef14ad4dc2eec23a159dc7a90580e256067f",
  "pixelcoat/CHANGELOG.md": "f9155b765b6a040b5dffe9431510ebaee94ad34ec0fd809362d539a1636165d7",
  "zoo/CHANGELOG.md": "5623960c91640cb756ab83aa7978a2f29965887b78116e89f784072df309d928"
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
    import ast as _ast
    import glob as _glob
    import json as _json
    import tempfile as _tf

    NEW = ("metal_painted", "metal_bare")

    from zoo_keeper.core import skins
    from pixelcoat.core import material_grammar as mg

    # ---- 1. the vocabulary agrees with itself -----------------------------
    #      This mirrors tests/test_kind_vocabulary.py, which is the test that
    #      would otherwise fail the whole suite. Catching it here gives a
    #      readable message instead of a red run.
    msrc = os.path.join(ROOT, "zoo", "zoo_keeper", "bpylayer", "materials.py")
    text = open(msrc, encoding="utf-8").read()
    tree = _ast.parse(text)

    def _dict_keys(name):
        for node in tree.body:
            if isinstance(node, _ast.Assign) and \
               any(getattr(t, "id", None) == name for t in node.targets):
                if isinstance(node.value, _ast.Dict):
                    return [k.value for k in node.value.keys]
        return None

    rough = _dict_keys("ROUGHNESS")
    metal = _dict_keys("METALLIC")
    if rough is None:
        fails.append("ROUGHNESS is no longer a dict literal -- the vocabulary "
                     "test parses it with ast and would go blind")
    if metal is None:
        fails.append("METALLIC is no longer a dict literal")
    known = set(skins.KNOWN_KINDS)
    if rough is not None and known != set(rough):
        fails.append("KNOWN_KINDS and ROUGHNESS disagree:\n"
                     "      KNOWN only: %s\n      ROUGHNESS only: %s"
                     % (sorted(known - set(rough)), sorted(set(rough) - known)))
    if metal is not None and not set(metal) <= known:
        fails.append("METALLIC names kinds nothing else knows: %s"
                     % sorted(set(metal) - known))
    if len(skins.KNOWN_KINDS) != len(set(skins.KNOWN_KINDS)):
        fails.append("KNOWN_KINDS has duplicates")
    for k in NEW:
        if k not in known:
            fails.append("%r is not in KNOWN_KINDS" % k)
        if rough is not None and k not in rough:
            fails.append("%r has no ROUGHNESS -- it would take the 0.6 default"
                         % k)

    # ---- 2. THE NUMBER THE SPLIT EXISTS FOR --------------------------------
    #      If these collapse, there was no reason to make two kinds.
    ns = {}
    for node in tree.body:
        if isinstance(node, _ast.Assign) and \
           any(getattr(t, "id", None) == "METALLIC" for t in node.targets):
            mod = _ast.Module(body=[node], type_ignores=[])
            _ast.fix_missing_locations(mod)
            exec(compile(mod, msrc, "exec"), ns)
    mt = ns.get("METALLIC", {})
    if mt.get("metal_painted") != 0.0:
        fails.append("METALLIC['metal_painted'] is %r, want 0.0 -- paint is a "
                     "dielectric and this is the whole reason for two kinds"
                     % mt.get("metal_painted"))
    if not mt.get("metal_bare", 0) > 0.5:
        fails.append("METALLIC['metal_bare'] is %r, want a conductor value"
                     % mt.get("metal_bare"))
    if mt.get("metal_painted") == mt.get("metal_bare"):
        fails.append("metal_painted and metal_bare have the SAME metallic "
                     "value -- the split buys nothing")

    # ---- 3. profiles exist, are the right kind, are tintable, are paintable -
    prof = os.path.join(ROOT, "pixelcoat", "profiles")
    for kind, pid in (("metal_painted", "metal_painted_neutral"),
                      ("metal_bare", "metal_bare_neutral")):
        p = os.path.join(prof, "materials", pid + ".json")
        if not os.path.isfile(p):
            fails.append("%s.json is missing" % pid)
            continue
        g = _json.load(open(p, encoding="utf-8"))
        if g.get("kind") != kind:
            fails.append("%s is kind %r, want %r -- build_theme_library would "
                         "raise" % (pid, g.get("kind"), kind))
        if g.get("tintable") is not True:
            fails.append("%s is not tintable; mapping it would paint every "
                         "prop of that kind one colour" % pid)
        for hexc in g.get("base_colors", []):
            r, gg, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
            if max(r, gg, b) - min(r, gg, b) > 12:
                fails.append("%s base colour %s is not achromatic (spread %d)"
                             % (pid, hexc, max(r, gg, b) - min(r, gg, b)))
            if min(r, gg, b) < 200:
                fails.append("%s base colour %s is too dark to tint (min %d)"
                             % (pid, hexc, min(r, gg, b)))

    # ---- 4. every theme maps both, and `metal` was NOT disturbed -----------
    themes = sorted(_glob.glob(os.path.join(prof, "themes", "*.json")))
    if len(themes) != 9:
        fails.append("expected 9 themes, found %d" % len(themes))
    for t in themes:
        d = _json.load(open(t, encoding="utf-8"))
        mats = d.get("materials", {})
        for kind, pid in (("metal_painted", "metal_painted_neutral"),
                          ("metal_bare", "metal_bare_neutral")):
            if mats.get(kind) != pid:
                fails.append("theme %r maps %s -> %r, want %r"
                             % (d.get("theme"), kind, mats.get(kind), pid))
        if "metal" not in mats:
            fails.append("theme %r LOST its plain `metal` mapping -- the "
                         "architecture would stop resolving" % d.get("theme"))

    # ---- 5. END TO END: build a library, resolve it back through Zoo -------
    with _tf.TemporaryDirectory() as td:
        mg.build_theme_library(os.path.join(prof, "themes", "delco.json"),
                               os.path.join(prof, "materials"), td, size=32)
        for kind, want_tint in (("metal_painted", True), ("metal_bare", True),
                                ("metal", False), ("brick", False)):
            pack = skins.find_pack(td, kind, "delco")
            if pack is None:
                fails.append("Zoo cannot resolve %r from the rebuilt library"
                             % kind)
            elif pack.get("tintable") is not want_tint:
                fails.append("%r resolves tintable=%r, want %r%s"
                             % (kind, pack.get("tintable"), want_tint,
                                "  (architecture would be repainted!)"
                                if kind in ("metal", "brick") else ""))

    # ---- 6. no genome names the new kinds yet (this patch is inert) --------
    sp = _glob.glob(os.path.join(ROOT, "zoo", "zoo_keeper", "genome",
                                 "species", "*.json"))
    early = []
    for p in sp:
        d = _json.load(open(p, encoding="utf-8"))
        m = d.get("materials", {})
        seen = set([m.get("default")]) | set(m.get("options", []))
        for s in d.get("styles", {}).values():
            if isinstance(s, dict) and "material" in s:
                seen.add(s["material"])
        if seen & set(NEW):
            early.append(d.get("species"))
    if early:
        print("  NOTE: genomes already naming the new kinds: %s" % sorted(early))

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("SELFTEST OK -- 6 groups: vocabulary agreement, the METALLIC values "
          "the split exists for, both profiles achromatic+tintable, all 9 "
          "themes (metal preserved), and a real library resolved back through "
          "Zoo with metal/brick still NOT tintable")
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
