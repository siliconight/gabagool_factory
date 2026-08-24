import os, re, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DC = os.path.join(ROOT, "deli_counter")
OLD, NEW, SIDE = "0.91.0", "0.92.0", ".pre_dc092"

ENTRY = """## [0.92.0] - 2026-08-21

### Added
- `navgate_baseline.json` and `test_navgate_population.py`. nav_gate reports
  `markers: 0 checked -- reachability UNJUDGED` for a shell with no marker whose
  type ends in `_spawn`, and the exit code is deliberately unchanged, so that set
  could grow with nothing failing. It is now frozen: a new entrant fails, and a
  shell that gets fixed must be removed or the test says so.

### Corrected
- A prior note recorded "3/135 shells fail, 18 have no spawn marker". Measured
  from the per-shell results: 3 stair failures is right
  (`cbp_town_finale_midbalanced_schemafixed`, `night_pawn`, `primos_pizza`), but
  the unjudged set is 17, not 18, and five of its members were never named --
  `cr_pawn`, `gs_auto_shop`, `gs_facade_rowhome`, `gs_facade_storefront`,
  `lf_art_probe_001_5017`.
- 16 shells report `navigable: null` against 17 unjudged. That is not an
  inconsistency: `night_pawn` also fails the stair gate, and `navigable` is a
  conjunction, so a stair failure forces `False` without marker state mattering.
  Recorded in the baseline as explained rather than filed as a defect.

### Notes
- WHAT THIS DOES NOT CERTIFY: it says nothing about whether these shells SHOULD
  have spawn markers. Twelve of the seventeen carry `RECORDED, NOT EXPLAINED`.
  Only `gs_facade_*` (facade-only, no interior) and `lf_art_probe_001_5017` (a
  probe artifact) are classified, and those from their names alone.
- The per-shell `.navgate.json` files live in `build/`, which is not committed,
  so the sweep SKIPS in a clean checkout. The baseline's own integrity is
  asserted there instead, so a clean checkout never reports a green sweep of
  nothing.

"""

def bump(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    eol = "\r\n" if b"\r\n" in raw else "\n"
    t = raw.decode("utf-8").replace("\r\n", "\n")
    if NEW in t and OLD not in t:
        return None
    if t.count(OLD) != 1:
        return "%s contains %r %d time(s), expected 1" % (path, OLD, t.count(OLD))
    if not os.path.exists(path + SIDE):
        shutil.copyfile(path, path + SIDE)
    with open(path, "wb") as fh:
        fh.write(t.replace(OLD, NEW).replace("\n", eol).encode("utf-8"))
    print("  bumped %s" % os.path.basename(path))
    return None

err = bump(os.path.join(DC, "VERSION"))
if err:
    print("REFUSING -- %s" % err); sys.exit(1)

cp = os.path.join(DC, "CHANGELOG.md")
with open(cp, "rb") as fh:
    raw = fh.read()
eol = "\r\n" if b"\r\n" in raw else "\n"
t = raw.decode("utf-8").replace("\r\n", "\n")
if "## [0.92.0]" in t:
    print("  changelog already has 0.92.0")
else:
    m = re.search(r'^## ', t, re.M)
    if not m:
        print("REFUSING -- no '## ' heading in CHANGELOG.md"); sys.exit(1)
    if not os.path.exists(cp + SIDE):
        shutil.copyfile(cp, cp + SIDE)
    out = t[:m.start()] + ENTRY + t[m.start():]
    with open(cp, "wb") as fh:
        fh.write(out.replace("\n", eol).encode("utf-8"))
    print("  prepended 0.92.0 to CHANGELOG.md")
print("OK")
