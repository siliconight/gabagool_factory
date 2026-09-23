"""Record each occluder's uncovered area, and refuse a bake that caps an
opening.

The bake now skips a module whose mesh leaves more than `HOLE_MIN_M2` of its
own box uncovered. That makes the emitted set correct BY CONSTRUCTION, which
is worth very little on its own: a gate that only trusts the thing it is
gating has learned nothing. So the bake records the measured figure on every
row it emits, and the Python side -- which owns the verdict -- asserts it.

That is a real check on the artefact. If the test is removed, loosened, or
regresses, the numbers in `occluders.json` say so and the export refuses,
rather than a basement quietly disappearing again and waiting for somebody to
walk into it.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GD = ROOT / "level_factory" / "assets" / "godot" / "bake_occluders.gd"
PY = ROOT / "level_factory" / "packages" / "exporting" / "occluders.py"

# --------------------------------------------------------------- gd anchor
GD_A = '''		rows.append({
			"node": String(n.name),
			"module": stem,
'''

GD_N = '''		rows.append({
			"node": String(n.name),
			"module": stem,
			# The measured figure, not a flag: a number a reader can argue
			# with, and the one `occluders.assert_no_capped_openings` checks.
			"uncovered_m2": _r(uncovered),
'''

# --------------------------------------------------------------- py anchors
PY_A1 = '''def _fmt(v) -> str:'''

PY_N1 = '''#: Mirrors `bake_occluders.HOLE_MIN_M2`. Derived there, and the derivation is
#: worth repeating because it is the whole reason this gate exists: the
#: smallest opening this pipeline cuts is a 1.10 x 1.30 m ladder hole
#: (1.43 m2), and the measured uncovered area of every module WITHOUT an
#: opening was 0.000000 m2 across 381 of them on cold run 9072's package.
HOLE_MIN_M2 = 0.25


def assert_no_capped_openings(report: dict) -> int:
    """Raise `OccluderError` if any emitted occluder covers an opening.

    WHAT THIS CAUGHT. Cold run 9072 shipped 17 floor and 17 ceiling occluders
    as full-room horizontal boxes -- `floor_main_floor` was 36 x 13 m, 2 cm
    thick, spanning a stair opening. Standing on that floor and looking down
    the stair, the basement was culled. The walker found it by turning the
    flag off; five gates had passed the package.

    An UNRECOGNISED SHAPE FAILS. A report whose rows carry no `uncovered_m2`
    came from a bake that cannot have taken this measurement, and reading its
    absence as "nothing over the limit" is the `or []` mistake CLAUDE.md
    records -- a checker that cannot find its field has learned nothing.
    """
    rows = report.get("modules")
    if not isinstance(rows, list):
        raise OccluderError("report carries no `modules` list to check")
    missing = [r for r in rows if "uncovered_m2" not in r]
    if missing:
        raise OccluderError(
            "%d of %d occluder row(s) carry no `uncovered_m2`: this bake did "
            "not measure whether its boxes cap an opening, and an unmeasured "
            "occluder must not ship as a measured one"
            % (len(missing), len(rows)))
    bad = [r for r in rows if float(r["uncovered_m2"]) > HOLE_MIN_M2]
    if bad:
        worst = sorted(bad, key=lambda r: -float(r["uncovered_m2"]))[:6]
        lines = ["OCCLUDER_CAPS_AN_OPENING: %d occluder(s) cover more hole "
                 "than %.2f m2" % (len(bad), HOLE_MIN_M2)]
        for r in worst:
            lines.append("    %-34s %-22s %8.2f m2 uncovered"
                         % (str(r.get("module"))[:34], str(r.get("node"))[:22],
                            float(r["uncovered_m2"])))
        lines.append("  an occluder over an opening hides whatever is visible "
                     "through it -- a stair, a mezzanine, a basement")
        raise OccluderError("\\n".join(lines))
    return len(rows)


def _fmt(v) -> str:'''

PY_A2 = '''    if not isinstance(report.get("modules"), list):
        raise OccluderError("report carries no `modules` list")
    return report
'''

PY_N2 = '''    if not isinstance(report.get("modules"), list):
        raise OccluderError("report carries no `modules` list")
    assert_no_capped_openings(report)
    return report
'''


def _apply(path: Path, edits, binary_lf=True) -> None:
    data = path.read_bytes()
    if binary_lf and b"\r\n" in data:
        raise SystemExit(f"REFUSED: {path.name} expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(edits, 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(
                f"REFUSED: {path.name} anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    path.write_bytes(out)
    print(f"{path.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


def main() -> None:
    _apply(GD, ((GD_A, GD_N),))
    _apply(PY, ((PY_A1, PY_N1), (PY_A2, PY_N2)), binary_lf=False)


if __name__ == "__main__":
    main()
