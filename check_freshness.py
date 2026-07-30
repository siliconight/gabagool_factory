"""Does the geometry the library walks still match the spec and builder that made it?

THE DEFECT THIS CLOSES. `library_walk.py` stages a site by copying
`lot/specs/<site>/buildings/` into a throwaway project, so the .glb sitting in
each site folder IS the geometry that gets walked. Nothing in the toolchain checks
that it corresponds to anything. `deli_a01.json` was three days newer than its
export and no gate noticed; the sweep walked geometry that did not match its spec
and came back green.

The worse case is not a spec edit, though. It is a BUILDER edit. The stair ramp
foot fix changed `deli_counter/stairwell.py`, which staleneed every .glb in the
library at once without a single spec's contents changing. A check that only
compared a .glb against its own spec would have reported all 57 as fresh.

WHY HASHES, NOT MTIMES. Mtimes do not survive a git checkout: a fresh clone shows
every file with the same recent timestamp, so an mtime rule reports either
everything stale or nothing, depending on clone order. Instead
`rebuild_buildings.py --stamp` writes `<stem>.buildstamp.json` beside each export
recording the SHA-256 of the spec that fed it, of the builder sources that
produced it, and of the .glb itself. This recomputes those three and compares.
Content, not clock.

WHAT COUNTS AS "THE BUILDER". Every root-level `*.py` in `deli_counter/` except
`test_*.py`. That is one rule rather than a hand-picked list, because a
hand-picked list of builder modules is exactly the thing that silently stops
matching reality -- the recurring defect of this whole toolchain. It over-reports:
editing a status script staleness everything. Over-reporting costs a rebuild;
under-reporting ships a level that does not match its spec.

NO STAMP IS NOT A PASS. A .glb with no stamp reports UNSTAMPED and, when
--mtime-proxy is passed, additionally shows the mtime comparison clearly labelled
as a proxy. It never reports fresh.

    python check_freshness.py                 # verify
    python check_freshness.py --mtime-proxy   # plus the clock, labelled
    python check_freshness.py --json out.json

Exit 1 if anything is stale, tampered, or unstamped.
"""
import argparse
import hashlib
import json
import os
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parent
SITES = ROOT / "lot" / "specs"
DC = ROOT / "deli_counter"
DC_SPECS = DC / "specs"
STAMP_SUFFIX = ".buildstamp.json"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def builder_files():
    """The inputs whose contents can change exported geometry.

    Every root-level .py in deli_counter except tests, plus agent_contract.json.
    Deliberately a RULE and not a curated list: a hand-picked set of builder
    modules stops matching reality quietly, and this errs toward reporting a
    rebuild that was not strictly needed.

    The contract is in here because it is a build INPUT, not just a document --
    deli_counter/agent_contract.py reads it, so a clearance change can move
    geometry with no source file touched. It changed after the last library
    rebuild (unassisted_step_max_m 0.117 -> 0.1025), which is exactly the case a
    .py-only rule would have called fresh.
    """
    out = [p for p in DC.glob("*.py") if not p.name.startswith("test_")]
    contract = DC / "agent_contract.json"
    if contract.exists():
        out.append(contract)
    return sorted(out)


