"""tools/factory_retire.py --pushed-only: the push is the only question for a pushed run's workspace (the walker,
2026-10-19), and every cold run's clean job applies it that way.

WHY. On 2026-10-16 the disk filled -- C: 466 GB used, 447 MB free -- and killed cold run 9319 at its art stage.
The factory held 79 cold-run workspaces, about 1 GB each, and 67 of them had their record pushed. The retire's
own rules found 0.6 GB: the pushed-runs rule kept every workspace a record names, and the records name them
literally on purpose, so a built name cannot let the retire take an arm a finding still reads. A name in a record
was never meant to pin a gigabyte, but the rule cannot tell a name that still reads the workspace from one that
cites it (`docs/findings/disk_full_2026_10_16/`). Asked whether the retire should take any cold-run workspace
whose record is pushed, even when a record names it, the walker said "yes, add --pushed-only to the retire tool".

WHAT IT CHANGES (anchored; each file pinned by hash; nothing written on a miss):
  * tools/factory_retire.py -- `plan(..., pushed_only=False)`: with it, the pushed-runs rule no longer spares a
    workspace a record names; the newest KEEP_PUSHED (4) still stay, a tracked path is still never touched, and
    an UNPUSHED run's named workspace still stays (it is not regenerable from a pushed record). The `why` of a
    named one says so. `--pushed-only` on the command line; an unknown argument refuses rather than falling back
    to the other rule in silence. The selftest grows a pushed, named run (goes with the flag, stays without it)
    and a named, unpushed one (stays either way).
  * tools/cold_drive/cold_drive.sh -- the clean job, every cold run's last step, passes `--pushed-only`.
  * tools/factory_hygiene.py -- RETIRABLE reports the rule the clean job applies.
  * docs/FILING.md, docs/COMMANDS.md -- say so; FILING's "walk exports older than a mission's newest" was the
    rule the tool's own selftest refuted, and now reads "untouched for thirty days", which is what it does.

    python patches/patch_retire_pushed_only.py --tests && python tools/factory_retire.py --selftest   # fails
    git checkout -- tools/factory_retire.py
    python patches/patch_retire_pushed_only.py && python tools/factory_retire.py --selftest          # ok
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "factory_retire.py"
DRIVE = ROOT / "tools" / "cold_drive" / "cold_drive.sh"
HYGIENE = ROOT / "tools" / "factory_hygiene.py"
FILING = ROOT / "docs" / "FILING.md"
COMMANDS = ROOT / "docs" / "COMMANDS.md"
SHA = {TOOL: "aa2c93b4146e1de1", DRIVE: "335e3cd24ee6eb9f", HYGIENE: "a86f6dbab4711812",
       FILING: "897728621bead898", COMMANDS: "0d6742b55092c5b2"}

# ---- tools/factory_retire.py -------------------------------------------------------------------------------
USAGE_OLD = r'''    python tools/factory_retire.py --selftest  # prove the rules on a throwaway tree
'''
USAGE_NEW = r'''    python tools/factory_retire.py --selftest  # prove the rules on a throwaway tree
    python tools/factory_retire.py --pushed-only [--apply]  # a pushed run's workspace goes even when named
'''

RULE_OLD = r'''  pushed runs    a cold-run workspace beyond the newest KEEP_PUSHED whose
                 docs/cold_runs/cold_N/NOTES.md is pushed (a price takes the
                 previous run's package as its control, so four stay).
'''
RULE_NEW = r'''  pushed runs    a cold-run workspace beyond the newest KEEP_PUSHED whose
                 docs/cold_runs/cold_N/NOTES.md is pushed (a price takes the
                 previous run's package as its control, so four stay).
                 WITH --pushed-only (the walker, 2026-10-19) the push is the
                 only question: a pushed run's workspace goes even when a
                 record names it. The disk filled on 2026-10-16 with 79
                 cold-run workspaces, 67 of them pushed and kept because
                 records named them (docs/findings/disk_full_2026_10_16/). A
                 record's script that reads one regenerates it from
                 docs/cold_runs/cold_N/ first; an UNPUSHED run's named
                 workspace still stays. Every cold run's last step
                 (tools/cold_drive/cold_drive.sh) applies it this way.
'''

PLAN_OLD = r'''def plan(root, keep=KEEP_WORKSPACES, keep_pushed=KEEP_PUSHED, package_dir=None):
    """``[{path, why, bytes}]`` the rules would remove, newest-first within a rule."""
'''
PLAN_NEW = r'''def plan(root, keep=KEEP_WORKSPACES, keep_pushed=KEEP_PUSHED, package_dir=None, pushed_only=False):
    """``[{path, why, bytes}]`` the rules would remove, newest-first within a rule.

    With ``pushed_only`` (the walker, 2026-10-19) a pushed run's workspace beyond
    ``keep_pushed`` goes even when a record names it; an unpushed one a record
    names still stays."""
'''

LOOP_OLD = r'''            if p in already or d in named or _tracked(root, "workspaces/" + d):
                continue
            n = d.split("-")[1]
            if _pushed(root, upstream, "docs/cold_runs/cold_%s/NOTES.md" % n):
                out.append({"path": p, "why": "cold-run workspace beyond the newest %d whose record is pushed" % keep_pushed, "bytes": _size(p)})
'''
LOOP_NEW = r'''            if p in already or (d in named and not pushed_only) or _tracked(root, "workspaces/" + d):
                continue
            n = d.split("-")[1]
            if _pushed(root, upstream, "docs/cold_runs/cold_%s/NOTES.md" % n):
                why = "cold-run workspace beyond the newest %d whose record is pushed" % keep_pushed
                if d in named:
                    why += "; a record names it, and --pushed-only retires it anyway"
                out.append({"path": p, "why": why, "bytes": _size(p)})
'''

TEST_REC_OLD = r'''    write("docs/findings/stranger_install/install_test_1/steps.txt", "ok\n")
    git("add", "-A")
    git("commit", "-q", "-m", "records")
'''
TEST_REC_NEW = r'''    write("docs/findings/stranger_install/install_test_1/steps.txt", "ok\n")
    # --pushed-only (2026-10-19): run 3's record is pushed and a finding names its
    # workspace; the same finding names run 2's, whose record is not pushed
    write("docs/cold_runs/cold_3/NOTES.md", "run 3\n")
    write("docs/findings/reads/README.md", "reads workspaces/cold-3-ws and workspaces/cold-2-ws\n")
    git("add", "-A")
    git("commit", "-q", "-m", "records")
'''

TEST_ASSERT_OLD = r'''    assert got == want, got
    # with no upstream the pushed rules say nothing
    git("branch", "--unset-upstream")
    assert plan(root, keep=12, keep_pushed=2, package_dir=pkgs) == []
'''
TEST_ASSERT_NEW = r'''    assert got == want, got
    # --pushed-only: the push is the only question for a pushed run -- cold-3-ws goes
    # though a record names it; cold-2-ws, named and unpushed, stays
    got = sorted(os.path.basename(p["path"]) for p in plan(root, keep=12, keep_pushed=2, package_dir=pkgs,
                                                            pushed_only=True))
    assert got == sorted(want + ["cold-3-ws"]), got
    # with no upstream the pushed rules say nothing
    git("branch", "--unset-upstream")
    assert plan(root, keep=12, keep_pushed=2, package_dir=pkgs) == []
    assert plan(root, keep=12, keep_pushed=2, package_dir=pkgs, pushed_only=True) == []
'''

MAIN_OLD = r'''def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import factory_index
    root = factory_index.factory_root()
    items = plan(root)
'''
MAIN_NEW = r'''def main():
    argv = sys.argv[1:]
    # a misspelt flag must not fall back to the other rule in silence
    unknown = [a for a in argv if a not in ("--apply", "--selftest", "--pushed-only")]
    if unknown:
        print("unknown argument(s): %s\n%s" % (" ".join(unknown), __doc__.split("\n\n")[1]))
        sys.exit(2)
    if "--selftest" in argv:
        return selftest()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import factory_index
    root = factory_index.factory_root()
    pushed_only = "--pushed-only" in argv
    if pushed_only:
        print("  --pushed-only: a pushed run's workspace beyond the newest %d goes even when a record names it"
              % KEEP_PUSHED)
    items = plan(root, pushed_only=pushed_only)
'''

# ---- tools/cold_drive/cold_drive.sh --------------------------------------------------------------------------
DRIVE_OLD = r'''# own workspace stays: its record is not pushed yet. Never fatal to the run.
step retire; python tools/factory_retire.py --apply 2>&1 | tail -1 || true
'''
DRIVE_NEW = r'''# own workspace stays: its record is not pushed yet. Never fatal to the run.
# --pushed-only (2026-10-19, the walker): a pushed run's workspace goes even when a
# record names it -- the disk filled on 2026-10-16 with 67 of them kept that way.
step retire; python tools/factory_retire.py --apply --pushed-only 2>&1 | tail -1 || true
'''

# ---- tools/factory_hygiene.py --------------------------------------------------------------------------------
HYG_DOC_OLD = "  RETIRABLE      bulk the retention rule would remove (`factory_retire.py`), in GB -- reported, never failed on\n"
HYG_DOC_NEW = ("  RETIRABLE      bulk the retention rule would remove (`factory_retire.py --pushed-only`, the rule every\n"
               "                 cold run's last step applies), in GB -- reported, never failed on\n")
HYG_OLD = r'''        import factory_retire
        plan = factory_retire.plan(root)
        gb = sum(p["bytes"] for p in plan) / 1e9
        lines.append(("RETIRABLE", round(gb, 1), "GB in %d item(s); tools/factory_retire.py" % len(plan)))
'''
HYG_NEW = r'''        import factory_retire
        # the rule every cold run's last step applies (--pushed-only since 2026-10-19)
        plan = factory_retire.plan(root, pushed_only=True)
        gb = sum(p["bytes"] for p in plan) / 1e9
        lines.append(("RETIRABLE", round(gb, 1), "GB in %d item(s); tools/factory_retire.py --pushed-only" % len(plan)))
'''

# ---- docs ----------------------------------------------------------------------------------------------------
FILING_OLD = r'''   (dry-run by default, `--apply` to act) retires perf copies that have
   their JSON, walk exports older than a mission's newest, and cold-run
'''
FILING_NEW = r'''   (dry-run by default, `--apply` to act) retires perf copies that have
   their JSON, walk exports untouched for thirty days, and cold-run
'''
FILING2_OLD = r'''   applying it (`tools/cold_drive/cold_drive.sh`'s last step), so the disk
   does not wait for somebody to remember.
'''
FILING2_NEW = r'''   applying it (`tools/cold_drive/cold_drive.sh`'s last step), so the disk
   does not wait for somebody to remember. **It applies it with
   `--pushed-only`** (2026-10-19, the walker): a pushed run's workspace goes
   even when a record names it, so a finding whose script reads one
   regenerates it from `docs/cold_runs/cold_N/` first. The disk filled on
   2026-10-16 with 67 pushed runs' workspaces kept because records named
   them (`docs/findings/disk_full_2026_10_16/`).
'''
FILING3_OLD = "python tools/factory_retire.py               # what the retention rule would remove; --apply removes it\n"
FILING3_NEW = (FILING3_OLD +
               "python tools/factory_retire.py --pushed-only # the rule every cold run applies: a pushed run's workspace goes even when named\n")
COMMANDS_OLD = "python tools/factory_retire.py              # what the retention rule would remove (dry run); --apply removes it\n"
COMMANDS_NEW = (COMMANDS_OLD +
                "python tools/factory_retire.py --pushed-only  # the rule every cold run's last step applies: a pushed run's workspace goes even when named\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(path):
    raw = path.read_bytes()
    assert b"\r\n" not in raw, f"{path.name} is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA[path], (f"{path.name} is not the file this patch read", got)
    return raw.decode("utf-8")


def main(argv):
    tool = _read(TOOL)
    assert "pushed_only" not in tool, "already applied"
    tool = _once(tool, TEST_REC_OLD, TEST_REC_NEW, "the selftest's records")
    tool = _once(tool, TEST_ASSERT_OLD, TEST_ASSERT_NEW, "the selftest's assertions")
    if "--tests" in argv:
        TOOL.write_bytes(tool.encode("utf-8"))
        print("factory_retire.py: the selftest only (prove it fails, then `git checkout -- tools/factory_retire.py`)")
        return 0
    tool = _once(tool, USAGE_OLD, USAGE_NEW, "the usage lines")
    tool = _once(tool, RULE_OLD, RULE_NEW, "the pushed-runs rule")
    tool = _once(tool, PLAN_OLD, PLAN_NEW, "plan's signature")
    tool = _once(tool, LOOP_OLD, LOOP_NEW, "the pushed-runs loop")
    tool = _once(tool, MAIN_OLD, MAIN_NEW, "main")
    drive = _once(_read(DRIVE), DRIVE_OLD, DRIVE_NEW, "the clean job")
    hyg = _read(HYGIENE)
    hyg = _once(hyg, HYG_DOC_OLD, HYG_DOC_NEW, "hygiene's docstring")
    hyg = _once(hyg, HYG_OLD, HYG_NEW, "hygiene's RETIRABLE")
    filing = _read(FILING)
    filing = _once(filing, FILING_OLD, FILING_NEW, "FILING's walk-export rule")
    filing = _once(filing, FILING2_OLD, FILING2_NEW, "FILING's clean job")
    filing = _once(filing, FILING3_OLD, FILING3_NEW, "FILING's checks")
    commands = _once(_read(COMMANDS), COMMANDS_OLD, COMMANDS_NEW, "COMMANDS' hygiene block")
    for path, text in ((TOOL, tool), (DRIVE, drive), (HYGIENE, hyg), (FILING, filing), (COMMANDS, commands)):
        path.write_bytes(text.encode("utf-8"))
    print("factory_retire.py --pushed-only, applied by every cold run's clean job; hygiene and the docs say so")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
