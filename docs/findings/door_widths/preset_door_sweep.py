"""Every enterable Deli Counter preset, made as Level Factory makes it, linted -- before and after the door widths
(roadmap 197; Deli Counter 0.214.0).

    python docs/findings/door_widths/preset_door_sweep.py <deli_counter dir>

Level Factory builds each mission's own building from a preset at run time (its Deli Counter adapter plans
`presets.make` with the job's seed), so a preset's door that a lint refuses refuses a cold run. This imports the
presets and the lint from the given directory -- the repository, or a scratch copy with the change -- and for
every preset that is not an Empty, in each mode the preset takes ("heist", "assault") and eight seeds
(9000 + 97 k), makes the spec with `presets.make` and runs `layout_lint.lint_spec`. It prints, a preset a line,
the variants made, the FAILs and their rules, and the doors the made specs carry under the contract's
`min_door_width_m`. Prints what it measured and stops.

    python docs/findings/door_widths/preset_door_sweep.py <deli_counter dir> --variants

The adapter also hands a preset the brief's `floors` and `basement` (`new_level.py --floors`, `--basement`,
`--no-basement`), and a preset's own default mode can be neither of the two above (`hospital`'s is
"survival"). `--variants` makes every preset, on one seed (9104), in each of "heist", "assault" and
"survival", at 1 to 4 floors, with a basement and without where the preset takes a basement: a
combination the preset refuses (a TypeError or ValueError) is counted as refused, not made.
"""
import collections
import inspect
import json
import pathlib
import re
import sys

DC = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(DC))

import layout_lint   # noqa: E402
import presets       # noqa: E402
from spec_types import Opening   # noqa: E402

NEED = float(json.loads((DC / "agent_contract.json").read_text(encoding="utf-8"))["clearances"]["min_door_width_m"])
SEEDS = [9000 + 97 * k for k in range(8)]


def narrow(spec):
    n = 0
    for w in (spec.get("ext_walls") or []) + (spec.get("partitions") or []):
        for o in w.get("openings") or []:
            if o.get("kind") == "door":
                width = Opening(kind="door", pos=0.0, width=o.get("width")).resolved()["width"]
                if float(width) < NEED - 1e-9:
                    n += 1
    return n


def _calls(name):
    """(label, kwargs) for every make this run asks of one preset. `basement` only where the preset takes
    one: `auto_shop` and `pawn_shop` do not, and passing it refuses every call."""
    if "--variants" not in sys.argv:
        return [("%s_%d" % (mode, seed), dict(seed=seed, mode=mode))
                for mode in ("heist", "assault") for seed in SEEDS]
    basements = (True, False) if "basement" in inspect.signature(presets.REGISTRY[name]).parameters else (None,)
    out = []
    for mode in ("heist", "assault", "survival"):
        for floors in (1, 2, 3, 4):
            for basement in basements:
                kwargs = dict(seed=9104, mode=mode, floors=floors)
                if basement is not None:
                    kwargs["basement"] = basement
                out.append(("%s_f%d_b%s" % (mode, floors, basement), kwargs))
    return out


def main():
    total = collections.Counter()
    for name in sorted(presets.REGISTRY):
        if presets.REGISTRY[name]().get("facade"):
            continue
        made = fails = doors = refused = 0
        rules = collections.Counter()
        for label, kwargs in _calls(name):
            try:
                spec = presets.make(name, **kwargs)
            except (TypeError, ValueError):
                refused += 1
                continue
            made += 1
            _name, f, _w = layout_lint.lint_spec(spec, "%s_%s" % (name, label))
            fails += len(f)
            for msg in f:
                m = re.match(r"\s*(L\d+)", msg)
                rules[m.group(1) if m else msg[:30]] += 1
            doors += narrow(spec)
        total["made"] += made
        total["refused"] += refused
        total["fails"] += fails
        total["doors"] += doors
        print("%-20s made %2d, refused %2d, FAIL %3d %s, doors under %.2f: %d" % (
            name, made, refused, fails, dict(rules) if rules else "", NEED, doors))
    print("all presets: made %d, refused %d, FAIL %d, doors under %.2f: %d" % (
        total["made"], total["refused"], total["fails"], NEED, total["doors"]))


if __name__ == "__main__":
    main()
