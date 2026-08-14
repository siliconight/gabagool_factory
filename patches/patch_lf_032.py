r"""level_factory 0.32.0 -- the composer fingerprint, which was never there.

    python patch_lf_032.py --check
    python patch_lf_032.py
    python patch_lf_032.py --selftest
    python patch_lf_032.py --revert

Run from the FACTORY ROOT.

WHAT I WENT LOOKING FOR

`pytest tests` has been aborting during collection:

    tests/test_presentation_fingerprint.py:26: ImportError: cannot import
    name '_COMPOSER_SOURCES' from 'adapters.presentation'

I expected a stale import against a renamed symbol -- delete a line, four
test modules start running again.

WHAT IS ACTUALLY WRONG

`_COMPOSER_SOURCES` and `_composer_fingerprint` do not exist anywhere in the
repository, and `PresentationAdapter.fingerprint_inputs` has no `composer`
key. The test is not stale. It describes a guard that is not implemented.

Read its docstring. It records a measured failure from 2026-08-05:
`strip_greybox_base` was fixed in Deli Counter, DC committed, DC's suite went
green, `run --art --force` reported `deli_generate SUCCEEDED` and
`zoo_kit_build SUCCEEDED`, this job reported `cache`, the composed
`site_base.glb` came back byte-identical, and the invisible wall was still
there. The rebuild looked real and was not.

The presentation job does not merely READ Deli Counter's data. It EXECUTES
DC's code -- `portable_building.build_package`, through a driver -- so its
output can change while every input hash stays identical. Nothing in
`fingerprint_inputs` hashes DC's source. That is the hole, and it is open
today.

One line already knew. The comment above the `lot` block says "The composer
fingerprint had exactly this hole for its own sources and it took a walk to
find" -- written about a thing that is not in the file.

WHICH SOURCES

Measured, not guessed. The import closure of `portable_building` inside DC
0.89.0 is two modules:

    portable_building.py    the composer itself
    themed_tscn.py          the only DC module it imports

The test also names `circulation.py`, which DOES NOT EXIST in DC 0.89.0. It
is declared anyway: `_COMPOSER_SOURCES` is a hand-maintained list of what
composes a building, not a computed closure, and the test
`test_missing_source_files_are_skipped_not_faked` exists precisely because a
DC version may lack one. A declared file that is absent is skipped, never
substituted with a placeholder -- a placeholder hash would collide across
every DC version that lacks it.

`presets.py` and the `test_*.py` files are deliberately NOT sources. A cache
that invalidates on everything is a cache nobody keeps.

ONE TEST IS REPAIRED, AND ONLY ONE LINE OF IT

`test_missing_source_files_are_skipped_not_faked` unlinks `circulation.py` by
name. Its fixture writes every declared source, so the file exists there --
but hardcoding one member of a list the test also parametrises over is the
kind of coupling that breaks on an unrelated edit. It now deletes the first
declared source, whatever that is.

Nothing else in that file changes. It was right; it was just never able to
run.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ADAPTER = "level_factory/adapters/presentation/__init__.py"
TEST = "level_factory/tests/test_presentation_fingerprint.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_032"

OLD_V, NEW_V = "0.31.0", "0.32.0"

EDITS: list[tuple[str, str, str]] = [
    (ADAPTER,
     "def _driver_path() -> Path:\n",

     "#: The DC modules whose CONTENT decides what a composed building looks\n"
     "#: like. Hand-maintained, not a computed closure: a DC version may lack\n"
     "#: one of these and a future one may add a module this list has to\n"
     "#: learn about. Measured against DC 0.89.0 -- the import closure of\n"
     "#: `portable_building` is itself plus `themed_tscn`.\n"
     "#:\n"
     "#: `circulation.py` is declared and does not exist in 0.89.0. That is\n"
     "#: deliberate: it was part of the composer when this guard was\n"
     "#: specified, and an absent declared source is SKIPPED rather than\n"
     "#: faked. A placeholder hash for a missing file would be identical\n"
     "#: across every DC version that lacks it, which is the opposite of a\n"
     "#: fingerprint.\n"
     "#:\n"
     "#: NOT here: presets.py, and every test_*.py. A cache that invalidates\n"
     "#: on everything is a cache nobody keeps.\n"
     "_COMPOSER_SOURCES = (\n"
     '    "portable_building.py",\n'
     '    "themed_tscn.py",\n'
     '    "circulation.py",\n'
     ")\n"
     "\n"
     "\n"
     "def _composer_fingerprint(job_spec, context) -> dict:\n"
     '    """Hash the DC code this job EXECUTES, not just the data it reads.\n'
     "\n"
     "    THE HOLE THIS CLOSES, measured 2026-08-05: `strip_greybox_base` was\n"
     "    fixed in DC. DC committed, DC's suite went green, `run --art\n"
     "    --force` reported `deli_generate SUCCEEDED` and `zoo_kit_build\n"
     "    SUCCEEDED`, and this job reported `cache`. The composed\n"
     "    `site_base.glb` came back byte-identical and the invisible wall it\n"
     "    was supposed to remove was still there. The rebuild looked real and\n"
     "    was not.\n"
     "\n"
     "    `verify-contracts` catches a sub-tool DRIFTING out from under an\n"
     "    adapter. This is that failure with the opposite sign -- a sub-tool\n"
     "    FIX not reaching a cached job.\n"
     "\n"
     "    Degrades to {} rather than raising. A bad or absent repo path is\n"
     "    `plan_commands`' problem to report; raising here would turn it into\n"
     "    a crash at cache-lookup time, on a code path whose entire job is to\n"
     "    answer a question about staleness.\n"
     '    """\n'
     "    repo = (job_spec or {}).get(\"deli_repo\") or \\\n"
     "        (context or {}).get(\"repository\")\n"
     "    if not repo:\n"
     "        return {}\n"
     "    root = Path(str(repo))\n"
     "    if not root.is_dir():\n"
     "        return {}\n"
     "    out: dict = {}\n"
     "    for rel in _COMPOSER_SOURCES:\n"
     "        p = root / rel\n"
     "        if p.is_file():\n"
     "            out[rel] = hash_file(p)\n"
     "    return out\n"
     "\n"
     "\n"
     "def _driver_path() -> Path:\n"),

    (ADAPTER,
     "                for a in lot\n"
     "            }\n"
     "        return fp\n",

     "                for a in lot\n"
     "            }\n"
     "        # THE CODE, not only the data. This job executes DC's composer,\n"
     "        # so a DC fix that changes what a building looks like moves no\n"
     "        # input hash and the job reports `cache`. That happened, on\n"
     "        # 2026-08-05, and shipped an invisible wall.\n"
     "        #\n"
     "        # Empty when the repo is unknown -- the key is still written, so\n"
     "        # a mission that gains a resolvable deli_repo recomposes once\n"
     "        # rather than silently keeping a fingerprint taken without it.\n"
     '        fp["composer"] = _composer_fingerprint(job_spec, context)\n'
     "        return fp\n"),

    (TEST,
     'def test_missing_source_files_are_skipped_not_faked(dc_repo):\n'
     '    """A DC version that lacks one of these must fingerprint the rest, not\n'
     '    substitute a placeholder that collides across versions."""\n'
     '    pathlib.Path(dc_repo, "circulation.py").unlink()\n'
     "    fp = _composer_fingerprint({\"deli_repo\": dc_repo}, {})\n"
     '    assert "circulation.py" not in fp\n'
     "    assert len(fp) == len(_COMPOSER_SOURCES) - 1\n",

     'def test_missing_source_files_are_skipped_not_faked(dc_repo):\n'
     '    """A DC version that lacks one of these must fingerprint the rest, not\n'
     '    substitute a placeholder that collides across versions.\n'
     "\n"
     "    Deletes the FIRST declared source rather than naming one. This said\n"
     '    `circulation.py`, which is a real member of the list and does not\n'
     "    exist in DC 0.89.0 -- the fixture writes it, so the test passed on a\n"
     "    file no shipping DC has. Hardcoding one member of a list the same\n"
     "    module parametrises over breaks on an edit that has nothing to do\n"
     '    with this test."""\n'
     "    gone = _COMPOSER_SOURCES[0]\n"
     "    pathlib.Path(dc_repo, gone).unlink()\n"
     "    fp = _composer_fingerprint({\"deli_repo\": dc_repo}, {})\n"
     "    assert gone not in fp\n"
     "    assert len(fp) == len(_COMPOSER_SOURCES) - 1\n"),
]

