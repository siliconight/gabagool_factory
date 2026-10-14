"""Which of Deli Counter's numbers might be body-sized? A census of its module-level numeric constants.

    python docs/findings/agent_contract_follows/literal_census.py <deli_counter dir> [--all]

The walker wants one change to `agent_contract.json` to re-size everything once the characters' sizes are known,
so a number whose right value depends on a body -- a width a body passes, a height it stands under or sees over,
a step it climbs, the floor it needs beside a door or a stair -- must be read from the contract, not spelt. This
lists the CANDIDATES; it decides nothing. Each top-level module in the given directory (tests and `migrations/`
left out) is parsed, and every module-level `NAME = <number>` -- a number, or a tuple, list or dict holding only
numbers -- is read with its comment: the `#` lines directly above and any on the line. A constant is FLAGGED
when its name or comment holds a body word (`WORDS`), or its value spells a number the contract carries
(`CONTRACT_VALUES`, the distinctive ones only -- 1.0 and 2.0 are everywhere). Constants assigned from a call,
an expression or another name are not literals and are not listed. With `--all`, unflagged literals print too.

Prints, a flagged constant a line: file:line, name, value, what flagged it, and the comment's first 110
characters; then the counts. Prints what it measured and stops.
"""
import ast
import io
import pathlib
import re
import sys
import tokenize

DC = pathlib.Path(sys.argv[1]).resolve()
SHOW_ALL = "--all" in sys.argv

WORDS = re.compile(r"\b(body|bodies|capsule|radius|agent|navmesh|nav|door\w*|corridor|aisle|headroom|"
                   r"clearance|step|riser|landing|walk\w*|passage|eye|chest|crouch|cover|stand\w*|player|crew|"
                   r"character|person|people|human|shoulder|reach|contract)\b", re.I)
#: The contract's distinctive numbers (agent_contract.json at Deli Counter 0.215.0) and its derived ones.
CONTRACT_VALUES = {0.35: "body radius", 0.4: "bake radius", 1.8: "body height", 1.6: "eye height",
                   1.25: "door minimum", 1.1: "corridor minimum", 0.1025: "unassisted step",
                   1.3: "cover break / vault width", 2.1: "vault height", 1.2: "flight width / crouch"}


def _numbers(node):
    """The numbers a literal node holds, or None when it is not purely numeric."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return [float(node.value)]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        inner = _numbers(node.operand)
        return None if inner is None else [-v if isinstance(node.op, ast.USub) else v for v in inner]
    if isinstance(node, (ast.Tuple, ast.List)):
        out = []
        for elt in node.elts:
            inner = _numbers(elt)
            if inner is None:
                return None
            out += inner
        return out or None
    if isinstance(node, ast.Dict):
        out = []
        for v in node.values:
            inner = _numbers(v)
            if inner is None:
                return None
            out += inner
        return out or None
    return None


def _comments(src):
    """{line: comment text} for every `#` comment in the source."""
    out = {}
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            out[tok.start[0]] = tok.string.lstrip("#:").strip()
    return out


def census(path):
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    comments = _comments(src)
    rows = []
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name, value = node.targets[0].id, node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            name, value = node.target.id, node.value
        else:
            continue
        nums = _numbers(value)
        if nums is None:
            continue
        above = []
        ln = node.lineno - 1
        while ln >= 1 and lines[ln - 1].lstrip().startswith("#"):
            above.insert(0, comments.get(ln, ""))
            ln -= 1
        inline = [comments[n] for n in range(node.lineno, (node.end_lineno or node.lineno) + 1) if n in comments]
        comment = " ".join(above + inline)
        why = sorted({m.group(0).lower() for m in WORDS.finditer(name.replace("_", " ") + " " + comment)})
        hits = sorted({CONTRACT_VALUES[v] for v in nums if v in CONTRACT_VALUES})
        rows.append((node.lineno, name, ast.get_source_segment(src, value), why, hits, comment))
    return rows


def main():
    files = sorted(p for p in DC.glob("*.py") if not p.name.startswith("test_"))
    total = flagged = 0
    for path in files:
        for lineno, name, value, why, hits, comment in census(path):
            total += 1
            if not (why or hits) and not SHOW_ALL:
                continue
            flagged += bool(why or hits)
            reason = "; ".join(filter(None, [",".join(why), ",".join("= " + h for h in hits)])) or "-"
            print("%s:%d  %s = %s  [%s]  %s" % (path.name, lineno, name, " ".join(value.split())[:40], reason,
                                                comment[:110]))
    print("%d module-level numeric constant(s) in %d module(s); %d flagged" % (total, len(files), flagged))


if __name__ == "__main__":
    main()
