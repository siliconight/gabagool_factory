#!/usr/bin/env python3
"""The route pass starves while the opening pass leaves pieces unspent.

MEASURED ON lot_demo_001, candidate seed_5219, level_factory 0.40.0 / lot
0.42.0, five buildings and a real collision reading:

    placed      : 16     (5 opening + 11 route)
    route_open  : 14
    unbreakable : 0
    pinches     : 0

The opening pass closed every marker sightline with FIVE of its twelve pieces.
The route pass exhausted its own budget of eleven and left fourteen stretches
of the crew's walk inside an enemy's reach with nothing between. Seven pieces
sat unspent beside fourteen uncovered stretches of ground the crew has to
cross, because the two passes have separate allowances and no way to pass one
to the other.

`LOT_ROUTE_EXPOSED` reports it in Lot's own voice -- "the crew is inside the
firing envelope while it walks, so the bot takes hits it cannot answer and its
cover-seek has nothing in reach to break for."

WHAT THIS DOES NOT UNDO

The separate budgets exist for a stated, measured reason, in this module's own
comment: "sharing one allowance would let a site with nine long spawn lines
spend everything before reaching the approach, which is exactly how a 74 m walk
ended up with four pieces of cover at the far end of it." That protection runs
ONE WAY -- the opening starving the route -- and it is preserved exactly. The
opening pass still runs first and still gets its full `limit`. Only what it
DECLINES to use flows down. A site with nine long spawn lines spends twelve on
the opening, carries nothing, and behaves as it does today.

WHAT IS NOT CLAIMED

`unbreakable: 0` does NOT mean a spot exists for those fourteen. The loop exits
on `placed_here >= budget` and `route_open` is whatever was still pending, so
those lines were never attempted. Extra budget will attempt them; some may be
refused, and refusals land in `unbreakable` where they can be counted. This
buys attempts, not outcomes, and the re-run is what settles it.

More cover is also not free: pieces can pinch a lane too narrow to walk.
`pinches` is 0 on that candidate today and the selftest checks it does not
become non-zero on the constructed case. The real answer is the mission re-run.

    lot/site_cover.py : 40,013 B  sha256 56C56597C324...  (post crew-first)

USAGE

    python patches\\patch_lot_cover_spare_budget.py --check
    python patches\\patch_lot_cover_spare_budget.py --selftest
    python patches\\patch_lot_cover_spare_budget.py
    python patches\\patch_lot_cover_spare_budget.py --revert
"""
from __future__ import annotations

import hashlib
import math
import shutil
import sys
from pathlib import Path

TAG = "r53sparebudget"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "lot" / "site_cover.py"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)

EXPECT_BYTES = 40013


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def _eol(raw: bytes) -> str:
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    if crlf and lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has mixed line endings "
                         f"({crlf} CRLF, {lf} LF).")
    if not crlf and not lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has no line endings.")
    return "\r\n" if crlf else "\n"


def _n(t: str) -> str:
    return t.replace("\r\n", "\n")


OLD = '''        route_length = sum(math.dist(a, b) for a, b in zip(route, route[1:]))
        budget = max(1, int(math.ceil(route_length / route_metres_per_piece)))
'''

NEW = '''        route_length = sum(math.dist(a, b) for a, b in zip(route, route[1:]))
        # ...plus whatever the opening pass declined to use.
        #
        # The two allowances stay separate in the direction that matters: the
        # opening runs FIRST and gets its full `limit`, so a site with nine
        # long spawn lines still spends everything there and carries nothing,
        # exactly as the comment above requires. What changes is the other
        # direction, which was never a decision -- it was an absence.
        #
        # Measured on `lot_demo_001` seed_5219 (five buildings, real collision):
        # the opening closed every marker sightline with 5 of its 12, the route
        # pass spent all 11 of its own, and 14 stretches of the crew's walk
        # were left inside an enemy's reach with nothing between. Seven pieces
        # unspent, fourteen stretches open, and no way for one to reach the
        # other.
        #
        # This buys ATTEMPTS, not outcomes. Those 14 were never tried -- the
        # loop had run out of budget, not out of places -- so some may still be
        # refused, and refusals are counted in `unbreakable` where they show.
        spare = max(0, limit - len(plan.cover))
        budget = max(1, int(math.ceil(route_length / route_metres_per_piece)))
        budget += spare
'''

EDITS = [("plan_cover: the route pass inherits the opening's unspent budget",
          OLD, NEW)]


def _load():
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET} does not exist.")
    raw = TARGET.read_bytes()
    return raw, _eol(raw), _n(raw.decode("utf-8"))


