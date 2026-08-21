#!/usr/bin/env python
"""patch_loud_collisions.py -- zoo 0.45.0 -> 0.46.0, deli_counter 0.90.0 -> 0.91.0

WHAT
  Makes two long-silent conditions loud. Changes NO geometry, NO filenames,
  NO acoustics -- it only reports what was already happening.

  * zoo `plan_kit` now returns `stem_collisions` and prints one line per
    collision. Two buckets sharing one filename previously produced no
    output at all. 19 stems across 17 buildings, all floor/ceiling.

  * deli_counter `_resolve_material` has always set `"unresolved": True` for
    a material the spec does not declare. NOTHING READ IT. Now the build
    prints them, with the consequence stated: an undeclared material
    inherits default_material's acoustics AND its skin style, and style
    picks the Pixelcoat pack and goes in the filename.

WHAT THIS DELIBERATELY DOES NOT DO
  It does not add `_m<material>` to the stem. That would separate 1,677
  filenames and leave carpet still wearing concrete's skin, because the skin
  follows `style`, not the stem. The real fix is adding carpet/tile/
  ceiling_tile to presets._PALETTE and migrating 139 specs -- held back
  because the palette's `acoustic` names are consumed by gool, nothing
  validates them, and it changes how every interior looks.

USAGE   (run from anywhere; paths are absolute)
  python patch_loud_collisions.py --check
  python patch_loud_collisions.py
  python patch_loud_collisions.py --selftest
  python patch_loud_collisions.py --revert

CONTRACT
  * refuses on drift (sha256 per target)
  * all-or-nothing across both repos; anchors must occur EXACTLY ONCE
  * .pre_loud sidecars for --revert
  * __pycache__ purged after any write
"""
import argparse, hashlib, io, json, os, shutil, sys, tempfile

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
TAG = "loud"
M = json.loads(r"""{
 "tool": "multi",
 "from_version": "zoo 0.45.0 / deli_counter 0.90.0",
 "to_version": "zoo 0.46.0 / deli_counter 0.91.0",
 "tag": "loud",
 "edits": [
  {
   "path": "zoo/zoo_keeper/core/kit.py",
   "anchor": "    return {\n        \"building_id\": manifest.get(\"building_id\"),\n",
   "after": "    # STEM COLLISION -- two modules, one filename.\n    #\n    # The bucket key above carries slot_material; `module_stem` does not. So\n    # two buckets can be two DISTINCT modules with ONE stem: they build\n    # differently (dna.resolve_module_plan reads module[\"material\"] as an\n    # override) and one overwrites the other on disk. Deli Counter's resolver\n    # then hands both zones whichever file won.\n    #\n    # Measured 2026-08-21 over 280 manifests: 19 stems across 17 buildings,\n    # every one floor or ceiling.\n    #\n    # THE ROOT CAUSE IS UPSTREAM AND THIS DOES NOT FIX IT. `carpet`, `tile`\n    # and `ceiling_tile` are absent from every spec's `materials` list, so\n    # Deli Counter's skin_style.style_for falls through to `default_material`\n    # and hands all of them one style -- 410 of 574 (building, plate material)\n    # pairs are style 1. Identical style means identical Pixelcoat pack AND\n    # identical stem. Adding material to the stem would separate the\n    # filenames and leave carpet still wearing concrete's skin.\n    #\n    # What this does is stop the collision being SILENT. It was producing two\n    # buckets and one name and saying nothing at all.\n    by_stem: dict = {}\n    for _m in modules:\n        by_stem.setdefault(_m[\"stem\"], []).append(_m)\n    stem_collisions = [\n        {\"stem\": _s,\n         \"type\": _g[0][\"type\"],\n         \"materials\": sorted({str(_x.get(\"material\")) for _x in _g}),\n         \"styles\": sorted({_x.get(\"style\") for _x in _g}),\n         \"dims\": [_x.get(\"dims\") for _x in _g],\n         \"count\": len(_g)}\n        for _s, _g in sorted(by_stem.items()) if len(_g) > 1\n    ]\n    for _c in stem_collisions:\n        print(\"[zoo] STEM COLLISION %s: %d modules share this filename, \"\n              \"materials=%s style=%s -- one will overwrite the other\"\n              % (_c[\"stem\"], _c[\"count\"], \",\".join(_c[\"materials\"]),\n                 \",\".join(str(_v) for _v in _c[\"styles\"])))\n\n    return {\n        \"building_id\": manifest.get(\"building_id\"),\n        \"stem_collisions\": stem_collisions,\n"
  },
  {
   "path": "deli_counter/deli_counter.py",
   "anchor": "        m = self._material_index.get(mid)\n        if m is None:\n            return {\"id\": mid, \"acoustic\": None, \"absorption\": None,\n                    \"damping\": None, \"unresolved\": True}\n",
   "after": "        m = self._material_index.get(mid)\n        if m is None:\n            # SILENT NO LONGER. This branch has always known: a material a\n            # slot names but the spec does not DECLARE lands here and is\n            # marked unresolved. Nothing read that flag, so the condition\n            # never surfaced -- and it is not rare. Measured 2026-08-21 over\n            # 142 specs: `ceiling_tile` and `tile` are missing from ALL of\n            # them and `carpet` from 137.\n            #\n            # The cost is not only acoustic. skin_style.style_for falls back\n            # the same way, so an undeclared material inherits\n            # default_material's STYLE -- and style is what picks the\n            # Pixelcoat pack and what goes in the module filename. 410 of 574\n            # (building, plate material) pairs resolve to style 1. A carpet\n            # floor and a concrete floor in one building have been getting\n            # the same skin, the same acoustics and the same filename.\n            self._unresolved_materials = getattr(\n                self, \"_unresolved_materials\", {})\n            self._unresolved_materials[mid] = \\\n                self._unresolved_materials.get(mid, 0) + 1\n            return {\"id\": mid, \"acoustic\": None, \"absorption\": None,\n                    \"damping\": None, \"unresolved\": True}\n"
  },
  {
   "path": "deli_counter/deli_counter.py",
   "anchor": "        print(f\"[deli_counter] built '{self.s.name}' seed={self.s.seed}: \"\n              f\"{len(self.VISUAL.objects)} visual, \"\n              f\"{len(self.COLLISION.objects)} collision, \"\n              f\"{len(self.MARKERS.objects)} markers\")\n",
   "after": "        print(f\"[deli_counter] built '{self.s.name}' seed={self.s.seed}: \"\n              f\"{len(self.VISUAL.objects)} visual, \"\n              f\"{len(self.COLLISION.objects)} collision, \"\n              f\"{len(self.MARKERS.objects)} markers\")\n        unresolved = getattr(self, \"_unresolved_materials\", None)\n        if unresolved:\n            listing = \", \".join(\"%s x%d\" % (k, v)\n                                for k, v in sorted(unresolved.items()))\n            print(f\"[deli_counter] UNRESOLVED MATERIALS in '{self.s.name}': \"\n                  f\"{listing}\")\n            print(f\"[deli_counter]   not declared in spec.materials, so each \"\n                  f\"inherits default_material \"\n                  f\"'{self.s.default_material}' -- its acoustics, its skin \"\n                  f\"style, and therefore its module filename\")\n"
  }
 ],
 "new": {},
 "whole": {
  "zoo/VERSION": "Zoo 0.46.0\n",
  "deli_counter/VERSION": "Deli Counter 0.91.0\n"
 },
 "changelogs": {
  "zoo/CHANGELOG.md": "## [0.46.0] - two modules with one filename now say so\n\n`plan_kit` builds its bucket key from (type, width, state, species, glaze,\nstyle, MATERIAL, dims, voids, openings). `module_stem` builds the filename\nfrom everything in that list EXCEPT material. So two buckets can be two\ndistinct modules with one stem: they build differently, because\n`dna.resolve_module_plan` reads `module[\"material\"]` as an override, and one\noverwrites the other on disk.\n\nMeasured over 280 manifests: 19 stems across 17 buildings, every one floor or\nceiling.\n\n### Added\n- `plan_kit` returns `stem_collisions` and prints one line per collision.\n\n### THIS DOES NOT FIX THE COLLISION, and adding material to the stem would have been the wrong fix\nSix hypotheses were tested before this landed. The root cause is upstream in\nDeli Counter: `carpet`, `tile` and `ceiling_tile` are absent from every\nspec's `materials` list, so `skin_style.style_for` falls through to\n`default_material` and hands all of them one style. 410 of 574\n(building, plate material) pairs resolve to style 1.\n\nStyle is what selects the Pixelcoat pack AND what goes in the filename. So\n`_m<material>` in the stem would have separated 1,677 filenames while leaving\na carpet floor still wearing concrete's skin -- fixing the visible 3% and\nentrenching the other 97%. What was wrong was never the naming law.\n\nRuled out along the way, each by reading rather than reasoning: manifests\npredating per-slot style (all 1,677 plate slots carry one); `skin_style`\nnever written (it exists); `style_for` never called (floors.py:231, :240,\nroofs.py:81); the wiring being incomplete (it is complete).\n\n",
  "deli_counter/CHANGELOG.md": "## [0.91.0] - the unresolved flag gets a reader\n\n`_resolve_material` has always marked a material the spec does not declare\n`\"unresolved\": True`. Nothing ever read that flag. It was set in one place\nand consumed in none, so the condition it detects has been invisible for as\nlong as it has existed -- and it is not an edge case.\n\nMeasured over 142 specs: `ceiling_tile` and `tile` are missing from ALL of\nthem, `carpet` from 137.\n\n### Added\n- The build now prints unresolved materials, with the consequence spelled\n  out rather than left to be inferred.\n\n### What that condition actually costs\nAn undeclared material falls back to `default_material` -- and the fallback\nis not only acoustic. `skin_style.style_for` falls back the same way, so the\nmaterial inherits the default's STYLE. Style selects the Pixelcoat pack and\ngoes into the module filename. 410 of 574 (building, plate material) pairs\nresolve to style 1.\n\nSo a carpet floor, a tile floor and a concrete floor in one building have\nbeen getting the same acoustics, the same skin and, when their dimensions\nmatch, the same file. That last one surfaced first, as 19 stem collisions in\nZoo, and looked like a naming-law problem for most of a session.\n\n### Not fixed here, deliberately\nAdding `carpet`, `tile` and `ceiling_tile` to `presets._PALETTE` and\nmigrating the 139 existing specs is the actual fix. It is held back because\nthe palette's `acoustic` names (\"Concrete\", \"Drywall\", \"Glass\", \"Metal\",\n\"Wood\") are consumed by gool, nothing validates them, and inventing\n\"Carpet\" would fail silently downstream -- the same class of defect this\nentry exists to end. It also changes how every interior in the project\nlooks, which deserves a session where it can be looked at.\n\n"
 },
 "pre_sha": {
  "zoo/zoo_keeper/core/kit.py": "e3699fa029748132b4e9749876e15a3d4110392fea63a3ffec6ed9494a8c5c86",
  "deli_counter/deli_counter.py": "4de69a871d9a11b20ff5ebc92f1b183ca0f3e6e88aa3f7ec03796a1906451706",
  "zoo/VERSION": "0ba85a304d12b119174101bf4fbc9d2532caf84246985dff6ffd6e2928137293",
  "deli_counter/VERSION": "028d5b04bbd917e343d87b67ba729c8a4f46b7a6a8979f7c5b4f531b48f963fd",
  "zoo/CHANGELOG.md": "e37ec9c78c20aecb6724435de03636388532912b88ee16cbeb123fc20dd8213d",
  "deli_counter/CHANGELOG.md": "6ba4db474377389d8650ffbf16089b1466cd5ad15d3095c42a5a25bb879bf0a9"
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

    # NOT every CHANGELOG in this factory carries a "# Changelog" title.
    # zoo, pixelcoat and the factory do; deli_counter opens straight at its
    # newest "## [x.y.z]" heading. Hardcoding one shape refused a repo that
    # was perfectly well formed, so the header is DETECTED per file and the
    # entry goes in above the newest release either way.
    head = "# Changelog\n\n"
    for cl_rel, entry in M["changelogs"].items():
        cl = _read(_abs(cl_rel))
        if cl.startswith(head):
            out[cl_rel] = head + entry + cl[len(head):]
        elif cl.lstrip().startswith("## "):
            out[cl_rel] = entry + cl
        else:
            print("REFUSED -- %s starts with neither a '# Changelog' title "
                  "nor a '## ' release heading; refusing to guess where an "
                  "entry belongs" % cl_rel)
            return 1

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
    import io as _io
    import json as _json
    import contextlib as _ctx

    from zoo_keeper.core import kit

    # ---- 1. a manifest with TWO plate slots, same dims, different material.
    #         This is the exact shape of the 19 real collisions.
    man = {
        "building_id": "selftest_collide",
        "slots": [
            {"slot_id": "floor_a", "role": "floor", "style": 1,
             "material": "concrete",
             "fit": {"dims": [4.0, 3.0, 0.02], "pivot": "center"}},
            {"slot_id": "floor_b", "role": "floor", "style": 1,
             "material": "tile",
             "fit": {"dims": [4.0, 3.0, 0.02], "pivot": "center"}},
        ],
    }
    buf = _io.StringIO()
    with _ctx.redirect_stdout(buf):
        plan = kit.plan_kit(man, theme="delco", style=1)
    out = buf.getvalue()

    if "stem_collisions" not in plan:
        fails.append("plan_kit does not return stem_collisions")
    else:
        cols = plan["stem_collisions"]
        if len(cols) != 1:
            fails.append("expected exactly 1 stem collision, got %d (%s)"
                         % (len(cols), [c.get("stem") for c in cols]))
        else:
            c = cols[0]
            if sorted(c["materials"]) != ["concrete", "tile"]:
                fails.append("collision materials are %s, want "
                             "['concrete','tile']" % c["materials"])
            if c["count"] != 2:
                fails.append("collision count is %r, want 2" % c["count"])
    if "STEM COLLISION" not in out:
        fails.append("plan_kit printed nothing -- the whole point is that it "
                     "is no longer silent (stdout was %r)" % out[:120])

    # ---- 2. THE CONTROL. Same two slots, DIFFERENT dims -> no collision.
    #         Without this, check 1 passes for a plan_kit that flags
    #         everything.
    man2 = _json.loads(_json.dumps(man))
    man2["slots"][1]["fit"]["dims"] = [5.0, 3.0, 0.02]
    buf2 = _io.StringIO()
    with _ctx.redirect_stdout(buf2):
        plan2 = kit.plan_kit(man2, theme="delco", style=1)
    if plan2.get("stem_collisions"):
        fails.append("two DIFFERENT-sized plates reported as colliding: %s"
                     % plan2["stem_collisions"])
    if "STEM COLLISION" in buf2.getvalue():
        fails.append("printed a collision for two distinct stems")

    # ---- 3. AND the other control: different material, different STYLE.
    #         This is what the upstream fix will produce, and it must stop
    #         being reported the moment the specs are corrected.
    man3 = _json.loads(_json.dumps(man))
    man3["slots"][1]["style"] = 2
    buf3 = _io.StringIO()
    with _ctx.redirect_stdout(buf3):
        plan3 = kit.plan_kit(man3, theme="delco", style=1)
    if plan3.get("stem_collisions"):
        fails.append("distinct styles still reported as colliding -- the "
                     "upstream fix would not clear this report")

    # ---- 4. deli_counter: the flag now has a reader ------------------------
    dc = os.path.join(ROOT, "deli_counter", "deli_counter.py")
    src = open(dc, encoding="utf-8").read()
    if "_unresolved_materials" not in src:
        fails.append("deli_counter.py never records unresolved materials")
    if src.count("_unresolved_materials") < 3:
        fails.append("_unresolved_materials is written but never read back "
                     "(%d mentions) -- that is the defect this patch fixes"
                     % src.count("_unresolved_materials"))
    if "UNRESOLVED MATERIALS" not in src:
        fails.append("nothing prints the unresolved materials")

    # ---- 5. the claim in the changelog is checkable ------------------------
    cl = open(os.path.join(ROOT, "zoo", "CHANGELOG.md"),
              encoding="utf-8").read()
    if "410 of 574" not in cl:
        fails.append("the zoo changelog no longer carries the measurement")

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("SELFTEST OK -- a real collision is reported AND printed, two "
          "controls (different dims, different styles) are NOT reported, and "
          "the unresolved flag now has a reader")
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
