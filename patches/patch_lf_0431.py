#!/usr/bin/env python3
"""level_factory 0.43.1 -- the suite was RED, and a version pin is why.

`test_both_adapters_use_the_one_rule` asserts, under the comment "and the bump
that makes the fix take effect":

    assert LuxAdapter.adapter_version == "0.4.0"
    assert LotAdapter.adapter_version == "0.4.0"

The INTENT is "the bump happened and nobody reverted it" -- because reverting it
would serve cache entries written before the shared-payload rule landed. That
intent is right and the test is worth having.

The EXPRESSION is equality on a monotonically increasing value, so it is true
only until the next legitimate bump. 0.42.0 folded the staged Godot driver into
the Lux fingerprint and moved `adapter_version` to 0.5.0 for exactly the reason
this assertion exists -- to invalidate stale entries -- and the assertion read
that as a regression:

    AssertionError: assert '0.5.0' == '0.4.0'

So a check written to protect a cache invalidation fired on a cache
invalidation.

Fixed by comparing version TUPLES with `>=`, which still catches the revert it
was written for (0.3.x fails) while allowing the bumps it was written to
encourage. Both adapters, because Lot will bump for its own reasons one day and
should not take the suite down when it does.

TWO PROCESS FAILURES WORTH RECORDING, BOTH MINE:

  1. 0.42.0's `--selftest` runs the full suite and would have caught this. Its
     output was never read; the release was called green from the commit line.
  2. 0.43.0 was committed with the suite red, because the commit ran in the
     same pasted block as the selftest that failed.

Neither is fixed by code. Both are why this file records them.

Usage:
    pwsh> python patch_lf_0431.py --check
    pwsh> python patch_lf_0431.py
    pwsh> python patch_lf_0431.py --selftest
    pwsh> python patch_lf_0431.py --revert
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LF = ROOT / "level_factory"
TEST = LF / "tests" / "unit" / "test_scene_payload.py"
VERSION = LF / "VERSION"
CHANGELOG = LF / "CHANGELOG.md"

TAG = "pre_0431"
NEW_VERSION = "0.43.1"
TOUCHED = [TEST, VERSION, CHANGELOG]

E1_OLD = "from packages.core.hashing import scene_payload_hashes\n"
E1_NEW = (
    "from packages.core.hashing import scene_payload_hashes\n"
    "\n"
    "\n"
    "def _ver(s: str) -> tuple[int, ...]:\n"
    "    \"\"\"A version as a comparable tuple.\n"
    "\n"
    "    The two adapter-version assertions below were written as EQUALITY --\n"
    "    `== \"0.4.0\"` -- to pin that a bump had happened and had not been\n"
    "    reverted. Equality on a number that only goes up is true until the\n"
    "    next legitimate bump, and on 2026-08-18 level_factory 0.42.0 moved\n"
    "    LuxAdapter to 0.5.0 for precisely the reason the assertion exists (it\n"
    "    folded the staged Godot driver into the fingerprint, so stale entries\n"
    "    had to retire). The suite went red on a correct change: a check\n"
    "    written to protect a cache invalidation fired ON a cache\n"
    "    invalidation.\n"
    "    \"\"\"\n"
    "    return tuple(int(p) for p in s.split(\".\"))\n"
)

E2_OLD = (
    "    # and the bump that makes the fix take effect\n"
    "    assert LuxAdapter.adapter_version == \"0.4.0\"\n"
)
E2_NEW = (
    "    # and the bump that makes the fix take effect. `>=`, not `==`: this\n"
    "    # pins that the bump HAPPENED, which a later bump also satisfies. A\n"
    "    # revert to 0.3.x still fails, which is the case it was written for.\n"
    "    assert _ver(LuxAdapter.adapter_version) >= (0, 4, 0), \\\n"
    "        LuxAdapter.adapter_version\n"
)

E3_OLD = "    assert LotAdapter.adapter_version == \"0.4.0\"\n"
E3_NEW = (
    "    assert _ver(LotAdapter.adapter_version) >= (0, 4, 0), \\\n"
    "        LotAdapter.adapter_version\n"
)

EDITS = [("a comparable version helper", E1_OLD, E1_NEW),
         ("Lux: >= rather than ==", E2_OLD, E2_NEW),
         ("Lot: >= rather than ==", E3_OLD, E3_NEW)]

CHANGELOG_ENTRY = """## [0.43.1] - the suite was red, and a version pin is why

`test_both_adapters_use_the_one_rule` carried, under the comment "and the bump
that makes the fix take effect":

    assert LuxAdapter.adapter_version == "0.4.0"

0.42.0 moved `LuxAdapter.adapter_version` to 0.5.0 for exactly the reason that
assertion exists -- it folded the staged Godot driver into the fingerprint, so
entries cached before the driver was visible had to retire. The assertion read
the invalidation as a regression:

    AssertionError: assert '0.5.0' == '0.4.0'

A check written to protect a cache invalidation fired ON a cache invalidation.

The intent was right; the expression was equality on a value that only goes up,
which is true only until the next legitimate bump. Both assertions now compare
version TUPLES with `>=`. A revert to 0.3.x -- the case the test was written
for -- still fails. A bump does not.

Only two such pins existed; both were in this file. `test_tool_revision_dirty`
pins `tool_version == "0.88.0"` but that is a repository revision compared
clean-against-dirty, which is the subject of the test rather than a version
floor, and it is left alone.

TWO PROCESS FAILURES, RECORDED BECAUSE NO CODE FIXES THEM

