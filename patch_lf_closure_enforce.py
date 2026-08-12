r"""Promote the closure verdict from a warning to a wall.

    python patch_lf_closure_enforce.py --check
    python patch_lf_closure_enforce.py
    python patch_lf_closure_enforce.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

`CLOSURE_ENFORCED` was False with a stated precondition: "wants the missing-art
copy fixed first -- otherwise it fails on a defect it did not cause." That is
done, and it took three separate fixes, not one. lot_demo_001 --mode
portable-godot now passes end to end with the engine's own agreement.

AND A SECOND EDIT, WHICH IS WHY THIS IS NOT A ONE-CHARACTER PATCH.
`ClosureResult.ok` reads SEVEN counters. The summary that goes into the
exception names FIVE. `misrooted_resource_count` and
`unresolved_relative_count` were both added after that string was written, and
neither was threaded into it, so an export failing purely on either one would
raise with every number in its own message reading zero:

    EXPORT_CLOSURE_BROKEN: 0 unresolved res:// reference(s), 0 absolute
    path(s), 0 external reference(s), 0 required plugin(s), 0 required
    autoload(s)

Harmless while the flag only printed a warning nobody had to act on. The moment
it raises, that message is the entire diagnosis somebody gets at 2am, and it
would be five zeros and no reason. `patch_lf_score_split.py` wrote the rule
this breaks: "a number that silently describes four fifths of a table is worse
than no number: it looks actionable and is not."

REFUSES if `closure.py` does not carry both counters -- formatting a field the
dataclass does not have turns a closure failure into an AttributeError, which
is a worse error than the one it was reporting.

BLAST RADIUS. Exactly one mission in one mode has been verified. `pure-shell`
and a graybox `--art`-less run have never been scanned under the relative-path
check. Export those next; if one fails, read the verdict before assuming the
gate is wrong, and `--revert` is one command either way.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("level_factory/packages/exporting/export.py")
CLOSURE = Path("level_factory/packages/exporting/closure.py")
SIDECAR = ".pre_enforce"


OLD_FLAG = '''#: Whether a broken resource closure fails the export outright.
#:
#: False for the same reason ``deli_counter.stairwell.CONTAINMENT_ENFORCED`` and
#: ``WALKTEST_ENFORCED`` are: no export has ever been scanned at this point in
#: the pipeline, the first run that did found the current one broken, and
#: promoting on day one would fail every export before anyone has looked at one.
#:
#: The scan ALWAYS runs and ALWAYS writes its verdict to
#: export_closure_scan.json. This flag decides only whether the verdict stops
#: the build. Flipping it is its own pass, and wants the missing-art copy fixed
#: first -- otherwise it fails on a defect it did not cause.
CLOSURE_ENFORCED = False'''

NEW_FLAG = '''#: Whether a broken resource closure fails the export outright.
#:
#: TRUE since 2026-08-12. It was False for the same reason
#: ``deli_counter.stairwell.CONTAINMENT_ENFORCED`` and ``WALKTEST_ENFORCED``
#: are: no export had ever been scanned at this point in the pipeline, the
#: first run that did found the current one broken, and promoting on day one
#: would have failed every export before anyone had looked at one. The stated
#: precondition was "wants the missing-art copy fixed first -- otherwise it
#: fails on a defect it did not cause."
#:
#: That precondition is met, and meeting it took three fixes, not one:
#:
#:   * THE MISSING ART. QA harnesses stripped, and the root `site.tscn` copy
#:     decided by the presentation scene instead of guessed. 21 unresolved -> 0.
#:   * THE SCANNER. It resolved `res://` by suffix -- which Godot has never
#:     done -- and certified the broken package at `ok: true, 0 missing`. With
#:     the suffix match renamed to what it actually finds: 132 misrooted.
#:   * THE PACKAGES. Each building is staged as its own `res://` root and was
#:     copied under another without rewriting. 137 references rerooted, 5 of
#:     which had been resolving to the site's base mesh instead of dangling.
#:
#: lot_demo_001 --mode portable-godot then passed with the engine agreeing:
#: `parser_error_count: 0`, `shader_error_count: 0`, `scene_instantiated: true`,
#: `status: PASS` in a clean Godot 4.7 project.
#:
#: The scan ALWAYS runs and ALWAYS writes its verdict to
#: export_closure_scan.json. This flag decides only whether the verdict stops
#: the build. Setting it back to False for a mode nobody has scanned yet is a
#: legitimate move -- but write down WHICH mode and WHY, because the comment
#: that used to sit here outlived its own reason without anyone noticing.
CLOSURE_ENFORCED = True'''


OLD_SUMMARY = '''        summary = (
            "EXPORT_CLOSURE_BROKEN: %d unresolved res:// reference(s), "
            "%d absolute path(s), %d external reference(s), "
            "%d required plugin(s), %d required autoload(s)"
            % (scan.missing_resource_count, scan.absolute_path_count,
               scan.external_reference_count, scan.required_plugin_count,
               scan.required_autoload_count))'''

NEW_SUMMARY = '''        # EVERY counter `ClosureResult.ok` reads, or the message lies. This
        # reported five of seven for as long as there were seven: an export
        # failing purely on misrooted or unresolved-relative references raised
        # with every number in its own summary reading zero. Tolerable while
        # the flag only printed; the moment it raises, this string IS the
        # diagnosis. A counter added to `ok` gets added here in the same edit.
        summary = (
            "EXPORT_CLOSURE_BROKEN: %d unresolved res:// reference(s), "
            "%d misrooted, %d unresolved relative, %d absolute path(s), "
            "%d external reference(s), %d required plugin(s), "
            "%d required autoload(s)"
            % (scan.missing_resource_count, scan.misrooted_resource_count,
               scan.unresolved_relative_count, scan.absolute_path_count,
               scan.external_reference_count, scan.required_plugin_count,
               scan.required_autoload_count))'''


OLD_RAISE = '''        if CLOSURE_ENFORCED:
            raise ExportClosureError(summary + "\\n  " + detail)'''

NEW_RAISE = '''        if CLOSURE_ENFORCED:
            raise ExportClosureError(
                summary + "\\n  " + detail + "\\n  full verdict: "
                + str(export_dir / "export_closure_scan.json"))'''


EDITS = {TARGET: ((OLD_FLAG, NEW_FLAG), (OLD_SUMMARY, NEW_SUMMARY),
                  (OLD_RAISE, NEW_RAISE))}

#: Fields the new summary formats. Absent from closure.py -> the raise becomes
#: an AttributeError, which is a worse error than the one it reports.
REQUIRED_FIELDS = ("misrooted_resource_count", "unresolved_relative_count")

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
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
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
        print(f"REFUSING: {path.name} -- the patched file does not parse: "
              f"{exc}")
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

    # The new summary formats fields that arrived with patch_lf_closure_relative
    # and patch_lf_closure_misrooted. Check the file, do not assume the order
    # patches were applied in.
    closure = root / CLOSURE
    if not closure.is_file():
        raise SystemExit(f"cannot find {CLOSURE}")
    ctext = closure.read_text(encoding="utf-8")
    absent = [f for f in REQUIRED_FIELDS if f not in ctext]
    if absent:
        print(f"REFUSING: {CLOSURE.name} has no {', '.join(absent)}.")
        print("  The enforced summary formats those fields; without them the "
              "raise is an AttributeError.")
        print("  Apply patch_lf_closure_misrooted.py and "
              "patch_lf_closure_relative.py first.")
        return 1
    print(f"  closure.py carries all {len(REQUIRED_FIELDS)} counter(s) the "
          f"summary needs")

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