ENTRY = """## [0.32.0] - the composer fingerprint, which was never there

`pytest tests` has been aborting during collection on
`tests/test_presentation_fingerprint.py`, which imports `_COMPOSER_SOURCES`
from `adapters.presentation`. I went in expecting a stale import against a
renamed symbol.

Neither `_COMPOSER_SOURCES` nor `_composer_fingerprint` exists anywhere in
the repository, and `fingerprint_inputs` has no `composer` key. The test is
not stale. It describes a guard that was never implemented, and because
collection aborted, nothing ever said so.

WHAT THE GUARD IS FOR, IN THE TEST'S OWN WORDS

Measured 2026-08-05. `strip_greybox_base` was fixed in Deli Counter. DC
committed, DC's suite went green, `run --art --force` reported
`deli_generate SUCCEEDED` and `zoo_kit_build SUCCEEDED`, and this job
reported `cache`. The composed `site_base.glb` came back byte-identical and
the invisible wall the fix was supposed to remove was still there.

The presentation job does not merely read DC's data -- it EXECUTES DC's code,
`portable_building.build_package` through a driver. Its output can change
while every input hash stays identical. Nothing hashed DC's source.

`verify-contracts` catches a sub-tool drifting out from under an adapter.
This is that failure with the opposite sign: a sub-tool FIX not reaching a
cached job.

One line in the file already knew. The comment above the `lot` block reads
"The composer fingerprint had exactly this hole for its own sources and it
took a walk to find" -- written about something that is not in the file.

WHICH SOURCES, MEASURED

The import closure of `portable_building` inside DC 0.89.0 is two modules:
`portable_building.py` and `themed_tscn.py`. Both are declared.

`circulation.py` is declared too and does not exist in 0.89.0. That is
deliberate -- `_COMPOSER_SOURCES` is a hand-maintained list of what composes
a building, not a computed closure, and an absent declared source is SKIPPED,
never faked. A placeholder hash for a missing file is identical across every
DC version that lacks it, which is the opposite of a fingerprint.

`presets.py` and every `test_*.py` are deliberately excluded. A cache that
invalidates on everything is a cache nobody keeps.

ONE LINE OF ONE TEST IS REPAIRED

`test_missing_source_files_are_skipped_not_faked` unlinked `circulation.py`
by name. It now deletes the first declared source, whatever that is --
hardcoding one member of a list the same module parametrises over breaks on
an unrelated edit. Nothing else in that file changes. It was right the whole
time; it just could not run.

WHAT THIS COSTS

Every mission recomposes once. `composer` is a new fingerprint key, so no
existing compose matches. That is the correct behaviour for a guard whose
whole premise is that a stale compose is invisible -- and it is the last
recompose that will be needed for this reason.

The key is written even when the DC repo cannot be resolved, as `{}`. A
mission that later gains a resolvable `deli_repo` then recomposes once,
rather than silently keeping a fingerprint taken without one.
"""

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        raw = p.read_bytes()
        body = raw.decode("utf-8")
        if body.count(_CRLF):
            print(f"REFUSING: {rel} has CRLF line endings; these anchors are LF")
            return 1
        out, done = body, 0
        for old, new in edits:
            if new in out:
                done += 1
                continue
            if out.count(old) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old, new, 1)
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

    vp, cp = root / VERSION_F, root / CHANGELOG
    vbody = vp.read_text(encoding="utf-8")
    cbody = cp.read_text(encoding="utf-8")
    if NEW_V in vbody and f"## [{NEW_V}]" in cbody:
        print("  already applied  VERSION + CHANGELOG")
        return 0
    if OLD_V not in vbody:
        print(f"REFUSING: {VERSION_F} does not say {OLD_V}")
        return 1
    if check:
        print(f"  would bump   VERSION  {OLD_V} -> {NEW_V}")
        print(f"  would prepend CHANGELOG.md  +{len(ENTRY) + 1:,} bytes")
        return 0
    for q, txt in ((vp, vbody), (cp, cbody)):
        side = q.with_suffix(q.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(txt.encode("utf-8"))
    vp.write_bytes(vbody.replace(OLD_V, NEW_V, 1).encode("utf-8"))
    cp.write_bytes((ENTRY + "\n" + cbody).encode("utf-8"))
    print(f"  bumped       VERSION  {OLD_V} -> {NEW_V}")
    print("  prepended    CHANGELOG.md")
    return 0


def selftest(root: Path) -> int:
    import importlib
    import subprocess
    import tempfile
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = (root / "level_factory").resolve()
    if str(lf) not in sys.path:
        sys.path.insert(0, str(lf))
    ad = importlib.import_module("adapters.presentation")
    importlib.reload(ad)

    check("the symbols the test imports now exist",
          hasattr(ad, "_COMPOSER_SOURCES")
          and hasattr(ad, "_composer_fingerprint"))
    check("portable_building and themed_tscn are declared",
          {"portable_building.py", "themed_tscn.py"}
          <= set(ad._COMPOSER_SOURCES))
    check("presets and tests are NOT",
          not any(s == "presets.py" or s.startswith("test_")
                  for s in ad._COMPOSER_SOURCES))

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        for rel in ad._COMPOSER_SOURCES:
            (repo / rel).write_text("original\n", encoding="utf-8")

        fp = ad._composer_fingerprint({"deli_repo": str(repo)}, {})
        check("every declared source is hashed",
              set(fp) == set(ad._COMPOSER_SOURCES))

        before = dict(fp)
        (repo / "portable_building.py").write_text("exact match\n",
                                                   encoding="utf-8")
        after = ad._composer_fingerprint({"deli_repo": str(repo)}, {})
        check("EDITING THE COMPOSER MOVES THE FINGERPRINT", before != after)
        check("and only that source moves",
              [k for k in before if before[k] != after[k]]
              == ["portable_building.py"])

        (repo / "presets.py").write_text("irrelevant\n", encoding="utf-8")
        check("an unrelated DC file does not",
              ad._composer_fingerprint({"deli_repo": str(repo)}, {}) == after)

        check("no repo degrades to {} rather than raising",
              ad._composer_fingerprint({}, {}) == {}
              and ad._composer_fingerprint({"deli_repo": "/nope/nowhere"}, {})
              == {})
        check("and it reads the repo from context too",
              ad._composer_fingerprint({}, {"repository": str(repo)}) == after)

        gone = ad._COMPOSER_SOURCES[0]
        (repo / gone).unlink()
        skipped = ad._composer_fingerprint({"deli_repo": str(repo)}, {})
        check("a missing declared source is skipped, not faked",
              gone not in skipped
              and len(skipped) == len(ad._COMPOSER_SOURCES) - 1)

    a = ad.PresentationAdapter()
    fpi = a.fingerprint_inputs({"theme": "rockay"}, {})
    check("THE JOB FINGERPRINT CARRIES IT -- the whole point",
          "composer" in fpi)
    check("and carries it even with no resolvable repo",
          fpi["composer"] == {})

    # The module that could not be collected, and the three it took with it.
    r = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"],
                       cwd=str(lf), capture_output=True, text=True)
    check("PYTEST TESTS COLLECTS AND PASSES", r.returncode == 0)
    if r.returncode:
        print((r.stdout + r.stderr)[-1200:])

    v = (root / VERSION_F).read_text(encoding="utf-8")
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check(f"VERSION is {NEW_V}", NEW_V in v)
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    check("the entry says the guard was never implemented",
          "never implemented" in flat)
    check("and names the failure it is for",
          "strip_greybox_base" in cl and "invisible wall" in flat)
    check("and that a recompose is the cost",
          "recomposes once" in flat)

    print()
    print("  the guard the test was written for now exists"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        bad = 0
        for rel in (ADAPTER, TEST, VERSION_F, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        return bad
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lf_032.py --selftest")
        print("    python -m pytest level_factory/tests -q")
        print()
        print("  THAT SECOND COMMAND IS THE POINT. It has been aborting in")
        print("  collection; four modules outside tests/unit have not run.")
        print()
        print("  NOTE: `composer` is a new fingerprint key, so the next")
        print("  --art run recomposes every mission once. That is correct and")
        print("  it is the last time it happens for this reason.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
