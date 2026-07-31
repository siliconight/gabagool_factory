"""Print eliminated candidates, and give each not-run job its reason.

`patch_run_summary.py` added the never-dispatched list. Now that a candidate can
be eliminated without stopping the run, that list needs to say WHICH of the two
happened -- otherwise the honest new output reads as five things going wrong on
a run where four candidates built cleanly and one was correctly dropped.

Asserts its target before writing.
"""
import pathlib

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
CMDS = ROOT / "level_factory" / "apps" / "cli" / "commands" / "__init__.py"

OLD = 'print(f"    - {_jid}")'
NEW = '''print(f"    - {_jid}: "
{i}                  f"{getattr(summary, 'not_run_reason', {}).get(_jid, 'no reason recorded')}")
{i}dropped = getattr(summary, "eliminated_candidates", {}) or {}
{i}if dropped:
{i}    # Not a failure line. Generating five candidates is only worth
{i}    # anything if the weak ones can be dropped, and until the scheduler
{i}    # learned to scope a failure, one bad candidate halted the run and
{i}    # took the good ones with it.
{i}    print(f"  {{len(dropped)}} candidate(s) eliminated (the rest carried on):")
{i}    for _cid, _at in sorted(dropped.items()):
{i}        print(f"    - {{_cid}}  at {{_at}}")'''


def main() -> int:
    text = CMDS.read_text(encoding="utf-8")
    if "eliminated_candidates" in text:
        print("already patched")
        return 0
    if text.count(OLD) != 1:
        raise SystemExit(
            f"expected exactly one {OLD!r}; found {text.count(OLD)}. "
            f"Nothing written -- run patch_run_summary.py first, or re-aim.")
    n = text.index(OLD)
    line_start = text.rfind("\n", 0, n) + 1
    indent = text[line_start:n]
    text = text[:n] + NEW.format(i=indent[:-4] if len(indent) >= 4 else indent) \
        + text[n + len(OLD):]
    CMDS.write_text(text, encoding="utf-8")
    print(f"patched {CMDS}")

    import py_compile
    py_compile.compile(str(CMDS), doraise=True)
    print("compiles")

    lines = CMDS.read_text(encoding="utf-8").splitlines()
    for k, ln in enumerate(lines):
        if "never_dispatched" in ln:
            for m in range(max(0, k - 2), min(len(lines), k + 22)):
                print(f"{m+1:5d}  {lines[m]}")
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
