r"""Make verify-manifest notice a VERSION that no longer describes its code.

    python patch_lf_manifest_staleness.py --check
    python patch_lf_manifest_staleness.py
    python patch_lf_manifest_staleness.py --selftest   (run it AFTER applying)
    python patch_lf_manifest_staleness.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

WHAT IT MISSED, MEASURED. On 2026-08-14 `verify-manifest` reported:

    OK  deli_counter    0.88.0 matches certified 0.88.0
    OK  level_factory   0.22.0 matches certified 0.22.0

    deli_counter/VERSION    written 2026-07-25   check.py changed 2026-08-13
    level_factory/VERSION   written 2026-07-28   model.py changed 2026-08-13

Both tools had nineteen days of code changes after their VERSION was last
written, and both reported OK -- because the check compares the pin to the
VERSION file and stops. Two numbers agreeing with each other, and with
nothing on disk.

This is the failure this repo keeps finding. `build_freshness.py` exists
because shells were 4.2 days behind the code that produced them and the nav
gate graded them with full confidence. Every recorded Laser Tag grade was
invalid because it described a greybox draw while the themed draw shipped.
Now the lockstep check, whose entire job is to catch drift, is blind to the
most ordinary kind: someone changed the code and did not bump the version.

WHAT THIS ADDS. A fifth status, STALE, between UNKNOWN and DRIFT:

    OK     the pin matches, and no source file is newer than VERSION
    STALE  the pin matches the VERSION file, but the VERSION file is older
           than the tool's own source -- the pin describes code that is gone

DRIFT and INCOMPATIBLE are untouched: if the numbers already disagree, the
staleness question is moot and the existing message is the more useful one.
STALE is only ever reached from what used to be a bare OK, so no result this
already flagged changes.

HOW STALENESS IS DECIDED. Git history, not mtimes: is the newest commit
touching source newer than the newest commit touching VERSION? Excluded from
"source" are VERSION and CHANGELOG (they move as part of the bump) plus
`.gitignore`, `.gitattributes`, `.editorconfig` and LICENSE -- repo
furniture, not code.

IT WAS MTIMES FIRST, AND THAT WAS WRONG. The first cut compared the newest
source mtime against VERSION's, and on its first real run it reported SIX of
ten tools stale, every one naming `.gitignore`. Excluding `.gitignore` would
only have moved the problem to whatever non-source file came next: an
exclusion list always trails what gets added. `docs/CLEANUP.md` settled the
same argument for artifact sweeping -- allow-list, never guess -- and history
is the allow-list that cannot fall behind, because it knows precisely which
commit touched what. It is also immune to fresh clones, which rewrite every
mtime and no commit dates at all.

WHEN IT CANNOT KNOW, IT SAYS NOTHING. No git, not a repo, or no commit
touching VERSION -> the tool reports OK. A warning nobody can act on is
worse than silence.

EXIT CODE. STALE returns EXIT_FINDINGS (1), or EXIT_CONFIG (3) under
`--strict`, matching how DRIFT is already handled.

EXPECT DRIFT ON deli_counter AND level_factory UNTIL THE MANIFEST IS
RE-CERTIFIED -- they were bumped to 0.89.0 and 0.23.0 on 2026-08-14 and the
manifest still pins 0.88.0 and 0.22.0. That is DRIFT doing its job, not this
patch misfiring.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CONTRACTS = Path("level_factory/packages/tools/contracts.py")
COMMANDS = Path("level_factory/apps/cli/commands/__init__.py")
SIDECAR = ".pre_stale"


OLD_SEV = "_SEVERITY = {OK: 0, UNKNOWN: 1, DRIFT: 2, INCOMPATIBLE: 3}"

NEW_SEV = '''#: The pin matches the VERSION file, and the VERSION file is older than the
#: code it names. Sits below DRIFT because the numbers still agree -- what has
#: gone stale is the claim that the number means anything.
STALE = "STALE"
_SEVERITY = {OK: 0, UNKNOWN: 1, STALE: 2, DRIFT: 3, INCOMPATIBLE: 4}
'''


OLD_MSG = '''        if self.status == OK:
            return f"{self.installed} matches certified {self.certified}"'''

NEW_MSG = '''        if self.status == OK:
            return f"{self.installed} matches certified {self.certified}"
        if self.status == STALE:
            return (f"{self.installed} matches certified {self.certified}, but "
                    f"VERSION is older than the code it names"
                    + (f" ({self.stale_because})" if self.stale_because else "")
                    + " -- bump the tool version, then re-certify")'''


OLD_FIELDS = '''    status: str
    source: str  # "lock" or "grounded"'''

NEW_FIELDS = '''    status: str
    source: str  # "lock" or "grounded"
    #: For STALE: the newest source file that outran VERSION. Naming it is the
    #: difference between a verdict and a place to look.
    stale_because: str | None = None'''


OLD_DICT = '''            "adapter": self.adapter_id, "certified": self.certified,
            "installed": self.installed, "status": self.status,
            "certified_from": self.source,'''

NEW_DICT = '''            "adapter": self.adapter_id, "certified": self.certified,
            "installed": self.installed, "status": self.status,
            "certified_from": self.source,
            "stale_because": self.stale_because,'''


OLD_VERIFY = '''        results.append(ContractResult(
            adapter_id=name,
            certified=pinned,
            installed=installed.get(name),
            status=compare(pinned, installed.get(name)),
            source="factory.manifest",
        ))
    return results'''

NEW_VERIFY = '''        status = compare(pinned, installed.get(name))
        because = None
        if status == OK:
            # ONLY from OK. If the numbers already disagree the staleness
            # question is moot, and DRIFT's message is the more useful one.
            from pathlib import Path as _P
            tool_dir = _P(str(factory_root)) / str(
                manifest["tools"][name].get("path", name))
            because = stale_source(tool_dir)
            if because:
                status = STALE
        results.append(ContractResult(
            adapter_id=name,
            certified=pinned,
            installed=installed.get(name),
            status=status,
            source="factory.manifest",
            stale_because=because,
        ))
    return results


def stale_source(tool_dir) -> str | None:
    """Name a source file whose last commit is newer than VERSION's.

    ASKS GIT, NOT THE FILESYSTEM. The first version of this compared mtimes
    and reported six of ten tools stale, every one of them naming
    `.gitignore` -- a file that is repo configuration, not code. Excluding
    `.gitignore` would only have moved the problem to the next non-source
    file, because an exclusion list always trails whatever gets added next.
    `docs/CLEANUP.md` already settled this argument for artifact sweeping:
    allow-list, never guess. History is the allow-list that cannot fall
    behind -- it knows exactly which commit touched what.

    ``None`` when the answer is not knowable: no git, not a repo, no commit
    touching VERSION, or a shallow clone. An unknowable answer is reported as
    OK rather than as a warning nobody can act on.

    Robust to fresh clones, which is what killed the mtime version: cloning
    rewrites every mtime but not a single commit date.
    """
    import subprocess
    from pathlib import Path as _P
    root = _P(str(tool_dir))
    if not (root / ".git").exists():
        return None

    #: Files whose change is not a code change. VERSION and CHANGELOG move as
    #: part of the bump itself; the rest is repo furniture.
    skip = ["VERSION", "CHANGELOG.md", ".gitignore", ".gitattributes",
            ".editorconfig", "LICENSE", "LICENSE.md"]

    def _git(args):
        try:
            r = subprocess.run(["git", "-C", str(root)] + args,
                               capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            return None
        return r.stdout.strip() if r.returncode == 0 else None

    when_version = _git(["log", "-1", "--format=%ct", "--", "VERSION"])
    if not (when_version or "").isdigit():
        return None

    pathspec = ["."] + [f":(exclude){s}" for s in skip]
    when_source = _git(["log", "-1", "--format=%ct", "--"] + pathspec)
    if not (when_source or "").isdigit():
        return None
    if int(when_source) <= int(when_version):
        return None

    sha = _git(["log", "-1", "--format=%H", "--"] + pathspec)
    if not sha:
        return "a commit newer than VERSION"
    names = (_git(["show", "--name-only", "--format=", sha]) or "").split()
    names = [n for n in names if n not in skip]
    if not names:
        return "a commit newer than VERSION"
    head = names[0]
    return head if len(names) == 1 else f"{head} +{len(names) - 1} more"'''


OLD_EXIT = '''    if worst == contracts.DRIFT:
        return EXIT_CONFIG if getattr(args, "strict", False) else EXIT_FINDINGS'''

NEW_EXIT = '''    if worst == contracts.DRIFT:
        return EXIT_CONFIG if getattr(args, "strict", False) else EXIT_FINDINGS
    if worst == getattr(contracts, "STALE", "STALE"):
        # A pin that matches a VERSION file older than its own code is not a
        # pass. Same exit treatment as DRIFT, because it wants the same thing
        # doing: bump the tool, then re-certify the set.
        return EXIT_CONFIG if getattr(args, "strict", False) else EXIT_FINDINGS'''


EDITS = {
    CONTRACTS: ((OLD_SEV, NEW_SEV), (OLD_FIELDS, NEW_FIELDS),
                (OLD_DICT, NEW_DICT), (OLD_MSG, NEW_MSG),
                (OLD_VERIFY, NEW_VERIFY)),
    COMMANDS: ((OLD_EXIT, NEW_EXIT),),
}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _find(body: str, anchor: str):
    candidate = _as(anchor, _eol(body))
    return candidate, body.count(candidate)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def selftest(root: Path) -> int:
    """Exercise the rule against real git repositories, not fixtures."""
    import importlib.util
    import shutil
    import subprocess
    import tempfile
    import time

    spec = importlib.util.spec_from_file_location(
        "_contracts_under_test", root / CONTRACTS)
    mod = importlib.util.module_from_spec(spec)
    # REGISTER BEFORE EXEC. `contracts.py` uses `from __future__ import
    # annotations`, so @dataclass resolves field types via sys.modules -- and
    # a module loaded by spec alone is not there yet, which kills the
    # decorator on `str | None`. A harness artefact, not a defect in the file
    # under test.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "STALE"):
        print("  the patched contracts.py has no STALE -- not applied")
        return 1

    bad = 0

    def check(label, got, want):
        nonlocal bad
        ok = got == want
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}: {got!r}")

    tmp = Path(tempfile.mkdtemp())
    try:
        tool = tmp / "widget"
        (tool / "pkg").mkdir(parents=True)

        def git(*args):
            subprocess.run(["git", "-C", str(tool)] + list(args),
                           check=True, capture_output=True)

        (tool / "VERSION").write_text("0.1.0\n", encoding="utf-8")
        (tool / "pkg" / "core.py").write_text("x\n", encoding="utf-8")
        (tool / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(tool)], check=True,
                       capture_output=True)
        git("config", "user.email", "t@t")
        git("config", "user.name", "t")
        git("add", "-A")
        git("commit", "-qm", "seed")
        check("VERSION committed with the code", mod.stale_source(tool), None)

        # THE CASE THAT BROKE THE MTIME VERSION: .gitignore is not code.
        time.sleep(1.1)
        (tool / ".gitignore").write_text("*.pyc\n*.log\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-qm", "touch gitignore")
        check("a .gitignore commit is not code", mod.stale_source(tool), None)

        # a real code change after VERSION -> stale, and it names the file
        time.sleep(1.1)
        (tool / "pkg" / "core.py").write_text("y\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-qm", "code change")
        check("code newer than VERSION", mod.stale_source(tool), "pkg/core.py")

        # bumping VERSION clears it
        time.sleep(1.1)
        (tool / "VERSION").write_text("0.2.0\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-qm", "0.2.0")
        check("after the bump", mod.stale_source(tool), None)

        # not a repo at all -> unknowable, so silent
        plain = tmp / "plain"
        plain.mkdir()
        (plain / "VERSION").write_text("1.0.0\n", encoding="utf-8")
        check("no git repo", mod.stale_source(plain), None)

        # severity ordering, so worst_status still escalates
        for lo, hi in ((mod.OK, mod.STALE), (mod.STALE, mod.DRIFT),
                       (mod.DRIFT, mod.INCOMPATIBLE)):
            ok = mod._SEVERITY[lo] < mod._SEVERITY[hi]
            bad += 0 if ok else 1
            print(f"  {'ok  ' if ok else 'FAIL'} {lo} ranks below {hi}")
        check("worst_status surfaces STALE over OK", mod.worst_status([
            mod.ContractResult("a", "1.0.0", "1.0.0", mod.OK, "m"),
            mod.ContractResult("b", "1.0.0", "1.0.0", mod.STALE, "m")]),
            mod.STALE)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("  staleness is read from history, not guessed" if not bad
          else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)
    eol = _eol(body)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()[:70]!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    try:
        compile(out, str(path), "exec")
    except SyntaxError as exc:
        print(f"REFUSING: {path.name} -- the patched file does not parse: {exc}")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    if not check:
        print()
        print("  now run: python -m level_factory verify-manifest --factory .")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
