#!/usr/bin/env python3
"""patch_thread3_close.py -- the test that catches an inert genome, plus versions.

  --check     preconditions only, writes nothing (also reports file shapes)
  (no flag)   apply, all or nothing
  --revert    restore from .pre_t3 sidecars, delete created files
  --selftest  verify versions agree and the new test actually catches the defect

Adds zoo/tests/test_recipe_reads_its_genome.py, which fails when a recipe that
builds materials never reads a "material" key -- the flat_top_grill defect. One
exemption (cheesesteak) is named with its reason, and the test ALSO fails if an
exempt recipe becomes healthy, so the exemption cannot rot unnoticed.
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIDE = ".pre_t3"
TODAY = "2026-08-21"

ZOO = os.path.join(ROOT, "zoo")
PC = os.path.join(ROOT, "pixelcoat")

ZOO_OLD, ZOO_NEW = "0.46.0", "0.47.0"
PC_OLD, PC_NEW = "0.15.0", "0.16.0"

MODE = "apply"
for a in sys.argv[1:]:
    if a in ("--check", "--revert", "--selftest"):
        MODE = a[2:]
    else:
        print("unknown argument %r" % a)
        sys.exit(2)


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def read(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    return raw, raw.decode("utf-8").replace("\r\n", "\n"), eol


def write(path, text, eol):
    with open(path, "wb") as fh:
        fh.write(text.replace("\n", eol).encode("utf-8"))


TEST_PATH = os.path.join(ZOO, "tests", "test_recipe_reads_its_genome.py")
TEST_SRC = '''"""A recipe that builds materials must read its genome's material.

THE DEFECT THIS CATCHES: flat_top_grill passed the literal "metal" to every
make_material call it made. Its genome had a material field. Editing that field
changed nothing -- silently. Nothing failed, nothing warned, and the genome was
decorative for as long as nobody looked.

The rule is deliberately module-level rather than call-level. A call-level rule
("plan[\\'material\\'] must appear in the arguments") reports flat_top_grill as
broken even after it was fixed, because the fix assigns kind = plan["material"]
and passes kind. Indirection through a local is normal and correct.

Sub-part literals are NOT a defect: a bottle cap is plastic, a boot sole is
rubber, the paper boat under the fries is paper. Those parts do not vary with
the body material and hardcoding them is right. This test says nothing about
them; it only requires that the module consult its genome at least once.
"""
import ast
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
RECIPES = os.path.join(os.path.dirname(HERE), "zoo_keeper", "recipes")

# A recipe may appear here only with a reason. The test below ALSO fails if an
# exempt recipe starts reading its genome, so a stale exemption cannot survive.
EXEMPT = {
    "cheesesteak": (
        "composite food prop: bun, crust, meat, cheese and seeds each carry "
        "their own material and there is no single body surface for the genome "
        "to control. Its genome offers exactly one option (paper), so nothing "
        "is rendered wrong today. If a second option is ever added, remove this "
        "exemption and give the wrapper plan['material']."
    ),
}


def _modules():
    out = []
    for fn in sorted(os.listdir(RECIPES)):
        if fn.endswith(".py") and not fn.startswith("_"):
            out.append((fn[:-3], os.path.join(RECIPES, fn)))
    return out


def _analyse(path):
    with open(path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    calls = 0
    reads = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if (getattr(fn, "id", None) or getattr(fn, "attr", None)) == "make_material":
                calls += 1
            if (getattr(fn, "attr", None) == "get" and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == "material"):
                reads += 1
        if (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
                and node.slice.value == "material"):
            reads += 1
    return calls, reads


MODULES = _modules()


def test_the_sweep_is_actually_reading_recipes():
    assert len(MODULES) >= 40, "only %d recipe modules found" % len(MODULES)
    assert sum(_analyse(p)[0] for _, p in MODULES) >= 40, "no make_material calls seen"


@pytest.mark.parametrize("name,path", MODULES, ids=[m[0] for m in MODULES])
def test_recipe_that_builds_materials_reads_its_genome(name, path):
    calls, reads = _analyse(path)
    if calls == 0:
        pytest.skip("builds no materials")
    if name in EXEMPT:
        assert reads == 0, (
            "%s is listed as EXEMPT but now reads its genome %d time(s). "
            "Remove it from EXEMPT -- a stale exemption hides the next "
            "regression." % (name, reads)
        )
        return
    assert reads > 0, (
        "%s calls make_material %d time(s) but never reads a \\'material\\' key, "
        "so its genome cannot affect it. Either pass plan['material'] to the "
        "body material, or add it to EXEMPT with a reason." % (name, calls)
    )


def test_every_exemption_names_a_real_recipe():
    names = {n for n, _ in MODULES}
    unknown = sorted(set(EXEMPT) - names)
    assert not unknown, "EXEMPT names no such recipe: %s" % ", ".join(unknown)
    for name, reason in EXEMPT.items():
        assert len(reason) > 40, "%s exemption needs a real reason" % name
'''

ZOO_ENTRY = """## [%s] - %s

