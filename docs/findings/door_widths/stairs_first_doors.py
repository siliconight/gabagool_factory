"""The doors stairs-first generation punches, at their width and at the contract's (roadmap 197; Deli Counter
0.214.0).

    python docs/findings/door_widths/stairs_first_doors.py <deli_counter dir> [--punch W] [--seeds N]

`stair_core._punch_door` puts a door in an enclosure's partition where it crosses a stair landing, at
`_PUNCH_DOOR_W` (1.1 m) -- under the contract's `min_door_width_m` -- and punches none where the crossing is
shorter than that width. Level Factory never builds stairs-first (its Deli Counter adapter passes no
`--stairs-first`), but `new_level.py --stairs-first` does, and `stair_regression.py` (in the pre-commit gate)
proves both generation orders. This generates every multi-storey preset stairs-first, on
`stair_regression`'s own seed schedule (1000 + 37 k) and through its own `generate`, with `_PUNCH_DOOR_W` as
the given directory has it or as `--punch` sets it, and prints, a preset a line: the variants made, the
doors punched, `stair_regression.check_variant`'s failures, `layout_lint`'s FAILs by rule, and the doors
under the contract's minimum (resolved, so a width-less door counts at the directory's own default). Last,
a sha256 over every variant's generated spec (`json.dumps`, keys sorted), so two directories' runs can be
compared for the bytes and not only the counts.

Prints what it measured and stops.
"""
import collections
import hashlib
import json
import pathlib
import re
import sys

ARGS = sys.argv[1:]
DC = pathlib.Path(ARGS[0]).resolve()
sys.path.insert(0, str(DC))


def _opt(flag, cast, default):
    return cast(ARGS[ARGS.index(flag) + 1]) if flag in ARGS else default


import layout_lint       # noqa: E402
import stair_core        # noqa: E402
import stair_regression  # noqa: E402
from spec_types import Opening   # noqa: E402

NEED = float(json.loads((DC / "agent_contract.json").read_text(encoding="utf-8"))["clearances"]["min_door_width_m"])
SEEDS = _opt("--seeds", int, 10)
if "--punch" in ARGS:
    stair_core._PUNCH_DOOR_W = _opt("--punch", float, None)

_punch = stair_core._punch_door
PUNCHED = collections.Counter()


def _counting(p, land, wall_thick):
    hit = _punch(p, land, wall_thick)
    if hit:
        PUNCHED["n"] += 1
    return hit


stair_core._punch_door = _counting


def narrow(spec):
    n = 0
    for w in (spec.get("ext_walls") or []) + (spec.get("partitions") or []):
        for o in w.get("openings") or []:
            if o.get("kind") == "door":
                width = Opening(kind="door", pos=0.0, width=o.get("width")).resolved()["width"]
                if float(width) < NEED - 1e-9:
                    n += 1
    return n


def main():
    print("Deli Counter at %s; _PUNCH_DOOR_W %.2f m; the contract's minimum %.2f m; %d seed(s) a preset"
          % (DC, stair_core._PUNCH_DOOR_W, NEED, SEEDS))
    total = collections.Counter()
    digest = hashlib.sha256()
    for p in stair_regression._multi_story_presets():
        made = fails = lint = doors = 0
        PUNCHED.clear()
        rules = collections.Counter()
        for k in range(SEEDS):
            seed = 1000 + 37 * k
            spec = stair_regression.generate(p, seed, True)
            if spec is None:
                break
            made += 1
            digest.update(json.dumps(spec, sort_keys=True).encode("utf-8"))
            fails += len(stair_regression.check_variant(spec))
            _name, f, _w = layout_lint.lint_spec(spec, "%s_%d" % (p, seed))
            lint += len(f)
            for msg in f:
                m = re.match(r"\s*(L\d+)", msg)
                rules[m.group(1) if m else msg[:30]] += 1
            doors += narrow(spec)
        if not made:
            continue
        for key, value in (("made", made), ("punched", PUNCHED["n"]), ("fails", fails), ("lint", lint),
                           ("doors", doors)):
            total[key] += value
        print("%-20s made %2d, punched %3d, regression failures %d, lint FAIL %3d %s, doors under %.2f: %d"
              % (p, made, PUNCHED["n"], fails, lint, dict(rules) if rules else "", NEED, doors))
    print("all: made %d, punched %d, regression failures %d, lint FAIL %d, doors under %.2f: %d"
          % (total["made"], total["punched"], total["fails"], total["lint"], NEED, total["doors"]))
    print("specs sha256 %s" % digest.hexdigest())


if __name__ == "__main__":
    main()