def _identity(raw: bytes):
    got = _sha(raw)
    mark = "" if len(raw) == EXPECT_BYTES else "   <-- not the size this was read against"
    print(f"  {TARGET.relative_to(ROOT)}")
    print(f"    bytes  : {len(raw)}   (expected {EXPECT_BYTES}){mark}")
    print(f"    sha256 : {got}")


def check() -> int:
    raw, _e, text = _load()
    _identity(raw)
    print()
    n = text.count(OLD)
    print(f"  [{'ok' if n == 1 else 'MISSING'}]  the route budget (found {n})")
    print()
    print("APPLICABLE." if n == 1
          else "NOT APPLICABLE: refusing rather than fuzzy-matching.")
    return 0 if n == 1 else 1


def apply() -> int:
    raw, eol, text = _load()
    _identity(raw)
    if text.count(OLD) != 1:
        raise SystemExit("REFUSING: the route budget is not present exactly "
                         "once. Nothing written.")
    if SIDECAR.exists():
        raise SystemExit(f"REFUSING: {SIDECAR.name} exists. Use --revert.")
    shutil.copy2(TARGET, SIDECAR)
    out = text.replace(OLD, NEW, 1)
    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
    TARGET.write_bytes(data)
    print()
    print(f"  {len(raw)} -> {len(data)} B  ({len(data) - len(raw):+d})")
    print(f"  sha256 {_sha(data)}")
    print()
    print("  NEXT -- the mission re-run is what settles it:")
    print("    cd lot; python -m pytest tests -q; cd ..")
    print("    $ws = \"workspaces\\lot-demo-ws\"")
    print("    python -u level_factory\\apps\\cli\\main.py -C $ws run lot_demo_001")
    print("    then read cover_plan from")
    print("    $ws\\.level_factory\\jobs\\lot_demo_001.lot_assemble.candidate"
          ".seed_5219\\out\\site.site.gameplay.json")
    print("    BEFORE: placed 16 (5 opening + 11 route), route_open 14, "
          "unbreakable 0, pinches 0")
    return 0


def revert() -> int:
    if not SIDECAR.exists():
        raise SystemExit(f"REFUSING: no {SIDECAR.name} to revert from.")
    before = TARGET.read_bytes()
    shutil.copy2(SIDECAR, TARGET)
    SIDECAR.unlink()
    after = TARGET.read_bytes()
    print(f"  reverted: {len(before)} -> {len(after)} B, sha256 {_sha(after)}")
    return 0


#: A site with the shape the defect needs: LOW opening demand (few marker
#: pairs, so the opening finishes under its limit) and a STARVED route. Tuned
#: to reproduce seed_5219's structure -- opening under limit, route exhausted,
#: nothing unbreakable -- rather than to flatter the change.
def _case():
    pts = {"LT_PlayerSpawn": (-120.0, 0.0), "LT_ObjectivePoint": (120.0, 0.0),
           "LT_ExtractionPoint": (-120.0, 0.0),
           "Enemy_0": (-40.0, 20.0), "Enemy_1": (40.0, 20.0)}
    return (pts, [(-14.0, 40.0, 14.0, 60.0)], (-160.0, -60.0, 160.0, 60.0),
            [pts["LT_PlayerSpawn"], pts["LT_ObjectivePoint"],
             pts["LT_ExtractionPoint"]])


