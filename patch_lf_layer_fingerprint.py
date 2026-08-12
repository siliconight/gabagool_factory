"""Fingerprint the layer FILE, not the directory it lives in.

Run from the factory root:

    python patch_lf_layer_fingerprint.py --check
    python patch_lf_layer_fingerprint.py

## The defect, measured

    internal error: [Errno 13] Permission denied:
      '...\\jobs\\lot_demo_001.zoo_dressing_build.depot_a01\\out'

`patch_lf_layer_resolve.py` changed what `dressing_glb` and `fixtures_glb`
MEAN -- from "the layer file" to "the directory the layer will be in" -- and
updated two of the three consumers. `validate_configuration` and
`plan_commands` both resolve the directory to a file. `fingerprint_inputs` was
missed: it still did `hash_file(Path(lp))`, and `Path(a_directory).exists()` is
True, so it sailed past the guard and tried to open a directory as a file.
Windows reports that as errno 13.

The lesson is not "add a check". It is that changing the meaning of a spec key
obliges you to find every reader of it, and I found two by editing the ones I
happened to be looking at. `grep dressing_glb` over the package takes one
command and names all three.

## The fix

`resolve_layer` already exists and already knows how to turn a layer directory
into its one file. The fingerprint uses it, like the other two readers.

A layer that cannot be resolved is SKIPPED here rather than raised, because
`validate_configuration` runs first and fails the job with a message naming the
building. Raising here too would replace that message with a stack trace from a
hashing routine.
"""
from __future__ import annotations

import sys
from pathlib import Path

PRES = Path("level_factory/adapters/presentation/__init__.py")
TEST = Path("level_factory/tests/unit/test_fanout.py")

BEFORE = '''\
        for key in ("dressing_glb", "fixtures_glb"):
            for aid, lp in sorted(_layer_map(job_spec.get(key)).items()):
                if not Path(str(lp)).exists():
                    continue
'''

AFTER = '''\
        for key, suffix in (("dressing_glb", "_dressing.glb"),
                            ("fixtures_glb", "_fixtures.glb")):
            for aid, directory in sorted(_layer_map(job_spec.get(key)).items()):
                # The spec names a DIRECTORY -- the job that fills it has not
                # run when the spec is written. Resolve it the same way the
                # other two readers do. This hashed the value directly, and
                # `Path(a_directory).exists()` is True, so it opened a
                # directory as a file: [Errno 13] on Windows, mid-run.
                lp, problem = resolve_layer(directory, suffix)
                if problem:
                    # `validate_configuration` has already failed this job and
                    # named the building. A hashing routine should not be the
                    # thing that reports it.
                    continue
'''


T1_BEFORE = """\
    glb = tmp_path / "shell_dressing.glb"
    glb.write_bytes(b"glb")
    fp = PresentationAdapter().fingerprint_inputs(
        {"dressing_glb": {"": str(glb)}}, {})
    assert "dressing_glb_hash" in fp
    legacy = PresentationAdapter().fingerprint_inputs(
        {"dressing_glb": str(glb)}, {})
    assert legacy["dressing_glb_hash"] == fp["dressing_glb_hash"]
"""

T1_AFTER = """\
    # A layer value is the DIRECTORY the bake publishes into, not the file --
    # the spec is written before the job that fills it has run.
    out = tmp_path / "shell_out"
    out.mkdir()
    (out / "shell_dressing.glb").write_bytes(b"glb")
    fp = PresentationAdapter().fingerprint_inputs(
        {"dressing_glb": {"": str(out)}}, {})
    assert "dressing_glb_hash" in fp
    legacy = PresentationAdapter().fingerprint_inputs(
        {"dressing_glb": str(out)}, {})
    assert legacy["dressing_glb_hash"] == fp["dressing_glb_hash"]
"""

T2_BEFORE = """\
    layers = {}
    for i, aid in enumerate(ARCHETYPES[:LOT]):
        p = tmp_path / f"{aid}_dressing.glb"
        p.write_bytes(b"glb" + bytes([i]))
        layers[aid] = str(p)
"""

T2_AFTER = """\
    layers = {}
    for i, aid in enumerate(ARCHETYPES[:LOT]):
        out = tmp_path / aid
        out.mkdir()
        (out / f"{aid}_dressing.glb").write_bytes(b"glb" + bytes([i]))
        layers[aid] = str(out)
"""


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    edits = [(PRES, "fingerprint resolves the layer before hashing it",
              BEFORE, AFTER),
             (TEST, "test: the shell's layer value is a directory",
              T1_BEFORE, T1_AFTER),
             (TEST, "test:every building's layer value is a directory",
              T2_BEFORE, T2_AFTER)]
    for path in (PRES, TEST):
        if not path.is_file():
            print(f"[patch] {path} not found -- run from the factory root")
            return 1
    files = {}
    for path in (PRES, TEST):
        raw = path.read_bytes()
        crlf = b"\r\n" in raw
        files[path] = (raw, crlf, raw.decode("utf-8").replace("\r\n", "\n"))
        print(f"[patch] {path}: {len(raw)} bytes, "
              f"endings={'CRLF' if crlf else 'LF'}")
    problems = []
    for path, name, before, after in edits:
        text = files[path][2]
        if after in text:
            print(f"[patch]   ALREADY APPLIED: {name}")
        elif before not in text:
            print(f"[patch]   ANCHOR NOT FOUND: {name}")
            problems.append(name)
        elif text.count(before) != 1:
            print(f"[patch]   ANCHOR NOT UNIQUE ({text.count(before)}x): {name}")
            problems.append(name)
    if problems:
        print(f"[patch] REFUSING to write: {len(problems)} anchor(s) failed.")
        return 1
    for path, name, before, after in edits:
        raw, crlf, text = files[path]
        if after in text:
            continue
        files[path] = (raw, crlf, text.replace(before, after))
        print(f"[patch]   applied: {name}")
    if check_only:
        print("[patch] --check: no write")
        return 0
    for path, (raw, crlf, text) in files.items():
        payload = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
        path.write_bytes(payload)
        print(f"[patch] wrote {path}: {len(raw)} -> {len(payload)} bytes "
              f"({len(payload) - len(raw):+d})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
