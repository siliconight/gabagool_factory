"""The presets' half of Deli Counter 0.214.0's door widths: every walkable door a preset writes at the contract's
minimum (`patch_dc_door_width.py` imports `widen`; run alone it rewrites a `presets.py` given on the command line).

A door dict -- `"kind": "door"` with a literal `"width"` under 1.25 -- inside a preset function that builds an
enterable building has its width replaced by `DOOR_W`, the module's name for `agent_contract.min_door_width()`.
The Empties' functions (`EMPTY_FUNCTIONS`) keep theirs: their doors are shut and nothing walks through them. The
counts are asserted: `EXPECT` doors in `EXPECT_FUNCTIONS` functions, or nothing is changed.
"""
import ast
import re
import sys

EMPTY_FUNCTIONS = {"empty_rowhome", "empty_midrise"}
EXPECT = 61
EXPECT_FUNCTIONS = 15
DOOR = re.compile(r'(["\']kind["\']\s*:\s*["\']door["\'][^}\n]{0,200}?["\']width["\']\s*:\s*)([0-9.]+)')
CONSTANT_ANCHOR = "import stoop as stoop_geom\n"
CONSTANT = ("import stoop as stoop_geom\n"
            "import agent_contract\n"
            "\n"
            "#: THE CONTRACT'S DOOR (0.214.0, factory roadmap 197): every walkable door a\n"
            "#: preset writes is `clearances.min_door_width_m`. 61 were written at 1.1 and\n"
            "#: 1.2 m, under the contract's 1.25, as were 152 doors authored in the library's\n"
            "#: specs (`migrate_door_width.py`) and 47 that took this builder's old 1.2\n"
            "#: default. An Empty's doors are shut and nothing walks through them, so\n"
            "#: `empty_rowhome` and `empty_midrise` keep theirs.\n"
            "DOOR_W = agent_contract.min_door_width()\n")


def widen(src):
    """`src` with every enterable preset's narrow door at `DOOR_W` and the constant declared; asserts the counts."""
    tree = ast.parse(src)
    spans = [(n.lineno, n.end_lineno, n.name) for n in tree.body if isinstance(n, ast.FunctionDef)]
    lines = src.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))

    def owner(offset):
        line = next(i for i in range(len(starts) - 1) if starts[i] <= offset < starts[i + 1]) + 1
        return next((name for a, b, name in spans if a <= line <= b), None)

    edits, funcs = [], set()
    for m in DOOR.finditer(src):
        if float(m.group(2)) >= 1.25:
            continue
        fn = owner(m.start())
        if fn is None or fn in EMPTY_FUNCTIONS:
            continue
        edits.append((m.start(2), m.end(2)))
        funcs.add(fn)
    assert len(edits) == EXPECT and len(funcs) == EXPECT_FUNCTIONS, (len(edits), len(funcs), sorted(funcs))
    out = src
    for a, b in reversed(edits):
        out = out[:a] + "DOOR_W" + out[b:]
    assert out.count(CONSTANT_ANCHOR) == 1, "the import the constant follows"
    return out.replace(CONSTANT_ANCHOR, CONSTANT), sorted(funcs)


if __name__ == "__main__":
    path = sys.argv[1]
    text = open(path, encoding="utf-8", newline="").read()
    new, funcs = widen(text.replace("\r\n", "\n"))
    open(path, "w", encoding="utf-8", newline="").write(new.replace("\n", "\r\n") if "\r\n" in text else new)
    print("%d door(s) in %d preset(s) at DOOR_W: %s" % (EXPECT, len(funcs), ", ".join(funcs)))