### Added
- `tests/test_recipe_reads_its_genome.py` sweeps every recipe module and fails
  when one builds materials but never reads a `material` key -- the defect that
  made `flat_top_grill`'s genome inert. `cheesesteak` is exempt with a written
  reason, and the test also fails if an exempt recipe starts reading its genome,
  so the exemption cannot go stale unnoticed.

### Notes
- Measured, not assumed: 53 recipe modules, 79 `make_material` calls. Exactly
  one recipe (`cheesesteak`) never consults its genome. Every inert genome
  offers a single option, so nothing renders wrong today; the exposure is that
  a second option would be ignored in silence.
- An earlier pass flagged 7 literals as shadowing their genome. 6 were false
  positives: the body already passed `plan["material"]` and the literal was a
  sub-part with its own fixed colour -- a bottle cap, a safe's trim, the paper
  boat under the fries. Replacing those would have tinted the boat with the fry
  colour. Sub-part literals are correct and this test says nothing about them.
- Ten material kinds became resolvable this release via pixelcoat %s: canvas,
  carbon, dirt, gravel, laminate, leather, paper, rubber, tar, vegetation. All
  ten resolve through `skins.find_pack` in all five built themes.

""" % (ZOO_NEW, TODAY, PC_NEW)

PC_ENTRY = """## [%s] - %s

### Added
- Five material grammars for kinds that had none: `laminate_neutral`,
  `paper_neutral`, `carbon_neutral`, `tar_neutral`, `vegetation_neutral`.
  `laminate` and `paper` are `tintable` with achromatic bases; the other three
  carry their own colour. All five use only `fbm` and `worley_f1`, the two
  generators with worked examples in the existing profiles.

### Changed
- `pebble_gravel` declared `kind: dirt` while `gravel` had no profile at all.
  Retagged to `kind: gravel` on the evidence of its own content -- an aggregate
  block of six stone colours with a gap colour, at roughness 0.9. `dirt` keeps
  `dirt_delco`, which is soil: browns, an undercoat, and a chips block.
- All nine theme profiles now list ten previously unmapped kinds. `canvas`,
  `dirt`, `leather` and `rubber` already had `_delco` profiles that no theme
  referenced, so they had never been built.

### Notes
- The theme profile is the gate: a kind is built only if a theme names a
  profile for it. Libraries went from 68 packs to 118, `MISMATCHES=0`.
- `bank`, `casino`, `delco` and `stadium` are wired but still have no built
  library. `carpet` is themed by 7 of 9 by design -- a service alley and a
  street have no carpet.