def _run(mod, mpp):
    pts, rects, ground, route = _case()
    plan = mod.plan_cover(pts, rects, ground, opening_range=45.0, route=route,
                          route_metres_per_piece=mpp)
    op = [c for c in plan.cover if c.breaks and not c.breaks.startswith("route@")]
    rp = [c for c in plan.cover if c.breaks and c.breaks.startswith("route@")]
    return {"opening": len(op), "route": len(rp),
            "route_open": len(plan.route_open),
            "unbreakable": len(plan.unbreakable), "pinches": len(plan.pinches)}


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    raw, eol, text = _load()
    ok(len(raw) == EXPECT_BYTES, f"target is {EXPECT_BYTES} B (got {len(raw)})")
    ok(text.count(OLD) == 1, "the route budget is present exactly once")

    # The protection this must not undo has to still be in the file, or the
    # reasoning in the new comment is about something that is no longer there.
    # Whitespace-NORMALISED, and with comment markers stripped: this sentence
    # wraps across three source lines as "...nine long spawn\n    # lines
    # spend...", so a naive substring search finds nothing and reports the
    # protection as missing. That is the trap CLAUDE.md names in as many words,
    # and the first draft of this check walked into it.
    flat = " ".join(text.replace("#", " ").split())
    ok("sharing one allowance would let a site with nine long spawn lines "
       "spend everything before reaching the approach" in flat,
       "the comment stating why the budgets are separate is still present")
    ok("sharing one allowance would let a site with nine long spawn lines"
       not in text,
       "...and it really does span a line break, so the naive search would "
       "have been wrong rather than merely lucky")

    out = text.replace(OLD, NEW, 1)
    ok(out != text, "the edit changes the file")
    code = "\n".join(l for l in out.split("\n") if not l.lstrip().startswith("#"))
    ok(code.count("spare = max(0, limit - len(plan.cover))") == 1,
       "exactly one spare computation reaches the CODE")
    ok(code.count("budget += spare") == 1, "and it is added to the budget once")
    ok(out.index("spare = max(0, limit") > out.index("while remaining and len(plan.cover) < limit"),
       "the spare is computed AFTER the opening loop, so it sees the real count")

    try:
        compile(out, str(TARGET), "exec")
        ok(True, "site_cover.py compiles after the edit")
    except SyntaxError as exc:
        ok(False, f"site_cover.py compiles after the edit ({exc})")

    # -- BOTH versions executed on the constructed case ---------------------
    import importlib.util
    lot_dir = str(TARGET.parent)
    if lot_dir not in sys.path:
        sys.path.insert(0, lot_dir)
    saved = sys.modules.pop("site_cover", None)

    def _mod(name, source):
        spec = importlib.util.spec_from_loader(name, loader=None)
        m = importlib.util.module_from_spec(spec)
        m.__file__ = str(TARGET)
        sys.modules[name] = m
        exec(compile(source, str(TARGET), "exec"), m.__dict__)
        return m

    try:
        old_m = _mod("_r53_cov_old", text)
        new_m = _mod("_r53_cov_new", out)

        # STARVED: route budget small, opening demand low -> spare exists.
        b = _run(old_m, 120.0)
        a = _run(new_m, 120.0)
        print(f"        starved  before: {b}")
        print(f"        starved  after : {a}")
        ok(b["opening"] < 12 and b["route_open"] > 0,
           f"the case reproduces the defect (opening {b['opening']}/12, "
           f"route_open {b['route_open']})")
        ok(a["opening"] == b["opening"],
           "the OPENING pass is untouched -- same pieces, same order")
        ok(a["route"] > b["route"],
           f"the route pass gets more attempts ({b['route']} -> {a['route']})")
        ok(a["route_open"] < b["route_open"],
           f"fewer stretches left open ({b['route_open']} -> {a['route_open']})")
        ok(a["route"] - b["route"] <= 12 - b["opening"],
           f"and never more than the opening actually left unspent "
           f"({a['route'] - b['route']} <= {12 - b['opening']})")
        ok(a["pinches"] == b["pinches"] == 0,
           f"no lane is pinched by the extra pieces "
           f"({b['pinches']} -> {a['pinches']})")

        # NOT STARVED: route budget already ample -> the change must be inert.
        b2 = _run(old_m, 25.0)
        a2 = _run(new_m, 25.0)
        print(f"        ample    before: {b2}")
        print(f"        ample    after : {a2}")
        ok(a2 == b2,
           "a site whose route budget already suffices is UNCHANGED")

        # THE PROTECTION: opening spends its full limit -> nothing to carry.
        # Forced by giving the opening more demand than it can satisfy.
        pts, rects, ground, route = _case()
        for i, x in enumerate(range(-100, 110, 20)):
            pts[f"Enemy_x{i}"] = (float(x), -25.0)
        def _full(mod):
            p = mod.plan_cover(pts, rects, ground, opening_range=45.0,
                               route=route, route_metres_per_piece=120.0)
            op = [c for c in p.cover if c.breaks
                  and not c.breaks.startswith("route@")]
            rp = [c for c in p.cover if c.breaks
                  and c.breaks.startswith("route@")]
            return len(op), len(rp)
        bo, br = _full(old_m)
        ao, ar = _full(new_m)
        print(f"        saturated before: opening {bo} route {br}")
        print(f"        saturated after : opening {ao} route {ar}")
        ok(bo == 12, f"the saturated case really does spend all 12 ({bo})")
        ok((ao, ar) == (bo, br),
           "when the opening spends everything, the route carries NOTHING -- "
           "the 74 m-walk protection is intact")
    finally:
        for k in ("_r53_cov_old", "_r53_cov_new"):
            sys.modules.pop(k, None)
        if saved is not None:
            sys.modules["site_cover"] = saved

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s)")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("SELFTEST PASSED")
    return 0


def main(argv) -> int:
    arg = argv[1] if len(argv) > 1 else ""
    if arg == "--check":
        return check()
    if arg == "--selftest":
        return selftest()
    if arg == "--revert":
        return revert()
    if arg == "":
        return apply()
    raise SystemExit(f"unknown argument {arg!r}; "
                     f"use --check, --selftest, --revert, or no argument")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
