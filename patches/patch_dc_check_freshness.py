r"""Ask whether the shells are current BEFORE grading them.

    python patch_dc_check_freshness.py --check
    python patch_dc_check_freshness.py
    python patch_dc_check_freshness.py --revert

Run from the FACTORY ROOT (the directory holding `deli_counter/`).

`check.py` runs `nav_gate.py --all`, which grades the built shells in `build/`.
It has never asked whether those shells are current. `build_freshness.py`
exists to ask, was written on 2026-08-05 after `nav_gate --all` reported ten
unwalkable stairs across seven shells that were all fossils, and proposes this
exact wiring in its own docstring:

    `check.py` already runs `catalog.py --check` to confirm CATALOG.md is not
    stale. This is the same idea one directory over, for the artefacts every
    downstream gate reads.

It was never wired in. Measured 2026-08-12, seven days later: **every shell in
`build/` is 4.1-4.2 days behind the code**, and a ladder that a fix had already
corrected still climbed into a solid roof, because Zoo dressed a roof slot
baked three days before the slot could express a hole. Four days of every gate
that reads `build/` reporting with total confidence on geometry the code no
longer produces.

ORDER MATTERS, which is why this is not appended at the end. The freshness
check runs IMMEDIATELY BEFORE the nav gate, so a stale library is named before
the gate that misreads it rather than after. Reading "10 stairs unwalkable"
first and "your shells are four days old" second is how the fossils got
believed the first time.

IT FAILS, it does not warn. `--warn-only` exists and is the wrong choice here:
`nav_gate --all` on a stale library does not produce a weaker verdict, it
produces a confident wrong one, and `catalog.py --check` in the same file
already fails for the same reason on a much cheaper mistake.

THE OTHER HALF IS NOT THIS FILE. `check.py` is a source-control gate somebody
runs before committing. Level Factory consumes the same `build/` on every run
and also never asks -- `packages/pipeline/building_library.py::index` reads the
directory and reports missing manifests and unthemeable archetypes without ever
reporting a stale one. That is where today's cost actually landed, and it wants
its own pass.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("deli_counter/check.py")
SIDECAR = ".pre_freshgate"


OLD = '''    print("== nav traversal gate (built shells; needs Godot 4) ==")
    rc |= run(["nav_gate.py", "--all"])'''

NEW = '''    # BEFORE the nav gate, deliberately. That gate grades the shells in
    # build/, and a stale shell does not make it answer weakly -- it makes it
    # answer wrongly with full confidence. `build_freshness.py` was written on
    # 2026-08-05 after `nav_gate --all` reported ten unwalkable stairs across
    # seven shells, every one a fossil, and its docstring proposed exactly this
    # wiring: "check.py already runs catalog.py --check to confirm CATALOG.md
    # is not stale. This is the same idea one directory over, for the artefacts
    # every downstream gate reads."
    #
    # It was not wired in, and on 2026-08-12 every shell in build/ was 4.2 days
    # behind the code. A ladder that `patch_dc_roof_voids.py` had already fixed
    # still climbed into a solid roof, because Zoo dressed a roof slot baked
    # three days before that slot could express a hole. Named first here so the
    # cause is read before the symptom.
    print("== build freshness (are the shells older than the code?) ==")
    rc |= run(["build_freshness.py"])
    print("== nav traversal gate (built shells; needs Godot 4) ==")
    rc |= run(["nav_gate.py", "--all"])'''


EDITS = {TARGET: ((OLD, NEW),)}

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
    # The gate must run before the one it protects, or it is decoration.
    order = out.find('run(["build_freshness.py"])')
    navg = out.find('run(["nav_gate.py", "--all"])')
    if order == -1 or navg == -1 or order > navg:
        print(f"REFUSING: {path.name} -- the freshness check must sit BEFORE "
              f"the nav gate.")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        print(f"  order verified: build_freshness before nav_gate")
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
    if not (root / "deli_counter" / "build_freshness.py").is_file():
        raise SystemExit("deli_counter/build_freshness.py is missing -- this "
                         "patch wires a call to it and would add a dead one")

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