0.42.0's `--selftest` runs the full suite and would have caught this. Its
output was never read; the release was called green from the commit line alone
-- the same shape as reading a git tag and concluding a commit had happened,
which had already been corrected once the same day.

0.43.0 was then committed with the suite red, because the commit ran in the
same pasted block as the selftest that failed. A selftest whose result nobody
waits for is a check that cannot fail, which is the defect class this release
series has spent itself on.

"""


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:8].upper()


def _stamp(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    return f"{p.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


def _eol(p: Path) -> str:
    return "\r\n" if b"\r\n" in p.read_bytes() else "\n"


def _require() -> None:
    missing = [str(p) for p in TOUCHED if not p.is_file()]
    if missing:
        sys.exit("REFUSING: not found:\n  " + "\n  ".join(missing))


def _plan(text: str) -> str:
    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(
                f"REFUSING: anchor for '{label}' occurs {n} times, expected 1.")
        text = text.replace(old, new, 1)
        print(f"  ok  {label}")
    return text


def cmd_check() -> int:
    _require()
    for p in TOUCHED:
        print("   ", _stamp(p))
    t = TEST.read_text(encoding="utf-8")
    if "def _ver(" in t:
        print("\nALREADY APPLIED.")
        return 0
    print()
    _plan(t)
    print(f"\nVERSION {VERSION.read_text(encoding='utf-8').strip()} -> {NEW_VERSION}")
    return 0


def cmd_apply() -> int:
    _require()
    src = TEST.read_text(encoding="utf-8")
    if "def _ver(" in src:
        print("ALREADY APPLIED; nothing to do.")
        return 0
    ver = VERSION.read_text(encoding="utf-8").strip()
    if ver == NEW_VERSION:
        raise SystemExit(f"REFUSING: VERSION already {NEW_VERSION}")
    log = CHANGELOG.read_text(encoding="utf-8")
    if f"[{NEW_VERSION}]" in log:
        raise SystemExit(f"REFUSING: CHANGELOG already has [{NEW_VERSION}]")

    out = _plan(src)
    for p in TOUCHED:
        (p.parent / f"{p.name}.{TAG}").write_bytes(p.read_bytes())
    e = _eol(TEST)
    TEST.write_text(out if e == "\n" else out.replace("\n", "\r\n"),
                    encoding="utf-8", newline="")
    tail = "\n" if b"\n" in VERSION.read_bytes() else ""
    VERSION.write_text(NEW_VERSION + tail, encoding="utf-8", newline="")
    ec = _eol(CHANGELOG)
    entry = CHANGELOG_ENTRY if ec == "\n" else CHANGELOG_ENTRY.replace("\n", "\r\n")
    CHANGELOG.write_text(entry + log, encoding="utf-8", newline="")

    print(f"  ok  VERSION {ver} -> {NEW_VERSION}")
    print(f"  ok  CHANGELOG [{NEW_VERSION}] prepended")
    print("\nafter:")
    for p in TOUCHED:
        print("   ", _stamp(p))
    print(f"\nsidecars .{TAG}; `--revert` restores them.")
    return 0


def cmd_revert() -> int:
    n = 0
    for p in TOUCHED:
        s = p.parent / f"{p.name}.{TAG}"
        if s.is_file():
            p.write_bytes(s.read_bytes()); s.unlink()
            print(f"  restored {p.name}"); n += 1
    if not n:
        print("nothing to revert.")
    return 0


def _pytest(args):
    return subprocess.run([sys.executable, "-m", "pytest"] + args,
                          cwd=str(LF), capture_output=True, text=True)


def cmd_selftest() -> int:
    _require()
    if "def _ver(" not in TEST.read_text(encoding="utf-8"):
        raise SystemExit("SELFTEST: patch is not applied.")

    r = _pytest([str(TEST.relative_to(LF))])
    if r.returncode != 0:
        raise SystemExit("SELFTEST FAILED: the fixed file does not pass.\n"
                         + r.stdout[-3000:])
    print("  ok  test_scene_payload.py passes (rc=0)")

    # The revert this assertion was written to catch must STILL fail.
    lux = LF / "adapters" / "lux" / "__init__.py"
    orig = lux.read_bytes()
    try:
        cur = orig.decode("utf-8")
        m = [l for l in cur.splitlines() if "adapter_version = " in l]
        lux.write_bytes(cur.replace(m[0], '    adapter_version = "0.3.0"')
                        .encode("utf-8"))
        r = _pytest([str(TEST.relative_to(LF))])
        if r.returncode == 0:
            raise SystemExit("SELFTEST FAILED: reverting LuxAdapter to 0.3.0 "
                             "no longer fails the test, so the floor is not "
                             "being enforced at all.")
        if r.returncode == 5:
            raise SystemExit("SELFTEST FAILED: pytest collected NOTHING (rc=5)")
        print(f"  ok  falsified: a revert to 0.3.0 still fails  (rc={r.returncode})")
    finally:
        lux.write_bytes(orig)

    r = _pytest([])
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    if r.returncode == 5:
        raise SystemExit("SELFTEST FAILED: full suite collected NOTHING (rc=5)")
    if r.returncode != 0:
        raise SystemExit(f"SELFTEST FAILED: full suite STILL RED, rc="
                         f"{r.returncode}\n" + r.stdout[-4000:])
    print(f"  ok  FULL SUITE GREEN :: {lines[-1] if lines else '(no summary)'}")
    print("\nSELFTEST PASSED")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--revert", action="store_true")
    g.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.check:
        return cmd_check()
    if a.revert:
        return cmd_revert()
    if a.selftest:
        return cmd_selftest()
    return cmd_apply()


if __name__ == "__main__":
    raise SystemExit(main())