def builder_hash(files=None):
    """One hash over the builder sources, name-and-content, order-independent."""
    files = files if files is not None else builder_files()
    h = hashlib.sha256()
    for p in files:
        h.update(p.name.encode("utf-8"))
        h.update(b"\0")
        h.update(sha(p).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest(), len(files)


def stamp_for(glb: pathlib.Path, spec: pathlib.Path, bhash, bcount):
    return {
        "glb": glb.name,
        "glb_sha256": sha(glb),
        "glb_bytes": glb.stat().st_size,
        "spec": spec.name,
        "spec_sha256": sha(spec),
        "builder_sha256": bhash,
        "builder_files": bcount,
        "deli_counter_version": (DC / "VERSION").read_text(
            encoding="utf-8").strip() if (DC / "VERSION").exists() else None,
        "stamped_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def write_stamp(glb: pathlib.Path, spec: pathlib.Path, bhash, bcount):
    path = glb.with_name(glb.stem + STAMP_SUFFIX)
    path.write_text(json.dumps(stamp_for(glb, spec, bhash, bcount), indent=2)
                    + "\n", encoding="utf-8")
    return path


def verify(glb: pathlib.Path, bhash, bcount):
    """(state, detail). state is one of fresh / STALE-SPEC / STALE-BUILDER /
    TAMPERED / UNSTAMPED / NO-SPEC."""
    spec = DC_SPECS / f"{glb.stem}.json"
    if not spec.exists():
        return "NO-SPEC", "no deli_counter spec; cannot be rebuilt or verified"
    st = glb.with_name(glb.stem + STAMP_SUFFIX)
    if not st.exists():
        return "UNSTAMPED", "no build stamp; nothing to compare against"
    try:
        rec = json.loads(st.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return "UNSTAMPED", f"stamp unreadable ({type(e).__name__})"
    if sha(glb) != rec.get("glb_sha256"):
        return "TAMPERED", ("the .glb differs from the one that was stamped -- "
                            "edited or replaced outside the pipeline")
    if sha(spec) != rec.get("spec_sha256"):
        return "STALE-SPEC", f"{spec.name} changed since this was exported"
    if bhash != rec.get("builder_sha256"):
        return "STALE-BUILDER", (
            f"deli_counter sources changed since this was exported "
            f"({rec.get('builder_files')} files then, {bcount} now)")
    return "fresh", ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stamp", action="store_true",
                    help="write a stamp for every .glb as it stands NOW; only "
                         "honest immediately after a rebuild")
    ap.add_argument("--mtime-proxy", action="store_true",
                    help="also show spec vs .glb modification times, labelled "
                         "as the proxy they are")
    ap.add_argument("--json", default=None, help="write the result as JSON")
    ap.add_argument("--only", nargs="*", default=None, help="these stems only")
    args = ap.parse_args()

    if not SITES.is_dir():
        print(f"no {SITES} -- wrong root?")
        return 1

    glbs = sorted(SITES.glob("*/buildings/*.glb"))
    if args.only:
        keep = set(args.only)
        glbs = [g for g in glbs if g.stem in keep]
    if not glbs:
        print("no .glb found under lot/specs/*/buildings/")
        return 1

    bfiles = builder_files()
    bhash, bcount = builder_hash(bfiles)
    print(f"  builder: {bcount} source file(s) in deli_counter, combined "
          f"{bhash[:16]}")
    print(f"  geometry: {len(glbs)} .glb across "
          f"{len({g.parent.parent.name for g in glbs})} site(s)\n")

    if args.stamp:
        n = 0
        for glb in glbs:
            spec = DC_SPECS / f"{glb.stem}.json"
            if not spec.exists():
                print(f"  skip   {glb.stem:<26} no spec, nothing to stamp")
                continue
            write_stamp(glb, spec, bhash, bcount)
            n += 1
        print(f"\n  stamped {n} .glb. This asserts the geometry on disk RIGHT "
              f"NOW matches\n  the spec and builder on disk right now -- only "
              f"true straight after a\n  rebuild. If you have not just rebuilt, "
              f"you have recorded a false claim.")
        return 0

    rows = []
    for glb in glbs:
        state, detail = verify(glb, bhash, bcount)
        row = {"stem": glb.stem, "site": glb.parent.parent.name,
               "state": state, "detail": detail,
               "glb": str(glb.relative_to(ROOT))}
        if args.mtime_proxy:
            spec = DC_SPECS / f"{glb.stem}.json"
            if spec.exists():
                sm, gm = spec.stat().st_mtime, glb.stat().st_mtime
                row["mtime_proxy"] = (
                    f"spec {time.strftime('%Y-%m-%d %H:%M', time.localtime(sm))}"
                    f"  glb {time.strftime('%Y-%m-%d %H:%M', time.localtime(gm))}"
                    + ("   spec is NEWER" if sm > gm + 1 else ""))
        rows.append(row)

    width = max(len(r["stem"]) for r in rows) + 2
    for r in rows:
        line = f"  {r['state']:<14}{r['stem']:<{width}}{r['site']:<20}"
        if r["state"] != "fresh":
            line += r["detail"]
        print(line)
        if r.get("mtime_proxy"):
            print(f"  {'':<14}{'':<{width}}proxy only: {r['mtime_proxy']}")

    from collections import Counter
    tally = Counter(r["state"] for r in rows)
    print()
    for state, n in sorted(tally.items()):
        print(f"  {n:>3}  {state}")

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps({"builder_sha256": bhash, "builder_files": bcount,
                        "rows": rows}, indent=2) + "\n", encoding="utf-8")
        print(f"\n  wrote {args.json}")

    # Two different failures, two different exit codes. STALE and TAMPERED mean
    # the geometry is KNOWN not to match; UNSTAMPED and NO-SPEC mean it cannot be
    # checked at all. Collapsing them would leave the gate permanently red for
    # every building that has no deli_counter spec, and a gate that is always red
    # gets ignored -- which is the same end state as a gate that is always green.
    wrong = [r for r in rows
             if r["state"].startswith("STALE") or r["state"] == "TAMPERED"]
    unknown = [r for r in rows if r["state"] in ("UNSTAMPED", "NO-SPEC")]
    if not wrong and not unknown:
        print("\n  Every building matches the spec and the builder that made "
              "it.")
        return 0

    print()
    if tally.get("UNSTAMPED"):
        print(f"  {tally['UNSTAMPED']} building(s) have no stamp, so nothing can "
              f"be verified about them.\n  Rebuild through "
              f"rebuild_buildings.py, or -- if you are certain the geometry\n  "
              f"on disk is current -- run --stamp to establish a baseline. Do "
              f"not run\n  --stamp to make this table green; that records a "
              f"claim rather than checking one.")
    if tally.get("STALE-BUILDER") or tally.get("STALE-SPEC"):
        stems = sorted({r["stem"] for r in rows
                        if r["state"].startswith("STALE")})
        print(f"  Rebuild the {len(stems)} stale building(s):")
        if tally.get("STALE-BUILDER") and len(stems) > 8:
            # A builder change staleness everything; listing 57 stems is noise.
            print("    python rebuild_buildings.py --blender <path>")
        else:
            print(f"    python rebuild_buildings.py --blender <path> --only "
                  f"{' '.join(stems)}")
    if tally.get("TAMPERED"):
        print("  A TAMPERED .glb was changed outside the pipeline. Rebuilding "
              "will discard\n  whatever was done to it -- find out what that "
              "was first.")
    # 1 = the geometry is known wrong. 2 = it could not be checked.
    return 1 if wrong else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Piping into `head` or `Select-Object -First` closes the stream early.
        # Let it end quietly rather than dumping a traceback over the report.
        import sys
        try:
            sys.stdout.close()
        except Exception:
            pass
        raise SystemExit(0)
