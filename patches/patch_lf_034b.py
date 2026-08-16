r"""level_factory 0.34.0 (amendment) -- the test helper, written twice.

    python patches\patch_lf_034b.py --check
    python patches\patch_lf_034b.py
    python patches\patch_lf_034b.py --selftest
    python patches\patch_lf_034b.py --revert

Run from the FACTORY ROOT. Apply AFTER patch_lf_034.py.

WHAT FAILED

    FAILED tests/unit/test_export_layers.py::test_the_gameplay_layer_is_independent
    pathlib/__init__.py:1011: FileExistsError
    1 failed, 5 passed

`_dirs` called `mkdir(parents=True)` with no `exist_ok`, and that one test
calls it twice against the same `tmp_path`, so the second call tried to
create `handoff/out` again.

THE HELPER WAS WRITTEN TWICE

0.34.0's own selftest contains the same helper, and ITS copy reads
`d.mkdir(parents=True, exist_ok=True)`. The selftest therefore passed on the
code path the shipped test file failed on, and the copy I trusted was the one
that will never run in CI. Two derivations of one idea, one of them correct:
the failure this codebase keeps writing docstrings about, committed by the
patch that quotes one of them.

THE FIX IS HERMETIC CALLS, NOT exist_ok

`exist_ok=True` alone makes the crash go away and leaves a worse bug
standing. The second call to `_dirs` would still see directories the FIRST
call created, so a test that asks for "gameplay" and then for "nothing" gets
gameplay both times -- silently, with no exception to notice. It would pass
or fail for reasons unrelated to what it claims to check, which is the exact
disease the 0.34.0 fix was written to cure in `cmd_export`.

So every call now roots itself in `tmp_path / f"case{tag}"`. Calls are
independent by construction rather than by the caller remembering.
`exist_ok=True` goes in as well -- hermetic AND idempotent costs one keyword.

A test is added that asserts the contamination case rather than merely
avoiding it: ask for gameplay, then ask for nothing, and the second answer
must be empty.

`test_it_is_never_narrower_than_the_code_it_replaced` already did this, with
`tmp_path / f"c{compose}l{lux}h{handoff}"` per iteration -- which is why the
exhaustive test passed while the two-line one crashed.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TEST = "level_factory/tests/unit/test_export_layers.py"
SIDECAR = ".pre_034b"

EDITS: list[tuple[str, str, str]] = [
    (TEST,
     "def _dirs(tmp_path, *, compose=False, lux=False, handoff=False):\n"
     '    c = tmp_path / "compose" / "out" / "presentation"\n'
     '    l = tmp_path / "lux" / "out"\n'
     '    h = tmp_path / "handoff" / "out"\n'
     "    if compose:\n"
     "        c.mkdir(parents=True)\n"
     "    if lux:\n"
     "        l.mkdir(parents=True)\n"
     "    if handoff:\n"
     "        h.mkdir(parents=True)\n"
     '    return {"compose_root": c, "lux_dir": l, "handoff_dir": h}\n',

     'def _dirs(tmp_path, *, compose=False, lux=False, handoff=False, tag="0"):\n'
     '    """Three job directories, under a root belonging to THIS call.\n'
     "\n"
     "    HERMETIC BY CONSTRUCTION. Two calls in one test shared `tmp_path`\n"
     "    and the second `mkdir(parents=True)` raised FileExistsError. The\n"
     "    small fix is `exist_ok=True`; the correct one is that a call must\n"
     "    not see what an earlier call created, or a test asking for 'no\n"
     "    layers' after asking for 'gameplay' is handed gameplay and passes\n"
     "    or fails for a reason it does not state.\n"
     '    """\n'
     '    base = tmp_path / f"case{tag}"\n'
     '    c = base / "compose" / "out" / "presentation"\n'
     '    l = base / "lux" / "out"\n'
     '    h = base / "handoff" / "out"\n'
     "    for wanted, d in ((compose, c), (lux, l), (handoff, h)):\n"
     "        if wanted:\n"
     "            d.mkdir(parents=True, exist_ok=True)\n"
     '    return {"compose_root": c, "lux_dir": l, "handoff_dir": h}\n'),

    (TEST,
     "def test_the_gameplay_layer_is_independent(tmp_path):\n"
     "    assert _layers_produced(**_dirs(tmp_path, handoff=True)) == {LAYER_GAMEPLAY}\n"
     "    assert _layers_produced(\n"
     "        **_dirs(tmp_path, compose=True, handoff=True)\n"
     "    ) == {LAYER_ART, LAYER_GAMEPLAY}\n",

     "def test_the_gameplay_layer_is_independent(tmp_path):\n"
     "    # Distinct tags: the second call must not inherit the first's dirs.\n"
     "    assert _layers_produced(\n"
     '        **_dirs(tmp_path, handoff=True, tag="gameplay-only")\n'
     "    ) == {LAYER_GAMEPLAY}\n"
     "    assert _layers_produced(\n"
     '        **_dirs(tmp_path, compose=True, handoff=True, tag="both")\n'
     "    ) == {LAYER_ART, LAYER_GAMEPLAY}\n"
     "\n"
     "\n"
     "def test_two_calls_in_one_test_do_not_contaminate_each_other(tmp_path):\n"
     '    """THE BUG, as an assertion rather than a crash.\n'
     "\n"
     "    Ask for gameplay, then ask for nothing. The second answer must be\n"
     "    empty. Under a shared root the second call inherits the first\n"
     "    call's directory and reports gameplay, with no exception to make\n"
     '    anyone look."""\n'
     "    assert _layers_produced(\n"
     '        **_dirs(tmp_path, handoff=True, tag="a")) == {LAYER_GAMEPLAY}\n'
     '    assert _layers_produced(**_dirs(tmp_path, tag="b")) == set()\n'),
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def _as(text: str, eol: str) -> str:
    return text if eol == "\n" else text.replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here (apply patch_lf_034.py first)")
            return 1
        raw = p.read_bytes()
        eol = _eol(raw)
        out, done = raw.decode("utf-8"), 0
        for old, new in edits:
            old_f, new_f = _as(old, eol), _as(new, eol)
            if new_f in out:
                done += 1
                continue
            if out.count(old_f) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old_f)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old_f, new_f, 1)
        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
        try:
            compile(out, str(p), "exec")
        except SyntaxError as exc:
            print(f"REFUSING: {rel} -- does not parse after the edit: {exc}")
            return 1
        data = out.encode("utf-8")
        if data == raw:
            print(f"  already applied  {rel}")
            continue
        if check:
            print(f"  would patch  {rel}  {len(raw):,} -> {len(data):,} bytes "
                  f"({len(data) - len(raw):+,})")
            continue
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        p.write_bytes(data)
        print(f"  patched      {rel}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import ast
    import subprocess
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = (root / "level_factory").resolve()
    src = (root / TEST).read_text(encoding="utf-8")

    check("each call roots itself in its own subdirectory",
          'base = tmp_path / f"case{tag}"' in src)
    check("and is idempotent as well as hermetic",
          "exist_ok=True" in src)
    # AST, NOT A SUBSTRING. The docstring this patch writes EXPLAINS the bug
    # by quoting `mkdir(parents=True)`, so a text search over the file finds
    # the prose that documents the fix and reports the fix missing. Stripping
    # `#` lines does not help -- it is a docstring, not a comment. Parse it
    # and look at the calls.
    bare = [n.lineno for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "mkdir"
            and not any(k.arg == "exist_ok" for k in n.keywords)]
    check("every mkdir CALL passes exist_ok (prose may quote the old form)",
          not bare)
    if bare:
        print(f"       bare mkdir at line(s): {bare}")
    check("the contamination case is asserted, not merely avoided",
          "test_two_calls_in_one_test_do_not_contaminate_each_other" in src)

    # RUN IT. A helper bug is precisely what a string check cannot see --
    # 0.34.0's selftest passed against its own private copy of this helper.
    print()
    print("  running the unit file that failed --")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/test_export_layers.py"],
        cwd=str(lf), capture_output=True, text=True,
    )
    combined = r.stdout + r.stderr
    for line in combined.strip().splitlines()[-4:]:
        print(f"       {line}")
    check("IT PASSES", r.returncode == 0)
    check("no FileExistsError anywhere in the run",
          "FileExistsError" not in combined)

    print()
    print("  NOT VERIFIED HERE: service + integration. 0.34.0's selftest")
    print("  measured those at 28 passed and this touches one unit file.")

    print()
    print("  the helper is written once, and it is hermetic"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        p = root / TEST
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {TEST}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {TEST}")
        return 0
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lf_034b.py --selftest")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