""" % (PC_NEW, TODAY)


def bump_version_file(path, old, new, problems, plan):
    if not os.path.isfile(path):
        problems.append("missing %s" % rel(path))
        return
    raw, text, eol = read(path)
    if new in text and old not in text:
        return  # already applied
    n = text.count(old)
    if n != 1:
        problems.append("%s contains %r %d time(s), expected exactly 1 -- got: %r"
                        % (rel(path), old, n, text.strip()[:120]))
        return
    plan.append((path, text.replace(old, new), eol, False))


def prepend_changelog(path, entry, ver, problems, plan):
    if not os.path.isfile(path):
        problems.append("missing %s" % rel(path))
        return
    raw, text, eol = read(path)
    if ("## [%s]" % ver) in text:
        return  # already applied
    m = re.search(r'^## ', text, re.M)
    if not m:
        problems.append("%s has no '## ' heading to insert before" % rel(path))
        return
    new = text[:m.start()] + entry + text[m.start():]
    plan.append((path, new, eol, False))


# ------------------------------------------------------------- revert
if MODE == "revert":
    n = 0
    for base in (ZOO, PC):
        for dp, dns, fns in os.walk(base):
            for fn in fns:
                if fn.endswith(SIDE):
                    side = os.path.join(dp, fn)
                    tgt = side[: -len(SIDE)]
                    shutil.copyfile(side, tgt)
                    os.remove(side)
                    print("  restored %s" % rel(tgt))
                    n += 1
    if os.path.isfile(TEST_PATH):
        os.remove(TEST_PATH)
        print("  removed  %s" % rel(TEST_PATH))
    print("REVERTED -- %d restored" % n)
    sys.exit(0)

# ----------------------------------------------------------- selftest
if MODE == "selftest":
    fails = []
    vp = os.path.join(PC, "pixelcoat", "version.py")
    vf = os.path.join(PC, "VERSION")
    _, vtext, _ = read(vp)
    _, ftext, _ = read(vf)
    # VERSION files carry a name prefix ("Pixelcoat 0.16.0"), so check for the
    # presence of the new version and the ABSENCE of the old one, rather than
    # asserting an exact form. The first version of this check assumed a bare
    # number and failed against correct files.
    if PC_NEW not in vtext:
        fails.append("version.py does not carry %s" % PC_NEW)
    if PC_OLD in vtext:
        fails.append("version.py still carries %s" % PC_OLD)
    if PC_NEW not in ftext:
        fails.append("pixelcoat VERSION does not carry %s -- it says %r"
                     % (PC_NEW, ftext.strip()))
    if PC_OLD in ftext:
        fails.append("pixelcoat VERSION still carries %s" % PC_OLD)
    _, ztext, _ = read(os.path.join(ZOO, "VERSION"))
    if ZOO_NEW not in ztext:
        fails.append("zoo VERSION does not carry %s -- it says %r"
                     % (ZOO_NEW, ztext.strip()))
    if ZOO_OLD in ztext:
        fails.append("zoo VERSION still carries %s" % ZOO_OLD)
    if not os.path.isfile(TEST_PATH):
        fails.append("test file missing")
    if fails:
        print("SELFTEST FAILED")
        for f in fails:
            print("      %s" % f)
        sys.exit(1)

    # FALSIFICATION: the new test must FAIL on a recipe that ignores its genome.
    import ast as _ast
    src = open(TEST_PATH, "r", encoding="utf-8").read()
    # the test module resolves its own path from __file__, so give it one --
    # an empty globals dict makes it raise NameError before it can be reused
    ns = {"__file__": TEST_PATH, "__name__": "_t3_selftest_probe"}
    exec(compile(src, TEST_PATH, "exec"), ns)
    analyse, exempt = ns["_analyse"], ns["EXEMPT"]
    recipes = ns["RECIPES"]
    inert = []
    for fn in sorted(os.listdir(recipes)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        calls, reads = analyse(os.path.join(recipes, fn))
        if calls and reads == 0:
            inert.append(fn[:-3])
    unexempt = [n for n in inert if n not in exempt]
    if unexempt:
        print("SELFTEST FAILED -- inert and not exempt: %s" % ", ".join(unexempt))
        sys.exit(1)
    if sorted(inert) != sorted(exempt):
        print("SELFTEST FAILED -- EXEMPT is %s but the inert set is %s; a stale"
              % (sorted(exempt), sorted(inert)))
        print("                   exemption would hide the next regression")
        sys.exit(1)
    if not inert:
        print("SELFTEST FAILED -- the analyser found NO inert recipe at all, so it")
        print("                   would not have caught flat_top_grill either")
        sys.exit(1)

    print("SELFTEST OK -- pixelcoat %s (version.py and VERSION agree), zoo %s,"
          % (PC_NEW, ZOO_NEW))
    print("               the analyser finds exactly the inert set %s, which is"
          % sorted(inert))
    print("               exactly the exempted set, and it is non-empty -- so the")
    print("               test would still catch a flat_top_grill-shaped defect")
    sys.exit(0)

# ---------------------------------------------------------- preflight
problems = []
plan = []

if os.path.isfile(TEST_PATH):
    _, cur, _ = read(TEST_PATH)
    if cur != TEST_SRC:
        problems.append("%s exists with different content -- refusing" % rel(TEST_PATH))
else:
    plan.append((TEST_PATH, TEST_SRC, "\n", True))

bump_version_file(os.path.join(PC, "pixelcoat", "version.py"), PC_OLD, PC_NEW,
                  problems, plan)
bump_version_file(os.path.join(PC, "VERSION"), PC_OLD, PC_NEW, problems, plan)
bump_version_file(os.path.join(ZOO, "VERSION"), ZOO_OLD, ZOO_NEW, problems, plan)
prepend_changelog(os.path.join(PC, "CHANGELOG.md"), PC_ENTRY, PC_NEW, problems, plan)
prepend_changelog(os.path.join(ZOO, "CHANGELOG.md"), ZOO_ENTRY, ZOO_NEW, problems, plan)

print("PRE-FLIGHT")
for path, _, _, is_new in plan:
    print("  %-7s %s" % ("create" if is_new else "rewrite", rel(path)))

# report the wording of the stale 0.45.0 claim for a follow-up patch
zc = os.path.join(ZOO, "CHANGELOG.md")
if os.path.isfile(zc):
    _, t, _ = read(zc)
    hits = [(i + 1, l) for i, l in enumerate(t.splitlines()) if "53" in l]
    if hits:
        print("")
        print("  FYI -- lines in zoo/CHANGELOG.md mentioning 53 (the 0.45.0 claim")
        print("         that all 53 genomes round-trip; it is 49 of 53):")
        for i, l in hits[:10]:
            print("      %4d  %s" % (i, l.strip()[:110]))

if problems:
    print("")
    print("REFUSING -- %d precondition(s) failed, nothing written:" % len(problems))
    for p in problems:
        print("      %s" % p)
    sys.exit(1)
if not plan:
    print("")
    print("NOTHING TO DO -- already applied")
    sys.exit(0)
if MODE == "check":
    print("")
    print("CHECK OK -- %d file(s) would change" % len(plan))
    sys.exit(0)

for path, text, eol, is_new in plan:
    if not is_new and not os.path.exists(path + SIDE):
        shutil.copyfile(path, path + SIDE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write(path, text, eol)
    print("  wrote %s" % rel(path))

for base in (PC, ZOO):
    for dp, dns, fns in os.walk(base):
        if os.path.basename(dp) == "__pycache__":
            shutil.rmtree(dp, ignore_errors=True)
            dns[:] = []

print("")
print("APPLIED -- %d file(s). Run --selftest, then rebuild the libraries so the" % len(plan))
print("           packs restamp tool_version to %s, then the zoo suite." % PC_NEW)
