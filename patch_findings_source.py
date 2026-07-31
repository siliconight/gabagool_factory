"""Phase 2: read findings from the thing that measured them.

WHAT PHASE 1 EXPOSED. `patch_sweep_gates.py` had to hardcode a GATE_SEVERITY map
because it re-derived findings from printed text. Its first contact with a real
sweep produced 8 unclassified codes, and reading the emitters showed why the map
was doomed:

    LOT_DESTINATION_ABOVE_FLOOR   major       site_spawns.py:515
    LOT_SIGHTLINE_UNBREAKABLE     moderate    site_cover.py:479
    LOT_ENEMY_SPAWN_STANDOFF      minor       site_spawns.py:669
    LOT_DESTINATION_RESOLVED      minor       site_spawns.py:584
    LOT_SIGHTLINE_OPEN            minor       site_cover.py:493

Every severity was already set by the code that raised the finding, including a
`moderate` level the map did not have -- so any guess at that code would have been
wrong in both directions. A second opinion about a value the source already holds
is not a fallback, it is drift with a schedule.

AND THE DATA IS ALREADY ON DISK. `merged["tactical"] = tactical_report` at
lot.py:1596, and `merged` is serialised to `<site>.site.gameplay.json` at :1749.
Every finding from site_extent, site_ground, site_spawns and site_cover is in that
file, with its real severity, next to the scene. No sidecar is needed; phase 2 is
smaller than planned.

ONE GAP. The step gate runs at :1775, AFTER the contract is written, because it
reads back the .tscn that :1761 emits. So `result_steps` reaches the return value
and never reaches the file. This folds it in and rewrites, so the contract on disk
carries every finding rather than most of them.

TWO CHANGES.

lot.py       after the step gate, extend tactical_report["findings"] with the step
             findings and rewrite the gameplay contract.

library_walk read `<stem>.site.gameplay.json` and take `tactical.findings`.
             GATE_SEVERITY and gate_findings() are deleted -- 30 lines of parser
             and a stale lookup table replaced by reading a field. The severity a
             finding reports is now the severity its emitter set, and a new gate
             needs no registration anywhere.

WHAT STAYS UNCHANGED. No verdict. Phase 1's whole point was that the list gets read
before it binds, and this changes where the list comes from, not what it decides.
Making it binding is step 3, and it is now nearly free: `major` means major
because site_spawns said so.

Asserts every target, refuses on a miss, idempotent, byte-compiles both.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LOT_PY = ROOT / "lot" / "lot.py"
LW = ROOT / "library_walk.py"

# --- lot.py: fold the step findings into the contract ------------------------

LOT_OLD = '''        for _i in result_steps:
            # Column zero, and the prefix library_walk.py filters on. Its
            # forwarder does `if line.startswith("[lot]")` and adds the indent
            # itself, so a leading space here means the line is dropped -- which
            # silently hid this gate's first live run, findings and failures
            # alike.
            print(f"[lot] {_i['code']}: {_i['message']}")
'''

LOT_NEW = '''        for _i in result_steps:
            # Column zero, and the prefix library_walk.py filters on. Its
            # forwarder does `if line.startswith("[lot]")` and adds the indent
            # itself, so a leading space here means the line is dropped -- which
            # silently hid this gate's first live run, findings and failures
            # alike.
            print(f"[lot] {_i['code']}: {_i['message']}")
        # This gate necessarily runs AFTER the gameplay contract was written,
        # because it reads back the .tscn emitted above. Fold its findings in and
        # rewrite, so <site>.site.gameplay.json carries EVERY finding with the
        # severity its emitter gave it. Anything downstream can then read one
        # file instead of re-deriving severity from printed text -- which is what
        # library_walk was doing, with a hardcoded lookup table that was already
        # missing a severity level the emitters use.
        if result_steps:
            tactical_report.setdefault("findings", []).extend(result_steps)
            with open(gp_out, "w", encoding="utf-8") as _gf:
                json.dump(merged, _gf, indent=2)
'''

# --- library_walk.py: read the contract, delete the parser -------------------

LW_HELPER_OLD = '''#: Severity per gate code. Explicit, because the printed `[lot]` line does not
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
'''

LW_HELPER_NEW = '''#: Severities the emitters actually use. Not a classification -- only an ordering,
#: so the report can rank and the verdict can eventually threshold. A severity not
#: listed here is surfaced as-is rather than assumed harmless.
SEVERITY_RANK = {"major": 3, "moderate": 2, "minor": 1, "info": 0}


def gate_findings(proj, stem):
    """Every finding the build recorded, from the contract it already writes.

    lot.py puts tactical_report into `merged` and serialises it to
    <site>.site.gameplay.json, so each finding is on disk with the severity the
    code that raised it assigned. Reading that field is the whole job.

    This replaced a parser over the build's stdout plus a hardcoded severity
    table. That table's first contact with a real sweep produced 8 unclassified
    codes and, worse, did not contain `moderate` -- a level site_cover.py uses --
    so any guess at those codes was wrong in both directions. A second opinion
    about a value the source already holds is drift with a schedule.

    Returns [(code, severity, message)]; [] when the contract is unreadable, which
    the caller reports as unchecked rather than clean.
    """
    path = os.path.join(proj, f"{stem}.site.gameplay.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            gp = json.load(f)
    except (OSError, ValueError):
        return None                        # distinct from "no findings"
    found = ((gp.get("tactical") or {}).get("findings")) or []
    out = []
    for f_ in found:
        if not isinstance(f_, dict):
            continue
        out.append((str(f_.get("code") or "UNCODED"),
                    str(f_.get("severity") or "unspecified"),
                    str(f_.get("message") or "")))
    return out
'''

LW_CALL_OLD = '''        gates = gate_findings(out)
        for line in out.splitlines():
'''

LW_CALL_NEW = '''        for line in out.splitlines():
'''

LW_ATTACH_OLD = '''        s = summarise(read(proj, stem))
        s["rc"] = rc
        s["gates"] = gates
'''

LW_ATTACH_NEW = '''        s = summarise(read(proj, stem))
        s["rc"] = rc
        # Read AFTER the build, from the contract the build wrote. None means the
        # contract could not be read at all, which is not the same as a clean
        # site and is reported separately below.
        s["gates"] = gate_findings(proj, stem)
'''

LW_ROW_OLD = '''        _g = s.get("gates") or []
        _major = sum(1 for _c, _sev, _m in _g if _sev in ("major",
                                                          "unclassified"))
'''

LW_ROW_NEW = '''        _g = s.get("gates")
        _major = ("?" if _g is None else
                  sum(1 for _c, _sev, _m in _g
                      if SEVERITY_RANK.get(_sev, 3) >= 2))
'''

LW_TAIL_OLD = '''    _blocking, _unclassified, _minor = [], [], 0
    for name, _mid, _was, s in results:
        for code, sev, msg in (s.get("gates") or []):
            if sev == "major":
                _blocking.append((name, code, msg))
            elif sev == "unclassified":
                _unclassified.append((name, code, msg))
            else:
                _minor += 1
'''

LW_TAIL_NEW = '''    _blocking, _unclassified, _minor = [], [], 0
    for name, _mid, _was, s in results:
        _g = s.get("gates")
        if _g is None:
            # The contract could not be read. Not clean -- unchecked.
            _unclassified.append((name, "CONTRACT UNREADABLE",
                                  "no <site>.site.gameplay.json to read "
                                  "findings from"))
            continue
        for code, sev, msg in _g:
            rank = SEVERITY_RANK.get(sev)
            if rank is None:
                _unclassified.append((name, code, f"severity {sev!r}: {msg}"))
            elif rank >= 2:
                _blocking.append((name, code, msg))
            else:
                _minor += 1
'''

LW_MSG_OLD = '''        print(f"\\n{len(_unclassified)} finding(s) with a code this script does "
              f"not know. Classify them in\\nGATE_SEVERITY before the verdict "
              f"starts depending on it -- an unknown code\\nmust not pass for a "
              f"harmless one:")
'''

LW_MSG_NEW = '''        print(f"\\n{len(_unclassified)} finding(s) this script could not rank, "
              f"or sites whose contract\\ncould not be read. Neither is clean, "
              f"and neither may pass for it:")
'''

LW_FOOT_OLD = '''    print(f"\\n{_minor} minor/info finding(s) not listed. A site with no gate "
          f"column entry\\nhad no major finding; a site whose build failed had no "
          f"gates to report at all.")
'''

LW_FOOT_NEW = '''    print(f"\\n{_minor} minor/info finding(s) not listed. Severity comes from "
          f"the emitter that\\nraised each finding, not from this script -- "
          f"major and moderate are listed\\nabove, minor and info are counted "
          f"here, and `?` in the gates column means the\\ncontract could not be "
          f"read.")
'''


def _swap(src, old, new, label, done):
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"{label}: target appears {n} time(s), expected exactly "
                         f"1. NOTHING WRITTEN.")
    done.append(label)
    return src.replace(old, new)


def main() -> int:
    for p in (LOT_PY, LW):
        if not p.exists():
            raise SystemExit(f"missing {p}. Nothing written.")

    lot_src = LOT_PY.read_text(encoding="utf-8")
    lw_src = LW.read_text(encoding="utf-8")
    if "GATE_SEVERITY" not in lw_src:
        raise SystemExit("library_walk.py has no GATE_SEVERITY -- run "
                         "patch_sweep_gates.py first, or this is already "
                         "applied. NOTHING WRITTEN.")
    done = []

    if "tactical_report.setdefault(\"findings\", []).extend(result_steps)" in lot_src:
        done.append("lot.py: step findings already in the contract")
    else:
        lot_src = _swap(lot_src, LOT_OLD, LOT_NEW,
                        "lot.py: step findings folded into the contract", done)

    lw_src = _swap(lw_src, LW_HELPER_OLD, LW_HELPER_NEW,
                   "library_walk.py: parser + severity table replaced by a read",
                   done)
    lw_src = _swap(lw_src, LW_CALL_OLD, LW_CALL_NEW,
                   "library_walk.py: stdout no longer scraped", done)
    lw_src = _swap(lw_src, LW_ATTACH_OLD, LW_ATTACH_NEW,
                   "library_walk.py: findings read from the contract", done)
    lw_src = _swap(lw_src, LW_ROW_OLD, LW_ROW_NEW,
                   "library_walk.py: column ranks by real severity", done)
    lw_src = _swap(lw_src, LW_TAIL_OLD, LW_TAIL_NEW,
                   "library_walk.py: unreadable contract counted as unchecked",
                   done)
    lw_src = _swap(lw_src, LW_MSG_OLD, LW_MSG_NEW,
                   "library_walk.py: the unranked notice", done)
    lw_src = _swap(lw_src, LW_FOOT_OLD, LW_FOOT_NEW,
                   "library_walk.py: the footer", done)

    for path, text, suffix in ((LOT_PY, lot_src, ".py.pre_source"),
                               (LW, lw_src, ".py.pre_source")):
        backup = path.with_suffix(suffix)
        if not backup.exists():
            shutil.copy2(path, backup)
        path.write_text(text, encoding="utf-8")
        py_compile.compile(str(path), doraise=True)

    print("applied:")
    for line in done:
        print(f"  {line}")
    print("  both compile; previous copies kept as *.pre_source")
    print(f"\n  library_walk.py: {len(LW_HELPER_OLD.splitlines())} lines of "
          f"parser and lookup table replaced by "
          f"{len(LW_HELPER_NEW.splitlines())} that read a field.")
    print("\n  Severity now comes from the emitter. A new gate needs no "
          "registration\n  anywhere, and `moderate` -- which the old table did "
          "not contain -- ranks\n  correctly without anyone remembering to add "
          "it.\n")
    print("  NO VERDICT CHANGED, again. Re-run and the table should be "
          "comparable,\n  with the 8 previously-unclassified codes now ranked "
          "by their real severity:\n")
    print("    python library_walk.py --timeout 1800")
    print("\n  Expect the gates column to move: it now counts major AND "
          "moderate, so\n  ballpark_block's LOT_SIGHTLINE_UNBREAKABLE starts "
          "counting and its\n  LOT_ENEMY_SPAWN_STANDOFF stops.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
