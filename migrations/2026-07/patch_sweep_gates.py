"""Phase 1 step 1: show what the gates found. Change no verdict.

THE PROBLEM. library_walk decides a site's verdict from the walktest JSON alone:

    now = "pass" if s["ok"] is True else str(s["ok"])

The build's gate findings never reach it. They are printed and thrown away:

    for line in out.splitlines():
        if line.startswith("[lot]"):
            print("  " + line)

So ballpark_block reported `pass 25/25` while carrying LOT_STEP_BLOCKS_A_ROUTE,
and ref_pvp still reports `pass 15/15` with an objective at 0% traversal. Until a
major finding can fail a sweep, every gate in this toolchain is advisory.

THIS DOES NOT MAKE THEM BINDING. It adds a column and a per-site breakdown, and
stops there, deliberately. A verdict change that fails four sites on its first run
is indistinguishable from a broken verdict change, and a gate that fails a good
site gets disabled by whoever is trying to ship -- at which point it is worse than
no gate. So: report, read the list, establish for each site whether it is a real
defect or a wrong gate, and only then make it bind. That is step 3.

THE SCRAPING IS A KNOWN STOPGAP. This parses `[lot] CODE: message` out of the
build's stdout, which is a cheap observable standing in for structured truth --
the defect class this whole pass has been about. It is acceptable here only
because it is confined to a reporting column and because assemble() already
returns its findings as dicts, so phase 2 replaces this by writing them to a
sidecar and reading that instead. See GUARDRAILS_PLAN.md. Do not build anything
else on this parse.

UNKNOWN CODES ARE NOT ASSUMED HARMLESS. Severity is not in the printed line, so it
comes from an explicit map below. A code that is not in the map is reported as
`unclassified` and counted separately, rather than defaulting to minor -- a new
gate must not be able to slip in as harmless by being new.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LW = ROOT / "library_walk.py"

# --- 1. severity map + parser ------------------------------------------------

HELPER_ANCHOR = '''def main() -> int:
'''

HELPER_NEW = '''#: Severity per gate code. Explicit, because the printed `[lot]` line does not
#: carry it. A code missing from here is reported as `unclassified` and counted on
#: its own -- a new gate must not be able to arrive as harmless by being unknown.
GATE_SEVERITY = {
    "LOT_STEP_BLOCKS_A_ROUTE": "major",
    "LOT_STEP_TOO_TALL_TO_WALK": "major",
    "LOT_SURFACE_STACK_IMPOSSIBLE": "major",
    "LOT_DESTINATION_ABOVE_FLOOR": "major",
    "LOT_STEP_NEEDS_ASSIST": "minor",
    "LOT_KERB_CROSSED_SHALLOW": "minor",
    "LOT_GROUND_EXTENDED": "minor",
    "LOT_GROUND_OFF_CENTRE": "minor",
    "LOT_ENEMY_SPAWN_PUSHED": "minor",
    "LOT_ENEMY_SPAWN_CLOSE": "minor",
    "LOT_COVER_PLACED": "info",
    "LOT_ROUTE_COVER_PLACED": "info",
    "LOT_ROUTE_EXPOSED": "minor",
}


def gate_findings(build_output):
    """[(code, severity, message)] from the build's forwarded [lot] lines.

    STOPGAP. assemble() returns these as dicts already; this re-derives them from
    printed text because library_walk only receives stdout. Phase 2 writes a
    findings sidecar and this function goes away -- see GUARDRAILS_PLAN.md. Do not
    build on it.
    """
    out = []
    for line in (build_output or "").splitlines():
        line = line.strip()
        if not line.startswith("[lot]"):
            continue
        body = line[len("[lot]"):].strip()
        code, _sep, msg = body.partition(":")
        code = code.strip()
        # A gate code is UPPER_SNAKE. Without that shape, prose like
        # "[lot]   mode: pvp_heist (gates passed)" parses as a code called
        # `mode` and lands in the unclassified list -- an instrument inventing
        # findings, which is worse than one missing them.
        if not code or " " in code or not code.isupper() or "_" not in code:
            continue                       # a note, not a coded finding
        out.append((code, GATE_SEVERITY.get(code, "unclassified"), msg.strip()))
    return out


def main() -> int:
'''

# --- 2. capture instead of discard ------------------------------------------

CAPTURE_OLD = '''        for line in out.splitlines():
            if line.startswith("[lot]"):
                print("  " + line)
'''

CAPTURE_NEW = '''        gates = gate_findings(out)
        for line in out.splitlines():
            if line.startswith("[lot]"):
                print("  " + line)
'''

ATTACH_OLD = '''        s = summarise(read(proj, stem))
        s["rc"] = rc
'''

ATTACH_NEW = '''        s = summarise(read(proj, stem))
        s["rc"] = rc
        s["gates"] = gates
'''

# --- 3. the table ------------------------------------------------------------

HEAD_OLD = '''    print(f"{'site':<22} {'was':<12} {'now':<14} {'anchors':>7} {'strand':>6} "
          f"{'nofloor':>7} {'barrier':>7} {'legs':>9} {'stuck':>5}")
    print("-" * 104)
'''

HEAD_NEW = '''    print(f"{'site':<22} {'was':<12} {'now':<14} {'anchors':>7} {'strand':>6} "
          f"{'nofloor':>7} {'barrier':>7} {'legs':>9} {'stuck':>5} {'gates':>7}")
    print("-" * 112)
'''

ROW_OLD = '''        print(f"{name:<22} {was:<12} {now:<14} {s['anchors']:>7} "
              f"{s['stranded']:>6} {s['no_floor']:>7} {s['barrier']:>7} "
              f"{legs:>9} {s['stuck']:>5}")
'''

ROW_NEW = '''        _g = s.get("gates") or []
        _major = sum(1 for _c, _sev, _m in _g if _sev in ("major",
                                                          "unclassified"))
        print(f"{name:<22} {was:<12} {now:<14} {s['anchors']:>7} "
              f"{s['stranded']:>6} {s['no_floor']:>7} {s['barrier']:>7} "
              f"{legs:>9} {s['stuck']:>5} {(_major or ''):>7}")
'''

TAIL_OLD = '''    print(f"{len(clean)} of {len(results)} come back ok; "
          f"{time.time() - t_all:.0f}s total")
'''

TAIL_NEW = '''    print(f"{len(clean)} of {len(results)} come back ok; "
          f"{time.time() - t_all:.0f}s total")

    # What the gates found, REPORTING ONLY -- no verdict above depends on it yet.
    # This is the list to read before making them binding: every site here either
    # has a real defect or a gate that is wrong about it, and which one has to be
    # established per site. See GUARDRAILS_PLAN.md, phase 1.
    _blocking, _unclassified, _minor = [], [], 0
    for name, _mid, _was, s in results:
        for code, sev, msg in (s.get("gates") or []):
            if sev == "major":
                _blocking.append((name, code, msg))
            elif sev == "unclassified":
                _unclassified.append((name, code, msg))
            else:
                _minor += 1
    print()
    if _blocking:
        print(f"{len(_blocking)} MAJOR gate finding(s) on "
              f"{len({n for n, _c, _m in _blocking})} site(s). These do NOT "
              f"affect the verdict above yet:")
        for name, code, msg in _blocking:
            print(f"  {name:<22} {code}")
            print(f"  {'':<22}   {msg[:150]}")
    else:
        print("No major gate findings.")
    if _unclassified:
        print(f"\\n{len(_unclassified)} finding(s) with a code this script does "
              f"not know. Classify them in\\nGATE_SEVERITY before the verdict "
              f"starts depending on it -- an unknown code\\nmust not pass for a "
              f"harmless one:")
        for name, code, msg in _unclassified:
            print(f"  {name:<22} {code}")
    print(f"\\n{_minor} minor/info finding(s) not listed. A site with no gate "
          f"column entry\\nhad no major finding; a site whose build failed had no "
          f"gates to report at all.")
'''


def main() -> int:
    if not LW.exists():
        raise SystemExit(f"missing {LW}. Nothing written.")
    src = LW.read_text(encoding="utf-8")
    if "def gate_findings(" in src:
        print("library_walk.py: already reports gate findings")
        return 0
    edits = (("the severity map and parser", HELPER_ANCHOR, HELPER_NEW),
             ("capturing the [lot] lines", CAPTURE_OLD, CAPTURE_NEW),
             ("attaching them to the result", ATTACH_OLD, ATTACH_NEW),
             ("the table header", HEAD_OLD, HEAD_NEW),
             ("the table row", ROW_OLD, ROW_NEW),
             ("the summary", TAIL_OLD, TAIL_NEW))
    for label, old, _new in edits:
        if src.count(old) != 1:
            raise SystemExit(f"library_walk.py: target for '{label}' appears "
                             f"{src.count(old)} time(s), expected exactly 1. "
                             f"NOTHING WRITTEN.")
    for label, old, new in edits:
        src = src.replace(old, new)
    backup = LW.with_suffix(".py.pre_gates")
    if not backup.exists():
        shutil.copy2(LW, backup)
    LW.write_text(src, encoding="utf-8")
    py_compile.compile(str(LW), doraise=True)
    for label, _o, _n in edits:
        print(f"  library_walk.py: {label}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  NO VERDICT CHANGED. The `gates` column and the list under the "
          "table are\n  reporting only, so this sweep is directly comparable "
          "with the last one.\n")
    print("    python library_walk.py --timeout 1800")
    print("\n  Read the MAJOR list afterwards. For each site, decide whether it "
          "is a real\n  defect or a gate that is wrong -- that decision is what "
          "phase 1 step 3 needs,\n  and making the verdict binding before making "
          "it is how a gate gets disabled\n  by the next person trying to ship.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
